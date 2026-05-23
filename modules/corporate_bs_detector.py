"""
Corporate BS Detector — 互联网黑话检测器

Detects empty student language and weak verbs in resumes and interview answers.
Then rewrites them into real internet-industry professional expression.

This is the viral feature — it's satisfying to see your BS get called out.
"""

from utils import callLlm, safeCallLlm
import re

SYSTEM_PROMPT = """你是互联网表达专家。你的核心能力是识别「学生空话」并将其转化为「互联网化表达」。

你的方法：
- 识别弱动词（参与、协助、学习、了解...）
- 识别空话（提升用户体验、优化产品体验、赋能...）
- 识别无数据表达（很多、大量、显著、极大...）
- 识别被动表达（被安排、跟着做、帮...做...）
- 每一项检测都必须解释「为什么这是空话」
- 每一项都必须给出「互联网版本」

你的风格：直接、毒舌、有洞察、让人脸红但心服。"""


# ═══════════════════════════════════════════════
# Rule-based detection patterns (instant, no LLM needed)
# ═══════════════════════════════════════════════

WEAK_VERBS = {
    "参与": {"severity": "high", "reason": "弱动词——面试官无法判断你做了什么", "replace": ["主导", "推进", "负责", "独立完成"]},
    "协助": {"severity": "high", "reason": "弱动词——暗示你不是核心角色", "replace": ["深度参与", "主导协同", "推动落地"]},
    "学习": {"severity": "medium", "reason": "学生感——公司不是学校，展示你做了什么而非学了什么", "replace": ["掌握并应用", "实践", "落地"]},
    "了解": {"severity": "medium", "reason": "浅层表达——了解=没用过", "replace": ["深入研究", "实操", "掌握"]},
    "负责": {"severity": "low", "reason": "模糊动词——负责可以是打杂也可以是主导", "replace": ["主导并推进", "从0到1完成", "独立负责"]},
    "做了": {"severity": "high", "reason": "没有信息量——做了什么？结果是什么？", "replace": ["完成", "推动上线", "交付"]},
    "帮忙": {"severity": "high", "reason": "不是你的项目——你在帮别人做事", "replace": ["协同推进", "支持落地"]},
    "跟着": {"severity": "high", "reason": "被动参与——你在看别人做", "replace": ["深度参与", "协同执行"]},
}

EMPTY_PHRASES = {
    "提升用户体验": {"reason": "空话——怎么提升的？提升多少？", "replace": "优化新用户核心路径，将关键行为转化率提升X%"},
    "优化产品体验": {"reason": "空话——优化了什么？效果如何？", "replace": "通过[具体改动]，将[核心指标]从X优化至Y"},
    "赋能": {"reason": "互联网黑话过度使用——具体赋能了什么？", "replace": "为[具体角色]提供[具体能力]，使其[具体结果]"},
    "闭环": {"reason": "黑话——如果说不清闭环的具体环节，等于没说", "replace": "完成从[发现问题]到[验证效果]的完整链路"},
    "抓手": {"reason": "阿里黑话——字节不这么说", "replace": "切入点、核心杠杆"},
    "对齐": {"reason": "黑话——你想说的是达成共识还是同步信息？", "replace": "达成共识、同步"},
    "拉通": {"reason": "黑话——拉通了什么？", "replace": "协调、推动跨团队协作"},
}

VAGUE_QUANTIFIERS = {
    "很多": {"reason": "没有数据——很多是多少？", "replace": "具体数字或比例"},
    "大量": {"reason": "没有数据——大量是多大？", "replace": "具体数字或比例"},
    "显著": {"reason": "没有数据——显著是多显著？", "replace": "从X%提升至Y%"},
    "极大": {"reason": "夸张且无数据——极大是多大？", "replace": "具体数据"},
    "大幅": {"reason": "没有数据——大幅是多少？", "replace": "具体变化幅度"},
    "若干": {"reason": "模糊——若干是几个？", "replace": "具体数字"},
    "多个": {"reason": "模糊——多个是几个？", "replace": "具体数字"},
    "各种": {"reason": "模糊——各种是哪些？", "replace": "列举具体类型"},
}


def detect(text: str) -> dict:
    """
    Detect all empty language, weak verbs, and vague quantifiers in text.

    Args:
        text: Resume content or interview answer to analyze

    Returns:
        {
            "total_issues": int,
            "weak_verbs": [{"found": str, "severity": str, "reason": str, "suggestions": [str]}],
            "empty_phrases": [{"found": str, "reason": str, "rewrite": str}],
            "vague_quantifiers": [{"found": str, "reason": str, "rewrite": str}],
            "overall_score": int (0-100, higher = more BS),
            "severity_count": {"high": int, "medium": int, "low": int},
            "markdown": str
        }
    """
    issues = {
        "weak_verbs": [],
        "empty_phrases": [],
        "vague_quantifiers": [],
    }

    # Detect weak verbs
    for verb, info in WEAK_VERBS.items():
        if verb in text:
            issues["weak_verbs"].append({
                "found": verb,
                "severity": info["severity"],
                "reason": info["reason"],
                "suggestions": info["replace"],
            })

    # Detect empty phrases
    for phrase, info in EMPTY_PHRASES.items():
        if phrase in text:
            issues["empty_phrases"].append({
                "found": phrase,
                "reason": info["reason"],
                "rewrite": info["replace"],
            })

    # Detect vague quantifiers
    for word, info in VAGUE_QUANTIFIERS.items():
        if word in text:
            issues["vague_quantifiers"].append({
                "found": word,
                "reason": info["reason"],
                "rewrite": info["replace"],
            })

    total = sum(len(v) for v in issues.values())

    severity_count = {"high": 0, "medium": 0, "low": 0}
    for v in issues["weak_verbs"]:
        severity_count[v["severity"]] += 1

    # Score: more issues = higher BS score
    overall_score = min(100, total * 12 + severity_count["high"] * 10)

    result = {
        "total_issues": total,
        "weak_verbs": issues["weak_verbs"],
        "empty_phrases": issues["empty_phrases"],
        "vague_quantifiers": issues["vague_quantifiers"],
        "overall_score": overall_score,
        "severity_count": severity_count,
    }

    result["markdown"] = _render_markdown(result, text)
    return result


def rewrite(text: str, target_role: str = "产品经理") -> dict:
    """
    Deep rewrite — use LLM to transform the entire text into internet-professional style.

    Args:
        text: Text to rewrite
        target_role: Target position for context

    Returns:
        {"original": str, "rewritten": str, "changes": [dict], "markdown": str}
    """
    prompt = f"""请将以下文本从「学生表达」重构为「互联网化表达」。

目标岗位：{target_role}

原始文本：
{text}

重构原则：
- 把弱动词（参与/协助/学习）替换为强动词（主导/推进/独立完成）
- 把空话（提升用户体验）替换为具体表达（优化XX路径，将XX指标提升XX%）
- 把模糊量词（很多/大量/显著）替换为具体数据或比例
- 强调结果而非过程
- 强调 Owner 意识
- 强调 AI 协同（如果相关）
- 强调数据闭环

输出 JSON：
```json
{{
  "rewritten": "完整改写后的文本",
  "changes": [
    {{"original": "原文片段", "rewritten": "改写后", "reason": "为什么这样改"}}
  ]
}}
```"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["original"] = text
        result["markdown"] = _render_rewrite_markdown(result)

    return result


def _render_markdown(data: dict, original_text: str) -> str:
    """Render BS detection results as Markdown."""
    score = data["overall_score"]
    level = "🔴 重度学生腔" if score >= 60 else "🟡 中等学生腔" if score >= 30 else "🟢 轻度学生腔"

    lines = [
        "# 🔍 互联网表达检测报告",
        "",
        f"## 空话指数：{score}/100  {level}",
        "",
    ]

    if data["weak_verbs"]:
        lines.append("## ⚠️ 弱动词检测")
        lines.append("")
        lines.append("| 检测到 | 严重度 | 问题 | 建议替换 |")
        lines.append("|--------|--------|------|----------|")
        for v in data["weak_verbs"]:
            sev_emoji = "🔴" if v["severity"] == "high" else "🟡" if v["severity"] == "medium" else "🟢"
            lines.append(f"| {sev_emoji} {v['found']} | {v['severity']} | {v['reason']} | {', '.join(v['suggestions'][:2])} |")
        lines.append("")

    if data["empty_phrases"]:
        lines.append("## 🫧 空话检测")
        lines.append("")
        for p in data["empty_phrases"]:
            lines.append(f"> ⚠️ **「{p['found']}」**")
            lines.append(f"> 问题：{p['reason']}")
            lines.append(f"> 建议：{p['rewrite']}")
            lines.append("")

    if data["vague_quantifiers"]:
        lines.append("## 📊 模糊量化词")
        lines.append("")
        for q in data["vague_quantifiers"]:
            lines.append(f"- **「{q['found']}」**：{q['reason']} → 建议：{q['rewrite']}")
        lines.append("")

    if data["total_issues"] == 0:
        lines.append("> ✅ 未检测到明显的学生表达问题。但别放松——没有空话不等于表达优秀。")

    return "\n".join(lines)


def _render_rewrite_markdown(data: dict) -> str:
    """Render rewrite result as Markdown."""
    lines = [
        "# 🔥 互联网化重构",
        "",
        "## 改写结果",
        data.get("rewritten", ""),
        "",
        "## 改动清单",
        "",
        "| 原文 | 改写 | 原因 |",
        "|------|------|------|",
    ]
    for c in data.get("changes", []):
        lines.append(f"| {c['original']} | {c['rewritten']} | {c['reason']} |")

    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Black Speech Translator — 互联网黑话翻译器
# ═══════════════════════════════════════════════

TRANSLATION_TABLE = {
    # 学生空话 → 互联网表达
    "提升用户体验": "优化核心功能触达路径，提升关键行为转化率",
    "优化产品体验": "通过[具体改动]，将[核心指标]从 X 提升至 Y",
    "参与项目开发": "负责[核心模块]设计与推进，完成从需求到落地的完整闭环",
    "负责开发": "主导[模块]从 0 到 1 的技术方案与落地",
    "学习新技术": "快速掌握[技术]并应用于[场景]，[时间]内完成[产出]",
    "做了很多功能": "主导[X]个核心功能的设计与上线，其中[Y]个达到预期指标",
    "用户反馈很好": "NPS 达到 X，用户自传播率 Y%，核心功能次日留存 Z%",
    "团队协作": "推动跨[角色]协同，对齐目标后在[时间]内完成[里程碑]",
    "数据驱动": "定义核心指标[具体指标]，通过数据归因发现[洞察]，推动[决策]",
    "快速迭代": "[时间]一个迭代周期，每版基于[X]指标验证，[版数]版后[指标]从[A]到[B]",
    "从0到1": "独立完成[产品/功能]的市场验证→MVP→上线→数据验证全流程",
    "增长黑客": "通过[具体渠道/方法]，在[时间]内实现[指标]从[A]到[B]，ROI 为[X]",
}

TRANSLATE_SYSTEM_PROMPT = """你是互联网表达翻译官。你的工作是把「学生空话」翻译成「互联网表达」。

翻译原则：
- 学生说「参与」→ 你说「负责/主导」（除非他真的只是参与者）
- 学生说「学习」→ 你说「掌握并应用于」
- 学生说「提升用户体验」→ 你追问「怎么提升的？提升多少？」
- 学生说「很多/大量/显著」→ 你要求具体数字
- 学生说「负责」但没内容 → 你拆解成「做了什么 + 结果是什么」

你的翻译风格：直接、具体、可量化。不添加候选人没做过的事。"""


def translate(text: str, mode: str = "harsh") -> dict:
    """
    Translate student language into internet professional expression.

    Args:
        text: Student-style text to translate
        mode: "harsh" (exact translation) or "rewrite" (full rewrite)

    Returns:
        {
            "original": str,
            "translations": [{"original": str, "translated": str, "note": str}],
            "full_translation": str,
            "markdown": str
        }
    """
    # Phase 1: Rule-based instant translation
    quick_translations = []
    remaining = text
    for student, internet in TRANSLATION_TABLE.items():
        if student in text:
            quick_translations.append({
                "original": student,
                "translated": internet,
                "note": "规则匹配 — 空话→互联网表达",
            })
            remaining = remaining.replace(student, f"[已翻译: {internet[:30]}...]")

    # Phase 2: Also detect weak verbs and vague quantifiers
    from modules.corporate_bs_detector import WEAK_VERBS, VAGUE_QUANTIFIERS
    for verb, info in WEAK_VERBS.items():
        if verb in remaining:
            replacement = info["replace"][0] if info["replace"] else "具体描述"
            quick_translations.append({
                "original": verb,
                "translated": f"[{replacement}] + 具体做了什么",
                "note": f"弱动词替换 — {info['reason']}",
            })

    for word, info in VAGUE_QUANTIFIERS.items():
        if word in remaining:
            quick_translations.append({
                "original": word,
                "translated": f"[{info['replace']}]",
                "note": f"模糊量化词 — {info['reason']}",
            })

    # Phase 3: LLM full translation
    if mode == "rewrite":
        prompt = f"""请将以下学生表达翻译为互联网化表达。

原始文本：
{text}

规则翻译已处理：
{chr(10).join("- {0} → {1}".format(t["original"], t["translated"]) for t in quick_translations) if quick_translations else "无"}

请输出 JSON：
```json
{{
  "full_translation": "完整翻译后的互联网版文本",
  "additional_notes": ["额外的翻译说明"]
}}
```

要求：
- 不添加候选人没做过的事
- 具体化模糊表达
- 强动词替换弱动词"""

        llm_result = safeCallLlm(prompt, TRANSLATE_SYSTEM_PROMPT, output_format="json")
        full = llm_result.get("full_translation", "") if isinstance(llm_result, dict) else ""
    else:
        full = ""

    result = {
        "original": text,
        "translations": quick_translations,
        "full_translation": full or "（规则翻译已在上方列出，如需完整改写请使用 mode='rewrite'）",
    }
    result["markdown"] = _render_translation(result)
    return result


def _render_translation(data: dict) -> str:
    """Render translation as a visual card."""
    lines = [
        "```",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🌐  互联网黑话翻译器",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
        "## 原文",
        f"> {data['original'][:200]}",
        "",
        "## 逐句翻译",
        "",
    ]

    for t in data.get("translations", []):
        lines.append(f"**{t['original']}**")
        lines.append(f"→ {t['translated']}")
        lines.append(f"  _{t['note']}_")
        lines.append("")

    if data.get("full_translation") and "规则翻译" not in data["full_translation"]:
        lines.append("## 完整翻译")
        lines.append(data["full_translation"])
        lines.append("")

    if not data.get("translations"):
        lines.append("> ✅ 未检测到明显的空话或弱动词。")

    return "\n".join(lines)
