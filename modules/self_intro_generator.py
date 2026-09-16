"""
Self-Intro Generator — 自我介绍 / 项目介绍生成器

面试第一分钟决定面试官的预期。这个模块负责：
1. generate_intro       — 按时长 / 风格 / 场景生成自我介绍稿（含钩子、结构、口语提示、避坑）
2. generate_project_pitch — 把项目经历整理成 STAR 讲稿 + 预判追问 + 应对策略

No mock data. Every output is LLM-driven via safeCallLlm().
"""

from utils import callLlm, safeCallLlm

SYSTEM_PROMPT = """你是互联网大厂的资深面试官，同时也是一位面试表达教练。
你听过 800+ 次自我介绍，能在 15 秒内判断这个人是背稿还是真懂。

你对好的自我介绍的定义：
- 第一句话就有钩子：一个数字、一个结果、一个反常识的事实
- 结构是「我是谁 → 我做成过什么 → 为什么是这个岗位」，不是「我叫 XX 来自 XX 大学 XX 专业」
- 每一段都有具体的名词和数字，没有「负责」「参与」「学习了」
- 时长精准：30 秒 ≈ 90 字，1 分钟 ≈ 180 字，3 分钟 ≈ 500 字（中文口语速度）
- 最后一句要把话头递给面试官，引导他问你最想被问的那个项目

你对项目介绍的定义：
- STAR 不是套模板，是让面试官 30 秒内看清「问题有多难、你做了什么决定、结果怎么验证」
- Action 部分必须是「我」而不是「我们」，必须有取舍和决策
- Result 必须有数字，没有数字就说清楚为什么没有、你用什么替代指标
- 好的项目介绍会主动埋 2-3 个「钩子」，引导面试官往你准备好的方向追问

你的风格：直接、具体、不写鸡汤。稿子要能直接开口念，不是书面语。
禁止：「我是一个热爱学习的人」「我具备良好的沟通能力」「贵公司」——这些一出现面试官就走神了。"""


DURATION_MAP = {
    "30": {"seconds": 30, "words": "80-100 字"},
    "60": {"seconds": 60, "words": "160-200 字"},
    "180": {"seconds": 180, "words": "450-550 字"},
}

STYLE_MAP = {
    "结构化": "「我是谁 → 三个亮点 → 为什么这个岗位」的清晰三段式，适合技术岗和大部分校招场景",
    "讲故事": "从一个具体的转折点或项目切入，用叙事带出能力，适合产品、运营、市场岗",
    "数据流": "全程用数字说话，每一句都有量化结果，适合有真实业务数据的候选人和社招",
}

SCENE_MAP = {
    "校招": "应届生校招。面试官想看到：潜力、学习速度、项目的真实程度、为什么选这个方向",
    "社招": "社招。面试官想看到：过往业绩、能直接上手的能力、跳槽动机是否合理、稳定性",
    "实习": "实习。面试官想看到：基础是否扎实、能否快速融入、有没有主动性、时间是否充足",
    "转行": "转行。面试官想看到：可迁移的能力、为什么转、为转行做了什么具体准备、不是一时冲动",
}


def generate_intro(
    resume_text: str,
    jd_text: str = "",
    duration: str = "60",
    style: str = "结构化",
    scene: str = "校招",
    target_role: str = "",
    company: str = "",
) -> dict:
    """
    生成自我介绍稿。

    Args:
        resume_text: 简历或个人背景文本
        jd_text: 目标 JD（可选，有的话会针对性调整）
        duration: "30" | "60" | "180"（秒）
        style: "结构化" | "讲故事" | "数据流"
        scene: "校招" | "社招" | "实习" | "转行"
        target_role: 目标岗位
        company: 目标公司（可选）

    Returns:
        {
            "hook": str,                       # 开场第一句
            "script": str,                     # 完整讲稿
            "structure": [{"section", "content", "seconds"}],
            "closing": str,                    # 收尾引导句
            "speaking_tips": [str],            # 口语化提示
            "avoid": [str],                    # 这份简历最容易踩的坑
            "predicted_first_question": str,   # 面试官听完最可能问的第一个问题
            "word_count": int,
            "markdown": str
        }
    """
    duration = str(duration) if str(duration) in DURATION_MAP else "60"
    style = style if style in STYLE_MAP else "结构化"
    scene = scene if scene in SCENE_MAP else "校招"
    d = DURATION_MAP[duration]

    prompt = f"""请为以下候选人生成一份自我介绍稿。

【候选人背景 / 简历】
{resume_text[:5000]}

【目标岗位】{target_role or '未指定，请根据简历判断'}
【目标公司】{company or '未指定'}

【目标 JD】
{jd_text[:3000] if jd_text else '未提供'}

【参数】
- 时长：{d['seconds']} 秒（{d['words']}，中文口语）
- 风格：{style} — {STYLE_MAP[style]}
- 场景：{scene} — {SCENE_MAP[scene]}

请严格按以下 JSON 结构输出：

```json
{{
  "hook": "开场第一句话，必须有一个具体的数字或结果，10-25 字",
  "script": "完整讲稿，可以直接开口念的口语文本，严格控制在 {d['words']}",
  "structure": [
    {{"section": "段落名（如：开场钩子 / 核心项目 / 为什么这个岗位）", "content": "这一段的要点", "seconds": 15}}
  ],
  "closing": "最后一句，把话头递给面试官、引导他追问你最强的项目",
  "speaking_tips": [
    "口语化建议 1：哪里该停顿、哪里该放慢、哪个数字要加重",
    "口语化建议 2"
  ],
  "avoid": [
    "基于这份简历，这个候选人最容易说出的空话 / 最容易踩的坑 1",
    "坑 2"
  ],
  "predicted_first_question": "面试官听完这段自我介绍后，最可能追问的第一个问题",
  "word_count": 180
}}
```

要求：
- script 必须是口语，不是书面语；不能出现「贵公司」「热爱学习」「沟通能力强」
- hook 必须来自简历里真实存在的内容，不能编造数字
- structure 里的 seconds 加起来必须等于 {d['seconds']}
- 如果简历里没有数字，script 里要用「具体的事」替代，并在 avoid 里指出「简历缺量化结果」
- {scene}场景下要覆盖面试官最关心的点
- 如果提供了 JD，script 里至少要有一处明确呼应 JD 的核心要求"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result and "error" not in result:
        result["params"] = {"duration": duration, "style": style, "scene": scene, "target_role": target_role}
        result["markdown"] = _render_intro(result, d["seconds"], style, scene)

    return result


def generate_project_pitch(
    project_text: str,
    jd_text: str = "",
    depth: str = "3min",
    target_role: str = "",
) -> dict:
    """
    把一段项目经历整理成面试讲稿。

    Args:
        project_text: 项目描述（简历里的原文即可）
        jd_text: 目标 JD（可选）
        depth: "1min" | "3min" | "deep"（深挖版，含技术/业务细节，用于二面三面）
        target_role: 目标岗位

    Returns:
        {
            "project_name": str,
            "one_liner": str,                  # 一句话说清这个项目
            "star": {"situation", "task", "action", "result"},
            "script": str,                     # 按 depth 的完整讲稿
            "hooks": [str],                    # 埋在讲稿里的钩子（引导面试官追问的方向）
            "predicted_questions": [{"question", "why_asked", "answer_strategy"}],
            "risk_points": [str],              # 这个项目描述里面试官会质疑的地方
            "missing_data": [str],             # 缺失的量化信息，面试前要补上
            "markdown": str
        }
    """
    depth = depth if depth in ("1min", "3min", "deep") else "3min"
    depth_desc = {
        "1min": "1 分钟版本（150-200 字），一面开场用，只说问题、决策、结果",
        "3min": "3 分钟版本（450-550 字），标准项目介绍，STAR 完整展开",
        "deep": "深挖版本（700-900 字），二面三面用，包含技术选型 / 业务取舍 / 失败的尝试 / 数据怎么验证的",
    }[depth]

    prompt = f"""请把以下项目经历整理成面试讲稿。

【项目描述（候选人原文）】
{project_text[:5000]}

【目标岗位】{target_role or '未指定，请根据项目判断'}

【目标 JD】
{jd_text[:3000] if jd_text else '未提供'}

【版本】{depth_desc}

请严格按以下 JSON 结构输出：

```json
{{
  "project_name": "项目名",
  "one_liner": "一句话说清这个项目解决了什么问题、结果是什么（30 字内）",
  "star": {{
    "situation": "背景：问题有多难、为什么值得做（2-3 句）",
    "task": "目标：你的具体职责和要达成的指标（1-2 句，必须是「我」）",
    "action": "行动：你做了哪些关键决策和取舍、为什么这么选、放弃了什么（3-5 句）",
    "result": "结果：量化数据 + 怎么验证的 + 有没有反思（2-3 句）"
  }},
  "script": "完整口语讲稿，可以直接念，符合版本字数要求",
  "hooks": [
    "讲稿里埋的钩子 1：你希望面试官往哪个方向追问、为什么这是你的优势区",
    "钩子 2"
  ],
  "predicted_questions": [
    {{
      "question": "面试官最可能追问的问题",
      "why_asked": "他为什么问这个（在验证什么）",
      "answer_strategy": "回答策略：要点、要用的数据、要避开的坑"
    }}
  ],
  "risk_points": [
    "这段项目描述里面试官会质疑的地方（如：数据来源、是否真实用户、你的真实贡献占比）"
  ],
  "missing_data": [
    "面试前必须补上的量化信息（如：DAU 多少、留存多少、上线前后对比）"
  ]
}}
```

要求：
- action 必须是「我」的决策，不能是「我们团队」；如果原文全是「我们」，在 risk_points 里指出
- predicted_questions 至少 5 个，按被问概率排序，第一个必须是最尖锐的那个
- 不能编造原文没有的数字；缺数字的地方写进 missing_data
- script 必须是口语，能直接开口念
- 如果提供了 JD，hooks 里至少有一个指向 JD 的核心能力"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result and "error" not in result:
        result["params"] = {"depth": depth, "target_role": target_role}
        result["markdown"] = _render_pitch(result, depth)

    return result


# ═══════════════════════════════════════════════════════════
# Rendering
# ═══════════════════════════════════════════════════════════

def _render_intro(data: dict, seconds: int, style: str, scene: str) -> str:
    lines = [
        f"# 🎙️ 自我介绍稿 · {seconds} 秒 · {style} · {scene}",
        "",
        "## 开场钩子",
        f"> **{data.get('hook', '')}**",
        "",
        "## 完整讲稿",
        "",
        data.get("script", ""),
        "",
        f"*约 {data.get('word_count', '?')} 字*",
        "",
    ]

    if data.get("structure"):
        lines.extend(["## 结构拆解", "", "| 段落 | 要点 | 时长 |", "|------|------|------|"])
        for s in data["structure"]:
            lines.append(f"| {s.get('section', '')} | {s.get('content', '')} | {s.get('seconds', '')}s |")
        lines.append("")

    if data.get("closing"):
        lines.extend(["## 收尾引导", f"> {data['closing']}", ""])

    if data.get("speaking_tips"):
        lines.append("## 🗣️ 口语提示")
        for t in data["speaking_tips"]:
            lines.append(f"- {t}")
        lines.append("")

    if data.get("avoid"):
        lines.append("## ⚠️ 你最容易踩的坑")
        for a in data["avoid"]:
            lines.append(f"- {a}")
        lines.append("")

    if data.get("predicted_first_question"):
        lines.extend([
            "## 🎯 面试官听完最可能问的第一个问题",
            f"> {data['predicted_first_question']}",
            "",
            "*建议：把这个问题丢进「模拟面试」预演一遍。*",
            "",
        ])

    return "\n".join(lines)


def _render_pitch(data: dict, depth: str) -> str:
    depth_label = {"1min": "1 分钟版", "3min": "3 分钟版", "deep": "深挖版"}[depth]
    lines = [
        f"# 🎯 项目讲稿 · {data.get('project_name', '')} · {depth_label}",
        "",
        f"> {data.get('one_liner', '')}",
        "",
    ]

    star = data.get("star", {})
    if star:
        lines.extend([
            "## STAR 拆解",
            "",
            f"**S · 背景**：{star.get('situation', '')}",
            "",
            f"**T · 目标**：{star.get('task', '')}",
            "",
            f"**A · 行动**：{star.get('action', '')}",
            "",
            f"**R · 结果**：{star.get('result', '')}",
            "",
        ])

    lines.extend(["## 完整讲稿", "", data.get("script", ""), ""])

    if data.get("hooks"):
        lines.append("## 🪝 埋的钩子（引导面试官往这里追问）")
        for h in data["hooks"]:
            lines.append(f"- {h}")
        lines.append("")

    if data.get("predicted_questions"):
        lines.extend(["## 🔮 预判追问", ""])
        for i, q in enumerate(data["predicted_questions"], 1):
            lines.append(f"**{i}. {q.get('question', '')}**")
            lines.append(f"- 他在验证什么：{q.get('why_asked', '')}")
            lines.append(f"- 回答策略：{q.get('answer_strategy', '')}")
            lines.append("")

    if data.get("risk_points"):
        lines.append("## 🔴 面试官会质疑的地方")
        for r in data["risk_points"]:
            lines.append(f"- {r}")
        lines.append("")

    if data.get("missing_data"):
        lines.append("## 📌 面试前必须补上的数据")
        for m in data["missing_data"]:
            lines.append(f"- [ ] {m}")
        lines.append("")

    return "\n".join(lines)
