"""
Contradiction Engine — 矛盾检测 + 精准追问

The most feared interviewer move: remembering what you said 5 minutes ago
and catching the contradiction in your 3rd answer.

This engine:
1. Stores all candidate answers
2. Detects logical contradictions between answers
3. Generates precise follow-up questions that cite the contradiction
"""

from utils import callLlm, safeCallLlm
from typing import Optional


SYSTEM_PROMPT = """你是字节跳动的资深面试官，你的核心能力是发现候选人回答中的矛盾。

你的方法：
- 记住候选人之前说的每一句话
- 在新的回答中寻找与之前回答的矛盾
- 一旦发现矛盾，立即指出并追问
- 追问必须引用候选人的原话，不能凭空捏造
- 追问语气取决于面试模式：温和（好奇）、高压（质疑）、地狱（压迫）

矛盾类型：
1. 事实矛盾 — 前面说 A，后面说非 A
2. 逻辑矛盾 — 前面说因为 X，后面做的却是反 X
3. 程度矛盾 — 前面说很重视某件事，后面承认没做过
4. 时间矛盾 — 时间线对不上
5. 角色矛盾 — 前面说是自己主导，后面暴露只是参与者"""


def detect_contradiction(
    chat_history: list[dict],
    latest_answer: str,
    mode: str = "高压",
) -> dict:
    """
    Analyze the latest answer against all previous answers for contradictions.

    Args:
        chat_history: All previous messages (interviewer + candidate)
        latest_answer: The candidate's most recent answer
        mode: Interview mode (affects the tone of the follow-up)

    Returns:
        {
            "has_contradiction": bool,
            "contradiction_type": str or None,
            "previous_statement": str or None,
            "current_statement": str or None,
            "follow_up_question": str or None,
            "analysis": str
        }
    """
    # Extract candidate answers
    candidate_answers = []
    for msg in chat_history:
        if msg["role"] == "candidate":
            candidate_answers.append(msg["content"])

    if len(candidate_answers) < 1:
        return {
            "has_contradiction": False,
            "contradiction_type": None,
            "previous_statement": None,
            "current_statement": None,
            "follow_up_question": None,
            "analysis": "Not enough answers to detect contradiction",
        }

    # Build previous answers context (exclude the latest, which is being analyzed)
    previous_text = "\n---\n".join(candidate_answers)

    prompt = f"""分析候选人的最新回答是否与之前的回答存在矛盾。

【候选人历史回答】
{previous_text[:4000]}

【候选人最新回答】
{latest_answer}

【面试模式】{mode}

请检测是否存在以下矛盾：
1. 事实矛盾 — 前面说 A，后面说非 A
2. 逻辑矛盾 — 前面说因为 X，后面做的却是反 X
3. 程度矛盾 — 前面说很重视某件事，后面承认没做过
4. 时间矛盾 — 时间线对不上
5. 角色矛盾 — 前面说是自己主导，后面暴露只是参与者

输出 JSON：
```json
{{
  "has_contradiction": true,
  "contradiction_type": "程度矛盾",
  "previous_statement": "引用候选人之前说的原话",
  "current_statement": "引用候选人现在说的原话",
  "follow_up_question": "精准的追问，必须引用两段原话，语气匹配 {mode} 模式",
  "analysis": "简要分析这个矛盾说明了什么"
}}
```

要求：
- 如果没有矛盾，has_contradiction 为 false
- 追问必须具体、有压迫感、引用原话
- 语气匹配面试模式：温和=好奇追问，高压=质疑追问，地狱=压迫追问"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")
    return result


def generate_precision_followup(
    contradiction: dict,
    mode: str = "高压",
) -> str:
    """
    Generate a single precision follow-up question from a contradiction.

    Args:
        contradiction: Output from detect_contradiction()
        mode: Interview mode

    Returns:
        A sharp follow-up question string
    """
    if not contradiction.get("has_contradiction"):
        return ""

    followup = contradiction.get("follow_up_question", "")
    if followup:
        return followup

    # Fallback: construct from pieces
    prev = contradiction.get("previous_statement", "")
    curr = contradiction.get("current_statement", "")
    ctype = contradiction.get("contradiction_type", "")

    templates = {
        "温和": f"我注意到一个细节想确认一下。你之前提到「{prev}」，但现在你说「{curr}」。这两者之间你是怎么看的？",
        "高压": f"等一下，你之前说过「{prev}」。但你刚才说的是「{curr}」。这两句话是矛盾的。你怎么解释？",
        "地狱": f"打断你。你前面说「{prev}」。现在你说「{curr}」。你自己意识到这之间的矛盾了吗？说清楚。",
    }

    return templates.get(mode, templates["高压"])
