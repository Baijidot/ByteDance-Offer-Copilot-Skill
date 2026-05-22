"""
Growth Advisor — AI 时代的个人成长路线顾问。

Generates:
- Recommended career route
- 30-day sprint plan with weekly tasks
- Top 3 projects to build
- Content creation direction
- What NOT to do
- Milestone checkpoints

No mock data. Every output is LLM-driven.
"""

from utils import callLlm

SYSTEM_PROMPT = """你是字节跳动的 P8 产品负责人，同时是校招 mentor。
你带过 30+ 校招生，深知什么样的成长路径最高效。

你的核心理念：AI 时代，传统的「刷实习 + 考证」路径已经过时。
你推崇：用 AI 做作品、用作品证明能力、用数据证明增长 sense。

核心信念：
1. 作品集 > 简历
2. 增长案例 > 实习数量
3. AI 协同能力 > 传统技能
4. 内容输出 > 证书堆积
5. 深度项目 > 广度涉猎

AI 编程工具现状（2026年5月）：
- 2026 年 AI 编程已进入 Agent 时代，AI 能自主完成 Plan → Code → Review → Deploy 全流程
- 主流工具包括 Trae Solo（字节）、Codex（OpenAI）、Cursor 等
- 字节内部已全面推行 AI 辅助编程，面试官看重候选人是否将 AI 嵌入日常工作流
- AI 协同分两层：Chat 层面（问答式）vs Workflow 层面（AI 自主完成完整任务链路），后者才是面试官想看到的

你的风格：直接告诉候选人什么该做、什么不该做。
你不怕打击人 — 虚假的希望比真实的打击更有害。"""


def generate_plan(
    resume_text: str = "",
    jd_text: str = "",
    target_role: str = "产品经理",
    school: str = "",
    major: str = "",
    grade: str = "大三",
    project_level: int = 5,
    product_sense: int = 5,
    growth_sense: int = 5,
    data_level: int = 5,
    ai_level: int = 5,
    content_level: int = 5,
    existing_projects: str = "",
    time_commitment: str = "每天 3-4 小时",
) -> dict:
    """
    生成个性化的 AI 时代成长路线。

    Args:
        resume_text: 完整简历文本（优先使用）
        jd_text: 目标岗位 JD
        target_role: 目标岗位
        school: 学校
        major: 专业
        grade: 年级
        project_level: 项目能力 1-10
        product_sense: 产品 Sense 1-10
        growth_sense: 增长意识 1-10
        data_level: 数据能力 1-10
        ai_level: AI 能力 1-10
        content_level: 内容能力 1-10
        existing_projects: 已有项目描述
        time_commitment: 每天可用时间

    Returns:
        {
            "recommended_route": str,
            "weekly_plans": [{"week": str, "title": str, "tasks": [str], "output": str, "check": str}],
            "top_projects": [{"name": str, "why": str, "how": str, "tools": str, "expected": str}],
            "content_direction": {"platforms": [str], "direction": str, "frequency": str, "expected": str, "why": str},
            "dont_do": [str],
            "milestones": [{"time": str, "milestone": str, "check": str}],
            "role_specific_advice": str,
            "markdown": str
        }
    """
    prompt = f"""请基于以下候选人情况，生成 AI 时代的成长路线：

【基本信息】
学校：{school or '未提供'}
专业：{major or '未提供'}
意向岗位：{target_role}
当前年级：{grade}

【当前能力评估】（1-10 分）
- 项目能力：{project_level}
- 产品 Sense：{product_sense}
- 增长意识：{growth_sense}
- 数据能力：{data_level}
- AI 能力：{ai_level}
- 内容能力：{content_level}

【已有项目/经历】
{existing_projects or resume_text or '未提供'}

【目标 JD】
{jd_text or '未提供'}

【时间投入】
{time_commitment}

请输出 JSON：
```json
{{
  "recommended_route": "推荐路线名称（如：AI 产品路线 / 增长运营路线 / 游戏策划路线）",
  "route_reason": "为什么推荐这条路而不是另一条",
  "weekly_plans": [
    {{
      "week": "Week 1",
      "title": "本周主题",
      "tasks": ["具体任务1（含预计耗时）", "具体任务2"],
      "output": "本周产出物",
      "check": "验收标准"
    }}
  ],
  "top_projects": [
    {{
      "name": "项目名",
      "why": "为什么做这个",
      "how": "具体怎么做",
      "tools": "推荐 AI 工具",
      "expected": "预期效果"
    }}
  ],
  "content_direction": {{
    "platforms": ["平台1", "平台2"],
    "direction": "内容方向",
    "frequency": "更新频率",
    "expected": "预期效果",
    "why": "为什么选这个方向"
  }},
  "dont_do": ["不要做1", "不要做2"],
  "milestones": [
    {{"time": "第7天", "milestone": "里程碑", "check": "验收标准"}}
  ],
  "role_specific_advice": "针对 {target_role} 的特殊建议"
}}
```

要求：
- weekly_plans 必须具体到每周每天做什么
- top_projects 必须是 AI 时代的项目（不是传统学生项目）
- dont_do 必须是有洞察的「反常识」建议
- 所有建议必须可执行、可验收
- 涉及 AI 工具推荐时，确保推荐的是 2026 年的最新工具和最佳实践，而非 2023-2024 年的过时信息"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_markdown(result)

    return result


def _render_markdown(data: dict) -> str:
    """Render growth plan as Markdown."""
    lines = [
        "# 🗺️ AI 时代成长路线",
        "",
        f"## 推荐路线：{data.get('recommended_route', '')}",
        "",
    ]

    if data.get("route_reason"):
        lines.append(f"> {data['route_reason']}")
        lines.append("")

    lines.append("## 📋 30 天冲刺计划")
    lines.append("")

    for week in data.get("weekly_plans", []):
        lines.append(f"### {week['week']}：{week['title']}")
        lines.append("")
        for task in week.get("tasks", []):
            lines.append(f"- [ ] {task}")
        lines.append("")
        lines.append(f"**产出物**：{week.get('output', '')}")
        lines.append(f"**验收标准**：{week.get('check', '')}")
        lines.append("")

    lines.append("## 🎨 最该做的作品（Top 3）")
    lines.append("")
    for i, proj in enumerate(data.get("top_projects", [])):
        lines.append(f"### 作品{i+1}：{proj.get('name', '')}")
        lines.append(f"- **为什么**：{proj.get('why', '')}")
        lines.append(f"- **怎么做**：{proj.get('how', '')}")
        lines.append(f"- **推荐工具**：{proj.get('tools', '')}")
        lines.append(f"- **预期效果**：{proj.get('expected', '')}")
        lines.append("")

    cd = data.get("content_direction", {})
    if cd:
        lines.append("## 📝 最适合的内容方向")
        lines.append("")
        lines.append(f"- **平台**：{', '.join(cd.get('platforms', []))}")
        lines.append(f"- **方向**：{cd.get('direction', '')}")
        lines.append(f"- **频率**：{cd.get('frequency', '')}")
        lines.append(f"- **预期**：{cd.get('expected', '')}")
        lines.append(f"- **为什么**：{cd.get('why', '')}")
        lines.append("")

    lines.append("## ❌ 不要做的事")
    lines.append("")
    for item in data.get("dont_do", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## 🎯 里程碑节点")
    lines.append("")
    lines.append("| 时间 | 里程碑 | 验收标准 |")
    lines.append("|------|--------|----------|")
    for m in data.get("milestones", []):
        lines.append(f"| {m['time']} | {m['milestone']} | {m['check']} |")
    lines.append("")

    if data.get("role_specific_advice"):
        lines.append("## 💡 方向专属建议")
        lines.append(data["role_specific_advice"])
        lines.append("")

    return "\n".join(lines)
