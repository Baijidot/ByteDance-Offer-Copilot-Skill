"""
Resume Rewriter — 将「学生腔」重构为字节味的互联网化表达。

Transforms:
- 「参与」→「主导并推进」
- 「学习」→「掌握并应用」
- 「做了」→「推动上线，达成 XX 效果」
- 无数据 → 量化成果
- 过程描述 → 结果描述
- 无 AI → 补充 AI 协同方式

No mock data. Every rewrite is LLM-driven.
"""

from utils import callLlm, safeCallLlm

SYSTEM_PROMPT = """你是字节跳动的 P8 产品面试官，同时也是简历筛选专家。
你每年筛选 5000+ 份校招简历，深知什么样的表达能通过筛选。

改写原则：
1. 强调结果和数据，而非过程
2. 强调 owner 意识 —「我主导了」而非「我参与了」
3. 强调增长意识 — 用户增长、数据增长、效率增长
4. 强调 AI 协同 — 展示你如何用 AI 提升效率
5. 强调效率 — 用时间量化成果（「72 小时完成」而非「花了三个月」）
6. 强调闭环 — 从发现问题到解决问题到验证效果

禁止：
- 「负责」「参与」「协助」等弱动词
- 没有数据的空洞描述
- 课堂作业式的表达
- 鸡汤和自嗨"""


def rewrite_project(original_text: str, target_role: str = "产品经理") -> dict:
    """
    将项目经历改写为字节风格。

    Args:
        original_text: 原始项目描述
        target_role: 目标岗位

    Returns:
        {
            "rewritten": str,
            "changes": [{"original": str, "rewritten": str, "reason": str}],
            "interview_script": {"one_minute": str, "three_minutes": str},
            "markdown": str
        }
    """
    prompt = f"""请将以下学生项目经历，改写成字节味的互联网化表达：

【原始项目经历】
{original_text}

【目标岗位】
{target_role}

请严格按以下 JSON 结构输出：

```json
{{
  "rewritten": "改写后的完整项目描述（2-3 句，包含数据、结果、AI 协同）",
  "changes": [
    {{"original": "原文", "rewritten": "改写后", "reason": "为什么要这样改"}}
  ],
  "interview_script": {{
    "one_minute": "1 分钟面试介绍版本",
    "three_minutes": "3 分钟面试介绍版本"
  }}
}}
```

要求：
- 每个改动都要说明原因
- 改写后必须有数据感或结果感
- 必须体现 AI 协同（如果是 AI 时代的项目）
- 面试话术要有记忆点"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_markdown(result)

    return result


def rewrite_intro(
    original_text: str,
    school: str = "",
    major: str = "",
    highlights: str = "",
    target_role: str = "产品经理",
) -> dict:
    """
    改写自我介绍。

    Returns:
        {"30s": str, "60s": str, "original": str, "markdown": str}
    """
    prompt = f"""改写以下自我介绍为字节风格：

【原始自我介绍】
{original_text}

【背景】
学校：{school or '未提供'}
专业：{major or '未提供'}
核心亮点：{highlights or '未提供'}
目标岗位：{target_role}

输出 JSON：
```json
{{
  "30s": "30秒版本",
  "60s": "1分钟版本"
}}
```

要求：
- 有记忆点
- 有互联网感
- 不做作"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")
    return result


def portfolio_advice(portfolio_items: str, target_role: str, weaknesses: str = "") -> dict:
    """
    作品集优化建议。

    Returns:
        {"keep": [str], "delete": [str], "add": [str], "narrative": str, "ai_era_bonus": [str], "markdown": str}
    """
    prompt = f"""给以下作品集提出优化建议：

【当前作品/项目】
{portfolio_items}

【目标岗位】
{target_role}

【当前短板】
{weaknesses or '项目太像学生作业，缺少数据闭环'}

输出 JSON：
```json
{{
  "keep": ["应该保留的作品和原因"],
  "delete": ["应该删除的作品和原因"],
  "add": ["应该新增的作品方向和原因"],
  "narrative": "如何把多个作品串成有说服力的叙事线",
  "ai_era_bonus": ["AI 时代作品集加分项"]
}}
```"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")
    return result


def _render_markdown(data: dict) -> str:
    """Render rewrite result as Markdown."""
    lines = ["# 🔥 字节味简历重构", ""]

    if data.get("rewritten"):
        lines.append("## 改写后")
        lines.append(data["rewritten"])
        lines.append("")

    if data.get("changes"):
        lines.append("## 改动说明")
        lines.append("")
        lines.append("| 原文 | 改写后 | 为什么 |")
        lines.append("|------|--------|--------|")
        for c in data["changes"]:
            lines.append(f"| {c['original']} | {c['rewritten']} | {c['reason']} |")
        lines.append("")

    if data.get("interview_script"):
        lines.append("## 面试话术")
        lines.append(f"**1 分钟版:** {data['interview_script'].get('one_minute', '')}")
        lines.append(f"**3 分钟版:** {data['interview_script'].get('three_minutes', '')}")
        lines.append("")

    return "\n".join(lines)
