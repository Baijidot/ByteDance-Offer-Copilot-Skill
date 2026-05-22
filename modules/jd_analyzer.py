"""
JD Analyzer — 拆解岗位 JD，揭示面试官真正的考察点。

Takes raw JD text and returns structured analysis:
- Core capabilities being tested
- Subtext / hidden meaning of each JD phrase
- Ideal candidate profile ByteDance is really looking for
- 30-day growth roadmap

No mock data. Every output is LLM-driven via callLlm().
"""

import json
from utils import callLlm, fetchInput

SYSTEM_PROMPT = """你是字节跳动的 P8 级产品面试官，8 年产品经验，面试过 500+ 候选人。
你极度擅长从 JD 中读出潜台词。
你的风格：直接、犀利、有洞察、不讲废话、不说鸡汤。

核心原则：
1. 从 JD 中提取「真正考察的能力」，而非字面要求
2. 解读「岗位潜台词」—— JD 里不直接写但面试官真正看重的
3. 输出必须有层级、有 Emoji、有视觉感
4. 绝对不允许模板化表达
5. 禁止说「加油」「努力」等空洞词汇

AI 编程工具现状（2026年5月）：
- 2026 年的 AI 编程已进入 Agent 时代，AI 可以自主完成 Plan → Code → Review → Deploy 全流程
- 主流工具包括 Trae Solo（字节）、Codex（OpenAI）、Cursor 等
- 字节跳动内部已全面推行 AI 辅助编程，面试官会考察候选人是否将 AI 嵌入日常工作流
- AI 协同深度分两层：Chat 层面（问答式）vs Workflow 层面（AI 自主完成完整任务链路），后者才是亮点"""


def analyze(jd_input: str, job_title: str = "", jd_url: str = "") -> dict:
    """
    拆解岗位 JD，返回结构化分析。

    支持三种输入方式（自动识别）：
    1. MD 文件路径    → "E:/jobs/字节产品经理.md"
    2. 网站 URL        → "https://jobs.bytedance.com/xxx"
    3. 直接粘贴 JD 文本 → "负责抖音内容生态..."

    Args:
        jd_input: JD 文本 / 文件路径 / URL
        job_title: 岗位名称（可选）
        jd_url: 岗位链接（可选，用于标记来源）

    Returns:
        {
            "job_title": str,
            "source_type": "file" | "url" | "text",
            "core_capabilities": [...],
            "subtexts": [...],
            "ideal_candidate": {...},
            "growth_path": [...],
            "key_insight": str,
            "markdown": str
        }
    """
    # Auto-detect input type and extract content
    jd_text, source_type = fetchInput(jd_input)

    prompt = f"""请深度拆解以下字节跳动岗位 JD：

【岗位名称】
{job_title or '未提供'}

【岗位 JD】
{jd_text[:8000]}

【岗位链接 / 来源】
{jd_url or jd_input if source_type == 'url' else '未提供'}
【输入方式】{source_type}

请严格按以下 JSON 结构输出（同时附带一份 Markdown 版本）：

```json
{{
  "job_title": "岗位名称",
  "jd_type": "产品经理/游戏策划/AI产品/运营/增长",
  "core_capabilities": [
    {{
      "name": "能力名称",
      "weight": "⭐⭐⭐⭐⭐ (1-5星)",
      "positive": "什么样的人通过",
      "negative": "什么样的人被刷"
    }}
  ],
  "subtexts": [
    {{
      "original": "JD 原文表述",
      "meaning": "潜台词",
      "insight": "一句话洞察"
    }}
  ],
  "ideal_candidate": {{
    "硬性条件": ["条件1", "条件2"],
    "软性素质": ["素质1", "素质2"],
    "隐藏加分项": ["加分1", "加分2"],
    "一票否决项": ["否决1", "否决2"]
  }},
  "growth_path": [
    {{
      "period": "前7天",
      "task": "核心任务",
      "actions": "具体行动",
      "output": "产出物",
      "effect": "预期效果"
    }}
  ],
  "key_insight": "这个岗位和普通岗位的根本区别，什么样的人一定能拿到 Offer"
}}
```

要求：
- 至少提取 5 条潜台词
- 每条评价必须具体，不允许泛泛而谈
- key_insight 必须一针见血，30 字以内
- 涉及 AI 工具推荐时，确保推荐的是 2026 年的最新工具和最佳实践，而非 2023-2024 年的过时信息"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")

    # Attach metadata
    if isinstance(result, dict) and "_trait" not in result:
        result["source_type"] = source_type
        result["markdown"] = _render_markdown(result)
    else:
        result["source_type"] = source_type

    return result


def _render_markdown(data: dict) -> str:
    """Render analysis result as Markdown."""
    lines = [
        f"# 🔍 JD 深度拆解：{data.get('job_title', '')}",
        "",
        "## 一、真正考察的核心能力",
        "",
        "| 能力 | 权重 | 什么样的人通过 | 什么样的人被刷 |",
        "|------|------|---------------|---------------|",
    ]

    for cap in data.get("core_capabilities", []):
        lines.append(f"| {cap['name']} | {cap['weight']} | {cap['positive']} | {cap['negative']} |")

    lines.extend(["", "## 二、岗位潜台词", ""])
    for sub in data.get("subtexts", []):
        lines.append(f"> **JD 原文:** 「{sub['original']}」")
        lines.append(f"> 👉 **潜台词:** {sub['meaning']}")
        lines.append(f"> 💡 {sub['insight']}")
        lines.append("")

    lines.extend(["", "## 三、字节真正想要的人", ""])
    ideal = data.get("ideal_candidate", {})
    for category, items in ideal.items():
        lines.append(f"### {category}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["", "## 四、30 天能力成长路线", ""])
    lines.append("| 时间段 | 核心任务 | 具体行动 | 产出物 | 预期效果 |")
    lines.append("|--------|----------|----------|--------|----------|")
    for step in data.get("growth_path", []):
        lines.append(f"| {step['period']} | {step['task']} | {step['actions']} | {step['output']} | {step['effect']} |")

    lines.extend(["", "## 五、决胜关键", ""])
    lines.append(f"> {data.get('key_insight', '')}")
    lines.append("")

    return "\n".join(lines)
