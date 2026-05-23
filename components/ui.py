"""
Web UI Components — ByteDance Offer Copilot
FastAPI-based web interface with dark ByteDance-style theme.
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import Optional
import json
import uuid

from modules import (
    analyze_jd, predict_offer, rewrite_project, rewrite_intro,
    start_interview, respond, evaluate, generate_plan,
    detect_bs, translate_bs,
    generate_persona, detect_authenticity, match_career,
    start_group_interview, group_respond, group_evaluate,
)
from utils import buildConfusionDiagnosis
from components.styles import CSS


# Store active interview sessions
active_sessions: dict = {}

# Store active group interview sessions
active_group_sessions: dict = {}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ByteDance Offer Copilot",
        description="AI时代的字节跳动校招作战室",
        version="2.3.0",
    )

    # ===== Routes =====

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render main page."""
        return HTMLResponse(content=get_html_template())

    @app.get("/api/styles", response_class=HTMLResponse)
    async def styles():
        """Serve CSS."""
        return HTMLResponse(content=f"<style>{CSS}</style>")

    @app.post("/api/analyze-jd")
    async def api_analyze_jd(
        jd_content: str = Form(...),
        job_title: str = Form(default=""),
        jd_url: str = Form(default=""),
    ):
        """Analyze a job description."""
        result = analyze_jd(jd_content, job_title, jd_url)
        return {"success": True, "analysis": result}

    @app.post("/api/rewrite-project")
    async def api_rewrite_project(
        original_text: str = Form(...),
        target_role: str = Form(default="产品经理"),
    ):
        """Rewrite project experience."""
        # Run BS detection first
        bs = detect_bs(original_text)
        result = rewrite_project(original_text, target_role)
        return {"success": True, "rewrite": result, "bs_detection": bs}

    @app.post("/api/predict-offer")
    async def api_predict_offer(
        school: str = Form(default=""),
        major: str = Form(default=""),
        degree: str = Form(default="本科"),
        target_role: str = Form(default="产品经理"),
        skills: str = Form(default=""),
        projects: str = Form(default=""),
        internships: str = Form(default=""),
        content_experience: str = Form(default=""),
        ai_capability: str = Form(default=""),
        other_highlights: str = Form(default=""),
    ):
        """Predict offer probability."""
        resume_parts = []
        if school:
            resume_parts.append(f"学校：{school}")
        if major:
            resume_parts.append(f"专业：{major}")
        if skills:
            resume_parts.append(f"技能：{skills}")
        if internships:
            resume_parts.append(f"实习：{internships}")
        resume_text = "\n".join(resume_parts) if resume_parts else "未提供简历"

        result = predict_offer(
            school=school, major=major, degree=degree, target_role=target_role,
            skills=skills, projects=projects, internships=internships,
            content_experience=content_experience, ai_capability=ai_capability,
            other_highlights=other_highlights,
        )
        return {"success": True, **result}

    @app.post("/api/interview/start")
    async def api_interview_start(
        mode: str = Form(default="高压"),
        target_role: str = Form(default="产品经理"),
    ):
        """Start a new mock interview."""
        sid = str(uuid.uuid4())[:8]
        result = start_interview(mode=mode, target_role=target_role)
        active_sessions[sid] = {
            "mode": mode,
            "role": target_role,
            "history": [{"role": "interviewer", "content": result.get("opening", "")}],
            "pressure": 30 if mode == "温和" else (55 if mode == "高压" else (75 if mode == "地狱" else 15)),
        }
        return {
            "success": True,
            "session_id": sid,
            "message": result.get("opening", "开始面试。"),
            "mode": mode,
        }

    @app.post("/api/interview/respond")
    async def api_interview_respond(
        session_id: str = Form(...),
        answer: str = Form(...),
    ):
        """Send candidate answer and get interviewer response."""
        if session_id not in active_sessions:
            return {"success": False, "error": "Session not found"}

        session = active_sessions[session_id]
        session["history"].append({"role": "candidate", "content": answer})

        from modules.mock_interviewer import calculate_pressure
        pres = calculate_pressure(answer, session["mode"], session["history"], session["pressure"])
        session["pressure"] = pres["pressure"]

        resp = respond(
            user_answer=answer, mode=session["mode"],
            target_role=session.get("role", "产品经理"),
            chat_history=session["history"],
        )
        msg = resp.get("interviewer_message", "") if isinstance(resp, dict) else str(resp)
        session["history"].append({"role": "interviewer", "content": msg})

        is_complete = resp.get("is_complete", False) if isinstance(resp, dict) else False
        return {
            "success": True,
            "message": msg,
            "pressure": pres,
            "is_complete": is_complete,
        }

    @app.post("/api/interview/evaluate")
    async def api_interview_evaluate(
        session_id: str = Form(...),
    ):
        """Evaluate completed interview."""
        if session_id not in active_sessions:
            return {"success": False, "error": "Session not found"}

        session = active_sessions[session_id]
        result = evaluate(
            session["history"], session["mode"],
            session.get("role", "产品经理"),
        )
        return {"success": True, **result}

    @app.post("/api/growth-plan")
    async def api_growth_plan(
        school: str = Form(default=""),
        major: str = Form(default=""),
        target_role: str = Form(default="产品经理"),
        grade: str = Form(default="大三"),
        project_level: str = Form(default="5"),
        product_sense: str = Form(default="5"),
        growth_sense: str = Form(default="5"),
        data_level: str = Form(default="5"),
        ai_level: str = Form(default="5"),
        content_level: str = Form(default="5"),
        existing_projects: str = Form(default=""),
        time_commitment: str = Form(default="每天 3-4 小时"),
    ):
        """Generate growth plan."""
        result = generate_plan(
            school=school, major=major, target_role=target_role,
            grade=grade, project_level=int(project_level),
            product_sense=int(product_sense), growth_sense=int(growth_sense),
            data_level=int(data_level), ai_level=int(ai_level),
            content_level=int(content_level),
            existing_projects=existing_projects,
            time_commitment=time_commitment,
        )
        return {"success": True, "plan": result}

    @app.post("/api/bs-detect")
    async def api_bs_detect(text: str = Form(...)):
        """Detect corporate BS in text."""
        result = detect_bs(text)
        return {"success": True, **result}

    @app.post("/api/persona")
    async def api_persona(
        resume: str = Form(default=""),
        projects: str = Form(default=""),
        content_exp: str = Form(default=""),
    ):
        """Generate internet persona."""
        result = generate_persona(resume_text=resume, projects=projects, content_experience=content_exp)
        return {"success": True, **result}

    @app.post("/api/authenticity")
    async def api_authenticity(text: str = Form(...)):
        """Detect project authenticity."""
        result = detect_authenticity(text)
        return {"success": True, **result}

    @app.post("/api/confusion-diagnosis")
    async def api_confusion_diagnosis(request: Request):
        """Career confusion diagnosis from 4 answers."""
        body = await request.json()
        answers = body.get("answers", [])
        result = buildConfusionDiagnosis(answers)
        return {"success": True, "diagnosis": result}

    @app.post("/api/career-match")
    async def api_career_match(profile: str = Form(...)):
        """Match student profile to top 3 career directions."""
        result = match_career(profile)
        return {"success": True, **result}

    @app.post("/api/demo")
    async def api_demo():
        """Demo mode — run full pipeline with sample data."""
        sample_jd = "产品经理-抖音内容生态，负责创作者工具和数据驱动的增长策略"
        sample_resume = "某985大学计算机科学专业本科，两个课程项目，一段小厂产品实习，参与过用户增长活动"
        jd_result = analyze_jd(sample_jd, job_title="产品经理")
        offer_result = predict_offer(resume_text=sample_resume, jd_text=sample_jd, target_role="产品经理")
        return {"success": True, "jd": jd_result, "offer": offer_result}

    @app.post("/api/group/start")
    async def api_group_start(
        role: str = Form(default="产品经理"),
        other_roles: str = Form(default="后端开发,运营,设计"),
        topic: str = Form(default="如何提升一款社交App的次日留存"),
    ):
        """Start a group interview session."""
        others = [r.strip() for r in other_roles.split(",") if r.strip()][:3]
        result = start_group_interview(role, others, topic)
        gid = result.get("session_id", str(uuid.uuid4())[:8])
        active_group_sessions[gid] = result
        active_group_sessions[gid]["session_id"] = gid
        return {
            "success": True,
            "session_id": gid,
            "opening": result.get("opening", ""),
            "all_roles": result.get("all_roles", []),
            "max_rounds": result.get("max_rounds", 5),
        }

    @app.post("/api/group/respond")
    async def api_group_respond(
        session_id: str = Form(...),
        answer: str = Form(...),
    ):
        """User speaks, AI roles respond."""
        if session_id not in active_group_sessions:
            return {"success": False, "error": "Session not found"}
        session = active_group_sessions[session_id]
        result = group_respond(session, answer)
        result["success"] = True
        return result

    @app.post("/api/group/evaluate")
    async def api_group_evaluate(
        session_id: str = Form(...),
    ):
        """Evaluate group interview."""
        if session_id not in active_group_sessions:
            return {"success": False, "error": "Session not found"}
        result = group_evaluate(active_group_sessions[session_id])
        result["success"] = True
        return result
    async def api_export_resume(
        resume_text: str = Form(...),
        format: str = Form(default="pdf"),
    ):
        """Export resume to PDF or Word."""
        from components.export import export_resume
        try:
            path = export_resume(resume_text, format)
            return {"success": True, "path": path, "format": format}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/download-resume")
    async def api_download_resume(path: str = ""):
        """Download exported resume file."""
        if not path or not os.path.exists(path):
            return {"success": False, "error": "File not found"}
        filename = os.path.basename(path)
        return FileResponse(path, filename=filename)

    return app

def get_html_template() -> str:
    """Return the complete HTML template with embedded CSS and JS."""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ByteDance Offer Copilot — AI时代的字节跳动校招作战室</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{CSS}</style>
</head>
<body>
    <div id="guideModal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;align-items:center;justify-content:center;z-index:1000;">
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);" onclick="closeGuide()"></div>
        <div style="position:relative;max-width:520px;width:90%;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-xl);padding:32px;z-index:1001;">
            <h2 style="margin-top:0;">🎯 Welcome to ByteDance Offer Copilot</h2>
            <p style="color:var(--text-secondary);">AI career coach. P8 interviewer perspective, helping you become who ByteDance really wants.</p>
            <div style="margin:20px 0;">
                <div style="padding:10px 14px;margin-bottom:8px;background:var(--bg-secondary);border-radius:var(--radius-md);font-size:14px;color:var(--text-secondary);">1. Start with diagnosis to find out where to begin</div>
                <div style="padding:10px 14px;margin-bottom:8px;background:var(--bg-secondary);border-radius:var(--radius-md);font-size:14px;color:var(--text-secondary);">2. Upload a JD for analysis to see what the role really tests</div>
                <div style="padding:10px 14px;margin-bottom:8px;background:var(--bg-secondary);border-radius:var(--radius-md);font-size:14px;color:var(--text-secondary);">3. Upload your resume for Offer probability prediction</div>
                <div style="padding:10px 14px;margin-bottom:8px;background:var(--bg-secondary);border-radius:var(--radius-md);font-size:14px;color:var(--text-secondary);">4. Rewrite your resume from student-speak to ByteDance style</div>
                <div style="padding:10px 14px;margin-bottom:8px;background:var(--bg-secondary);border-radius:var(--radius-md);font-size:14px;color:var(--text-secondary);">5. Do a mock interview — you can only practice interview skills</div>
            </div>
            <div style="text-align:right;">
                <button class="btn btn-primary" onclick="closeGuide()">Get Started</button>
            </div>
        </div>
    </div>
    <div class="app-container">
        <!-- Header -->
        <header class="header">
            <a href="/" class="header-logo">
                <div class="logo-icon">🎯</div>
                ByteDance Offer Copilot
            </a>
            <nav class="header-nav">
                <a href="#features" class="active">功能</a>
                <a href="#demo">Demo</a>
                <a href="https://github.com" target="_blank">GitHub</a>
            </nav>
        </header>

        <!-- Hero -->
        <section class="hero">
            <div class="hero-badge">🤖 AI 时代的校招作战室</div>
            <h1>你不是在投简历<br>你是在打一场 Offer 战役</h1>
            <p class="hero-subtitle">
                字节P8面试官视角，AI驱动的校招竞争力分析。<br>
                不是帮你"美化简历"，而是帮你"成为字节想要的人"。
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-value">5</div>
                    <div class="hero-stat-label">核心功能模块</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">100%</div>
                    <div class="hero-stat-label">AI驱动分析</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">P8</div>
                    <div class="hero-stat-label">面试官视角</div>
                </div>
            </div>
        </section>

        <!-- Tab Navigation -->
        <nav class="tab-nav" id="tabNav">
            <button class="tab-btn active" data-tab="jd">🔍 JD拆解</button>
            <button class="tab-btn" data-tab="predict">📊 Offer预测</button>
            <button class="tab-btn" data-tab="rewrite">🔥 简历重构</button>
            <button class="tab-btn" data-tab="interview">🎤 模拟面试</button>
            <button class="tab-btn" data-tab="confusion">🧭 迷茫诊断</button>
            <button class="tab-btn" data-tab="career">🎯 岗位匹配</button>
            <button class="tab-btn" data-tab="group">👥 群面模拟</button>
            <button class="tab-btn" data-tab="growth">🗺️ 成长路线</button>
        </nav>

        <!-- Tab: JD Analyzer -->
        <section class="tab-content" id="tab-jd">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">🔍</span>
                    <span class="card-title">JD 深度拆解器</span>
                </div>
                <div class="card-body">
                    <p>输入岗位JD，系统会拆解出"真正考察的能力"、"岗位潜台词"、以及"字节真正想要的人"。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-group">
                    <label class="form-label">岗位名称</label>
                    <input type="text" class="form-input" id="jdTitle" placeholder="例如：产品经理-抖音内容生态">
                </div>
                <div class="form-group">
                    <label class="form-label">岗位JD</label>
                    <textarea class="form-textarea" id="jdContent" placeholder="粘贴岗位JD全文...&#10;&#10;例如：&#10;负责抖音内容生态的产品规划和设计&#10;深入理解内容消费场景，挖掘用户需求&#10;数据驱动，通过AB实验验证产品方案"></textarea>
                </div>
                <button class="btn btn-primary btn-lg btn-block" onclick="analyzeJD()">
                    ⚡ 开始拆解
                </button>
            </div>

            <div class="result-panel" id="jdResult">
                <div class="markdown-content" id="jdResultContent"></div>
            </div>
        </section>

        <!-- Tab: Offer Predictor -->
        <section class="tab-content" id="tab-predict" style="display:none">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">📊</span>
                    <span class="card-title">Offer 概率预测</span>
                </div>
                <div class="card-body">
                    <p>基于字节真实评估维度，给出你的Offer概率和具体提升方向。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">学校</label>
                        <input type="text" class="form-input" id="predSchool" placeholder="你的学校">
                    </div>
                    <div class="form-group">
                        <label class="form-label">专业</label>
                        <input type="text" class="form-input" id="predMajor" placeholder="你的专业">
                    </div>
                    <div class="form-group">
                        <label class="form-label">学历</label>
                        <select class="form-select" id="predDegree">
                            <option>本科</option>
                            <option>硕士</option>
                            <option>博士</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">目标岗位</label>
                        <select class="form-select" id="predRole">
                            <option>产品经理</option>
                            <option>游戏策划</option>
                            <option>AI产品</option>
                            <option>运营</option>
                            <option>增长</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">技能</label>
                    <input type="text" class="form-input" id="predSkills" placeholder="Python, SQL, Figma, AI工具...">
                </div>
                <div class="form-group">
                    <label class="form-label">项目经历</label>
                    <textarea class="form-textarea" id="predProjects" placeholder="描述你做过的最有分量的项目...&#10;包含：项目是什么、你的角色、核心数据、用了什么工具"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">实习经历</label>
                    <textarea class="form-textarea" id="predInternships" placeholder="描述实习经历，包含公司、岗位、核心成果..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">内容/社区/账号经历</label>
                    <textarea class="form-textarea" id="predContent" placeholder="是否有运营账号、写文章、做视频等经历..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">AI能力</label>
                    <textarea class="form-textarea" id="predAI" placeholder="描述你使用AI工具的程度：用什么工具、怎么用的、带来什么改变..."></textarea>
                </div>
                <button class="btn btn-primary btn-lg btn-block" onclick="predictOffer()">
                    📊 计算Offer概率
                </button>
            </div>

            <div class="result-panel" id="predictResult">
                <div id="predictScoreCircle" style="text-align:center; margin-bottom:24px"></div>
                <div id="predictDimensions" class="dimension-list" style="margin-bottom:24px"></div>
                <div class="markdown-content" id="predictDetail"></div>
            </div>
        </section>

        <!-- Tab: Resume Rewriter -->
        <section class="tab-content" id="tab-rewrite" style="display:none">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">🔥</span>
                    <span class="card-title">字节味简历重构</span>
                </div>
                <div class="card-body">
                    <p>不是简单润色，而是"互联网化表达"——把"学生腔"变成"字节味"。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-group">
                    <label class="form-label">目标岗位</label>
                    <select class="form-select" id="rewriteRole">
                        <option>产品经理</option>
                        <option>游戏策划</option>
                        <option>AI产品</option>
                        <option>运营</option>
                        <option>增长</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">原始项目描述</label>
                    <textarea class="form-textarea" id="rewriteText" placeholder="粘贴你简历上的项目描述...&#10;&#10;例如：&#10;参与了一个小游戏的开发，负责部分UI设计和功能实现，学习了Unity引擎的使用"></textarea>
                </div>
                <button class="btn btn-primary btn-lg btn-block" onclick="rewriteProject()">
                    🔥 重构表达
                </button>
            </div>

            <div class="result-panel" id="rewriteResult">
                <div class="markdown-content" id="rewriteContent"></div>
            </div>
        </section>

        <!-- Tab: Mock Interview -->
        <section class="tab-content" id="tab-interview" style="display:none">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">🎤</span>
                    <span class="card-title">高压模拟面试</span>
                </div>
                <div class="card-body">
                    <p>真实字节面试官体验。三种模式可选：温和、高压、地狱。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">面试模式</label>
                        <select class="form-select" id="interviewMode">
                            <option>温和</option>
                            <option selected>高压</option>
                            <option>地狱</option>
                            <option>暖心</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">目标岗位</label>
                        <select class="form-select" id="interviewRole">
                            <option>产品经理</option>
                            <option>游戏策划</option>
                            <option>AI产品</option>
                            <option>运营</option>
                            <option>增长</option>
                        </select>
                    </div>
                    <div class="form-group" style="display:flex;align-items:flex-end">
                        <button class="btn btn-primary" onclick="startInterview()" id="startInterviewBtn">
                            🎤 开始面试
                        </button>
                        <button class="btn btn-danger" onclick="endInterview()" id="endInterviewBtn" style="display:none;margin-left:8px">
                            结束面试并评估
                        </button>
                    </div>
                </div>
            </div>

            <div class="chat-container" style="margin-top:16px;display:none" id="chatContainer">
                <div class="chat-header">
                    <div style="display:flex;align-items:center;gap:10px">
                        <span class="emoji-icon">👨‍💼</span>
                        <span style="font-weight:600">字节面试官</span>
                    </div>
                    <span class="chat-mode-badge hard" id="chatModeBadge">高压</span>
                </div>
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="chatInput" placeholder="输入你的回答..." onkeydown="if(event.key==='Enter')sendAnswer()">
                    <button class="btn btn-primary" onclick="sendAnswer()">发送</button>
                </div>
            </div>

            <div class="result-panel" id="interviewResult">
                <h2>📋 面试评估报告</h2>
                <div id="interviewScoreDisplay" style="text-align:center;margin-bottom:24px"></div>
                <div id="interviewDimensions" class="dimension-list" style="margin-bottom:24px"></div>
                <div id="interviewFeedback"></div>
            </div>
        </section>

        <!-- Tab: Growth Advisor -->
        <!-- Confusion Diagnosis Tab -->
        <section class="tab-content" id="tab-confusion" style="display:none">
            <div class="card">
                <div class="card-body">
                    <h3>🧭 Career Confusion Diagnosis</h3>
                    <p style="color:var(--text-secondary);margin-bottom:16px;">Answer 4 questions to find your highest-priority action.</p>
                    <div id="confusionQuestion" style="margin-bottom:16px;"></div>
                    <div id="confusionChoices" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;"></div>
                    <button class="btn btn-secondary" id="confusionRestart" onclick="restartConfusion()" style="display:none;">🔄 Restart</button>
                    <div class="result-panel" id="confusionResult">
                        <div id="confusionResultContent" class="markdown-content"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Career Match Tab -->
        <section class="tab-content" id="tab-career" style="display:none">
            <div class="card">
                <div class="card-body">
                    <h3>🎯 Career Match Analysis</h3>
                    <p style="color:var(--text-secondary);margin-bottom:16px;">Describe your background and get top 3 recommended career directions.</p>
                    <textarea id="careerProfile" class="form-textarea" rows="6" placeholder="Describe your background: skills, projects, internships, school, major, interests..."></textarea>
                    <div style="margin-top:12px;">
                        <button class="btn btn-primary" onclick="matchCareer()">🎯 Match</button>
                        <button class="btn btn-secondary" onclick="fillCareerDemo()" style="margin-left:8px;">📋 Demo</button>
                    </div>
                    <div class="result-panel" id="careerResult">
                        <div id="careerResultContent" class="markdown-content"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Group Interview Tab -->
        <section class="tab-content" id="tab-group" style="display:none">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">👥</span>
                    <span class="card-title">群面模拟 — 无领导小组讨论</span>
                </div>
                <div class="card-body">
                    <p>你扮演一个角色，AI 扮演 2-3 个其他角色。5 轮讨论后给出完整分析。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">你的角色</label>
                        <select class="form-select" id="groupRole">
                            <option>产品经理</option>
                            <option>后端开发</option>
                            <option>前端开发</option>
                            <option>算法工程师</option>
                            <option>运营</option>
                            <option>设计</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">AI 角色（逗号分隔，最多3个）</label>
                        <input type="text" class="form-input" id="groupOthers" value="后端开发, 运营, 设计" placeholder="后端开发, 运营, 设计">
                    </div>
                    <div class="form-group">
                        <label class="form-label">讨论主题</label>
                        <input type="text" class="form-input" id="groupTopic" value="如何提升一款社交App的次日留存" placeholder="讨论主题">
                    </div>
                    <div class="form-group" style="display:flex;align-items:flex-end">
                        <button class="btn btn-primary" onclick="startGroup()" id="startGroupBtn">
                            👥 开始群面
                        </button>
                        <button class="btn btn-danger" onclick="endGroup()" id="endGroupBtn" style="display:none;margin-left:8px">
                            结束并分析
                        </button>
                    </div>
                </div>
            </div>

            <div class="chat-container" style="margin-top:16px;display:none" id="groupChatContainer">
                <div class="chat-header">
                    <div style="display:flex;align-items:center;gap:10px">
                        <span class="emoji-icon">👥</span>
                        <span style="font-weight:600">无领导小组讨论 — <span id="groupRoundLabel">第 1/5 轮</span></span>
                    </div>
                </div>
                <div class="chat-messages" id="groupChatMessages"></div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="groupChatInput" placeholder="输入你的发言..." onkeydown="if(event.key==='Enter')sendGroupAnswer()">
                    <button class="btn btn-primary" onclick="sendGroupAnswer()">发言</button>
                </div>
            </div>

            <div class="result-panel" id="groupResult">
                <h2>📊 群面分析报告</h2>
                <div id="groupResultContent" class="markdown-content"></div>
            </div>
        </section>

        <section class="tab-content" id="tab-growth" style="display:none">
            <div class="card">
                <div class="card-header">
                    <span class="emoji-icon">🗺️</span>
                    <span class="card-title">AI时代成长路线</span>
                </div>
                <div class="card-body">
                    <p>根据你的情况，生成最适合的发展路线和30天冲刺计划。</p>
                </div>
            </div>

            <div class="card" style="margin-top:16px">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">目标岗位</label>
                        <select class="form-select" id="growthRole">
                            <option>产品经理</option>
                            <option>游戏策划</option>
                            <option>AI产品</option>
                            <option>运营</option>
                            <option>增长</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">年级</label>
                        <select class="form-select" id="growthGrade">
                            <option>大三</option>
                            <option>大四</option>
                            <option>研一</option>
                            <option>研二</option>
                            <option>研三</option>
                            <option>已毕业</option>
                        </select>
                    </div>
                </div>
                <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px">自我评分（1-10分）：</p>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">项目能力</label>
                        <input type="range" min="1" max="10" value="5" class="form-input" id="growthProject" style="padding:0" oninput="document.getElementById('growthProjectVal').textContent=this.value">
                        <span id="growthProjectVal" style="font-size:12px;color:var(--text-muted)">5</span>
                    </div>
                    <div class="form-group">
                        <label class="form-label">产品Sense</label>
                        <input type="range" min="1" max="10" value="5" class="form-input" id="growthProduct" style="padding:0" oninput="document.getElementById('growthProductVal').textContent=this.value">
                        <span id="growthProductVal" style="font-size:12px;color:var(--text-muted)">5</span>
                    </div>
                    <div class="form-group">
                        <label class="form-label">增长意识</label>
                        <input type="range" min="1" max="10" value="5" class="form-input" id="growthGrowth" style="padding:0" oninput="document.getElementById('growthGrowthVal').textContent=this.value">
                        <span id="growthGrowthVal" style="font-size:12px;color:var(--text-muted)">5</span>
                    </div>
                    <div class="form-group">
                        <label class="form-label">AI能力</label>
                        <input type="range" min="1" max="10" value="5" class="form-input" id="growthAI" style="padding:0" oninput="document.getElementById('growthAIVal').textContent=this.value">
                        <span id="growthAIVal" style="font-size:12px;color:var(--text-muted)">5</span>
                    </div>
                </div>
                <button class="btn btn-primary btn-lg btn-block" onclick="getGrowthPlan()">
                    🗺️ 生成成长路线
                </button>
            </div>

            <div class="result-panel" id="growthResult">
                <div class="markdown-content" id="growthContent"></div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>ByteDance Offer Copilot — AI时代的校招作战室</p>
            <p style="margin-top:8px">Built with ❤️ for ByteDance candidates</p>
            <p style="margin-top:4px;font-size:12px">本工具仅供学习参考，实际情况请以官方招聘为准</p>
        </footer>
    </div>

    <script>
        // ===== Guide Modal =====
        (function() {{
            if (!localStorage.getItem('hasSeenGuide')) {{
                document.getElementById('guideModal').style.display = 'flex';
                localStorage.setItem('hasSeenGuide', 'true');
            }}
        }})();
        function closeGuide() {{
            document.getElementById('guideModal').style.display = 'none';
        }}

        // ===== Tab Switching =====
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
                document.getElementById('tab-' + btn.dataset.tab).style.display = 'block';
            }});
        }});

        // ===== Helper Functions =====
        function showResult(panelId) {{
            document.getElementById(panelId).classList.add('visible');
        }}

        function hideResult(panelId) {{
            document.getElementById(panelId).classList.remove('visible');
        }}

        async function postForm(url, data) {{
            const formData = new FormData();
            for (const [key, value] of Object.entries(data)) {{
                formData.append(key, value);
            }}
            const resp = await fetch(url, {{ method: 'POST', body: formData }});
            return resp.json();
        }}

        function renderMarkdown(elementId, text) {{
            // Simple markdown to HTML
            let html = text
                .replace(/### (.+)/g, '<h3>$1</h3>')
                .replace(/## (.+)/g, '<h2>$1</h2>')
                .replace(/# (.+)/g, '<h1>$1</h1>')
                .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\|(.+)\\|/g, (match) => {{
                    const cells = match.split('|').filter(c => c.trim());
                    if (cells.length > 1) {{
                        return '<tr>' + cells.map(c => {{
                            const trimmed = c.trim();
                            if (trimmed.match(/^[-:]+$/)) return '';
                            return '<td>' + trimmed + '</td>';
                        }}).join('') + '</tr>';
                    }}
                    return match;
                }})
                .replace(/> (.+)/g, '<blockquote>$1</blockquote>')
                .replace(/^- (.+)/gm, '<li>$1</li>')
                .replace(/\\n/g, '<br>');

            document.getElementById(elementId).innerHTML = html;
        }}

        // ===== JD Analyzer =====
        async function analyzeJD() {{
            const title = document.getElementById('jdTitle').value;
            const content = document.getElementById('jdContent').value;

            if (!content) {{
                alert('请输入岗位JD内容');
                return;
            }}

            const result = await postForm('/api/analyze-jd', {{
                jd_content: content,
                job_title: title,
            }});

            if (result.success) {{
                renderMarkdown('jdResultContent', result.analysis);
                showResult('jdResult');
                document.getElementById('jdResult').scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // ===== Offer Predictor =====
        async function predictOffer() {{
            const result = await postForm('/api/predict-offer', {{
                school: document.getElementById('predSchool').value,
                major: document.getElementById('predMajor').value,
                degree: document.getElementById('predDegree').value,
                target_role: document.getElementById('predRole').value,
                skills: document.getElementById('predSkills').value,
                projects: document.getElementById('predProjects').value,
                internships: document.getElementById('predInternships').value,
                content_experience: document.getElementById('predContent').value,
                ai_capability: document.getElementById('predAI').value,
            }});

            if (result.success) {{
                // Score circle
                const prob = result.probability;
                const color = prob >= 70 ? '#2dd4bf' : prob >= 40 ? '#f59e0b' : '#ef4444';
                document.getElementById('predictScoreCircle').innerHTML = `
                    <div class="score-circle" style="border-color:${{color}};background:${{color}}15">
                        <div class="score-value" style="color:${{color}}">${{prob.toFixed(0)}}%</div>
                        <div class="score-label">Offer概率</div>
                    </div>
                `;

                // Dimension bars
                let dimsHtml = '';
                for (const dim of result.dimensions) {{
                    const pct = (dim.score / dim.max_score * 100);
                    const barColor = pct >= 80 ? '#2dd4bf' : pct >= 50 ? '#f59e0b' : '#ef4444';
                    dimsHtml += `
                        <div class="dimension-item">
                            <span class="dimension-name">${{dim.name}}</span>
                            <div class="dimension-bar-wrap">
                                <div class="dimension-bar-fill" style="width:${{pct}}%;background:${{barColor}}"></div>
                            </div>
                            <span class="dimension-score">${{dim.score.toFixed(1)}}/${{dim.max_score}}</span>
                        </div>
                    `;
                }}
                document.getElementById('predictDimensions').innerHTML = dimsHtml;

                // Detail
                let detailHtml = '';
                if (result.strengths && result.strengths.length) {{
                    detailHtml += '<h2>🟢 优势</h2><ul>' + result.strengths.map(s => '<li>' + s + '</li>').join('') + '</ul>';
                }}
                if (result.weaknesses && result.weaknesses.length) {{
                    detailHtml += '<h2>🟡 短板</h2><ul>' + result.weaknesses.map(w => '<li>' + w + '</li>').join('') + '</ul>';
                }}
                if (result.danger_signals && result.danger_signals.length) {{
                    detailHtml += '<h2>🔴 危险信号</h2><ul>' + result.danger_signals.map(d => '<li>⚠️ ' + d + '</li>').join('') + '</ul>';
                }}
                if (result.improvements && result.improvements.length) {{
                    detailHtml += '<h2>⚡ 最值得补的能力</h2>';
                    result.improvements.forEach((imp, i) => {{
                        detailHtml += '<h3>' + (i+1) + '. ' + imp.action + '</h3>';
                        detailHtml += '<p>为什么：' + imp.why + '<br>怎么做：' + imp.how + '<br>预计耗时：' + imp.time + '</p>';
                    }});
                }}
                if (result.interviewer_comment) {{
                    detailHtml += '<h2>💬 面试官评价</h2><blockquote>' + result.interviewer_comment + '</blockquote>';
                }}

                document.getElementById('predictDetail').innerHTML = detailHtml;
                showResult('predictResult');
                document.getElementById('predictResult').scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // ===== Resume Rewriter =====
        async function rewriteProject() {{
            const text = document.getElementById('rewriteText').value;
            if (!text) {{
                alert('请输入项目描述');
                return;
            }}

            const result = await postForm('/api/rewrite-project', {{
                original_text: text,
                target_role: document.getElementById('rewriteRole').value,
            }});

            if (result.success) {{
                renderMarkdown('rewriteContent', result.rewrite);
                showResult('rewriteResult');
                document.getElementById('rewriteResult').scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // ===== Mock Interview =====
        let currentSessionId = '';

        async function startInterview() {{
            const mode = document.getElementById('interviewMode').value;
            const role = document.getElementById('interviewRole').value;

            const result = await postForm('/api/interview/start', {{
                mode: mode,
                target_role: role,
            }});

            if (result.success) {{
                currentSessionId = result.session_id;
                document.getElementById('chatContainer').style.display = 'flex';
                document.getElementById('startInterviewBtn').style.display = 'none';
                document.getElementById('endInterviewBtn').style.display = 'inline-flex';
                document.getElementById('chatModeBadge').textContent = mode;

                // Update mode badge class
                const badge = document.getElementById('chatModeBadge');
                badge.className = 'chat-mode-badge ' + (mode === '温和' ? 'mild' : mode === '高压' ? 'hard' : 'hell');

                // Show opening
                addChatMessage('interviewer', result.message);
                hideResult('interviewResult');
            }}
        }}

        function addChatMessage(role, content) {{
            const messagesDiv = document.getElementById('chatMessages');
            const avatar = role === 'interviewer' ? '👨‍💼' : '🧑‍💻';
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message ' + role;
            msgDiv.innerHTML = `
                <div class="chat-avatar">${{avatar}}</div>
                <div class="chat-bubble">${{content}}</div>
            `;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        async function sendAnswer() {{
            const input = document.getElementById('chatInput');
            const answer = input.value.trim();
            if (!answer || !currentSessionId) return;

            addChatMessage('candidate', answer);
            input.value = '';

            const result = await postForm('/api/interview/respond', {{
                session_id: currentSessionId,
                answer: answer,
            }});

            if (result.success && result.message) {{
                setTimeout(() => addChatMessage('interviewer', result.message), 500);
            }}

            if (result.is_complete) {{
                document.getElementById('endInterviewBtn').click();
            }}
        }}

        async function endInterview() {{
            if (!currentSessionId) return;

            const result = await postForm('/api/interview/evaluate', {{
                session_id: currentSessionId,
            }});

            if (result.success) {{
                // Score
                const score = result.overall_score;
                const color = score >= 8 ? '#2dd4bf' : score >= 5 ? '#f59e0b' : '#ef4444';
                document.getElementById('interviewScoreDisplay').innerHTML = `
                    <div class="score-circle" style="border-color:${{color}};background:${{color}}15">
                        <div class="score-value" style="color:${{color}}">${{score.toFixed(1)}}</div>
                        <div class="score-label">综合评分 /10</div>
                    </div>
                `;

                // Dimensions
                let dimsHtml = '';
                for (const [name, s] of Object.entries(result.dimension_scores)) {{
                    const pct = s * 10;
                    const barColor = s >= 8 ? '#2dd4bf' : s >= 5 ? '#f59e0b' : '#ef4444';
                    dimsHtml += `
                        <div class="dimension-item">
                            <span class="dimension-name">${{name}}</span>
                            <div class="dimension-bar-wrap">
                                <div class="dimension-bar-fill" style="width:${{pct}}%;background:${{barColor}}"></div>
                            </div>
                            <span class="dimension-score">${{s}}/10</span>
                        </div>
                    `;
                }}
                document.getElementById('interviewDimensions').innerHTML = dimsHtml;

                // Feedback
                let feedbackHtml = '';
                if (result.strengths) {{
                    feedbackHtml += '<h3>🟢 亮点</h3><ul>' + result.strengths.map(s => '<li>' + s + '</li>').join('') + '</ul>';
                }}
                if (result.weaknesses) {{
                    feedbackHtml += '<h3>🟡 待提升</h3><ul>' + result.weaknesses.map(w => '<li>' + w + '</li>').join('') + '</ul>';
                }}
                feedbackHtml += '<h3>📋 结论</h3><blockquote>' + result.verdict + '</blockquote>';
                feedbackHtml += '<h3>💡 建议</h3><p>' + result.advice + '</p>';

                document.getElementById('interviewFeedback').innerHTML = feedbackHtml;
                showResult('interviewResult');
                document.getElementById('interviewResult').scrollIntoView({{ behavior: 'smooth' }});
            }}

            // Reset
            currentSessionId = '';
            document.getElementById('startInterviewBtn').style.display = 'inline-flex';
            document.getElementById('endInterviewBtn').style.display = 'none';
        }}

        // ===== Group Interview =====
        let groupSessionId = '';
        let groupRound = 0;
        let groupMaxRounds = 5;
        let groupAllRoles = [];

        async function startGroup() {{
            var role = document.getElementById('groupRole').value;
            var others = document.getElementById('groupOthers').value;
            var topic = document.getElementById('groupTopic').value;

            var result = await postForm('/api/group/start', {{
                role: role, other_roles: others, topic: topic
            }});

            if (result.success) {{
                groupSessionId = result.session_id;
                groupRound = 0;
                groupMaxRounds = result.max_rounds || 5;
                groupAllRoles = result.all_roles || [];

                document.getElementById('groupChatContainer').style.display = 'flex';
                document.getElementById('startGroupBtn').style.display = 'none';
                document.getElementById('endGroupBtn').style.display = 'inline-flex';
                document.getElementById('groupRoundLabel').textContent = '第 1/' + groupMaxRounds + ' 轮';
                document.getElementById('groupChatMessages').innerHTML = '';
                hideResult('groupResult');

                if (result.opening) {{
                    addGroupMessage('system', result.opening);
                }}
            }}
        }}

        function addGroupMessage(role, content) {{
            var messagesDiv = document.getElementById('groupChatMessages');
            var avatar = role === 'system' ? '📋' : '💬';
            var roleName = role === 'system' ? '开场引导' : role;
            var msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message ' + (role === 'system' ? 'interviewer' : 'candidate');
            msgDiv.innerHTML = '<div class="chat-avatar">' + avatar + '</div><div class="chat-bubble"><strong>' + roleName + '</strong><br>' + content + '</div>';
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        async function sendGroupAnswer() {{
            var input = document.getElementById('groupChatInput');
            var answer = input.value.trim();
            if (!answer || !groupSessionId) return;

            groupRound++;
            document.getElementById('groupRoundLabel').textContent = '第 ' + groupRound + '/' + groupMaxRounds + ' 轮';
            addGroupMessage('你', answer);
            input.value = '';

            var result = await postForm('/api/group/respond', {{
                session_id: groupSessionId, answer: answer
            }});

            if (result.success && result.responses) {{
                var responses = result.responses;
                responses.forEach(function(r, i) {{
                    setTimeout(function() {{ addGroupMessage(r.role, r.content); }}, (i + 1) * 600);
                }});
            }}

            if (result.is_complete || groupRound >= groupMaxRounds) {{
                setTimeout(function() {{ document.getElementById('endGroupBtn').click(); }}, 1500);
            }}
        }}

        async function endGroup() {{
            if (!groupSessionId) return;

            var result = await postForm('/api/group/evaluate', {{
                session_id: groupSessionId
            }});

            if (result.success && result.markdown) {{
                renderMarkdown('groupResultContent', result.markdown);
                showResult('groupResult');
                document.getElementById('groupResult').scrollIntoView({{ behavior: 'smooth' }});
            }}

            groupSessionId = '';
            groupRound = 0;
            document.getElementById('startGroupBtn').style.display = 'inline-flex';
            document.getElementById('endGroupBtn').style.display = 'none';
            document.getElementById('groupChatContainer').style.display = 'none';
        }}

        // ===== Growth Advisor =====
        async function getGrowthPlan() {{
            const result = await postForm('/api/growth-plan', {{
                target_role: document.getElementById('growthRole').value,
                grade: document.getElementById('growthGrade').value,
                project_level: document.getElementById('growthProject').value,
                product_sense: document.getElementById('growthProduct').value,
                growth_sense: document.getElementById('growthGrowth').value,
                ai_level: document.getElementById('growthAI').value,
            }});

            if (result.success) {{
                renderMarkdown('growthContent', result.plan);
                showResult('growthResult');
                document.getElementById('growthResult').scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // ===== Confusion Diagnosis =====
        let confusionStep = 0;
        const confusionAnswers = [];
        const confusionQuestions = [
            {{ text: 'Do you have a clear job direction?', choices: ['Yes', 'No'] }},
            {{ text: 'Have you written a resume you are satisfied with?', choices: ['Yes', 'No'] }},
            {{ text: 'Have you experienced technical/product interviews?', choices: ['Yes', 'No'] }},
            {{ text: 'What is your biggest weakness?', choices: ['Unclear about roles', 'Bad at resume writing', 'Interview anxiety', 'Projects not good enough'] }},
        ];

        function showConfusionQuestion() {{
            if (confusionStep >= confusionQuestions.length) {{
                fetch('/api/confusion-diagnosis', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{answers: confusionAnswers}})
                }}).then(r => r.json()).then(data => {{
                    if (data.success && data.diagnosis) {{
                        renderMarkdown('confusionResultContent', data.diagnosis.markdown);
                        showResult('confusionResult');
                    }}
                }});
                document.getElementById('confusionQuestion').innerHTML = '';
                document.getElementById('confusionChoices').innerHTML = '';
                document.getElementById('confusionRestart').style.display = 'inline-block';
                return;
            }}
            const q = confusionQuestions[confusionStep];
            document.getElementById('confusionQuestion').innerHTML = '<p style="font-size:16px;font-weight:600;">Q' + (confusionStep+1) + ': ' + q.text + '</p>';
            document.getElementById('confusionChoices').innerHTML = q.choices.map(function(c) {{
                return '<button class="btn btn-secondary" onclick="answerConfusion(\'' + c + '\')">' + c + '</button>';
            }}).join(' ');
        }}

        function answerConfusion(answer) {{
            confusionAnswers.push(answer);
            confusionStep++;
            showConfusionQuestion();
        }}

        function restartConfusion() {{
            confusionStep = 0;
            confusionAnswers.length = 0;
            hideResult('confusionResult');
            document.getElementById('confusionRestart').style.display = 'none';
            showConfusionQuestion();
        }}

        // Trigger confusion on tab switch
        (function() {{
            var btn = document.querySelector('[data-tab="confusion"]');
            if (btn) btn.addEventListener('click', function() {{
                if (confusionStep === 0 && confusionAnswers.length === 0) showConfusionQuestion();
            }});
        }})();

        // ===== Career Match =====
        function matchCareer() {{
            var profile = document.getElementById('careerProfile').value.trim();
            if (!profile) {{ alert('Please describe your background first'); return; }}
            hideResult('careerResult');
            var formData = new FormData();
            formData.append('profile', profile);
            fetch('/api/career-match', {{method: 'POST', body: formData}})
                .then(r => r.json()).then(data => {{
                    if (data.success && data.markdown) {{
                        renderMarkdown('careerResultContent', data.markdown);
                        showResult('careerResult');
                    }}
                }});
        }}

        function fillCareerDemo() {{
            document.getElementById('careerProfile').value = 'CS major at a top university, two course projects (campus marketplace, note-taking app), one startup backend internship, Python/Go/MySQL skills, 200 LeetCode problems solved, also interested in product management';
        }}

    </script>
</body>
</html>"""


# Create the app instance
app = create_app()

app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
