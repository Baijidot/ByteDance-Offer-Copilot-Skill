#!/usr/bin/env python3
"""
Offer Copilot v3.2 — 演示数据种子脚本（验收用）

通过真实 HTTP API 灌入：
  1. 一份「产品运营实习」简历档案（走 /api/profile/parse 规则解析 → /api/profile/save）
  2. 3 份 JD（走 /api/jds/add，规则层匹配分）
  3. 9 条不同状态的投递记录（/api/tracker/add → /api/tracker/status 逐步推进）

用法：python3 seed.py [BASE_URL]   # 默认 http://127.0.0.1:8000
只依赖标准库。
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))


def post_json(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def post_form(path, fields):
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


# ── 1. 简历 ────────────────────────────────────────────────
resume_text = read("resume.md")
parsed = post_json("/api/profile/parse", {"resume_text": resume_text})
print("[parse] success =", parsed.get("success"), "| parsed_by =", (parsed.get("profile") or {}).get("parsed_by"))
prof = parsed["profile"]
print("[parse] name =", prof.get("name"), "| target_role =", prof.get("target_role"), "| job_type =", prof.get("job_type"))
print("[parse] education =", prof.get("education"))
print("[parse] skills =", prof.get("skills"))
print("[parse] projects =", [p.get("name") for p in prof.get("projects", [])])
print("[parse] experience =", [e.get("title") for e in prof.get("experience", [])])
print("[parse] completeness =", prof.get("completeness"))

# 规则解析猜不准的字段，按「确认档案」那一步用户会手动修正的方式补齐
prof["name"] = prof.get("name") or "林晓雨"
prof["target_role"] = "产品运营"
prof["job_type"] = "实习"
prof["target_cities"] = "上海 / 杭州"
edu = prof.get("education") or {}
edu.setdefault("school", "华东师范大学")
edu["school"] = edu.get("school") or "华东师范大学"
edu["major"] = edu.get("major") or "传播学"
edu["degree"] = edu.get("degree") or "本科"
edu["graduation"] = edu.get("graduation") or "2027"
prof["education"] = edu
prof["summary"] = prof.get("summary") or "数据驱动的产品运营实习生，做过 2400+ 用户的校园平台从 0 到 1，小红书 / 网易有道两段运营实习。"
saved = post_json("/api/profile/save", {"profile": prof, "rematch": True})
print("[save] success =", saved.get("success"), "| completeness =", (saved.get("profile") or {}).get("completeness"))

# ── 2. JD ──────────────────────────────────────────────────
jds = [
    ("jd1-bytedance-douyin-ecom-ops-intern.md", "产品运营实习生", "字节跳动 · 抖音电商"),
    ("jd2-tencent-wechat-growth-ops-intern.md", "用户增长运营实习生", "腾讯 · 微信事业群"),
    ("jd3-taotian-data-analyst-intern.md", "商业数据分析实习生", "阿里 · 淘天集团"),
]
jd_ids = {}
for fname, title, company in jds:
    r = post_form("/api/jds/add", {"jd_text": read(fname), "title": title, "company": company})
    jd = r.get("jd") or {}
    m = jd.get("match") or {}
    jd_ids[company] = jd.get("id")
    print(f"[jd] {company} · {title} → id={jd.get('id')} score={m.get('score')} "
          f"hard_matched={m.get('hard', {}).get('matched')} hard_missing={m.get('hard', {}).get('missing')} "
          f"flags={[f['type'] for f in m.get('flags', [])]}")

# ── 3. 投递记录 ─────────────────────────────────────────────
# (company, position, channel, city, applied_at, salary, progression[], next_action, next_action_date)
apps = [
    ("字节跳动", "产品运营实习生", "内推", "上海", "2026-09-10", "", ["一面", "二面"], "准备二面：书语项目数据复盘", "2026-09-18"),
    ("腾讯", "用户增长运营实习生", "官网", "广州", "2026-09-08", "", ["笔试", "一面"], "", ""),
    ("淘天集团", "商业数据分析实习生", "官网", "杭州", "2026-08-20", "", ["已挂"], "", ""),
    ("美团", "到店业务运营实习生", "BOSS直聘", "上海", "2026-08-25", "", [], "", ""),               # 停滞 ≥14 天 → 预警
    ("小红书", "社区运营实习生", "内推", "上海", "2026-08-28", "300元/天", ["一面", "二面", "HR面", "Offer"], "", ""),
    ("网易", "内容运营实习生", "实习僧", "杭州", "2026-08-30", "250元/天", ["一面", "HR面"], "HR 面后等结果，周五前跟进", "2026-09-19"),
    ("拼多多", "产品运营实习生", "牛客", "上海", "2026-09-01", "", ["一面", "已挂"], "", ""),
    ("哔哩哔哩", "用户运营实习生", "官网", "上海", "2026-08-26", "", [], "", ""),                    # 停滞 ≥14 天 → 预警
    ("快手", "电商运营实习生", "内推", "北京", "2026-09-14", "", [], "", ""),
]
jd_for = {"字节跳动": jd_ids.get("字节跳动 · 抖音电商"), "腾讯": jd_ids.get("腾讯 · 微信事业群"), "淘天集团": jd_ids.get("阿里 · 淘天集团")}
for company, position, channel, city, applied_at, salary, steps, nxt, nxt_date in apps:
    r = post_form("/api/tracker/add", {
        "company": company, "position": position, "channel": channel, "city": city,
        "applied_at": applied_at, "salary": salary, "jd_id": jd_for.get(company) or "",
        "next_action": nxt, "next_action_date": nxt_date,
    })
    app = r.get("application") or {}
    aid = app.get("id")
    for st in steps:
        rr = post_form("/api/tracker/status", {"app_id": aid, "new_status": st,
                                               "next_action": nxt if st not in ("Offer", "已挂") else "",
                                               "next_action_date": nxt_date if st not in ("Offer", "已挂") else ""})
        if not rr.get("success"):
            print("   !! status update failed:", rr)
    print(f"[app] {company} · {position} → id={aid} final={steps[-1] if steps else '已投递'} applied={applied_at}")

print("\nDone. Seeded via", BASE)
