"""
Interview Feedback System — 真实字节面评生成器

Generates realistic ByteDance interviewer evaluation reports.
Not generic feedback — this reads like an actual internal review system entry.

Output style:
- Has advantages, risks, and a clear conclusion
- Uses "conditional pass" not "good performance"
- Lists specific risk points, not vague "needs improvement"
"""

from utils import callLlm, safeCallLlm

SYSTEM_PROMPT = """你是字节跳动的面试官，正在写面评。

你的面评风格：
- 像真实字节内部面评系统里写的，不是给候选人看的礼貌版本
- 有优点、有风险、有明确结论
- 会写「有条件通过」「建议不通过」而不是「表现不错」「继续努力」
- 会写具体风险点而不是「需要提升」
- 语言直接、专业、有判断力
- 不写废话，每句话都有信息量

面评结构：
1. 总体评价（一句话定性）
2. 优势（具体，不超过 3 条）
3. 风险/问题（具体，不超过 3 条）
4. 关键争议点（如果有）
5. 是否建议进入下一轮 + 理由"""


def generate_feedback(
    chat_history: list[dict],
    target_role: str = "产品经理",
    mode: str = "高压",
    candidate_name: str = "候选人",
) -> dict:
    """
    Generate a realistic interviewer evaluation report.

    Args:
        chat_history: Full interview transcript
        target_role: Target position
        mode: Interview mode (温和/高压/地狱)
        candidate_name: Name to use in the report

    Returns:
        {
            "overall_rating": str,
            "advantages": [str],
            "risks": [str],
            "disputes": [str],
            "verdict": str,
            "verdict_type": "pass" | "conditional_pass" | "reject",
            "action_items": [str],
            "markdown": str
        }
    """
    transcript = ""
    for msg in chat_history:
        role = "面试官" if msg["role"] == "interviewer" else "候选人"
        transcript += f"{role}: {msg['content']}\n\n"

    prompt = f"""你是字节跳动{target_role}面试官。请基于以下面试记录，写一份正式面评。

面试信息：
- 岗位：{target_role}
- 面试模式：{mode}
- 候选人：{candidate_name}

完整面试记录：
{transcript[:6000]}

请输出 JSON：
```json
{{
  "overall_rating": "一句话定性评价（如：产品sense中等偏上，但项目深度不足）",
  "advantages": [
    "具体优势1 — 必须引用面试中的实际回答作为证据",
    "具体优势2",
    "具体优势3（如有）"
  ],
  "risks": [
    "具体风险1 — 必须指出面试中暴露的具体问题",
    "具体风险2",
    "具体风险3（如有）"
  ],
  "disputes": [
    "争议点1 — 面试中有分歧或需要二面确认的地方"
  ],
  "verdict": "是否建议进入下一轮 + 一句话理由（如：有条件通过，建议补真实用户数据案例后再面一轮）",
  "verdict_type": "conditional_pass",
  "action_items": [
    "如果通过，建议候选人补充什么",
    "如果二面，重点考察什么"
  ]
}}
```

verdict_type 可选值: pass / conditional_pass / reject

要求：
- 每条评价必须引用面试中的实际对话作为证据
- risks 必须具体，不能写「需要提升」这种废话
- verdict 必须明确，不能含糊
- 风格必须像真实字节面评，不是给候选人看的礼貌版本"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json")

    if isinstance(result, dict) and "_trait" not in result:
        result["markdown"] = _render_markdown(result)

    return result


def _render_markdown(data: dict) -> str:
    """Render feedback as a realistic interview evaluation card."""
    verdict_type = data.get("verdict_type", "conditional_pass")
    verdict_emoji = {
        "pass": "✅",
        "conditional_pass": "⚠️",
        "reject": "❌",
    }
    verdict_label = {
        "pass": "建议通过",
        "conditional_pass": "有条件通过",
        "reject": "建议不通过",
    }
    emoji = verdict_emoji.get(verdict_type, "⚠️")
    label = verdict_label.get(verdict_type, "待定")

    lines = [
        "```",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📋  字节跳动面试评价表",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
        f"## 总体评价",
        f"> {data.get('overall_rating', '')}",
        "",
        "## 🟢 优势",
    ]

    for adv in data.get("advantages", []):
        lines.append(f"- {adv}")

    lines.extend(["", "## 🔴 风险"])

    for risk in data.get("risks", []):
        lines.append(f"- ⚠️ {risk}")

    if data.get("disputes"):
        lines.extend(["", "## 🟡 争议点"])
        for d in data.get("disputes", []):
            lines.append(f"- {d}")

    lines.extend([
        "",
        "```",
        f"  {emoji} 结论：{label}",
        f"  {data.get('verdict', '')}",
        "```",
        "",
    ])

    if data.get("action_items"):
        lines.append("## 📝 后续建议")
        for item in data["action_items"]:
            lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)
