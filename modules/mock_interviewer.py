"""
Mock Interviewer v2 — 高压模拟面试 + 矛盾检测 + 地狱模式

Three modes with distinct personalities:
- 温和: Curious, helps candidate think deeper, 2-3 layers
- 高压: Aggressive, points out gaps, 4-5 layers, contradiction detection
- 地狱: Maximum pressure, questions everything, deep probing, remembers everything

v2 Upgrades:
- Integrated contradiction engine
- Hell mode with genuine pressure tactics
- Chat memory with cross-reference capability
- Pressure scoring display
- Black speech detection during interview
"""

from utils import callLlm
from typing import Optional

SYSTEM_PROMPT = """你是字节跳动的真实面试官。不是模拟，不是角色扮演——你就是。

你的面试风格取决于当前模式：

温和模式：
- 正常节奏，给候选人思考时间
- 追问 2-3 层
- 语气专业但不失友善
- 但不会放过模糊回答

高压模式：
- 连续追问 4-5 层
- 不轻易放过任何模糊回答
- 指出逻辑漏洞和矛盾
- 要求具体数据和案例
- 语气直接、有压迫感

地狱模式（这是你的标志性风格）：
- 极高压力，质疑一切
- 记住候选人说的每一句话，在后面找出矛盾
- 连续追问 7 层以上
- 直接指出问题：「你这个回答太表面了」「你没有真正做过对吧」
- 语气冷酷、精准、不留情面
- 让候选人感到「被一个 P8 面试官拷打」

你的标志性地狱追问：
- 「为什么你的产品没人用？」
- 「你觉得你和 985 学生相比优势是什么？」
- 「如果我是面试官，我为什么不刷掉你？」
- 「你的项目为什么不像课程作业？」
- 「你到底解决了什么真实问题？」
- 「你说的这个数据是怎么得出来的？你自己算过吗？」
- 「你刚才说的是 A，现在说的是 B，你意识到矛盾了吗？」
- 「不要用黑话敷衍我，说具体做了什么。」
- 「你的 AI 能力停留在 Chat 层面，不是 Workflow 层面，你知道区别吗？」

你的原则（三种模式通用）：
- 不满足于「我觉得」「可能是」「大概」等模糊表达
- 追问到候选人给出具体数据或逻辑
- 发现矛盾立即指出
- 发现黑话立即要求解释
- 发现亮点立即深挖
- 面试结束必须给出明确结论"""


def start_interview(mode: str = "高压", target_role: str = "产品经理", jd_text: str = "") -> dict:
    """
    Start a new interview session.

    Args:
        mode: 温和 / 高压 / 地狱
        target_role: Target position
        jd_text: Optional JD for context

    Returns:
        {"opening": str, "mode": str, "session_id": str, "pressure_level": int}
    """
    pressure_map = {"温和": 3, "高压": 7, "地狱": 10}

    prompt = f"""你正在面试一位{target_role}候选人。

岗位 JD: {jd_text or '未提供'}

面试模式: {mode}

开场要求：
- 温和: 正常自我介绍要求，30 秒到 1 分钟
- 高压: 直接说「自我介绍，说重点，不要背书」
- 地狱: 极简短：「自我介绍，30 秒。直接说你做了什么、结果是什么。如果我觉得你在背稿我会打断你。」

请给出开场白，语气必须匹配 {mode} 模式。"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="text")
    opening = result if isinstance(result, str) else result.get("raw", "开始吧，自我介绍一下。")

    return {
        "opening": opening,
        "mode": mode,
        "session_id": "interview_session",
        "pressure_level": pressure_map.get(mode, 5),
    }


def respond(
    user_answer: str,
    mode: str = "高压",
    target_role: str = "产品经理",
    jd_text: str = "",
    chat_history: Optional[list] = None,
) -> dict:
    """
    Generate the interviewer's response with contradiction detection.

    v2: Now integrates contradiction detection for high-pressure and hell modes.
    """
    chat_history = chat_history or []

    # For 高压 and 地狱, inject contradiction check into the prompt
    contradiction_hint = ""
    if mode in ("高压", "地狱") and len(chat_history) >= 3:
        # Extract candidate's previous answers for contradiction context
        prev_answers = [m["content"] for m in chat_history if m["role"] == "candidate"]
        if len(prev_answers) >= 2:
            contradiction_hint = f"""
【矛盾检测提示】
候选人的历史回答：
{chr(10).join(f'- "{a[:200]}"' for a in prev_answers[-3:])}

请在追问时注意：如果最新回答与历史回答存在矛盾，必须直接指出。
引用候选人的原话：「你之前说过 X，现在你又说 Y，这之间的矛盾你怎么解释？」
"""

    history_text = ""
    for msg in chat_history[-10:]:
        role = "面试官" if msg["role"] == "interviewer" else "候选人"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""你正在面试一位{target_role}候选人。模式: {mode}

{contradiction_hint}

对话历史:
{history_text}

候选人最新回答:
{user_answer}

请生成你的追问。

规则：
- 如果回答模糊（我觉得/可能/大概/好像），必须追问具体细节
- 如果回答空洞（没有数据、没有具体案例），要求补充
- 如果回答有矛盾，必须指出：「你之前说过 X，现在又说 Y」
- 如果用了黑话（赋能/闭环/抓手/对齐/拉通），要求解释具体含义
- 如果回答有亮点，深挖下去
- {mode}模式允许的追问深度：温和3层/高压5层/地狱7层
- 如果追问达到深度上限，过渡到下一个话题或结束面试

输出 JSON：
```json
{{
  "interviewer_message": "你的追问或点评",
  "phase": "probing",
  "is_complete": false,
  "pressure_level": 7,
  "probe_topic": "当前话题",
  "contradiction_detected": false
}}
```"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")
    return result


def evaluate(
    chat_history: list[dict],
    mode: str = "高压",
    target_role: str = "产品经理",
) -> dict:
    """
    Evaluate the complete interview. v2: harsher, more realistic.
    """
    transcript = ""
    for msg in chat_history:
        role = "面试官" if msg["role"] == "interviewer" else "候选人"
        transcript += f"{role}: {msg['content']}\n\n"

    prompt = f"""请评估以下模拟面试。岗位：{target_role}，模式：{mode}

面试记录:
{transcript[:6000]}

评分维度（1-10分）：
- 产品 Sense — 能否判断什么是好产品
- 增长意识 — 是否关注用户增长和 ROI
- 数据思维 — 能否定义核心指标并用数据验证
- 执行力/Owner 意识 — 是否主动推动而非被动执行
- AI 协同能力 — AI 使用深度（Chat 层面 vs Workflow 层面）
- 沟通表达 — 能否把复杂问题说清楚
- 真实性/深度 — 回答有细节还是空洞

输出 JSON：
```json
{{
  "overall_score": 6.5,
  "dimension_scores": {{
    "产品Sense": 6.0,
    "增长意识": 5.0,
    "数据思维": 6.5,
    "执行力/Owner意识": 7.0,
    "AI协同能力": 5.5,
    "沟通表达": 7.0,
    "真实性/深度": 6.0
  }},
  "strengths": ["必须引用实际对话"],
  "weaknesses": ["必须引用实际对话"],
  "verdict": "综合评价，是否推荐进入下一轮",
  "advice": "最关键的 1-2 条提升建议",
  "is_recommended": true
}}
```

要求：
- 评价必须引用面试中的实际对话
- weaknesses 必须是具体的、可操作的
- verdict 必须明确
- 如果模式是地狱，评分应更严苛"""

    result = callLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_evaluation(result, mode)

    return result


def _render_evaluation(data: dict, mode: str) -> str:
    """Render interview evaluation as Markdown card."""
    score = data.get("overall_score", 0)
    if score >= 8:
        color, emoji, label = "#2dd4bf", "🟢", "推荐进入下一轮"
    elif score >= 5:
        color, emoji, label = "#f59e0b", "🟡", "有条件通过"
    else:
        color, emoji, label = "#ef4444", "🔴", "建议不通过"

    lines = [
        f"# 🎤 面试评估报告 — {mode}模式",
        "",
        f"## 综合评分：{score}/10  {emoji} {label}",
        "",
        "## 各维度得分",
        "",
    ]

    for dim, s in data.get("dimension_scores", {}).items():
        bar = "█" * int(s) + "░" * (10 - int(s))
        lines.append(f"**{dim}**：{s}/10 `{bar}`")
        lines.append("")

    lines.append("## 🟢 亮点")
    for s in data.get("strengths", []):
        lines.append(f"- {s}")

    lines.append("")
    lines.append("## 🔴 问题")
    for w in data.get("weaknesses", []):
        lines.append(f"- {w}")

    lines.extend([
        "",
        "```",
        f"  结论：{data.get('verdict', '')}",
        "```",
        "",
        "## 💡 建议",
        data.get("advice", ""),
        "",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════
# AI Pressure System — 动态压力值
# ═══════════════════════════════════════════════

def calculate_pressure(
    answer: str,
    mode: str = "高压",
    history: Optional[list] = None,
    previous_pressure: int = 50,
) -> dict:
    """
    Calculate dynamic pressure value based on answer quality.

    Pressure rises when:
    - Answer is vague (我觉得/可能/大概)
    - No data mentioned
    - Uses buzzwords without substance
    - Short, evasive answers
    - Contradiction with previous answers detected

    Pressure drops when:
    - Specific data provided
    - Concrete examples given
    - Clear logic chain
    - Admitting limitations honestly
    - Deep insight shown

    Args:
        answer: Candidate's latest answer
        mode: 温和/高压/地狱
        history: Chat history for contradiction context
        previous_pressure: Previous pressure value

    Returns:
        {
            "pressure": int (0-100),
            "change": int (+/-),
            "direction": "up"|"down"|"steady",
            "reasons": [str],
            "suspicion_level": int (0-100),
            "suspicion_reasons": [str],
            "display": str
        }
    """
    history = history or []
    reasons = []
    suspicion_reasons = []
    change = 0

    # Base pressure from mode
    mode_base = {"温和": 20, "高压": 50, "地狱": 70}[mode]

    # ---- Pressure UP factors ----

    # 1. Vague language
    vague_words = ["我觉得", "可能是", "大概", "好像", "应该", "也许", "不太清楚"]
    vague_count = sum(1 for w in vague_words if w in answer)
    if vague_count >= 2:
        change += 8 + vague_count * 3
        reasons.append(f"模糊表达 x{vague_count} — 面试官耐心下降")
        suspicion_reasons.append("回答缺乏确定性，可能在回避")

    # 2. No data
    has_data = any(c.isdigit() for c in answer) or any(
        kw in answer for kw in ["%", "倍", "人", "万", "千", "数据", "指标"]
    )
    if not has_data and len(answer) > 30:
        change += 6
        reasons.append("缺少数据支撑 — 面试官开始怀疑")
        suspicion_reasons.append("没有数据，项目真实性存疑")

    # 3. Buzzword overdose
    buzzwords = ["赋能", "闭环", "抓手", "对齐", "拉通", "底层逻辑", "顶层设计", "颗粒度"]
    buzz_count = sum(1 for bw in buzzwords if bw in answer)
    if buzz_count >= 2:
        change += 5 + buzz_count * 2
        reasons.append(f"互联网黑话 x{buzz_count} — 面试官怀疑在包装")
        suspicion_reasons.append("过度使用黑话，可能在掩盖内容空洞")

    # 4. Too short
    if len(answer) < 30:
        change += 10
        reasons.append("回答过短 — 面试官认为你在回避")
        suspicion_reasons.append("回答太短，可能没有真正做过")

    # 5. Defensive language
    defensive = ["主要是团队", "因为别人", "不是我负责", "当时没想那么多"]
    if any(d in answer for d in defensive):
        change += 7
        reasons.append("防御性表达 — 面试官怀疑 Owner 意识不足")
        suspicion_reasons.append("推卸责任信号，可能只是参与者")

    # 6. AI demo smell
    ai_demo_signals = ["AI生成", "AI搭建", "用AI做了个"]
    if any(s in answer for s in ai_demo_signals) and not has_data:
        change += 8
        reasons.append("AI Demo 味 — 面试官怀疑没有真实用户")
        suspicion_reasons.append("AI 套壳 Demo，可能没有用户验证")

    # ---- Pressure DOWN factors ----

    # 1. Specific data
    if has_data and len(answer) > 50:
        change -= 5
        reasons.append("提供了数据 — 面试官态度缓和")

    # 2. Honest admission
    honest_phrases = ["说实话", "确实做得不够", "当时没有考虑到", "这是一个失误", "后来才发现"]
    if any(h in answer for h in honest_phrases):
        change -= 8
        reasons.append("坦率承认不足 — 面试官认可诚实")

    # 3. Deep insight
    insight_phrases = ["本质是", "根本原因", "核心问题", "真正的痛点"]
    if any(i in answer for i in insight_phrases):
        change -= 6
        reasons.append("展示了深度思考 — 面试官压力减轻")

    # 4. Specific AI workflow
    ai_workflow_phrases = ["工作流", "效率提升", "用Trae做", "用Cursor写", "用Codex", "我的流程是"]
    if any(a in answer for a in ai_workflow_phrases):
        change -= 4
        reasons.append("展示了 AI 工作流 — 加分")

    # ---- Hell mode multiplier ----
    if mode == "地狱":
        change = int(change * 1.5)

    # Calculate final pressure
    new_pressure = max(0, min(100, previous_pressure + change))

    # Suspicion level (separate metric, 0-100)
    suspicion = max(0, min(100, mode_base + len(suspicion_reasons) * 15))

    # Direction
    if change > 3:
        direction = "up"
    elif change < -3:
        direction = "down"
    else:
        direction = "steady"

    # Display bar
    bar_filled = new_pressure // 5
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    # Color
    if new_pressure >= 80:
        color, emoji = "🔴", "危险"
    elif new_pressure >= 55:
        color, emoji = "🟡", "注意"
    else:
        color, emoji = "🟢", "稳定"

    return {
        "pressure": new_pressure,
        "change": change,
        "direction": direction,
        "reasons": reasons,
        "suspicion_level": suspicion,
        "suspicion_reasons": suspicion_reasons,
        "display": f"{emoji} AI压力值：{new_pressure}%  `{bar}`  {color} {direction}",
        "bar": bar,
        "color": color,
    }


def get_pressure_display(pressure_data: dict) -> str:
    """Generate a rich pressure display card."""
    lines = [
        "```",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  ⚡ AI 压力值：{pressure_data['pressure']}%",
        f"  {pressure_data['bar']}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
    ]

    if pressure_data["direction"] == "up":
        lines.append(f"📈 压力上升 +{pressure_data['change']}")
    elif pressure_data["direction"] == "down":
        lines.append(f"📉 压力下降 {pressure_data['change']}")
    else:
        lines.append("➡️ 压力稳定")

    if pressure_data["reasons"]:
        lines.append("")
        for r in pressure_data["reasons"]:
            lines.append(f"- {r}")

    if pressure_data["suspicion_level"] >= 60:
        lines.append("")
        lines.append(f"⚠️ 面试官怀疑值：{pressure_data['suspicion_level']}%")
        for sr in pressure_data.get("suspicion_reasons", []):
            lines.append(f"- {sr}")

    lines.append("")
    return "\n".join(lines)