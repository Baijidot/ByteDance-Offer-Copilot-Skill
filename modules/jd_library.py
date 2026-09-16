"""
JD Library — 岗位库 + 简历×JD 匹配分（v3.1）

参考 Jobscan Match Report / Teal Match Score 的做法：
- JD 存进库里（原帖下架也不丢），每条挂一个匹配分
- 匹配分规则层秒出：硬技能命中 / 缺失、软技能、学历与年限硬门槛、关键词高亮
- 深度分析（LLM）按需触发，不阻塞

存储：user_data/jds.json
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional

from modules.profile import HARD_SKILLS, SOFT_SKILLS, extract_skills, profile_as_resume_text


# ═══════════════════════════════════════════════════════════
# Storage
# ═══════════════════════════════════════════════════════════

def _data_path() -> str:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "user_data")
    os.makedirs(base, exist_ok=True)
    return os.path.join(os.path.abspath(base), "jds.json")


def _load() -> dict:
    path = _data_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "jds" in data:
                return data
        except Exception:
            pass
    return {"jds": []}


def _save(data: dict) -> None:
    with open(_data_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _find(data: dict, jd_id: str) -> Optional[dict]:
    for jd in data["jds"]:
        if jd["id"] == jd_id or jd["id"].startswith(jd_id):
            return jd
    return None


# ═══════════════════════════════════════════════════════════
# Rule-layer match — 参考 Jobscan：硬技能 / 软技能 / 硬门槛
# ═══════════════════════════════════════════════════════════

def _extract_soft(text: str) -> list:
    found = []
    lower = text.lower()
    for s in SOFT_SKILLS:
        if s.lower() in lower:
            found.append(s)
    return found


def _degree_rank(word: str) -> int:
    order = {"大专": 1, "专科": 1, "本科": 2, "学士": 2, "硕士": 3, "研究生": 3, "博士": 4}
    for k, v in order.items():
        if k in (word or ""):
            return v
    return 0


def _jd_hard_requirements(jd_text: str, profile: dict) -> list:
    """学历 / 年限 / 特定要求的硬门槛检查。"""
    flags = []
    # 学历
    m = re.search(r"(博士|硕士|研究生|本科|大专)(?:及以上|以上|学历)", jd_text)
    if m:
        need = _degree_rank(m.group(1))
        have = _degree_rank((profile.get("education") or {}).get("degree", ""))
        if have and need and have < need:
            flags.append({"type": "degree", "level": "high",
                          "text": f"JD 要求{m.group(1)}及以上，你是{(profile.get('education') or {}).get('degree')}——大概率过不了机筛，除非有内推"})
    # 年限
    m = re.search(r"(\d+)\s*年(?:及)?以上[^\n，,。；;]{0,12}?经验", jd_text)
    if m:
        years = int(m.group(1))
        if profile.get("job_type") in ("校招", "实习") or not profile.get("experience"):
            flags.append({"type": "experience", "level": "high" if years >= 3 else "medium",
                          "text": f"JD 要求 {years} 年以上经验，这是社招岗——校招/实习身份投递基本无效，确认一下是不是投错通道"})
    # 985/211
    if re.search(r"(985|211|双一流|重点院校|QS\s*\d+)", jd_text):
        flags.append({"type": "school", "level": "medium", "text": "JD 提到院校门槛（985/211/双一流），如果不满足，简历里项目和数据要更硬"})
    # 英语
    if re.search(r"(英语|English).{0,10}(流利|工作语言|口语|六级|CET-?6|雅思|托福)", jd_text, re.IGNORECASE):
        if not any(s in (profile.get("skills") or []) for s in ("英语", "CET-6", "六级", "雅思", "托福")):
            flags.append({"type": "language", "level": "medium", "text": "JD 要求英语能力，简历里没体现——有六级/雅思/英文项目就写上"})
    return flags


def match_jd_rules(jd_text: str, profile: dict) -> dict:
    """
    规则层匹配。不调 LLM，毫秒级。

    Returns:
        {
            "score": int | None,               # None = JD 里识别不出技能关键词
            "hard": {"matched": [...], "missing": [...]},
            "soft": {"matched": [...], "missing": [...]},
            "flags": [{"type", "level", "text"}],
            "highlights": [...],               # 给前端在 JD 里高亮的词
            "verdict": str,
            "markdown": str
        }
    """
    resume_text = profile_as_resume_text(profile)
    resume_lower = resume_text.lower()
    resume_skills = set(s.lower() for s in (profile.get("skills") or []))

    jd_hard = extract_skills(jd_text)
    jd_soft = _extract_soft(jd_text)

    def has(skill: str) -> bool:
        s = skill.lower()
        if s in resume_skills:
            return True
        if re.match(r"^[a-z0-9+#./ ]+$", s):
            return re.search(rf"(?<![a-z0-9]){re.escape(s)}(?![a-z0-9])", resume_lower) is not None
        return s in resume_lower

    hard_matched = [s for s in jd_hard if has(s)]
    hard_missing = [s for s in jd_hard if not has(s)]
    soft_matched = [s for s in jd_soft if s.lower() in resume_lower]
    soft_missing = [s for s in jd_soft if s.lower() not in resume_lower]
    flags = _jd_hard_requirements(jd_text, profile)

    if not jd_hard and not jd_soft:
        score = None
    else:
        hard_rate = len(hard_matched) / len(jd_hard) if jd_hard else 0.5
        soft_rate = len(soft_matched) / len(jd_soft) if jd_soft else 0.5
        score = 70 * hard_rate + 20 * soft_rate + 10
        for f in flags:
            score -= 25 if f["level"] == "high" else 8
        score = int(max(0, min(100, round(score))))

    if score is None:
        verdict = "JD 里没识别出具体技能词，规则层给不了分——点「深度分析」让 AI 读。"
    elif score >= 75:
        verdict = "匹配度高。别只投，去看 JD 潜台词，准备针对性的项目讲稿。"
    elif score >= 50:
        verdict = f"中等匹配。缺 {len(hard_missing)} 个硬技能——能在 2 周内补的就补，补不了的在简历里用相近经验对冲。"
    else:
        verdict = "匹配度低。除非有内推，这份投递大概率停在机筛。要么换岗位，要么先补技能再投。"
    if any(f["level"] == "high" for f in flags):
        verdict = "⛔ 有硬门槛没过（见下方）。" + verdict

    result = {
        "score": score,
        "hard": {"matched": hard_matched, "missing": hard_missing},
        "soft": {"matched": soft_matched, "missing": soft_missing},
        "flags": flags,
        "highlights": jd_hard + jd_soft,
        "verdict": verdict,
    }
    result["markdown"] = _render_match(result)
    return result


def _render_match(r: dict) -> str:
    score = r["score"]
    lines = [f"## 🎯 匹配分：{score if score is not None else '—'}/100", "", f"> {r['verdict']}", ""]
    if r["flags"]:
        lines.append("### ⛔ 硬门槛")
        for f in r["flags"]:
            lines.append(f"- {'🔴' if f['level'] == 'high' else '🟡'} {f['text']}")
        lines.append("")
    lines.append("### 🔧 硬技能")
    lines.append(f"- ✅ 命中（{len(r['hard']['matched'])}）：{'、'.join(r['hard']['matched']) or '无'}")
    lines.append(f"- ❌ 缺失（{len(r['hard']['missing'])}）：{'、'.join(r['hard']['missing']) or '无'}")
    lines.append("")
    lines.append("### 🤝 软技能")
    lines.append(f"- ✅ 体现：{'、'.join(r['soft']['matched']) or '无'}")
    lines.append(f"- ❌ 未体现：{'、'.join(r['soft']['missing']) or '无'}")
    lines.append("")
    if r["hard"]["missing"]:
        lines.append("### 下一步")
        lines.append(f"- 缺失技能里，有真实经验但没写的，现在补进简历（技能关键词就是机筛的命）")
        lines.append(f"- 完全没接触过的，评估 2 周能不能做出一个小 demo；不能就别硬投")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# CRUD
# ═══════════════════════════════════════════════════════════

def _guess_title_company(jd_text: str) -> tuple:
    first = next((l.strip() for l in jd_text.split("\n") if l.strip()), "")
    title, company = "", ""
    m = re.search(r"(岗位名称|职位名称|职位|岗位)[:：]\s*([^\n，,]{2,30})", jd_text)
    if m:
        title = m.group(2).strip()
    m = re.search(r"(公司名称|公司)[:：]\s*([^\n，,]{2,30})", jd_text)
    if m:
        company = m.group(2).strip()
    if not title and len(first) <= 40:
        title = first
    return title, company


def add_jd(jd_text: str, title: str = "", company: str = "", url: str = "", profile: dict = None,
           user_id: str = "default_user") -> dict:
    jd_text = (jd_text or "").strip()
    if len(jd_text) < 20:
        return {"error": "JD 太短", "markdown": "> ⚠️ JD 内容太短，粘贴完整的岗位描述"}
    g_title, g_company = _guess_title_company(jd_text)
    data = _load()
    jd = {
        "id": uuid.uuid4().hex[:8],
        "user_id": user_id,
        "title": (title or g_title or "未命名岗位").strip()[:60],
        "company": (company or g_company).strip()[:40],
        "url": url.strip(),
        "text": jd_text[:12000],
        "created_at": _now(),
        "match": None,
        "deep": None,
    }
    if profile:
        m = match_jd_rules(jd_text, profile)
        jd["match"] = {k: v for k, v in m.items() if k != "markdown"}
        jd["match"]["markdown"] = m["markdown"]
    data["jds"].append(jd)
    _save(data)
    return {"jd": jd, "markdown": (jd["match"] or {}).get("markdown", f"> ✅ 已保存：{jd['title']}")}


def rematch_all(profile: dict, user_id: str = "default_user") -> int:
    """简历更新后重算全部匹配分。"""
    data = _load()
    n = 0
    for jd in data["jds"]:
        if jd.get("user_id") != user_id:
            continue
        m = match_jd_rules(jd["text"], profile)
        jd["match"] = m
        n += 1
    _save(data)
    return n


def list_jds(user_id: str = "default_user") -> list:
    data = _load()
    jds = [j for j in data["jds"] if j.get("user_id") == user_id]
    jds.sort(key=lambda j: ((j.get("match") or {}).get("score") or -1, j.get("created_at", "")), reverse=True)
    return jds


def get_jd(jd_id: str, user_id: str = "default_user") -> Optional[dict]:
    jd = _find(_load(), jd_id)
    return jd if jd and jd.get("user_id") == user_id else None


def delete_jd(jd_id: str, user_id: str = "default_user") -> dict:
    data = _load()
    jd = _find(data, jd_id)
    if not jd or jd.get("user_id") != user_id:
        return {"error": "不存在", "markdown": "> ⚠️ 找不到这条 JD"}
    data["jds"] = [j for j in data["jds"] if j["id"] != jd["id"]]
    _save(data)
    return {"deleted": jd["id"], "markdown": f"> 🗑️ 已删除 {jd['title']}"}


def save_deep_analysis(jd_id: str, deep: dict, user_id: str = "default_user") -> None:
    data = _load()
    jd = _find(data, jd_id)
    if jd and jd.get("user_id") == user_id:
        jd["deep"] = {k: v for k, v in deep.items() if k in ("overall_probability", "strengths", "weaknesses", "danger_signals", "interviewer_comment", "markdown", "key_insight", "subtexts")}
        jd["deep"]["at"] = _now()
        _save(data)


def render_jd_list(jds: list) -> str:
    if not jds:
        return "> 📭 岗位库是空的。粘一段 JD 进来，立刻看匹配分。"
    lines = ["| 匹配分 | 岗位 | 公司 | 缺失硬技能 | 硬门槛 |", "|---|---|---|---|---|"]
    for j in jds:
        m = j.get("match") or {}
        score = m.get("score")
        s = f"**{score}**" if score is not None else "—"
        missing = "、".join((m.get("hard") or {}).get("missing", [])[:4]) or "-"
        flags = "⛔" if any(f.get("level") == "high" for f in m.get("flags", [])) else ("🟡" if m.get("flags") else "-")
        lines.append(f"| {s} | {j['title']} | {j.get('company') or '-'} | {missing} | {flags} |")
    return "\n".join(lines)
