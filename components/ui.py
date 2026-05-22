"""
Web UI Components — ByteDance Offer Copilot
FastAPI-based web interface with dark ByteDance-style theme.
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import json

from modules.jd_analyzer import JDAnalyzer
from modules.resume_rewriter import ResumeRewriter
from modules.offer_predictor import OfferPredictor
from modules.mock_interviewer import MockInterviewer, InterviewSession
from modules.growth_advisor import GrowthAdvisor
from components.styles import CSS


# Store active interview sessions
active_sessions: dict[str, InterviewSession] = {}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ByteDance Offer Copilot",
        description="AI时代的字节跳动校招作战室",
        version="1.0.0",
    )

    # Initialize modules
    jd_analyzer = JDAnalyzer()
    resume_rewriter = ResumeRewriter()
    offer_predictor = OfferPredictor()
    mock_interviewer = MockInterviewer()
    growth_advisor = GrowthAdvisor()

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
    async def analyze_jd(
        jd_content: str = Form(...),
        job_title: str = Form(default=""),
        jd_url: str = Form(default=""),
    ):
        """Analyze a job description."""
        result = jd_analyzer.analyze(jd_content, job_title, jd_url)
        output = jd_analyzer.format_output(result)
        return {"success": True, "analysis": output}

    @app.post("/api/rewrite-project")
    async def rewrite_project(
        original_text: str = Form(...),
        target_role: str = Form(default="产品经理"),
    ):
        """Rewrite project experience."""
        result = resume_rewriter.rewrite_project(original_text, target_role)
        output = resume_rewriter.format_project_output(result)
        return {"success": True, "rewrite": output}

    @app.post("/api/rewrite-intro")
    async def rewrite_intro(
        original_text: str = Form(...),
        school: str = Form(default=""),
        major: str = Form(default=""),
        highlights: str = Form(default=""),
        target_role: str = Form(default="产品经理"),
    ):
        """Rewrite self-introduction."""
        result = resume_rewriter.rewrite_self_intro(
            original_text, school, major, highlights, target_role,
        )
        return {"success": True, "intro": result}

    @app.post("/api/predict-offer")
    async def predict_offer(
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
        result = offer_predictor.predict(
            school=school,
            major=major,
            degree=degree,
            target_role=target_role,
            skills=skills,
            projects=projects,
            internships=internships,
            content_experience=content_experience,
            ai_capability=ai_capability,
            other_highlights=other_highlights,
        )
        return {
            "success": True,
            "probability": result.overall_probability,
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "max_score": d.max_score,
                    "comment": d.comment,
                }
                for d in result.dimensions
            ],
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "danger_signals": result.danger_signals,
            "improvements": result.improvements,
            "recommended_projects": result.recommended_projects,
            "interviewer_comment": result.interviewer_comment,
        }

    @app.post("/api/interview/start")
    async def interview_start(
        mode: str = Form(default="高压"),
        target_role: str = Form(default="产品经理"),
        session_id: str = Form(default=""),
    ):
        """Start a new mock interview."""
        import uuid
        sid = session_id or str(uuid.uuid4())[:8]
        session = mock_interviewer.start_session(mode, target_role)
        active_sessions[sid] = session

        opening = session.history[0].content if session.history else "开始面试。"
        return {
            "success": True,
            "session_id": sid,
            "message": opening,
            "phase": session.current_phase,
        }

    @app.post("/api/interview/respond")
    async def interview_respond(
        session_id: str = Form(...),
        answer: str = Form(...),
    ):
        """Send candidate answer and get interviewer response."""
        if session_id not in active_sessions:
            return {"success": False, "error": "会话已过期，请重新开始面试"}

        session = active_sessions[session_id]
        session = mock_interviewer.respond(session, answer)
        active_sessions[session_id] = session

        last_msg = session.history[-1]
        return {
            "success": True,
            "message": last_msg.content if last_msg.role == "interviewer" else "",
            "phase": session.current_phase,
            "is_complete": session.current_phase == "closing",
        }

    @app.post("/api/interview/evaluate")
    async def interview_evaluate(session_id: str = Form(...)):
        """Evaluate completed interview."""
        if session_id not in active_sessions:
            return {"success": False, "error": "会话已过期"}

        session = active_sessions[session_id]
        result = mock_interviewer.evaluate(session)

        return {
            "success": True,
            "overall_score": result.overall_score,
            "dimension_scores": result.dimension_scores,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "verdict": result.verdict,
            "advice": result.advice,
        }

    @app.post("/api/growth-plan")
    async def growth_plan(
        school: str = Form(default=""),
        major: str = Form(default=""),
        target_role: str = Form(default="产品经理"),
        grade: str = Form(default="大三"),
        project_level: int = Form(default=5),
        product_sense: int = Form(default=5),
        growth_sense: int = Form(default=5),
        data_level: int = Form(default=5),
        ai_level: int = Form(default=5),
        content_level: int = Form(default=5),
        existing_projects: str = Form(default=""),
        time_commitment: str = Form(default="每天3-4小时"),
    ):
        """Generate growth plan."""
        plan = growth_advisor.generate_plan(
            school=school,
            major=major,
            target_role=target_role,
            grade=grade,
            project_level=project_level,
            product_sense=product_sense,
            growth_sense=growth_sense,
            data_level=data_level,
            ai_level=ai_level,
            content_level=content_level,
            existing_projects=existing_projects,
            time_commitment=time_commitment,
        )
        output = growth_advisor.format_output(plan)
        return {"success": True, "plan": output}

    @app.get("/api/demo")
    async def demo():
        """Run demo with sample data and return all results."""
        results = {}

        # JD Analysis demo
        sample_jd = """
        负责抖音内容生态的产品规划和设计
        深入理解内容消费场景，挖掘用户需求
        数据驱动，通过AB实验验证产品方案
        有Owner意识，结果导向，抗压能力强
        熟悉AI工具者优先
        """
        jd_result = jd_analyzer.analyze(sample_jd, "产品经理-抖音内容生态")
        results["jd_analysis"] = jd_analyzer.format_output(jd_result)

        # Offer prediction demo
        pred_result = offer_predictor.predict(
            school="某985大学",
            major="计算机科学与技术",
            degree="本科",
            target_role="产品经理",
            skills="Python, SQL, 数据分析, Figma, AI工具(Trae, Cursor)",
            projects="用AI从0到1做了校园二手交易小程序，DAU 2000+，留存45%，用AI完成前端开发和用户调研",
            internships="中型互联网公司产品实习生，负责用户增长，DAU提升30%",
            content_experience="运营产品分析公众号，粉丝5000+，单篇最高阅读2万",
            ai_capability="深度使用AI：Trae写代码，Cursor做产品分析，效率提升3倍+",
        )
        results["offer_prediction"] = offer_predictor.format_output(pred_result)

        # Growth plan demo
        plan = growth_advisor.generate_plan(
            school="某985大学",
            major="计算机科学",
            target_role="产品经理",
            project_level=6,
            product_sense=5,
            growth_sense=4,
            data_level=6,
            ai_level=5,
            content_level=4,
        )
        results["growth_plan"] = growth_advisor.format_output(plan)

        return {"success": True, "demo": results}

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
    </script>
</body>
</html>"""


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
