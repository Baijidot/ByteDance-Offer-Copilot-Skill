"""
Web UI Components — Offer Copilot v3.1

简历优先（参考 Teal / Huntr / 超级简历）：
- 没有简历档案 → 整站只开放「导入简历」引导页，其他页面锁定
- 有档案 → 左侧栏工作台：工作台 / 我的简历 / 岗位库 / 投递看板 / 面试准备 / 模拟面试 / Offer 对比 / 更多工具
- 所有功能从档案自动预填，不再重复填表
"""

import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import Optional
import json
import uuid

from modules import (
    analyze_jd, predict_offer, rewrite_project,
    start_interview, respond, evaluate, generate_plan,
    detect_bs, rewrite_bs, translate_bs,
    generate_persona, detect_authenticity, match_career,
    start_group_interview, group_respond, group_evaluate,
    add_application, update_status, delete_application, get_tracker_stats, get_dashboard,
    generate_intro, generate_project_pitch,
    compare_offers,
    get_profile, save_profile, delete_profile, parse_resume, completeness, with_completeness,
    extract_text_from_upload, profile_as_resume_text,
    add_jd, list_jds, get_jd, delete_jd, rematch_all, save_deep_analysis,
    get_growth_report,
)
from utils import buildConfusionDiagnosis, loadLlmSettings, saveLlmSettings, getLlmConfig, maskKey, callLlm
from components.styles import CSS


active_sessions: dict = {}
active_group_sessions: dict = {}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Offer Copilot",
        description="AI 求职全流程教练 — 简历优先，从 JD 匹配到 Offer 选择的闭环",
        version="3.1.0",
    )

    def _require_profile():
        """无档案时的统一错误返回（前端据此弹回引导页）。"""
        return {"success": False, "error": "NO_PROFILE", "markdown": "> ⚠️ 还没有简历档案。先到「导入简历」把简历给我，这里才会解锁。"}

    # ===== Pages / static =====

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return HTMLResponse(content=get_html_template())

    @app.get("/api/styles", response_class=HTMLResponse)
    async def styles():
        return HTMLResponse(content=f"<style>{CSS}</style>")

    # ===== Profile (v3.1) =====

    @app.get("/api/profile")
    async def api_profile_get():
        p = get_profile()
        return {"success": True, "profile": with_completeness(p) if p else None}

    @app.post("/api/profile/parse")
    async def api_profile_parse(request: Request):
        """解析简历（不保存）。支持 JSON {resume_text} 或 multipart（文件 / 文本）。"""
        content_type = request.headers.get("content-type", "")
        text, source = "", "paste"
        if content_type.startswith("multipart/"):
            form = await request.form()
            upload = form.get("file")
            # 注意：不同版本里 fastapi.UploadFile 与 starlette 解析出的 UploadFile 不是同一个类，
            # 用鸭子类型判断（有 filename + read 就当文件处理）
            if upload is not None and getattr(upload, "filename", "") and hasattr(upload, "read"):
                content = await upload.read()
                text, source = extract_text_from_upload(upload.filename, content)
                if not text and upload.filename.lower().endswith(".pdf"):
                    return {"success": False, "error": "PDF_EXTRACT_FAILED",
                            "markdown": "> ⚠️ 这个 PDF 提取不出文本（可能是扫描件）。换成粘贴文本或 .docx / .md 文件。"}
                if not text:
                    return {"success": False, "error": "FILE_EXTRACT_FAILED",
                            "markdown": "> ⚠️ 读不出这个文件的内容。支持粘贴文本和 .txt / .md / .docx 文件。"}
            else:
                text = str(form.get("resume_text") or "")
        else:
            body = await request.json()
            text = str(body.get("resume_text") or "")
        if not text or len(text.strip()) < 30:
            return {"success": False, "error": "TEXT_TOO_SHORT",
                    "markdown": "> ⚠️ 内容太短，不像一份简历。粘贴完整简历（教育背景 / 项目经历 / 实习经历 / 专业技能）。"}
        profile = parse_resume(text, use_llm=True)
        return {"success": True, "profile": with_completeness(profile), "source": source}

    @app.post("/api/profile/save")
    async def api_profile_save(request: Request):
        body = await request.json()
        profile = body.get("profile") or {}
        if not profile.get("raw_text") or len(profile["raw_text"].strip()) < 30:
            return {"success": False, "error": "NO_RAW_TEXT", "markdown": "> ⚠️ 简历原文不能为空。"}
        if not profile.get("target_role"):
            return {"success": False, "error": "NO_TARGET_ROLE", "markdown": "> ⚠️ 目标岗位必填——所有分析都靠它定标准。"}
        saved = save_profile(profile)
        n = rematch_all(saved) if body.get("rematch", True) else 0
        return {"success": True, "profile": saved, "rematched": n}

    @app.post("/api/profile/delete")
    async def api_profile_delete():
        delete_profile()
        return {"success": True}

    @app.post("/api/profile/export")
    async def api_profile_export(format: str = Form(default="pdf")):
        p = get_profile()
        if not p:
            return _require_profile()
        md = _profile_markdown(p)
        from components.export import export_resume
        try:
            path = export_resume(md, format)
            return {"success": True, "path": path, "format": format}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== AI settings (v3.2) =====

    @app.get("/api/settings")
    async def api_settings_get():
        cfg = getLlmConfig()
        saved = loadLlmSettings()
        return {"success": True, "settings": {
            "configured": bool(cfg.get("api_key")),
            "api_key_masked": maskKey(cfg.get("api_key", "")),
            "base_url": cfg.get("base_url", ""),
            "model": cfg.get("model", ""),
            "from_env": bool(not saved.get("api_key") and (os.environ.get("TRADE_API_KEY") or os.environ.get("LLM_API_KEY"))),
        }}

    @app.post("/api/settings")
    async def api_settings_save(request: Request):
        body = await request.json()
        settings = {k: body.get(k) for k in ("api_key", "base_url", "model")}
        if settings["api_key"] and len(str(settings["api_key"]).strip()) < 8:
            return {"success": False, "error": "API Key 看起来不对（太短）"}
        if not settings["api_key"]:
            settings.pop("api_key")  # 留空 = 不改 Key
        saveLlmSettings(settings)
        return {"success": True}

    @app.post("/api/settings/test")
    async def api_settings_test():
        """用当前生效配置发一次最小请求。"""
        cfg = getLlmConfig()
        if not cfg.get("api_key"):
            return {"success": False, "error": "没有可用的 API Key（先保存）"}
        try:
            import time as _t
            start = _t.time()
            result = callLlm("请只回复两个字：成功", "你是连接测试器。", output_format="text")
            latency = int((_t.time() - start) * 1000)
            if isinstance(result, dict) and "_trait" in result:
                return {"success": False, "error": "配置未生效"}
            reply = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)[:80]
            return {"success": True, "reply": reply[:60], "model": cfg["model"], "latency_ms": latency}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}

    # ===== Dashboard (v3.1) =====

    @app.get("/api/dashboard")
    async def api_dashboard():
        p = get_profile()
        comp = completeness(p) if p else {"score": 0, "missing": ["还没有导入简历"], "level": "empty"}
        stats = get_tracker_stats()
        jds = list_jds()[:6]
        next_actions = []
        if not p:
            next_actions.append({"p": "p0", "page": "onboarding", "text": "导入简历 — 没有它，所有分析都无从谈起"})
        else:
            for m in comp["missing"][:3]:
                next_actions.append({"p": "p1", "page": "resume", "text": "补全档案：" + m})
        if p and not jds:
            next_actions.append({"p": "p1", "page": "jds", "text": "岗位库是空的 — 粘 3 个目标岗位的 JD 进来，看你的匹配分"})
        if p and jds and stats["total"] == 0:
            next_actions.append({"p": "p1", "page": "jds", "text": "从匹配分最高的那个 JD 开始，点「记为已投递」进入看板"})
        for a in stats.get("next_actions", []):
            if stats["total"] == 0:
                break
            pr = "p0" if a.startswith("🔴") else ("p1" if a.startswith("🟡") else "p2")
            next_actions.append({"p": pr, "page": "tracker", "text": a})
        if not next_actions:
            next_actions.append({"p": "p2", "page": "jds", "text": "数据健康。继续保持节奏，每周回来看一次漏斗。"})
        return {"success": True, "profile": with_completeness(p) if p else None,
                "completeness": comp, "stats": {k: v for k, v in stats.items() if k != "markdown"},
                "jds": jds, "next_actions": next_actions}

    # ===== JD library (v3.1) =====

    @app.get("/api/jds")
    async def api_jds_list():
        return {"success": True, "jds": list_jds()}

    @app.post("/api/jds/add")
    async def api_jds_add(
        jd_text: str = Form(...),
        title: str = Form(default=""),
        company: str = Form(default=""),
        url: str = Form(default=""),
    ):
        p = get_profile()
        if not p:
            return _require_profile()
        result = add_jd(jd_text, title=title, company=company, url=url, profile=p)
        ok = "error" not in result
        return {"success": ok, **result}

    @app.post("/api/jds/delete")
    async def api_jds_delete(jd_id: str = Form(...)):
        result = delete_jd(jd_id)
        return {"success": "error" not in result, **result}

    @app.post("/api/jds/deep")
    async def api_jds_deep(jd_id: str = Form(...)):
        """LLM 深度分析：简历×JD 概率预测，结果存回岗位库。"""
        jd = get_jd(jd_id)
        if not jd:
            return {"success": False, "error": "JD 不存在"}
        p = get_profile()
        if not p:
            return _require_profile()
        resume_text = profile_as_resume_text(p)
        deep = predict_offer(resume_text=resume_text, jd_text=jd["text"], target_role=p.get("target_role", ""))
        if isinstance(deep, dict) and not deep.get("error") and not deep.get("_error") and "_trait" not in deep:
            save_deep_analysis(jd_id, deep)
        return {"success": True, "jd": get_jd(jd_id), "deep": deep}

    # ===== JD analyzer（原始接口保留） =====

    @app.post("/api/analyze-jd")
    async def api_analyze_jd(
        jd_content: str = Form(...),
        job_title: str = Form(default=""),
        jd_url: str = Form(default=""),
    ):
        result = analyze_jd(jd_content, job_title, jd_url)
        return {"success": True, "analysis": result}

    # ===== Offer predictor（从档案预填） =====

    @app.post("/api/predict-offer")
    async def api_predict_offer(
        school: str = Form(default=""),
        major: str = Form(default=""),
        degree: str = Form(default=""),
        target_role: str = Form(default=""),
        skills: str = Form(default=""),
        projects: str = Form(default=""),
        internships: str = Form(default=""),
        content_experience: str = Form(default=""),
        ai_capability: str = Form(default=""),
        other_highlights: str = Form(default=""),
        jd_text: str = Form(default=""),
    ):
        p = get_profile()
        if p:
            edu = p.get("education") or {}
            school = school or edu.get("school", "")
            major = major or edu.get("major", "")
            degree = degree or edu.get("degree", "") or "本科"
            target_role = target_role or p.get("target_role", "")
            skills = skills or "、".join(p.get("skills", []))
            projects = projects or "\n\n".join(
                f"{x.get('name', '')}\n{x.get('description', '')}".strip() for x in p.get("projects", [])
            )
            internships = internships or "\n\n".join(
                f"{x.get('title', '')}\n{x.get('description', '')}".strip() for x in p.get("experience", [])
            )
        result = predict_offer(
            school=school, major=major, degree=degree or "本科", target_role=target_role,
            skills=skills, projects=projects, internships=internships,
            content_experience=content_experience, ai_capability=ai_capability,
            other_highlights=other_highlights, jd_text=jd_text,
        )
        return {"success": True, **result}

    # ===== Interview =====

    @app.post("/api/interview/start")
    async def api_interview_start(
        mode: str = Form(default="高压"),
        target_role: str = Form(default=""),
        jd_text: str = Form(default=""),
    ):
        p = get_profile()
        if p and not target_role:
            target_role = p.get("target_role", "")
        sid = str(uuid.uuid4())[:8]
        result = start_interview(mode=mode, target_role=target_role, jd_text=jd_text)
        active_sessions[sid] = {
            "mode": mode,
            "role": target_role,
            "jd_text": jd_text,
            "history": [{"role": "interviewer", "content": result.get("opening", "")}],
            "pressure": 30 if mode == "温和" else (55 if mode == "高压" else (75 if mode == "地狱" else 15)),
        }
        return {"success": True, "session_id": sid, "message": result.get("opening", "开始面试。"), "mode": mode}

    @app.post("/api/interview/respond")
    async def api_interview_respond(session_id: str = Form(...), answer: str = Form(...)):
        if session_id not in active_sessions:
            return {"success": False, "error": "Session not found"}
        session = active_sessions[session_id]
        session["history"].append({"role": "candidate", "content": answer})

        from modules.mock_interviewer import calculate_pressure
        pres = calculate_pressure(answer, session["mode"], session["history"], session["pressure"])
        session["pressure"] = pres["pressure"]

        resp = respond(
            user_answer=answer, mode=session["mode"],
            target_role=session.get("role", ""),
            jd_text=session.get("jd_text", ""),
            chat_history=session["history"],
        )
        msg = resp.get("interviewer_message", "") if isinstance(resp, dict) else str(resp)
        session["history"].append({"role": "interviewer", "content": msg})
        is_complete = resp.get("is_complete", False) if isinstance(resp, dict) else False
        return {"success": True, "message": msg, "pressure": pres, "is_complete": is_complete}

    @app.post("/api/interview/evaluate")
    async def api_interview_evaluate(session_id: str = Form(...)):
        if session_id not in active_sessions:
            return {"success": False, "error": "Session not found"}
        session = active_sessions[session_id]
        result = evaluate(session["history"], session["mode"], session.get("role", ""))
        return {"success": True, **result}

    # ===== Resume rewrite / bs =====

    @app.post("/api/rewrite-project")
    async def api_rewrite_project(original_text: str = Form(...), target_role: str = Form(default="")):
        bs = detect_bs(original_text)
        if not target_role:
            p = get_profile()
            target_role = p.get("target_role", "") if p else ""
        result = rewrite_project(original_text, target_role)
        return {"success": True, "rewrite": result, "bs_detection": bs}

    @app.post("/api/bs-detect")
    async def api_bs_detect(text: str = Form(...)):
        result = detect_bs(text)
        return {"success": True, **result}

    @app.post("/api/bs-translate")
    async def api_bs_translate(text: str = Form(...)):
        result = translate_bs(text, mode="harsh")
        return {"success": True, **result}

    @app.post("/api/persona")
    async def api_persona(resume: str = Form(default=""), projects: str = Form(default=""), content_exp: str = Form(default="")):
        p = get_profile()
        if p and not resume:
            resume = profile_as_resume_text(p)
        if not resume:
            return _require_profile()
        result = generate_persona(resume_text=resume, projects=projects, content_experience=content_exp)
        return {"success": True, **result}

    @app.post("/api/authenticity")
    async def api_authenticity(text: str = Form(...)):
        result = detect_authenticity(text)
        return {"success": True, **result}

    @app.post("/api/confusion-diagnosis")
    async def api_confusion_diagnosis(request: Request):
        body = await request.json()
        result = buildConfusionDiagnosis(body.get("answers", []))
        return {"success": True, "diagnosis": result}

    @app.post("/api/career-match")
    async def api_career_match(profile: str = Form(default="")):
        p = get_profile()
        base = profile_as_resume_text(p) if p else ""
        text = (base + "\n\n补充：" + profile) if (base and profile) else (profile or base)
        if not text:
            return _require_profile()
        result = match_career(text)
        return {"success": True, **result}

    @app.post("/api/growth-plan")
    async def api_growth_plan(
        school: str = Form(default=""),
        major: str = Form(default=""),
        target_role: str = Form(default=""),
        grade: str = Form(default=""),
        project_level: str = Form(default="5"),
        product_sense: str = Form(default="5"),
        growth_sense: str = Form(default="5"),
        data_level: str = Form(default="5"),
        ai_level: str = Form(default="5"),
        content_level: str = Form(default="5"),
        existing_projects: str = Form(default=""),
        time_commitment: str = Form(default="每天 3-4 小时"),
    ):
        p = get_profile()
        if p:
            edu = p.get("education") or {}
            school = school or edu.get("school", "")
            major = major or edu.get("major", "")
            target_role = target_role or p.get("target_role", "")
            existing_projects = existing_projects or "\n".join(x.get("name", "") for x in p.get("projects", []))
        result = generate_plan(
            school=school, major=major, target_role=target_role,
            grade=grade or "大三", project_level=int(project_level),
            product_sense=int(product_sense), growth_sense=int(growth_sense),
            data_level=int(data_level), ai_level=int(ai_level),
            content_level=int(content_level),
            existing_projects=existing_projects,
            time_commitment=time_commitment,
        )
        return {"success": True, "plan": result}

    @app.get("/api/growth-report")
    async def api_growth_report():
        return {"success": True, **get_growth_report()}

    # ===== Group interview =====

    @app.post("/api/group/start")
    async def api_group_start(
        role: str = Form(default=""),
        other_roles: str = Form(default="后端开发, 运营, 设计"),
        topic: str = Form(default="如何提升一款社交App的次日留存"),
    ):
        p = get_profile()
        if not role:
            role = (p.get("target_role", "") if p else "") or "产品经理"
        others = [r.strip() for r in other_roles.split(",") if r.strip()][:3]
        result = start_group_interview(role, others, topic)
        gid = result.get("session_id", str(uuid.uuid4())[:8])
        active_group_sessions[gid] = result
        active_group_sessions[gid]["session_id"] = gid
        return {"success": True, "session_id": gid, "opening": result.get("opening", ""),
                "all_roles": result.get("all_roles", []), "max_rounds": result.get("max_rounds", 5)}

    @app.post("/api/group/respond")
    async def api_group_respond(session_id: str = Form(...), answer: str = Form(...)):
        if session_id not in active_group_sessions:
            return {"success": False, "error": "Session not found"}
        result = group_respond(active_group_sessions[session_id], answer)
        result["success"] = True
        return result

    @app.post("/api/group/evaluate")
    async def api_group_evaluate(session_id: str = Form(...)):
        if session_id not in active_group_sessions:
            return {"success": False, "error": "Session not found"}
        result = group_evaluate(active_group_sessions[session_id])
        result["success"] = True
        return result

    # ===== Export =====

    @app.post("/api/export-resume")
    async def api_export_resume(resume_text: str = Form(...), format: str = Form(default="pdf")):
        from components.export import export_resume
        try:
            path = export_resume(resume_text, format)
            return {"success": True, "path": path, "format": format}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/download-resume")
    async def api_download_resume(path: str = ""):
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        abs_path = os.path.abspath(path)
        if not path or not abs_path.startswith(outputs_dir) or not os.path.exists(abs_path):
            return {"success": False, "error": "File not found"}
        return FileResponse(abs_path, filename=os.path.basename(abs_path))

    # ===== Tracker =====

    @app.get("/api/tracker/dashboard")
    async def api_tracker_dashboard():
        return {"success": True, **get_dashboard()}

    @app.post("/api/tracker/add")
    async def api_tracker_add(
        company: str = Form(...),
        position: str = Form(...),
        channel: str = Form(default=""),
        salary: str = Form(default=""),
        city: str = Form(default=""),
        applied_at: str = Form(default=""),
        notes: str = Form(default=""),
        next_action: str = Form(default=""),
        next_action_date: str = Form(default=""),
        jd_id: str = Form(default=""),
        jd_text: str = Form(default=""),
    ):
        result = add_application(
            company, position, channel=channel, salary=salary, city=city,
            jd_text=jd_text, notes=notes, applied_at=applied_at,
            next_action=next_action, next_action_date=next_action_date, jd_id=jd_id,
        )
        return {"success": "error" not in result, **result}

    @app.post("/api/tracker/status")
    async def api_tracker_status(
        app_id: str = Form(...),
        new_status: str = Form(...),
        note: str = Form(default=""),
        next_action: str = Form(default=""),
        next_action_date: str = Form(default=""),
    ):
        result = update_status(app_id, new_status, note=note, next_action=next_action, next_action_date=next_action_date)
        return {"success": "error" not in result, **result}

    @app.post("/api/tracker/delete")
    async def api_tracker_delete(app_id: str = Form(...)):
        result = delete_application(app_id)
        return {"success": "error" not in result, **result}

    # ===== Self intro =====

    @app.post("/api/intro/generate")
    async def api_intro_generate(
        resume_text: str = Form(default=""),
        jd_text: str = Form(default=""),
        duration: str = Form(default="60"),
        style: str = Form(default="结构化"),
        scene: str = Form(default=""),
        target_role: str = Form(default=""),
        company: str = Form(default=""),
    ):
        p = get_profile()
        if not resume_text:
            resume_text = profile_as_resume_text(p) if p else ""
        if not resume_text:
            return _require_profile()
        if not scene:
            scene = (p.get("job_type", "校招") if p else "校招") or "校招"
        if not target_role:
            target_role = (p.get("target_role", "") if p else "")
        result = generate_intro(resume_text=resume_text, jd_text=jd_text, duration=duration,
                                style=style, scene=scene, target_role=target_role, company=company)
        return {"success": True, **result}

    @app.post("/api/intro/project")
    async def api_intro_project(
        project_text: str = Form(...),
        jd_text: str = Form(default=""),
        depth: str = Form(default="3min"),
        target_role: str = Form(default=""),
    ):
        if not target_role:
            p = get_profile()
            target_role = (p.get("target_role", "") if p else "")
        result = generate_project_pitch(project_text=project_text, jd_text=jd_text, depth=depth, target_role=target_role)
        return {"success": True, **result}

    # ===== Offer comparator =====

    @app.get("/api/offers/prefill")
    async def api_offers_prefill():
        """看板里走到 HR面 / Offer 的记录 → 预填 Offer 对比卡片。"""
        from modules.application_tracker import list_applications
        apps = list_applications(active_only=False)["applications"]
        offers = [
            {"company": a["company"], "position": a["position"], "city": a.get("city", ""),
             "salary": a.get("salary", ""), "notes": a.get("notes", "")}
            for a in apps if a.get("status") in ("Offer", "HR面", "已入职")
        ]
        return {"success": True, "offers": offers}

    @app.post("/api/offers/compare")
    async def api_offers_compare(request: Request):
        body = await request.json()
        result = compare_offers(body.get("offers", []), weights=body.get("weights") or None, priorities=body.get("priorities", ""))
        return {"success": "error" not in result, **result}

    return app


def _profile_markdown(p: dict) -> str:
    """档案导出为 Markdown（供 PDF / Word）。"""
    edu = p.get("education") or {}
    lines = [f"# {p.get('name') or '求职者'}", ""]
    lines.append(f"求职意向：{p.get('target_role') or ''} · {p.get('job_type') or ''} · 期望城市：{p.get('target_cities') or '不限'}")
    lines.append("")
    if any(edu.values()):
        lines.append("## 教育背景")
        lines.append(f"{edu.get('school', '')} · {edu.get('major', '')} · {edu.get('degree', '')} · {edu.get('graduation', '')}届")
        lines.append("")
    if p.get("skills"):
        lines.append("## 专业技能")
        for s in p["skills"]:
            lines.append(f"- {s}")
        lines.append("")
    if p.get("projects"):
        lines.append("## 项目经历")
        for x in p["projects"]:
            lines.append(f"### {x.get('name', '')}")
            for ln in (x.get("description") or "").split("\n"):
                if ln.strip():
                    lines.append(f"- {ln.strip().lstrip('-•· ')}")
        lines.append("")
    if p.get("experience"):
        lines.append("## 实习 / 工作经历")
        for x in p["experience"]:
            lines.append(f"### {x.get('title', '')}")
            for ln in (x.get("description") or "").split("\n"):
                if ln.strip():
                    lines.append(f"- {ln.strip().lstrip('-•· ')}")
        lines.append("")
    if p.get("summary"):
        lines.append("## 自我评价")
        lines.append(p["summary"])
    return "\n".join(lines)


HTML_TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.html"), encoding="utf-8").read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.html")) else "<h1>app.html missing</h1>"


def get_html_template() -> str:
    """Return the complete HTML template with CSS injected."""
    return HTML_TEMPLATE.replace("__CSS__", CSS)


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
