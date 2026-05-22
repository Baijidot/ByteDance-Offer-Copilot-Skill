"""
Growth Tracker — 用户成长追踪系统

Records user progress over time:
- Resume versions
- Interview history
- Identified problems
- Growth suggestions
- Project changes
- Offer probability changes

Generates growth curve visualizations.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
from utils import loadGrowthData, saveGrowthData, callLlm


def record_session(
    user_id: str,
    session_type: str,
    data: dict,
) -> dict:
    """
    Record a user session for growth tracking.

    Args:
        user_id: Unique user identifier
        session_type: "jd_analysis" | "offer_prediction" | "resume_rewrite" | "interview" | "growth_plan"
        data: Session result data

    Returns:
        Updated user record
    """
    storage = loadGrowthData()

    if user_id not in storage["users"]:
        storage["users"][user_id] = {
            "created_at": datetime.now().isoformat(),
            "sessions": [],
            "resume_versions": [],
            "offer_probability_history": [],
            "problems_identified": [],
            "growth_milestones": [],
        }

    user = storage["users"][user_id]

    session_record = {
        "timestamp": datetime.now().isoformat(),
        "type": session_type,
        "summary": _extract_summary(session_type, data),
    }

    # Track offer probability changes
    if session_type == "offer_prediction" and "overall_probability" in data:
        user["offer_probability_history"].append({
            "date": datetime.now().isoformat(),
            "probability": data["overall_probability"],
            "dimensions": data.get("dimensions", []),
        })

    # Track problems identified
    if "weaknesses" in data:
        for w in data.get("weaknesses", []):
            if w not in [p["description"] for p in user["problems_identified"]]:
                user["problems_identified"].append({
                    "description": w,
                    "first_identified": datetime.now().isoformat(),
                    "status": "open",
                })

    # Track resume versions
    if session_type == "resume_rewrite" and "rewritten" in data:
        user["resume_versions"].append({
            "timestamp": datetime.now().isoformat(),
            "version": len(user["resume_versions"]) + 1,
            "content": data.get("rewritten", "")[:500],
        })

    user["sessions"].append(session_record)
    user["last_active"] = datetime.now().isoformat()

    storage["sessions"].append(session_record)
    saveGrowthData(storage)

    return user


def get_growth_report(user_id: str) -> dict:
    """
    Generate a growth report for a user.

    Args:
        user_id: User identifier

    Returns:
        {
            "user_id": str,
            "days_active": int,
            "total_sessions": int,
            "offer_probability_trend": [{"date": str, "probability": int}],
            "problems_resolved": int,
            "problems_open": int,
            "resume_versions": int,
            "growth_score": int,
            "markdown": str
        }
    """
    storage = loadGrowthData()
    user = storage["users"].get(user_id)

    if not user:
        return {
            "user_id": user_id,
            "error": "No data found for this user",
            "markdown": "> ⚠️ 暂无成长数据。开始使用 ByteDance Offer Copilot 以建立你的成长档案。",
        }

    # Calculate metrics
    created = datetime.fromisoformat(user["created_at"])
    days_active = (datetime.now() - created).days

    sessions = user.get("sessions", [])
    prob_history = user.get("offer_probability_history", [])
    problems = user.get("problems_identified", [])

    problems_resolved = sum(1 for p in problems if p["status"] == "resolved")
    problems_open = sum(1 for p in problems if p["status"] == "open")

    # Calculate growth score
    growth_score = _calculate_growth_score(user)

    # Build trend data
    trend = []
    for entry in prob_history[-10:]:  # Last 10 data points
        trend.append({
            "date": entry["date"][:10],
            "probability": entry["probability"],
        })

    report = {
        "user_id": user_id,
        "days_active": days_active,
        "total_sessions": len(sessions),
        "offer_probability_trend": trend,
        "problems_resolved": problems_resolved,
        "problems_open": problems_open,
        "resume_versions": len(user.get("resume_versions", [])),
        "growth_score": growth_score,
        "problems": problems,
    }

    report["markdown"] = _render_growth_markdown(report)
    return report


def resolve_problem(user_id: str, problem_index: int) -> dict:
    """Mark a previously identified problem as resolved."""
    storage = loadGrowthData()
    user = storage["users"].get(user_id)

    if user and problem_index < len(user.get("problems_identified", [])):
        user["problems_identified"][problem_index]["status"] = "resolved"
        user["problems_identified"][problem_index]["resolved_at"] = datetime.now().isoformat()
        saveGrowthData(storage)
        return {"success": True, "problem": user["problems_identified"][problem_index]}

    return {"success": False, "error": "Problem not found"}


def add_milestone(user_id: str, milestone: str) -> dict:
    """Add a growth milestone."""
    storage = loadGrowthData()
    user = storage["users"].get(user_id)

    if user:
        user["growth_milestones"].append({
            "milestone": milestone,
            "date": datetime.now().isoformat(),
        })
        saveGrowthData(storage)
        return {"success": True}

    return {"success": False, "error": "User not found"}


def _extract_summary(session_type: str, data: dict) -> str:
    """Extract a one-line summary from session data."""
    if session_type == "offer_prediction":
        prob = data.get("overall_probability", "?")
        return f"Offer probability: {prob}%"
    elif session_type == "jd_analysis":
        return f"Analyzed JD: {data.get('job_title', 'Unknown')}"
    elif session_type == "resume_rewrite":
        return "Resume rewritten"
    elif session_type == "interview":
        score = data.get("overall_score", "?")
        return f"Interview score: {score}/10"
    elif session_type == "growth_plan":
        return f"Growth plan: {data.get('recommended_route', 'Unknown')}"
    return session_type


def _calculate_growth_score(user: dict) -> int:
    """Calculate a composite growth score (0-100)."""
    score = 30  # Base

    sessions = user.get("sessions", [])
    prob_history = user.get("offer_probability_history", [])
    problems = user.get("problems_identified", [])
    milestones = user.get("growth_milestones", [])

    # More sessions = more engagement
    score += min(20, len(sessions) * 2)

    # Offer probability improvement
    if len(prob_history) >= 2:
        first = prob_history[0]["probability"]
        last = prob_history[-1]["probability"]
        improvement = last - first
        score += min(25, max(0, improvement))

    # Problems resolved
    resolved = sum(1 for p in problems if p["status"] == "resolved")
    total = len(problems)
    if total > 0:
        score += min(15, int(resolved / total * 15))

    # Milestones
    score += min(10, len(milestones) * 5)

    return min(100, score)


def _render_growth_markdown(report: dict) -> str:
    """Render growth report as Markdown."""
    if "error" in report:
        return report.get("markdown", "")

    score = report["growth_score"]
    score_color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

    lines = [
        "```",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📈  用户成长轨迹",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
        f"## 成长评分：{score}/100  {score_color}",
        "",
        f"| 指标 | 数据 |",
        f"|------|------|",
        f"| 使用天数 | {report['days_active']} 天 |",
        f"| 总会话数 | {report['total_sessions']} 次 |",
        f"| 简历版本 | {report['resume_versions']} 版 |",
        f"| 已解决问题 | {report['problems_resolved']} 个 |",
        f"| 待解决问题 | {report['problems_open']} 个 |",
        "",
    ]

    # Offer probability trend
    trend = report.get("offer_probability_trend", [])
    if len(trend) >= 2:
        lines.append("## 📊 Offer 概率变化")
        lines.append("")
        first = trend[0]
        last = trend[-1]
        change = last["probability"] - first["probability"]
        arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        lines.append(f"| 时间 | Offer 概率 |")
        lines.append(f"|------|-----------|")
        for t in trend:
            lines.append(f"| {t['date']} | {t['probability']}% |")

        lines.append("")
        lines.append(f"{arrow} 变化：{first['probability']}% → {last['probability']}% ({'+' if change > 0 else ''}{change}%)")
        lines.append("")

    # Problems
    problems = report.get("problems", [])
    if problems:
        lines.append("## 🎯 已识别的问题")
        lines.append("")
        for i, p in enumerate(problems):
            status = "✅" if p["status"] == "resolved" else "⬜"
            lines.append(f"- {status} {p['description']}")
        lines.append("")

    if score < 40:
        lines.append("> ⚠️ 成长数据较少，持续使用以建立完整的成长档案。")
    elif score < 70:
        lines.append("> 🟡 有进步但还有提升空间。关注待解决的问题。")
    else:
        lines.append("> 🟢 成长轨迹良好，保持势头。")

    lines.append("")
    return "\n".join(lines)
