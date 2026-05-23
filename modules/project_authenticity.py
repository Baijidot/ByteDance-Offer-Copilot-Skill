"""
Project Authenticity Detector — 项目真实性检测

Detects whether a project is a real product or a student demo.
Checks for: real users, data loop, iteration records, growth logic,
user feedback, engineering complexity.

Output: authenticity score + specific risk flags + what's missing.
Style: brutally honest, internet industry standard.
"""

from utils import callLlm, safeCallLlm
import re

SYSTEM_PROMPT = """你是字节跳动的技术评审。你看过 10000+ 个项目，能在 30 秒内分辨：
- 这是真正有人用的产品
- 这是课程作业套壳
- 这是 AI 生成的项目描述
- 这是包装过的 Demo

你的判断依据：
1. 有没有真实用户？不是「我找同学测了」，是「有陌生用户自发使用」
2. 有没有数据闭环？不是「DAU 2000」，是「DAU 怎么来的、怎么掉的、你做了什么」
3. 有没有迭代记录？不是「迭代了 3 版」，是「第 2 版因为 X 原因改了 Y，结果 Z」
4. 有没有增长逻辑？不是「发了个朋友圈」，是「用户从哪里来、为什么来、为什么留」
5. 有没有用户反馈？不是「用户说好」，是「用户的投诉/建议/行为数据驱动了改动」
6. 有没有工程复杂度？不是「用 React 写的」，是「解决了什么技术挑战」

你的风格：毒舌、直接、不留情面。看到学生 Demo 会直接说「这是课程作业」。"""


def detect_authenticity(project_text: str) -> dict:
    """
    Analyze project authenticity using both rule-based signals and LLM.

    Args:
        project_text: Full project description

    Returns:
        {
            "authenticity_score": int(0-100),
            "red_flags": [{"flag": str, "severity": "high"|"medium"|"low"}],
            "missing_elements": [str],
            "student_tells": [str],
            "real_world_gaps": [str],
            "verdict": str,
            "markdown": str
        }
    """
    # Phase 1: Rule-based red flag detection (instant)
    rule_flags = _rule_detect(project_text)

    # Phase 2: LLM deep analysis
    prompt = f"""请检测以下项目的真实性。像一个字节技术评审一样审查。

【项目描述】
{project_text[:5000]}

请从以下维度逐项审查：

1. 真实用户 — 有没有陌生用户在使用？用户量级是多少？
2. 数据闭环 — 有没有核心指标的定义和跟踪？有没有数据驱动的决策？
3. 迭代记录 — 有没有基于反馈的迭代？迭代理由是什么？
4. 增长逻辑 — 用户从哪里来？为什么来？为什么留下？
5. 用户反馈 — 有没有真实的用户反馈/投诉/行为数据？
6. 工程复杂度 — 解决了什么真实的技术/产品挑战？

规则检测已发现的红旗：
{chr(10).join("- {0} ({1})".format(f["flag"], f["severity"]) for f in rule_flags) if rule_flags else "无"}

输出 JSON：
```json
{{
  "authenticity_score": 45,
  "red_flags": [
    {{"flag": "具体风险描述", "severity": "high"}}
  ],
  "missing_elements": [
    "具体缺失的元素 — 不要泛泛而谈，要具体到这个项目"
  ],
  "student_tells": [
    "暴露学生身份的具体信号"
  ],
  "real_world_gaps": [
    "这个项目离真产品最缺的东西"
  ],
  "verdict": "一句话定性（如：典型的AI套壳Demo，缺少真实用户验证）"
}}
```

要求：
- 评价必须具体，引用项目描述中的原文
- 毒舌、直接、不留情面
- authenticity_score 必须严格——大多数学生项目应该在 30-50 分"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        # Merge rule flags
        all_flags = rule_flags + result.get("red_flags", [])
        result["red_flags"] = all_flags
        result["markdown"] = _render_markdown(result)

    return result


def _rule_detect(text: str) -> list[dict]:
    """Instant rule-based red flag detection."""
    flags = []

    # Student tells
    if "课程" in text or "作业" in text or "大作业" in text:
        flags.append({"flag": "明确标注了「课程/作业」——这是课程项目", "severity": "high"})
    if "学习" in text and ("项目" in text or "开发" in text):
        flags.append({"flag": "以「学习」为目的——公司项目不是为了学习", "severity": "medium"})
    if "同学" in text or "室友" in text or "朋友" in text:
        flags.append({"flag": "用户=同学/朋友——不是真实用户", "severity": "high"})

    # Missing data
    has_numbers = bool(re.search(r'\d+', text))
    if not has_numbers:
        flags.append({"flag": "没有任何数字——没有数据意识", "severity": "high"})
    elif not re.search(r'[%％]|\d+人|\d+万|\d+千|\d+\.\d+', text):
        flags.append({"flag": "数字偏少——缺少核心指标的量化", "severity": "medium"})

    # Missing users
    user_keywords = ["用户", "DAU", "dau", "留存", "活跃", "粉丝", "访问", "注册", "付费"]
    if not any(kw in text for kw in user_keywords):
        flags.append({"flag": "完全没有提到用户——这个项目可能没人用", "severity": "high"})

    # Missing iteration
    iter_keywords = ["迭代", "版本", "v1", "v2", "优化", "改进", "反馈"]
    if not any(kw in text for kw in iter_keywords):
        flags.append({"flag": "没有迭代记录——产品没有进化", "severity": "medium"})

    # AI demo smell
    ai_demo_signals = ["AI生成", "AI辅助开发", "用AI搭建", "AI驱动的Demo"]
    if any(kw in text for kw in ai_demo_signals):
        if not any(kw in text for kw in ["用户", "数据", "上线", "发布"]):
            flags.append({"flag": "AI Demo 味——AI 建了但没人用，这是 AI 套壳", "severity": "high"})

    # Missing failure
    if "失败" not in text and "问题" not in text and "bug" not in text.lower():
        flags.append({"flag": "只说了成功没说过失败——真实项目一定有挫折", "severity": "low"})

    # Buzzword overload
    buzzwords = ["赋能", "闭环", "抓手", "对齐", "拉通", "底层逻辑", "顶层设计"]
    buzz_count = sum(1 for bw in buzzwords if bw in text)
    if buzz_count >= 3:
        flags.append({"flag": f"黑话密度过高（{buzz_count}个）——在掩盖内容空洞", "severity": "medium"})

    return flags


def _render_markdown(data: dict) -> str:
    """Render authenticity report as Markdown."""
    score = data.get("authenticity_score", 50)
    if score >= 70:
        level, emoji = "真实项目", "🟢"
    elif score >= 40:
        level, emoji = "有学生味但有一定真实度", "🟡"
    else:
        level, emoji = "典型学生作品/课程项目", "🔴"

    lines = [
        "```",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🔍  项目真实性审查报告",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
        f"## 真实性评分：{score}/100  {emoji} {level}",
        f"`{'█' * (score // 5)}{'░' * (20 - score // 5)}`",
        "",
    ]

    # Verdict
    lines.extend([
        "## 📋 结论",
        f"> {data.get('verdict', '')}",
        "",
    ])

    # Red flags
    flags = data.get("red_flags", [])
    if flags:
        lines.append("## 🚩 红旗警告")
        lines.append("")
        for f in flags:
            sev_emoji = "🔴" if f["severity"] == "high" else "🟡" if f["severity"] == "medium" else "🟢"
            lines.append(f"- {sev_emoji} {f['flag']}")
        lines.append("")

    # Student tells
    tells = data.get("student_tells", [])
    if tells:
        lines.append("## 📚 学生味信号")
        lines.append("")
        for t in tells:
            lines.append(f"- {t}")
        lines.append("")

    # Missing elements
    missing = data.get("missing_elements", [])
    if missing:
        lines.append("## ❌ 缺了什么")
        lines.append("")
        for m in missing:
            lines.append(f"- {m}")
        lines.append("")

    # Real world gaps
    gaps = data.get("real_world_gaps", [])
    if gaps:
        lines.append("## 🌍 离真实产品最缺的")
        lines.append("")
        for g in gaps:
            lines.append(f"- {g}")
        lines.append("")

    return "\n".join(lines)
