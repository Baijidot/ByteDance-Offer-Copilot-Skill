"""
Internet Persona Radar — 互联网人格画像 + 雷达图数据

Generates a 9-dimension radar profile based on resume, projects,
interview answers, content experience, and AI projects.

Outputs JSON radar data + a brutal P8-level critique of the persona.
"""

from utils import callLlm

SYSTEM_PROMPT = """你是字节跳动的 P8 产品负责人。你的核心能力是看人。

你能在 5 分钟内判断一个校招生是什么类型的产品人：
- 是 idea 创业者还是产品经理？
- 是真正的 growth hacker 还是只会说增长？
- 是 AI Native 还是 ChatGPT User？
- 是真正做过用户增长还是自己觉得懂？

你看人极准。你从不夸人。你的评价让人脸红但心服。"""

DIMENSIONS = [
    {
        "key": "product_sense",
        "name": "产品Sense",
        "description": "能否判断什么是好产品，区分真伪需求",
        "signals_strong": ["能说出产品为什么好/不好", "有独立产品判断", "理解产品决策的 tradeoff"],
        "signals_weak": ["只会说「用户体验好」", "没有独立产品观点", "分不清「用户说需要」和「用户真的需要」"],
    },
    {
        "key": "growth_awareness",
        "name": "增长意识",
        "description": "是否关注用户增长和 ROI",
        "signals_strong": ["有增长方法论", "跑过真实实验", "关注核心指标和 ROI"],
        "signals_weak": ["只知道做活动", "算不清投入产出比", "没有增长实验经验"],
    },
    {
        "key": "owner_mindset",
        "name": "Owner意识",
        "description": "是否主动推动而非被动执行",
        "signals_strong": ["自己找问题做", "端到端推动", "独立决策"],
        "signals_weak": ["等人安排", "只是执行者", "项目描述用「参与」「协助」"],
    },
    {
        "key": "ai_capability",
        "name": "AI协同",
        "description": "AI 工具使用深度",
        "signals_strong": ["有 AI 工作流", "AI 深度整合", "能说清 AI 怎么改变效率"],
        "signals_weak": ["只用 ChatGPT 聊天", "AI 是点缀", "说不清 AI 具体怎么用"],
    },
    {
        "key": "data_sensitivity",
        "name": "数据敏感度",
        "description": "能否用数据驱动决策",
        "signals_strong": ["能定义核心指标", "有数据验证闭环", "用数据反驳直觉"],
        "signals_weak": ["凭感觉决策", "没有数据意识", "说不出项目的核心指标"],
    },
    {
        "key": "content_understanding",
        "name": "内容理解",
        "description": "是否理解内容消费心理和创作逻辑",
        "signals_strong": ["有内容账号", "理解内容消费心理", "能判断好内容"],
        "signals_weak": ["只会刷不会分析", "没有内容创作经验", "对内容没有自己的标准"],
    },
    {
        "key": "execution",
        "name": "执行力",
        "description": "能否把事情落地而非只停留在想法",
        "signals_strong": ["有上线产品", "快速交付", "能推动事情落地"],
        "signals_weak": ["想法很多但没落地", "项目拖延", "交付物不完整"],
    },
    {
        "key": "user_insight",
        "name": "用户洞察",
        "description": "是否真正理解用户而非纸上谈兵",
        "signals_strong": ["做过用户访谈", "有真实用户反馈", "能说出用户真正痛点"],
        "signals_weak": ["没和用户聊过", "用户理解靠猜测", "说不出具体用户场景"],
    },
    {
        "key": "learning_speed",
        "name": "学习速度",
        "description": "能否快速上手新领域并产出",
        "signals_strong": ["快速学习新工具", "短期内产出结果", "学习路径清晰"],
        "signals_weak": ["学习周期长", "依赖教程", "产出速度慢"],
    },
]


def generate_persona(
    resume_text: str = "",
    projects: str = "",
    interview_answers: str = "",
    content_experience: str = "",
    ai_projects: str = "",
    target_role: str = "产品经理",
) -> dict:
    """
    Generate a 9-dimension internet persona profile.

    Args:
        resume_text: Full resume text
        projects: Project descriptions
        interview_answers: Interview answer transcripts
        content_experience: Content creation / social media experience
        ai_projects: AI-related project descriptions
        target_role: Target position

    Returns:
        {
            "persona_type": str,
            "dimensions": [{"key": str, "name": str, "score": int(0-100), "critique": str, "evidence": str}],
            "strongest": {"dimension": str, "score": int, "why": str},
            "weakest": {"dimension": str, "score": int, "why": str, "danger": str},
            "overall_critique": str,
            "radar_data": {"labels": [str], "scores": [int]},
            "markdown": str
        }
    """
    combined = f"""
【简历】
{resume_text or '未提供'}

【项目】
{projects or '未提供'}

【面试回答】
{interview_answers or '未提供'}

【内容/账号经历】
{content_experience or '未提供'}

【AI 项目】
{ai_projects or '未提供'}
"""

    dims_desc = "\n".join(
        f"- {d['name']}: {d['description']}（强信号：{', '.join(d['signals_strong'][:2])}）（弱信号：{', '.join(d['signals_weak'][:2])}）"
        for d in DIMENSIONS
    )

    prompt = f"""请基于以下候选人的全部信息，生成互联网人格画像。

【候选人信息】
{combined[:6000]}

【目标岗位】{target_role}

【评分维度】
{dims_desc}

请输出 JSON：
```json
{{
  "persona_type": "一句话定性 — 这个人是哪种产品人？（如：AI Native 增长型产品人 / 学生感重的想法型候选人）",
  "dimensions": [
    {{
      "key": "product_sense",
      "name": "产品Sense",
      "score": 65,
      "critique": "一句锐评 — 具体好在哪里或差在哪里",
      "evidence": "从候选人材料中找到的具体证据"
    }}
  ],
  "strongest": {{
    "dimension": "最强的维度名",
    "score": 85,
    "why": "为什么这是最强项，引用证据"
  }},
  "weakest": {{
    "dimension": "最弱的维度名",
    "score": 25,
    "why": "为什么这是最弱项，引用证据",
    "danger": "这个短板在面试中会被怎么打穿"
  }},
  "overall_critique": "一段 3-5 句的总体锐评，P8 面试官语气，直接、犀利、不鸡汤"
}}
```

要求：
- 每个维度必须给出具体分数（0-100）+ 一句锐评 + 证据
- strongest/weakest 必须引用候选人材料中的具体信息
- overall_critique 必须犀利直接
- 禁止鸡汤、禁止鼓励"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["radar_data"] = _build_radar_data(result)
        result["markdown"] = _render_markdown(result)

    return result


def _build_radar_data(data: dict) -> dict:
    """Build radar chart compatible data."""
    dims = data.get("dimensions", [])
    return {
        "labels": [d["name"] for d in dims],
        "scores": [d["score"] for d in dims],
    }


def _render_markdown(data: dict) -> str:
    """Render persona as Markdown card."""
    lines = [
        "# 🧬 互联网人格画像",
        "",
        f"## 人格类型：{data.get('persona_type', '')}",
        "",
        "## 九维能力雷达",
        "",
    ]

    # Dimension bars
    for d in data.get("dimensions", []):
        score = d["score"]
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
        lines.append(f"**{d['name']}**：{score}/100 {emoji}")
        lines.append(f"`{bar}`")
        lines.append(f"> {d['critique']}")
        lines.append(f"> 📎 {d['evidence']}")
        lines.append("")

    # Strongest
    strongest = data.get("strongest", {})
    lines.extend([
        "## 🟢 最強能力",
        f"**{strongest.get('dimension', '')}** — {strongest.get('score', 0)}/100",
        f"> {strongest.get('why', '')}",
        "",
    ])

    # Weakest
    weakest = data.get("weakest", {})
    lines.extend([
        "## 🔴 最危险短板",
        f"**{weakest.get('dimension', '')}** — {weakest.get('score', 0)}/100",
        f"> {weakest.get('why', '')}",
        f"",
        f"⚠️ 面试危险：{weakest.get('danger', '')}",
        "",
    ])

    # Overall critique
    lines.extend([
        "## 💬 总体锐评",
        f"> {data.get('overall_critique', '')}",
        "",
    ])

    return "\n".join(lines)
