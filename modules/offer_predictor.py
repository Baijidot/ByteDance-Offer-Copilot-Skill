"""
Offer Predictor — 基于简历与 JD 匹配度，计算 Offer 概率。

Evaluates candidates across 7 dimensions calibrated to ByteDance campus hiring:
- 学历背景 (15%)
- 项目质量 (30%)
- 实习经历 (20%)
- 产品/增长 Sense (20%)
- AI 能力 (10%)
- 面试预期 (5%)

No mock data. Every output is LLM-driven.
"""

from utils import callLlm

SYSTEM_PROMPT = """你是字节跳动的资深校招面试官，每年面试 200+ 校招候选人。
你深刻理解什么样的学生能拿到 Offer。
你极度反感模板化评价，每一句话都要有具体指向。

评估原则：
- 项目质量 > 学校名气
- 增长案例 > 实习数量
- AI 协同能力是新兴加分项
- 内容/社区经历反映用户理解

禁止说：
- 「建议提升专业能力」（太空泛）
- 「多学习多思考」（废话）
- 「加油努力」（鸡汤）"""


def predict(
    resume_text: str = "",
    jd_text: str = "",
    school: str = "",
    major: str = "",
    degree: str = "本科",
    target_role: str = "产品经理",
    skills: str = "",
    projects: str = "",
    internships: str = "",
    content_experience: str = "",
    ai_capability: str = "",
    other_highlights: str = "",
) -> dict:
    """
    分析简历与 JD 匹配度，输出 Offer 概率 + 详细评估。

    Args:
        resume_text: 完整简历文本（如果提供，优先使用）
        jd_text: 目标岗位 JD 文本
        school: 学校
        major: 专业
        degree: 学历
        target_role: 意向岗位
        skills: 技能
        projects: 项目经历
        internships: 实习经历
        content_experience: 内容/社区/账号经历
        ai_capability: AI 能力描述
        other_highlights: 其他亮点

    Returns:
        {
            "overall_probability": int (0-100),
            "dimensions": [{"name": str, "score": float, "max_score": float, "comment": str}],
            "strengths": [str],
            "weaknesses": [str],
            "danger_signals": [str],
            "improvements": [{"action": str, "why": str, "how": str, "time": str}],
            "recommended_projects": [{"name": str, "why": str, "how": str, "expected": str}],
            "interviewer_comment": str,
            "markdown": str
        }
    """
    # If resume_text is provided, use it to populate fields
    if resume_text and not projects:
        projects = resume_text

    prompt = f"""请基于以下候选人信息，给出 Offer 概率评估：

【基本信息】
学校：{school or '未提供'}
专业：{major or '未提供'}
学历：{degree}
意向岗位：{target_role}

【技能】
{skills or '未提供'}

【项目经历】
{projects or '未提供'}

【实习经历】
{internships or '未提供'}

【内容/社区/账号经历】
{content_experience or '未提供'}

【AI 能力自评】
{ai_capability or '未提供'}

【其他亮点】
{other_highlights or '未提供'}

【目标 JD】
{jd_text or '未提供'}

请严格按以下 JSON 结构输出：

```json
{{
  "overall_probability": 78,
  "dimensions": [
    {{"name": "学历背景", "score": 10.0, "max_score": 15, "comment": "具体一句话评价"}},
    {{"name": "项目质量", "score": 18.0, "max_score": 30, "comment": "具体一句话评价"}},
    {{"name": "实习经历", "score": 12.0, "max_score": 20, "comment": "具体一句话评价"}},
    {{"name": "产品/增长Sense", "score": 14.0, "max_score": 20, "comment": "具体一句话评价"}},
    {{"name": "AI能力", "score": 5.0, "max_score": 10, "comment": "具体一句话评价"}},
    {{"name": "面试预期", "score": 3.0, "max_score": 5, "comment": "具体一句话评价"}}
  ],
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["短板1", "短板2"],
  "danger_signals": ["危险信号1"],
  "improvements": [
    {{"action": "具体行动", "why": "为什么", "how": "怎么做", "time": "预计耗时"}}
  ],
  "recommended_projects": [
    {{"name": "项目名", "why": "为什么做", "how": "怎么做", "expected": "预期效果"}}
  ],
  "interviewer_comment": "用面试官口吻写的真实评价，像面评系统里写的那样"
}}
```

要求：
- 每个维度的评价必须具体，不能泛泛而谈
- strengths/weaknesses 每条必须有具体指向
- danger_signals 必须是面试官看到会皱眉的真问题
- interviewer_comment 必须像真实面评，犀利直接"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_markdown(result)

    return result


def _render_markdown(data: dict) -> str:
    """Render prediction result as Markdown."""
    prob = data.get("overall_probability", 0)
    bar_len = 20
    filled = int(prob / 100 * bar_len)
    bar = "▰" * filled + "▱" * (bar_len - filled)

    lines = [
        f"# 📊 Offer 概率评估",
        "",
        f"## 综合概率：{prob}%",
        f"`{bar}`",
        "",
        "## 各维度得分",
        "",
        "| 维度 | 得分 | 满分 | 评价 |",
        "|------|------|------|------|",
    ]

    for dim in data.get("dimensions", []):
        lines.append(f"| {dim['name']} | {dim['score']} | {dim['max_score']} | {dim['comment']} |")

    lines.append("")
    lines.append("## 🟢 你的优势")
    for s in data.get("strengths", []):
        lines.append(f"- {s}")

    lines.append("")
    lines.append("## 🟡 你的短板")
    for w in data.get("weaknesses", []):
        lines.append(f"- {w}")

    if data.get("danger_signals"):
        lines.append("")
        lines.append("## 🔴 危险信号")
        for d in data["danger_signals"]:
            lines.append(f"- ⚠️ {d}")

    if data.get("improvements"):
        lines.append("")
        lines.append("## ⚡ 最值得补的能力")
        for i, imp in enumerate(data["improvements"]):
            lines.append(f"**{i+1}. {imp['action']}**")
            lines.append(f"- 为什么：{imp['why']}")
            lines.append(f"- 怎么做：{imp['how']}")
            lines.append(f"- 预计耗时：{imp['time']}")
            lines.append("")

    if data.get("recommended_projects"):
        lines.append("## 🎯 最应该做的项目")
        for i, proj in enumerate(data["recommended_projects"]):
            lines.append(f"### 项目{i+1}：{proj['name']}")
            lines.append(f"- 为什么：{proj['why']}")
            lines.append(f"- 怎么做：{proj['how']}")
            lines.append(f"- 预期效果：{proj['expected']}")
            lines.append("")

    lines.append("## 💬 面试官的真实评价")
    lines.append(f"> {data.get('interviewer_comment', '')}")
    lines.append("")

    return "\n".join(lines)
