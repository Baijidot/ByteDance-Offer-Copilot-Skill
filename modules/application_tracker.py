"""
Application Tracker — 投递记录追踪（求职数据闭环）

v2 自评说「没有数据闭环」是最致命的问题。这个模块就是回应。

纯规则引擎，不调用 LLM：
- 投递记录 CRUD + 状态流转 + 历史轨迹
- 漏斗转化率（投递 → 笔试 → 一面 → 二面 → HR面 → Offer）
- 停滞预警（超过 N 天无进展）
- 本周活跃度
- 基于数据的下一步行动建议

存储：user_data/applications.json
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

# 主流程（有序）；终态单独列
STATUS_FLOW = ["已投递", "笔试", "一面", "二面", "三面", "HR面", "Offer", "已入职"]
TERMINAL_STATUSES = ["已挂", "已放弃"]
ALL_STATUSES = STATUS_FLOW + TERMINAL_STATUSES

# 漏斗链。笔试是可跳过环节（很多岗位直接进一面），不进链，单独统计
FUNNEL_STAGES = ["已投递", "一面", "二面", "HR面", "Offer"]

STALE_DAYS = 14
CHANNELS = ["官网", "内推", "BOSS直聘", "牛客", "实习僧", "猎头", "校招宣讲", "其他"]

STATUS_EMOJI = {
    "已投递": "📨", "笔试": "📝", "一面": "1️⃣", "二面": "2️⃣", "三面": "3️⃣",
    "HR面": "🤝", "Offer": "🎉", "已入职": "🏁", "已挂": "💀", "已放弃": "🚫",
}


# ═══════════════════════════════════════════════════════════
# Storage
# ═══════════════════════════════════════════════════════════

def _data_path() -> str:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "user_data")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "applications.json")


def _load() -> dict:
    path = _data_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "applications" in data:
                    return data
        except Exception:
            pass
    return {"applications": []}


def _save(data: dict) -> None:
    with open(_data_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _parse_date(s: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _find(data: dict, app_id: str) -> Optional[dict]:
    for app in data["applications"]:
        if app["id"] == app_id or app["id"].startswith(app_id):
            return app
    return None


# ═══════════════════════════════════════════════════════════
# CRUD
# ═══════════════════════════════════════════════════════════

def add_application(
    company: str,
    position: str,
    channel: str = "",
    salary: str = "",
    city: str = "",
    jd_text: str = "",
    notes: str = "",
    status: str = "已投递",
    applied_at: str = "",
    next_action: str = "",
    next_action_date: str = "",
    user_id: str = "default_user",
    jd_id: str = "",
) -> dict:
    """
    新增一条投递记录。

    Returns:
        {"application": {...}, "markdown": str}
    """
    if not company or not position:
        return {"error": "公司和岗位不能为空", "markdown": "> ⚠️ 公司和岗位不能为空"}
    if status not in ALL_STATUSES:
        status = "已投递"

    data = _load()
    now = _now()
    applied_at = applied_at.strip() or _today()
    # 停滞天数从投递日开始算：8 月投的今天才补录，也已经停滞了一个月
    applied_dt = _parse_date(applied_at)
    updated_at = applied_dt.strftime("%Y-%m-%d %H:%M") if applied_dt and applied_dt < datetime.now() else now
    app = {
        "id": uuid.uuid4().hex[:8],
        "user_id": user_id,
        "company": company.strip(),
        "position": position.strip(),
        "channel": channel.strip() or "其他",
        "salary": salary.strip(),
        "city": city.strip(),
        "status": status,
        "applied_at": applied_at,
        "updated_at": updated_at,
        "next_action": next_action.strip(),
        "next_action_date": next_action_date.strip(),
        "notes": notes.strip(),
        "jd_text": jd_text.strip()[:4000],
        "jd_id": jd_id.strip(),
        "history": [{"status": status, "at": now, "note": "创建记录"}],
    }
    data["applications"].append(app)
    _save(data)

    return {
        "application": app,
        "markdown": f"> ✅ 已记录：**{app['company']} · {app['position']}**（{STATUS_EMOJI.get(status, '')} {status}）\n> ID: `{app['id']}`",
    }


def update_status(
    app_id: str,
    new_status: str,
    note: str = "",
    next_action: str = "",
    next_action_date: str = "",
    user_id: str = "default_user",
) -> dict:
    """
    推进投递状态。会追加到 history。

    Returns:
        {"application": {...}, "transition": "一面 → 二面", "markdown": str}
    """
    if new_status not in ALL_STATUSES:
        return {"error": f"未知状态：{new_status}", "markdown": f"> ⚠️ 未知状态 `{new_status}`，可选：{' / '.join(ALL_STATUSES)}"}

    data = _load()
    app = _find(data, app_id)
    if not app or app.get("user_id") != user_id:
        return {"error": "记录不存在", "markdown": f"> ⚠️ 找不到 ID 为 `{app_id}` 的投递记录"}

    old = app["status"]
    now = _now()
    app["status"] = new_status
    app["updated_at"] = now
    if next_action:
        app["next_action"] = next_action.strip()
    if next_action_date:
        app["next_action_date"] = next_action_date.strip()
    if new_status in ("Offer", "已入职", "已挂", "已放弃"):
        # 终态或 Offer：清空待办
        if not next_action:
            app["next_action"] = ""
            app["next_action_date"] = ""
    app["history"].append({"status": new_status, "at": now, "note": note.strip()})
    _save(data)

    emoji = STATUS_EMOJI.get(new_status, "")
    lines = [f"> {emoji} **{app['company']} · {app['position']}**：{old} → **{new_status}**"]
    if note:
        lines.append(f"> 备注：{note}")
    if new_status == "Offer":
        lines.append("> 🎉 恭喜！下一步：用「Offer 对比决策器」把它和其他 Offer 放在一起看。")
    elif new_status == "已挂":
        lines.append("> 💀 挂了不是终点。把面试记录丢给「面评生成器」，找出真正的问题。")
    elif new_status in ("一面", "二面", "三面", "HR面"):
        lines.append(f"> 🎤 进入 {new_status}。建议：用「自我介绍生成器」准备开场，用「模拟面试」预演追问。")

    return {"application": app, "transition": f"{old} → {new_status}", "markdown": "\n".join(lines)}


def update_application(app_id: str, user_id: str = "default_user", **fields) -> dict:
    """更新任意字段（company / position / channel / salary / city / notes / next_action / next_action_date / jd_text）。"""
    allowed = {"company", "position", "channel", "salary", "city", "notes", "next_action", "next_action_date", "jd_text"}
    data = _load()
    app = _find(data, app_id)
    if not app or app.get("user_id") != user_id:
        return {"error": "记录不存在", "markdown": f"> ⚠️ 找不到 ID 为 `{app_id}` 的投递记录"}
    changed = []
    for k, v in fields.items():
        if k in allowed and v is not None:
            app[k] = str(v).strip()
            changed.append(k)
    if changed:
        app["updated_at"] = _now()
        _save(data)
    return {"application": app, "changed": changed, "markdown": f"> ✏️ 已更新 {', '.join(changed) or '无字段'}"}


def delete_application(app_id: str, user_id: str = "default_user") -> dict:
    data = _load()
    app = _find(data, app_id)
    if not app or app.get("user_id") != user_id:
        return {"error": "记录不存在", "markdown": f"> ⚠️ 找不到 ID 为 `{app_id}` 的投递记录"}
    data["applications"] = [a for a in data["applications"] if a["id"] != app["id"]]
    _save(data)
    return {"deleted": app["id"], "markdown": f"> 🗑️ 已删除 {app['company']} · {app['position']}"}


def list_applications(user_id: str = "default_user", status_filter: str = "", active_only: bool = False) -> dict:
    """
    列出投递记录（默认按更新时间倒序）。

    Returns:
        {"applications": [...], "count": int, "markdown": str（看板视图）}
    """
    data = _load()
    apps = [a for a in data["applications"] if a.get("user_id") == user_id]
    if status_filter:
        apps = [a for a in apps if a["status"] == status_filter]
    if active_only:
        apps = [a for a in apps if a["status"] not in TERMINAL_STATUSES + ["已入职"]]
    apps.sort(key=lambda a: a.get("updated_at", ""), reverse=True)
    return {"applications": apps, "count": len(apps), "markdown": _render_kanban(apps)}


# ═══════════════════════════════════════════════════════════
# Stats — 漏斗 / 停滞 / 活跃度 / 行动建议
# ═══════════════════════════════════════════════════════════

def _reached_stage(app: dict, stage: str) -> bool:
    """
    该投递是否到达过某个漏斗阶段。

    漏斗要求单调递减，所以按「走到的最远阶段」推断：到了 HR 面就算经过了一面和二面，
    即使中间没有逐条记录。三面折算为二面档，已入职折算为 Offer 档，笔试折算为投递档。
    """
    return _furthest_stage_index(app) >= FUNNEL_STAGES.index(stage)


_STAGE_INDEX = {"已投递": 0, "笔试": 0, "一面": 1, "二面": 2, "三面": 2, "HR面": 3, "Offer": 4, "已入职": 4}


def _furthest_stage_index(app: dict) -> int:
    statuses = [h.get("status") for h in app.get("history", [])] + [app.get("status")]
    return max((_STAGE_INDEX.get(s, -1) for s in statuses), default=-1)


def _had_written_test(app: dict) -> bool:
    return any(h.get("status") == "笔试" for h in app.get("history", [])) or app.get("status") == "笔试"


def _days_since(date_str: str) -> int:
    d = _parse_date(date_str)
    if not d:
        return 0
    return (datetime.now() - d).days


def get_tracker_stats(user_id: str = "default_user", stale_days: int = STALE_DAYS) -> dict:
    """
    投递数据统计。

    Returns:
        {
            "total": int,
            "active": int,
            "by_status": {status: count},
            "by_channel": {channel: count},
            "funnel": [{"stage", "count", "rate_from_prev", "rate_from_start"}],
            "offer_rate": float,           # Offer / 投递
            "interview_rate": float,       # 一面 / 投递
            "stale": [{"id", "company", "position", "status", "days"}],
            "upcoming": [{"id", "company", "position", "next_action", "date"}],
            "this_week": {"added": int, "updated": int, "interviews": int},
            "next_actions": [str],
            "markdown": str
        }
    """
    data = _load()
    apps = [a for a in data["applications"] if a.get("user_id") == user_id]
    total = len(apps)

    if total == 0:
        return {
            "total": 0, "active": 0, "by_status": {}, "by_channel": {}, "funnel": [],
            "offer_rate": 0.0, "interview_rate": 0.0, "stale": [], "upcoming": [],
            "this_week": {"added": 0, "updated": 0, "interviews": 0},
            "next_actions": ["还没有投递记录。先投出第一份简历，然后用 add_application 记下来。"],
            "markdown": "> 📭 还没有投递记录。\n>\n> 求职是一个漏斗，不记录就不知道自己卡在哪一层。先投出第一份，然后记下来。",
        }

    by_status = {}
    by_channel = {}
    for a in apps:
        by_status[a["status"]] = by_status.get(a["status"], 0) + 1
        by_channel[a.get("channel", "其他")] = by_channel.get(a.get("channel", "其他"), 0) + 1

    # 漏斗（单调递减，见 _reached_stage）
    funnel = []
    prev_count = None
    for stage in FUNNEL_STAGES:
        count = sum(1 for a in apps if _reached_stage(a, stage))
        rate_prev = round(count / prev_count * 100, 1) if prev_count else (100.0 if count else 0.0)
        rate_start = round(count / total * 100, 1)
        funnel.append({"stage": stage, "count": count, "rate_from_prev": rate_prev, "rate_from_start": rate_start})
        prev_count = count
    written_test_count = sum(1 for a in apps if _had_written_test(a))

    offer_count = sum(1 for a in apps if _reached_stage(a, "Offer"))
    interview_count = sum(1 for a in apps if _reached_stage(a, "一面"))
    offer_rate = round(offer_count / total * 100, 1)
    interview_rate = round(interview_count / total * 100, 1)

    # 停滞
    active = [a for a in apps if a["status"] not in TERMINAL_STATUSES + ["已入职"]]
    stale = []
    for a in active:
        days = _days_since(a.get("updated_at", ""))
        if days >= stale_days:
            stale.append({"id": a["id"], "company": a["company"], "position": a["position"], "status": a["status"], "days": days})
    stale.sort(key=lambda x: -x["days"])

    # 待办
    upcoming = []
    for a in active:
        if a.get("next_action"):
            upcoming.append({
                "id": a["id"], "company": a["company"], "position": a["position"],
                "next_action": a["next_action"], "date": a.get("next_action_date", ""),
            })
    upcoming.sort(key=lambda x: x["date"] or "9999")

    # 本周
    week_ago = datetime.now() - timedelta(days=7)
    added = sum(1 for a in apps if (_parse_date(a.get("applied_at", "")) or datetime.min) >= week_ago)
    updated = sum(1 for a in apps if (_parse_date(a.get("updated_at", "")) or datetime.min) >= week_ago)
    interviews = 0
    for a in apps:
        for h in a.get("history", []):
            if h.get("status") in ("一面", "二面", "三面", "HR面") and (_parse_date(h.get("at", "")) or datetime.min) >= week_ago:
                interviews += 1
    this_week = {"added": added, "updated": updated, "interviews": interviews}

    next_actions = _build_next_actions(total, len(active), interview_rate, offer_rate, funnel, stale, upcoming, this_week, by_channel)

    result = {
        "total": total, "active": len(active), "by_status": by_status, "by_channel": by_channel,
        "funnel": funnel, "written_test_count": written_test_count,
        "offer_rate": offer_rate, "interview_rate": interview_rate,
        "stale": stale, "upcoming": upcoming, "this_week": this_week, "next_actions": next_actions,
    }
    result["markdown"] = _render_stats(result)
    return result


def _build_next_actions(total, active, interview_rate, offer_rate, funnel, stale, upcoming, this_week, by_channel) -> list:
    """规则层：基于数据给出下一步建议，不调用 LLM。"""
    actions = []

    if stale:
        top = stale[0]
        actions.append(f"🔴 {len(stale)} 条投递超过 {STALE_DAYS} 天没动静（最久的是 {top['company']} · {top['position']}，{top['days']} 天）。主动跟进 HR 或直接放弃，别让它占着你的注意力。")

    if total >= 5 and interview_rate < 20:
        actions.append(f"🔴 投递 → 一面转化率只有 {interview_rate}%，问题在简历。先做「黑话检测」和「简历重构」，再继续投。")

    stage_map = {f["stage"]: f for f in funnel}
    if stage_map.get("一面", {}).get("count", 0) >= 3:
        r = stage_map.get("二面", {}).get("rate_from_prev", 100)
        if r < 40:
            actions.append(f"🟡 一面 → 二面通过率 {r}%，一面在掉人。用「模拟面试 · 高压模式」练追问，用「面评生成器」复盘挂掉的那几场。")

    if stage_map.get("HR面", {}).get("count", 0) >= 2:
        r = stage_map.get("Offer", {}).get("rate_from_prev", 100)
        if r < 50:
            actions.append(f"🟡 HR 面 → Offer 转化率 {r}%，可能是薪资期望或稳定性表达出了问题。HR 面之前先用「自我介绍生成器 · 社招场景」准备动机陈述。")

    if this_week["added"] == 0 and active < 5:
        actions.append("🟡 本周 0 投递，在途只有 {} 条。求职是概率游戏，保持每周至少 5 份新投递。".format(active))

    if upcoming:
        u = upcoming[0]
        actions.append(f"🟢 最近待办：{u['company']} · {u['next_action']}{'（' + u['date'] + '）' if u['date'] else ''}")

    if len(by_channel) == 1 and total >= 5:
        only = next(iter(by_channel))
        actions.append(f"🟢 所有投递都来自「{only}」，渠道太单一。内推的简历通过率通常是官网的 2-3 倍，去找找校友和前同事。")

    if offer_rate > 0 and stage_map.get("Offer", {}).get("count", 0) >= 2:
        actions.append("🎉 手上有 2 个以上 Offer 了，去「Offer 对比决策器」做加权比较，别凭感觉选。")

    if not actions:
        actions.append("🟢 数据健康，继续保持节奏。每周回来看一次漏斗。")

    return actions


# ═══════════════════════════════════════════════════════════
# Rendering
# ═══════════════════════════════════════════════════════════

def _render_kanban(apps: list) -> str:
    if not apps:
        return "> 📭 暂无投递记录"

    lines = ["# 📋 投递看板", ""]
    for status in ALL_STATUSES:
        group = [a for a in apps if a["status"] == status]
        if not group:
            continue
        lines.append(f"## {STATUS_EMOJI.get(status, '')} {status}（{len(group)}）")
        lines.append("")
        lines.append("| ID | 公司 | 岗位 | 渠道 | 投递日期 | 停留 | 下一步 |")
        lines.append("|----|------|------|------|----------|------|--------|")
        for a in group:
            days = _days_since(a.get("updated_at", ""))
            stale_mark = " ⚠️" if days >= STALE_DAYS and status not in TERMINAL_STATUSES + ["已入职"] else ""
            nxt = a.get("next_action", "") or "-"
            if a.get("next_action_date"):
                nxt += f"（{a['next_action_date']}）"
            lines.append(f"| `{a['id']}` | {a['company']} | {a['position']} | {a.get('channel', '-')} | {a.get('applied_at', '-')} | {days}天{stale_mark} | {nxt} |")
        lines.append("")
    return "\n".join(lines)


def _render_stats(s: dict) -> str:
    lines = [
        "# 📊 求职漏斗",
        "",
        f"**总投递 {s['total']}** · 在途 {s['active']} · 一面率 {s['interview_rate']}% · Offer 率 {s['offer_rate']}%",
        "",
        "## 漏斗转化",
        "",
        "| 阶段 | 人数 | 环比转化 | 累计转化 | 分布 |",
        "|------|------|----------|----------|------|",
    ]
    max_count = max((f["count"] for f in s["funnel"]), default=1) or 1
    for f in s["funnel"]:
        bar_len = int(f["count"] / max_count * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"| {STATUS_EMOJI.get(f['stage'], '')} {f['stage']} | {f['count']} | {f['rate_from_prev']}% | {f['rate_from_start']}% | `{bar}` |")
    if s.get("written_test_count"):
        lines.append("")
        lines.append(f"*其中 {s['written_test_count']} 条经历了笔试环节（笔试可跳过，不计入漏斗链）*")

    lines.extend(["", "## 状态分布", ""])
    for status in ALL_STATUSES:
        if status in s["by_status"]:
            lines.append(f"- {STATUS_EMOJI.get(status, '')} {status}：{s['by_status'][status]}")

    if s["by_channel"]:
        lines.extend(["", "## 渠道分布", ""])
        for ch, n in sorted(s["by_channel"].items(), key=lambda x: -x[1]):
            lines.append(f"- {ch}：{n}")

    wk = s["this_week"]
    lines.extend(["", "## 本周", "", f"新增投递 {wk['added']} · 状态更新 {wk['updated']} · 面试 {wk['interviews']} 场"])

    if s["stale"]:
        lines.extend(["", f"## ⚠️ 停滞预警（≥{STALE_DAYS} 天无进展）", ""])
        for st in s["stale"]:
            lines.append(f"- `{st['id']}` {st['company']} · {st['position']}（{st['status']}，{st['days']} 天）")

    if s["upcoming"]:
        lines.extend(["", "## 📅 待办", ""])
        for u in s["upcoming"]:
            lines.append(f"- {u['company']} · {u['position']}：{u['next_action']}{'（' + u['date'] + '）' if u['date'] else ''}")

    lines.extend(["", "## 🎯 下一步", ""])
    for a in s["next_actions"]:
        lines.append(f"- {a}")
    lines.append("")
    return "\n".join(lines)


def get_dashboard(user_id: str = "default_user") -> dict:
    """看板 + 漏斗一次拿全，供 CLI / Web 首屏使用。"""
    listing = list_applications(user_id)
    stats = get_tracker_stats(user_id)
    return {
        "applications": listing["applications"],
        "stats": {k: v for k, v in stats.items() if k != "markdown"},
        "markdown": stats["markdown"] + "\n\n---\n\n" + listing["markdown"],
    }
