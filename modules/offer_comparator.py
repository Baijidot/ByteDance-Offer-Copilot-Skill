"""
Offer Comparator — Offer 对比决策器

规则引擎 + LLM 双层：
- 规则层（确定性数学）：六维加权评分、排名、薪资归一化、权重敏感性分析
- LLM 层（定性分析，可选）：隐藏风险、谈判筹码、各 Offer 适合什么人、最终建议

拿到多个 Offer 之后靠感觉选，是求职最后一步最常见的失误。
这个模块的目标：把「感觉」拆成六个可以打分的维度，让你知道自己到底在为什么买单。
"""

import json
from utils import callLlm, safeCallLlm

# (key, 中文名, 默认权重, 说明)
DIMENSIONS = [
    ("salary",    "薪酬包",     30, "总包（base + 奖金 + 股票/期权折现），按最高 Offer 归一化"),
    ("growth",    "职业成长",   25, "业务是否核心、能否接触关键项目、晋升通道、导师质量"),
    ("stability", "平台稳定性", 15, "公司现金流、业务线是否被裁风险、行业周期"),
    ("team",      "团队与氛围", 15, "直属 leader、团队年龄结构、加班文化、面试体感"),
    ("location",  "城市与通勤", 10, "城市偏好、通勤时间、生活成本、家庭因素"),
    ("track",     "赛道前景",    5, "所在行业 / 业务 3-5 年的天花板"),
]

DEFAULT_WEIGHTS = {k: w for k, _, w, _ in DIMENSIONS}
DIM_NAMES = {k: n for k, n, _, _ in DIMENSIONS}

SYSTEM_PROMPT = """你是互联网大厂的资深面试官，也做过 5 年 HRBP，看过上千次 Offer 谈判。
你知道候选人在选 Offer 时最容易犯的错：
- 只看总包，不看现金比例和股票兑现条件
- 被「核心业务」四个字忽悠，不问这条业务线去年的人员流动
- 选 leader 只看面试时聊得爽不爽，不问他带过的人现在在哪
- 把「大平台」当稳定，其实大平台的边缘业务比小公司核心业务更容易被裁

你的风格：直接、犀利、不替候选人做决定，但把每个选项的代价说清楚。
你从不说「都不错，看你自己」——这是废话。"""


# ═══════════════════════════════════════════════════════════
# Rule layer
# ═══════════════════════════════════════════════════════════

def _to_float(v, default=0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(str(v).replace("万", "").replace("k", "").replace("K", "").strip())
    except (ValueError, TypeError):
        return default


def _clamp(v: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, v))


def _normalize_offers(offers: list) -> list:
    """把用户输入整理成统一结构，缺省维度打 5 分。"""
    norm = []
    for i, o in enumerate(offers):
        if not isinstance(o, dict):
            continue
        company = str(o.get("company") or f"Offer {i + 1}").strip()
        position = str(o.get("position") or "").strip()
        total = _to_float(o.get("total_package"))
        base = _to_float(o.get("base_salary"))
        # 只填了 base 没填总包，用 base 顶上
        if total <= 0 < base:
            total = base
        norm.append({
            "company": company,
            "position": position,
            "city": str(o.get("city") or "").strip(),
            "total_package": total,
            "base_salary": base,
            "scores": {
                "growth": _clamp(_to_float(o.get("growth_score"), 5)),
                "stability": _clamp(_to_float(o.get("stability_score"), 5)),
                "team": _clamp(_to_float(o.get("team_score"), 5)),
                "location": _clamp(_to_float(o.get("location_score"), 5)),
                "track": _clamp(_to_float(o.get("track_score"), 5)),
            },
            "notes": str(o.get("notes") or "").strip(),
        })
    return norm


def _score_salary(norm: list) -> None:
    """薪酬按最高总包归一化到 0-10；没填薪资的一律 5 分并标记。"""
    max_pkg = max((o["total_package"] for o in norm), default=0)
    for o in norm:
        if o["total_package"] <= 0 or max_pkg <= 0:
            o["scores"]["salary"] = 5.0
            o["salary_missing"] = True
        else:
            o["scores"]["salary"] = round(o["total_package"] / max_pkg * 10, 2)
            o["salary_missing"] = False


def _weighted_total(scores: dict, weights: dict) -> float:
    total_w = sum(weights.values()) or 1
    return round(sum(scores.get(k, 5) * weights.get(k, 0) for k in weights) / total_w * 10, 1)


def _sensitivity(norm: list, weights: dict) -> list:
    """权重敏感性：把每个维度的权重 +15 之后排名第一会不会变。"""
    base_rank = sorted(norm, key=lambda o: -o["weighted_total"])
    leader = base_rank[0]["company"] if base_rank else ""
    flips = []
    for k in weights:
        w2 = dict(weights)
        w2[k] = w2[k] + 15
        rank2 = sorted(norm, key=lambda o: -_weighted_total(o["scores"], w2))
        if rank2 and rank2[0]["company"] != leader:
            flips.append({"dimension": DIM_NAMES[k], "new_leader": rank2[0]["company"]})
    return flips


def compare_offers(
    offers: list,
    weights: dict = None,
    priorities: str = "",
    use_llm: bool = True,
) -> dict:
    """
    对比多个 Offer。

    Args:
        offers: [
            {
                "company": "公司", "position": "岗位", "city": "城市",
                "total_package": 35,       # 年总包（万），可选
                "base_salary": 28,         # 年 base（万），可选
                "growth_score": 7,         # 1-10，以下同
                "stability_score": 6,
                "team_score": 8,
                "location_score": 9,
                "track_score": 7,
                "notes": "补充信息：股票 4 年兑现 / leader 是 xx / 加班情况 ..."
            }, ...
        ]
        weights: {"salary": 30, "growth": 25, ...} 可选，默认见 DEFAULT_WEIGHTS，总和不要求 100
        priorities: 一段话描述你现阶段最看重什么（给 LLM 用）
        use_llm: 是否调用 LLM 做定性分析

    Returns:
        {
            "ranking": [{"rank", "company", "position", "weighted_total", "scores", ...}],
            "weights": {...},
            "sensitivity": [{"dimension", "new_leader"}],
            "gap": float,                  # 第一名与第二名的分差
            "analysis": {...} | None,      # LLM 定性分析
            "markdown": str
        }
    """
    norm = _normalize_offers(offers)
    if len(norm) < 2:
        return {"error": "至少需要 2 个 Offer 才能对比", "markdown": "> ⚠️ 至少需要 2 个 Offer 才能对比。只有一个 Offer 的话，问题不是选哪个，是要不要接。"}

    weights = {k: _to_float((weights or {}).get(k), DEFAULT_WEIGHTS[k]) for k in DEFAULT_WEIGHTS}
    _score_salary(norm)
    for o in norm:
        o["weighted_total"] = _weighted_total(o["scores"], weights)

    ranking = sorted(norm, key=lambda o: -o["weighted_total"])
    for i, o in enumerate(ranking, 1):
        o["rank"] = i
    gap = round(ranking[0]["weighted_total"] - ranking[1]["weighted_total"], 1)
    sensitivity = _sensitivity(norm, weights)

    result = {
        "ranking": ranking,
        "weights": weights,
        "sensitivity": sensitivity,
        "gap": gap,
        "analysis": None,
    }

    if use_llm:
        result["analysis"] = _llm_analysis(ranking, weights, gap, sensitivity, priorities)

    result["markdown"] = _render(result)
    return result


# ═══════════════════════════════════════════════════════════
# LLM layer
# ═══════════════════════════════════════════════════════════

def _llm_analysis(ranking: list, weights: dict, gap: float, sensitivity: list, priorities: str):
    offers_desc = []
    for o in ranking:
        offers_desc.append({
            "排名": o["rank"],
            "公司": o["company"],
            "岗位": o["position"],
            "城市": o["city"],
            "年总包(万)": o["total_package"] or "未填",
            "年base(万)": o["base_salary"] or "未填",
            "六维打分": {DIM_NAMES[k]: v for k, v in o["scores"].items()},
            "加权总分": o["weighted_total"],
            "补充信息": o["notes"] or "无",
        })

    prompt = f"""候选人手上有 {len(ranking)} 个 Offer，已经用规则引擎算完加权分，请你做定性分析。

【Offer 列表（已按加权分排序）】
{json.dumps(offers_desc, ensure_ascii=False, indent=2)}

【权重】
{json.dumps({DIM_NAMES[k]: v for k, v in weights.items()}, ensure_ascii=False)}

【第一名领先第二名】{gap} 分
【权重敏感性】{'；'.join(f"{s['dimension']}权重+15 后第一名变成 {s['new_leader']}" for s in sensitivity) or '排名稳定，调权重不影响第一名'}

【候选人自述的优先级】
{priorities or '未提供'}

请严格按以下 JSON 输出：

```json
{{
  "verdict": "一句话结论：推荐哪个、为什么、代价是什么（40 字内，不许说「看你自己」）",
  "per_offer": [
    {{
      "company": "公司名",
      "hidden_risks": ["这个 Offer 里候选人可能没注意到的风险 1", "风险 2"],
      "hidden_upsides": ["被低估的优势（如有）"],
      "suits_who": "这个 Offer 适合什么样的人（一句话）",
      "must_ask_before_sign": ["签之前必须问 HR / 未来 leader 的问题 1", "问题 2"]
    }}
  ],
  "negotiation": [
    {{"target": "公司名", "leverage": "可以用什么做筹码（如另一个 Offer 的总包）", "ask": "具体要什么（涨 base / 签字费 / 定级 / 提前转正）", "script": "一句话的谈判话术"}}
  ],
  "blind_spot": "候选人打分和自述优先级之间的矛盾（如：说最看重成长但成长权重只给了 10）；没有就写「打分和优先级一致」",
  "final_advice": "3-5 句话的最终建议，直接、有判断、说清楚代价"
}}
```

要求：
- hidden_risks 必须基于补充信息和常识推断，不能泛泛地说「有风险」
- negotiation 必须具体到数字或条款，至少给排名前 2 的 Offer 各一条
- 如果薪资未填，在 hidden_risks 里指出「没填薪资就没法真正比较」
- verdict 必须有明确倾向"""

    return safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json",
                       fallback={"verdict": "", "per_offer": [], "negotiation": [], "blind_spot": "", "final_advice": ""})


# ═══════════════════════════════════════════════════════════
# Rendering
# ═══════════════════════════════════════════════════════════

def _render(r: dict) -> str:
    ranking = r["ranking"]
    weights = r["weights"]
    top = ranking[0]

    lines = [
        f"# ⚖️ Offer 对比 · {len(ranking)} 个",
        "",
        f"## 🏆 加权第一：{top['company']}{' · ' + top['position'] if top['position'] else ''} — {top['weighted_total']} 分",
        f"领先第二名 **{r['gap']}** 分" + ("（差距很小，别让分数替你做决定）" if r["gap"] < 5 else "（差距明显）"),
        "",
        "## 总分排名",
        "",
    ]
    max_score = max(o["weighted_total"] for o in ranking) or 1
    for o in ranking:
        bar_len = int(o["weighted_total"] / max_score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(o["rank"], f"{o['rank']}.")
        lines.append(f"{medal} **{o['company']}** {o['weighted_total']} `{bar}`")
    lines.append("")

    # 六维对比表
    header = "| 维度（权重） | " + " | ".join(o["company"] for o in ranking) + " |"
    sep = "|" + "---|" * (len(ranking) + 1)
    lines.extend(["## 六维对比", "", header, sep])
    for k, name, _, _ in DIMENSIONS:
        row = f"| {name}（{int(weights[k])}） | "
        cells = []
        for o in ranking:
            v = o["scores"][k]
            best = v == max(x["scores"][k] for x in ranking)
            cell = f"**{v}**" if best else f"{v}"
            if k == "salary" and o.get("salary_missing"):
                cell += " ⚠️未填"
            cells.append(cell)
        lines.append(row + " | ".join(cells) + " |")
    lines.append("")

    # 薪资明细
    if any(o["total_package"] > 0 for o in ranking):
        lines.extend(["## 薪资明细", "", "| 公司 | 年总包（万） | 年 base（万） | 城市 |", "|------|------|------|------|"])
        for o in ranking:
            lines.append(f"| {o['company']} | {o['total_package'] or '-'} | {o['base_salary'] or '-'} | {o['city'] or '-'} |")
        lines.append("")

    # 敏感性
    lines.append("## 🎚️ 权重敏感性")
    if r["sensitivity"]:
        lines.append("以下任一维度权重 +15，第一名就会变：")
        for s in r["sensitivity"]:
            lines.append(f"- 更看重「{s['dimension']}」→ 第一名变成 **{s['new_leader']}**")
        lines.append("")
        lines.append("> 排名不稳，说明你的选择真正取决于这几个维度。先想清楚它们对你的真实权重。")
    else:
        lines.append("> 任一维度权重 +15 都不改变第一名，排名稳定。")
    lines.append("")

    # LLM 分析
    a = r.get("analysis")
    if isinstance(a, dict) and not a.get("_error") and not a.get("error") and a.get("verdict"):
        lines.extend(["## 💬 面试官视角", "", f"> **{a['verdict']}**", ""])

        for po in a.get("per_offer", []):
            lines.append(f"### {po.get('company', '')}")
            if po.get("suits_who"):
                lines.append(f"*适合：{po['suits_who']}*")
                lines.append("")
            if po.get("hidden_risks"):
                lines.append("**🔴 隐藏风险**")
                for x in po["hidden_risks"]:
                    lines.append(f"- {x}")
            if po.get("hidden_upsides"):
                lines.append("**🟢 被低估的地方**")
                for x in po["hidden_upsides"]:
                    lines.append(f"- {x}")
            if po.get("must_ask_before_sign"):
                lines.append("**❓ 签之前必须问**")
                for x in po["must_ask_before_sign"]:
                    lines.append(f"- {x}")
            lines.append("")

        if a.get("negotiation"):
            lines.extend(["## 🤝 谈判要点", ""])
            for n in a["negotiation"]:
                lines.append(f"**对 {n.get('target', '')}**")
                lines.append(f"- 筹码：{n.get('leverage', '')}")
                lines.append(f"- 要什么：{n.get('ask', '')}")
                lines.append(f"- 话术：「{n.get('script', '')}」")
                lines.append("")

        if a.get("blind_spot"):
            lines.extend(["## 🪞 你的盲点", f"> {a['blind_spot']}", ""])

        if a.get("final_advice"):
            lines.extend(["## 🎯 最终建议", "", a["final_advice"], ""])
    elif isinstance(a, dict) and (a.get("_error") or a.get("error")):
        lines.extend(["## 💬 面试官视角", "", f"> ⚠️ 定性分析不可用：{a.get('_retry_hint') or a.get('error') or a.get('_error')}", "> 以上规则层结果不受影响。", ""])

    return "\n".join(lines)
