"""
Group Interview Simulator — 无领导小组讨论模拟。

User plays one role, AI plays 2-3 other roles.
5 rounds of discussion on a given topic.
Ends with analysis: speech count, idea quality, collaboration score.
"""

from utils import callLlm, safeCallLlm

GROUP_SYSTEM_PROMPT = """你是一个无领导小组讨论的 AI 引导者。
你能同时扮演多个角色，每个角色有鲜明的立场和表达风格。

你的原则：
- 每个角色的发言要符合其岗位视角（如开发关注技术可行性，运营关注用户增长）
- 角色之间要有自然的碰撞和呼应，不是各说各话
- 讨论要围绕主题推进，5 轮后要有明确结论
- 用户发言后，你要评估其观点质量，然后生成其他角色的回应
- 最后一轮结束后，给出完整分析"""


def start_group_interview(role: str, other_roles: list, topic: str) -> dict:
    """
    Start a group interview session.

    Args:
        role: User's role (e.g. "产品经理")
        other_roles: AI roles (e.g. ["后端开发", "运营", "设计"])
        topic: Discussion topic (e.g. "如何提升一款社交App的次日留存")

    Returns:
        Session state dict with opening context.
    """
    other_roles = other_roles[:3]  # Max 3 AI roles
    all_roles = [role] + other_roles

    prompt = f"""你正在主持一场无领导小组讨论。

讨论主题：{topic}
参与者角色：{', '.join(all_roles)}
用户扮演：{role}

请生成开场引导。内容包括：
1. 简要说明讨论主题和背景（2-3句话）
2. 每个 AI 角色的 1 句话开场立场（如开发说"从技术角度，我们先要确定可实现的方案"）
3. 引导用户（{role}）先发表观点

输出 JSON：
```json
{{
  "opening": "开场引导文本（纯文本，带角色立场）",
  "topic_summary": "主题一句话总结",
  "all_roles": ["{role}", {', '.join(f'"{r}"' for r in other_roles)}],
  "current_round": 0,
  "max_rounds": 5
}}
```"""

    result = safeCallLlm(prompt, GROUP_SYSTEM_PROMPT, output_format="json",
                         fallback={"opening": f"讨论主题：{topic}\n参与者：{', '.join(all_roles)}\n请{role}先发表观点。",
                                   "all_roles": all_roles, "current_round": 0, "max_rounds": 5})

    if isinstance(result, dict) and "_trait" not in result:
        result["session_id"] = "group_session"
        result["history"] = []
        result["role"] = role
        result["topic"] = topic
        result["other_roles"] = other_roles
        result["all_roles"] = all_roles

    return result


def group_respond(session_state: dict, user_answer: str) -> dict:
    """
    User speaks, AI roles respond. Advances one round.

    Args:
        session_state: State from start_group_interview or previous group_respond
        user_answer: User's latest statement

    Returns:
        Updated session_state with new responses and incremented round.
    """
    session_state["history"].append({"role": session_state["role"], "content": user_answer})
    current_round = session_state.get("current_round", 0) + 1
    session_state["current_round"] = current_round
    max_rounds = session_state.get("max_rounds", 5)
    is_final = current_round >= max_rounds

    # Build conversation context
    transcript = ""
    for msg in session_state["history"]:
        transcript += f"{msg['role']}: {msg['content']}\n"

    other_roles = session_state.get("other_roles", [])
    topic = session_state.get("topic", "")

    prompt = f"""无领导小组讨论 — 第 {current_round}/{max_rounds} 轮

讨论主题：{topic}

对话历史：
{transcript}

用户（{session_state.get('role', '')}）刚才的发言：{user_answer}

请生成其他角色的回应。每个角色基于自己的岗位视角发言，要有自然的观点碰撞。

{'这是最后一轮，讨论结束后每个角色应形成自己的结论。' if is_final else f'还有 {max_rounds - current_round} 轮讨论。'}

输出 JSON：
```json
{{
  "responses": [
    {{"role": "{other_roles[0] if other_roles else '角色A'}", "content": "角色发言内容"}},
    {{"role": "{other_roles[1] if len(other_roles) > 1 else '角色B'}", "content": "角色发言内容"}}
  ],
  "phase": "discussion",
  "is_complete": {str(is_final).lower()},
  "round_summary": "本轮讨论要点（1句话）"
}}
```"""

    result = safeCallLlm(prompt, GROUP_SYSTEM_PROMPT, output_format="json",
                         fallback={"responses": [{"role": r, "content": "（请阐述你的观点）"} for r in other_roles],
                                   "phase": "discussion", "is_complete": is_final})

    if isinstance(result, dict) and "_trait" not in result:
        for resp in result.get("responses", []):
            session_state["history"].append({"role": resp["role"], "content": resp["content"]})
        result["current_round"] = current_round
        result["max_rounds"] = max_rounds

    return result


def group_evaluate(session_state: dict) -> dict:
    """
    Evaluate the complete group interview.

    Args:
        session_state: Final session state after all rounds

    Returns:
        {
            "speech_analysis": [{"role": str, "count": int, "avg_length": int}],
            "idea_quality": [{"role": str, "score": int, "comment": str}],
            "collaboration_score": {"role": str, "score": int},
            "user_performance": {"strengths": [...], "weaknesses": [...], "tips": str},
            "overall": str,
            "markdown": str
        }
    """
    transcript = ""
    for msg in session_state.get("history", []):
        transcript += f"{msg['role']}: {msg['content']}\n"

    user_role = session_state.get("role", "")
    topic = session_state.get("topic", "")

    prompt = f"""请评估以下无领导小组讨论。

讨论主题：{topic}
用户角色：{user_role}

完整对话记录：
{transcript[:6000]}

请分析：

1. 发言统计 — 每个角色的发言次数和平均长度
2. 观点质量 — 每个角色的观点是否有深度、有数据、有逻辑（1-10分）
3. 协作度 — 每个角色的倾听和响应能力（1-10分）
4. 用户表现 — 针对 {user_role} 的具体评价（优点、不足、提升建议）

输出 JSON：
```json
{{
  "speech_analysis": [
    {{"role": "角色名", "count": 0, "avg_length": 0}}
  ],
  "idea_quality": [
    {{"role": "角色名", "score": 5, "comment": "一句话评价"}}
  ],
  "collaboration_score": [
    {{"role": "角色名", "score": 5, "comment": "一句话评价"}}
  ],
  "user_performance": {{
    "strengths": ["具体优点1", "具体优点2"],
    "weaknesses": ["具体不足1"],
    "tips": "最关键的 1 条提升建议"
  }},
  "overall": "整体评价（100字以内）"
}}
```"""

    result = safeCallLlm(prompt, GROUP_SYSTEM_PROMPT, output_format="json",
                         fallback={"overall": "评估暂时不可用", "markdown": "> 群面评估暂时不可用，请重试。"})

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_group_markdown(result, session_state)

    return result


def _render_group_markdown(data: dict, session_state: dict) -> str:
    """Render group interview analysis as Markdown."""
    topic = session_state.get("topic", "")
    role = session_state.get("role", "")
    all_roles = session_state.get("all_roles", [])

    lines = [
        "# 👥 群面模拟分析报告",
        "",
        f"**讨论主题：** {topic}",
        f"**你的角色：** {role}",
        f"**参与角色：** {', '.join(all_roles)}",
        f"**讨论轮次：** {session_state.get('current_round', 0)}",
        "",
        "## 📊 发言统计",
        "",
        "| 角色 | 发言次数 | 平均长度 |",
        "|---|---|---|",
    ]

    for s in data.get("speech_analysis", []):
        lines.append(f"| {s.get('role', '')} | {s.get('count', 0)} | {s.get('avg_length', 0)} 字 |")

    lines.extend(["", "## 💡 观点质量", ""])
    for iq in data.get("idea_quality", []):
        score = iq.get("score", 5)
        bar = "█" * score + "░" * (10 - score)
        lines.append(f"**{iq.get('role', '')}**：{score}/10 `{bar}`")
        lines.append(f"> {iq.get('comment', '')}")
        lines.append("")

    lines.extend(["", "## 🤝 协作度", ""])
    for cs in data.get("collaboration_score", []):
        lines.append(f"**{cs.get('role', '')}**：{cs.get('score', 0)}/10 — {cs.get('comment', '')}")

    up = data.get("user_performance", {})
    lines.extend([
        "",
        f"## 🎯 你的表现（{role}）",
        "",
        "### ✅ 优点",
    ])
    for s in up.get("strengths", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("### ⚠️ 不足")
    for w in up.get("weaknesses", []):
        lines.append(f"- {w}")
    lines.append("")
    lines.append(f"### 💡 提升建议")
    lines.append(f"> {up.get('tips', '')}")

    if data.get("overall"):
        lines.extend(["", "## 📝 整体评价", "", data["overall"], ""])

    return "\n".join(lines)
