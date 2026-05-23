#!/usr/bin/env python3
"""
ByteDance Offer Copilot v2 — AI 互联网职业教练

不是工具，不是一个简历优化器。
是一个真正的 AI 面试官 + 职业教练。

Usage:
    # Skill import
    from modules import analyze_jd, detect_bs, start_interview, generate_feedback, get_growth_report

    # Web UI
    python main.py web

    # CLI
    python main.py cli
"""

import sys
import os
import io
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import (
    analyze_jd, predict_offer, rewrite_project, rewrite_intro, portfolio_advice,
    start_interview, respond, evaluate, generate_plan,
    generate_feedback, detect_contradiction, detect_bs, rewrite_bs, translate_bs,
    record_session, get_growth_report, resolve_problem, add_milestone,
    calculate_pressure, get_pressure_display,
    generate_persona, detect_authenticity, match_career,
    start_group_interview, group_respond, group_evaluate,
)
from modules.self_review import get_self_review
from utils import buildConfusionDiagnosis, loadGrowthData


# ═══════════════════════════════════════════════════
# Skill entry point
# ═══════════════════════════════════════════════════

def run_skill(
    mode: str = "full",
    jd_text: str = "",
    resume_text: str = "",
    interview_mode: str = "地狱",
    target_role: str = "产品经理",
    user_id: str = "default_user",
) -> dict:
    """
    v2 Skill 主入口 — 一键运行全部分析 + 成长追踪。

    Args:
        mode: "full" | "jd" | "predict" | "rewrite" | "interview" | "growth" | "bs_check"
        jd_text: 岗位 JD（文本/文件路径/URL）
        resume_text: 简历文本
        interview_mode: 温和 / 高压 / 地狱
        target_role: 目标岗位
        user_id: 用户标识（用于成长追踪）

    Returns:
        Dict with all analysis results.
    """
    results = {"_meta": {"version": "2.0.0", "mode": mode, "user_id": user_id}}

    # Step 1: JD Analysis
    if mode in ("full", "jd") and jd_text:
        jd_result = analyze_jd(jd_text, job_title=target_role)
        results["jd_analysis"] = jd_result
        record_session(user_id, "jd_analysis", jd_result)

    # Step 1.5: BS Detection (always run if resume provided)
    if resume_text:
        bs_result = detect_bs(resume_text)
        results["bs_detection"] = bs_result

    # Step 2: Offer Prediction
    if mode in ("full", "predict") and resume_text:
        pred_result = predict_offer(resume_text=resume_text, jd_text=jd_text, target_role=target_role)
        results["offer_prediction"] = pred_result
        record_session(user_id, "offer_prediction", pred_result)

    # Step 3: Resume Rewrite
    if mode in ("full", "rewrite") and resume_text:
        rewrite_result = rewrite_project(resume_text, target_role)
        results["resume_rewrite"] = rewrite_result
        record_session(user_id, "resume_rewrite", rewrite_result)

    # Step 4: Interview Start
    if mode in ("full", "interview"):
        interview_result = start_interview(mode=interview_mode, target_role=target_role, jd_text=jd_text)
        results["interview_start"] = interview_result

    # Step 5: Growth Plan
    if mode in ("full", "growth"):
        growth_result = generate_plan(resume_text=resume_text, jd_text=jd_text, target_role=target_role)
        results["growth_plan"] = growth_result
        record_session(user_id, "growth_plan", growth_result)

    # Step 6: Growth Report
    results["growth_report"] = get_growth_report(user_id)

    return results


# ═══════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════

def run_cli():
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown
        from rich.prompt import Prompt
    except ImportError:
        print("pip install rich")
        return

    console = Console()
    console.print(Panel.fit(
        "[bold cyan]ByteDance Offer Copilot v2[/bold cyan]\n"
        "[dim]AI 互联网职业教练 — 不是工具，是面试官[/dim]",
        border_style="cyan",
    ))

    user_id = Prompt.ask("用户 ID（用于成长追踪）", default="user_001")

    # Check for --resume flag
    if "--resume" in sys.argv:
        idx = sys.argv.index("--resume")
        session_id = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if session_id:
            from modules.growth_tracker import load_interview_session
            session = load_interview_session(session_id)
            if "error" in session:
                console.print(f"[red]{session['error']}[/red]")
            else:
                _cli_resume_interview(console, user_id, session)
            return

    # First-time guide
    storage = loadGrowthData()
    if not storage.get("sessions"):
        console.print(Panel(
            "[bold]🎯 欢迎来到 ByteDance Offer Copilot！[/bold]\n\n"
            "这是一个 AI 互联网职业教练，不是简历美化工具。\n\n"
            "[bold]快速上手：[/bold]\n"
            "1. 先做「🧭 迷茫诊断」(选项12) — 了解你该从哪里开始\n"
            "2. 再做「🔍 JD拆解」(选项1) — 看看岗位真正要什么\n"
            "3. 上传简历做「📊 Offer预测」(选项2) — 看看你现在几成把握\n"
            "4. 用「🔥 简历重构」(选项3) — 把学生腔改成字节味\n"
            "5. 做一次「🎤 模拟面试」(选项4) — 面试能力只能靠练\n\n"
            "[dim]提示: 你的所有数据会保存在成长档案中，输入 0 退出。[/dim]",
            title="欢迎",
            border_style="cyan",
        ))

    while True:
        console.print("\n[bold]⚡ v2 功能菜单：[/bold]")
        console.print("  1. 🔍 JD 深度拆解（支持文件/URL/文本）")
        console.print("  2. 📊 Offer 概率预测")
        console.print("  3. 🔥 简历重构 + 黑话检测")
        console.print("  4. 🎤 模拟面试（温和/高压/地狱/暖心 + 压力值）")
        console.print("  5. 🗺️ 成长路线")
        console.print("  6. 🫧 黑话检测 + 翻译")
        console.print("  7. 📋 生成面评报告")
        console.print("  8. 📈 查看成长轨迹")
        console.print("  9. 🧬 互联网人格画像")
        console.print("  10. 🔍 项目真实性检测")
        console.print("  11. 🚀 一键全流程")
        console.print("  12. 🧭 求职迷茫诊断")
        console.print("  13. 🎯 岗位匹配度分析")
        console.print("  14. 👥 群面模拟")
        console.print("  0. 退出")

        choice = Prompt.ask("选项", choices=[str(i) for i in range(15)])

        if choice == "0":
            console.print("[dim]记住：项目质量 > 学校名气。去做作品。[/dim]")
            break
        elif choice == "1":
            _cli_jd(console, user_id)
        elif choice == "2":
            _cli_predict(console, user_id)
        elif choice == "3":
            _cli_rewrite(console, user_id)
        elif choice == "4":
            _cli_interview(console, user_id)
        elif choice == "5":
            _cli_growth(console, user_id)
        elif choice == "6":
            _cli_bs_translate(console)
        elif choice == "7":
            _cli_feedback(console)
        elif choice == "8":
            _cli_growth_report(console, user_id)
        elif choice == "9":
            _cli_persona(console)
        elif choice == "10":
            _cli_authenticity(console)
        elif choice == "11":
            _cli_full(console, user_id)
        elif choice == "12":
            _cli_confusion_diagnosis(console, user_id)
        elif choice == "13":
            _cli_career_match(console, user_id)
        elif choice == "14":
            _cli_group_interview(console, user_id)


def _cli_jd(console, user_id):
    console.print("\n[bold cyan]🔍 JD 深度拆解[/bold cyan]")
    console.print("[dim]支持：MD文件路径 / 网页URL / 直接粘贴JD文本[/dim]\n")
    jd_input = _read_input(console, "JD 输入")
    if not jd_input:
        return
    result = analyze_jd(jd_input)
    record_session(user_id, "jd_analysis", result)
    _print_markdown(console, result)


def _cli_predict(console, user_id):
    console.print("\n[bold cyan]📊 Offer 概率预测[/bold cyan]\n")
    resume = _read_input(console, "简历文本")
    jd = _read_input(console, "目标 JD（可选）")
    if not resume:
        return
    result = predict_offer(resume_text=resume, jd_text=jd)
    record_session(user_id, "offer_prediction", result)
    _print_markdown(console, result)


def _cli_rewrite(console, user_id):
    console.print("\n[bold cyan]🔥 简历重构[/bold cyan]\n")
    text = _read_input(console, "项目描述")
    if not text:
        return

    # First: BS detection
    console.print("\n[bold yellow]先检测空话...[/bold yellow]")
    bs = detect_bs(text)
    _print_markdown(console, bs)

    # Then: rewrite
    result = rewrite_project(text)
    record_session(user_id, "resume_rewrite", result)
    _print_markdown(console, result)

    # Export option
    export_choice = Prompt.ask("导出简历？", choices=["pdf", "docx", "n"], default="n")
    if export_choice != "n":
        try:
            from components.export import export_resume
            path = export_resume(result.get("rewritten", text), format=export_choice)
            console.print(f"[green]已导出到: {path}[/green]")
        except Exception as e:
            console.print(f"[yellow]导出失败: {e}[/yellow]")


def _cli_interview(console, user_id):
    console.print("\n[bold cyan]🎤 模拟面试[/bold cyan]\n")
    mode = Prompt.ask("面试模式", choices=["温和", "高压", "地狱", "暖心"], default="地狱")
    role = Prompt.ask("目标岗位", default="产品经理")

    result = start_interview(mode=mode, target_role=role)
    console.print(f"\n[bold red]面试官：[/bold red]{result['opening']}\n")

    history = [{"role": "interviewer", "content": result["opening"]}]
    pressure = 30 if mode == "温和" else 55 if mode == "高压" else 75

    while True:
        answer = Prompt.ask("[bold green]你[/bold green]")
        if answer.lower() in ("quit", "exit", "退出", "结束面试"):
            break

        history.append({"role": "candidate", "content": answer})

        # Calculate pressure
        pres_data = calculate_pressure(answer, mode, history, pressure)
        pressure = pres_data["pressure"]
        console.print(f"\n[dim]{pres_data['display']}[/dim]")
        if pres_data["suspicion_level"] >= 60:
            console.print(f"[dim]⚠️ 面试官怀疑值：{pres_data['suspicion_level']}%[/dim]")

        # Contradiction check for 高压/地狱
        if mode in ("高压", "地狱") and len(history) >= 5:
            contradiction = detect_contradiction(history, answer, mode)
            if contradiction.get("has_contradiction"):
                console.print(f"\n[bold red]⚠️ 矛盾检测：[/bold red]{contradiction.get('follow_up_question', '')}\n")

        resp = respond(user_answer=answer, mode=mode, target_role=role, chat_history=history)
        msg = resp.get("interviewer_message", "") if isinstance(resp, dict) else str(resp)
        console.print(f"\n[bold red]面试官：[/bold red]{msg}\n")
        history.append({"role": "interviewer", "content": msg})

        if resp.get("is_complete") if isinstance(resp, dict) else False:
            break

    # Final pressure summary
    console.print(f"\n[bold]最终 AI 压力值：{pressure}%[/bold]")
    console.print(get_pressure_display(pres_data))

    # Evaluate
    if Prompt.ask("查看评估？", choices=["y", "n"], default="y") == "y":
        eval_result = evaluate(history, mode, role)
        record_session(user_id, "interview", eval_result)
        _print_markdown(console, eval_result)

        # Save session for persistence
        try:
            from modules.growth_tracker import save_interview_session
            import uuid
            sid = str(uuid.uuid4())[:8]
            save_interview_session(user_id, sid, history, [], eval_result, mode, role)
            console.print(f"[dim]面试已保存 (session: {sid})[/dim]")
        except Exception:
            pass

        # Generate feedback
        if Prompt.ask("生成正式面评？", choices=["y", "n"], default="y") == "y":
            fb = generate_feedback(history, role, mode)
            _print_markdown(console, fb)


def _cli_growth(console, user_id):
    console.print("\n[bold cyan]🗺️ AI 时代成长路线[/bold cyan]\n")
    role = Prompt.ask("目标岗位", default="产品经理")
    grade = Prompt.ask("年级", default="大三")
    result = generate_plan(target_role=role, grade=grade)
    record_session(user_id, "growth_plan", result)
    _print_markdown(console, result)


def _cli_bs_translate(console):
    console.print("\n[bold cyan]🫧 互联网黑话检测 + 翻译[/bold cyan]\n")
    console.print("[dim]粘贴你的简历或回答，自动检测学生空话并翻译成互联网表达...[/dim]\n")
    text = _read_input(console, "文本")
    if not text:
        return

    # Step 1: BS Detection
    console.print("\n[bold yellow]Step 1: 空话检测[/bold yellow]")
    bs = detect_bs(text)
    _print_markdown(console, bs)

    # Step 2: Translate
    if bs.get("total_issues", 0) > 0:
        console.print("\n[bold yellow]Step 2: 互联网翻译[/bold yellow]")
        translated = translate_bs(text, mode="harsh")
        _print_markdown(console, translated)

        if Prompt.ask("是否完整重构？", choices=["y", "n"], default="y") == "y":
            console.print("\n[bold yellow]Step 3: 完整重构[/bold yellow]")
            rewrite_result = rewrite_bs(text)
            _print_markdown(console, rewrite_result)


def _cli_persona(console):
    console.print("\n[bold cyan]🧬 互联网人格画像[/bold cyan]\n")
    console.print("[dim]基于你的简历、项目、经历，生成九维能力雷达...[/dim]\n")
    resume = _read_input(console, "简历文本")
    projects = _read_input(console, "项目经历（可选）")
    content = _read_input(console, "内容/账号经历（可选）")
    if not resume:
        return
    result = generate_persona(
        resume_text=resume,
        projects=projects,
        content_experience=content,
    )
    _print_markdown(console, result)


def _cli_authenticity(console):
    console.print("\n[bold cyan]🔍 项目真实性检测[/bold cyan]\n")
    console.print("[dim]像一个真实的字节技术评审一样审查你的项目...[/dim]\n")
    text = _read_input(console, "项目描述")
    if not text:
        return
    result = detect_authenticity(text)
    _print_markdown(console, result)


def _cli_bs_detect(console):
    console.print("\n[bold cyan]🫧 互联网黑话检测器[/bold cyan]\n")
    console.print("[dim]粘贴你的简历或回答，系统会检测所有学生空话...[/dim]\n")
    text = _read_input(console, "文本")
    if not text:
        return
    result = detect_bs(text)
    _print_markdown(console, result)

    if result.get("total_issues", 0) > 0:
        if Prompt.ask("是否自动重构？", choices=["y", "n"], default="y") == "y":
            rewrite_result = rewrite_bs(text)
            _print_markdown(console, rewrite_result)


def _cli_feedback(console):
    console.print("\n[bold cyan]📋 面评生成器[/bold cyan]\n")
    console.print("[dim]粘贴面试对话记录，生成正式面评...[/dim]\n")

    # Simple: build chat history from user input
    history = []
    console.print("[dim]输入面试记录（每行一条，以'面:'或'我:'开头，输入 END 结束）：[/dim]")
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        if line.startswith("面:") or line.startswith("面："):
            history.append({"role": "interviewer", "content": line[2:].strip()})
        elif line.startswith("我:") or line.startswith("我："):
            history.append({"role": "candidate", "content": line[2:].strip()})

    if not history:
        console.print("[yellow]没有有效记录[/yellow]")
        return

    role = Prompt.ask("目标岗位", default="产品经理")
    fb = generate_feedback(history, role)
    _print_markdown(console, fb)


def _cli_growth_report(console, user_id):
    console.print("\n[bold cyan]📈 成长轨迹[/bold cyan]\n")
    report = get_growth_report(user_id)
    _print_markdown(console, report)


def _cli_full(console, user_id):
    console.print("\n[bold cyan]🚀 一键全流程 — v2[/bold cyan]\n")
    jd = _read_input(console, "岗位 JD（文件/URL/文本）")
    resume = _read_input(console, "简历文本")
    if not jd or not resume:
        console.print("[yellow]JD 和简历都是必填的[/yellow]")
        return

    results = run_skill(mode="full", jd_text=jd, resume_text=resume, user_id=user_id)

    order = ["jd_analysis", "bs_detection", "offer_prediction", "resume_rewrite", "growth_plan", "growth_report"]
    for key in order:
        if key in results:
            console.print(f"\n{'='*60}")
            console.print(f"  {key}")
            console.print(f"{'='*60}")
            _print_markdown(console, results[key])


def _cli_confusion_diagnosis(console, user_id):
    """🧭 求职迷茫诊断 — 4题问答 → 优先级清单"""
    console.print("\n[bold cyan]🧭 求职迷茫诊断[/bold cyan]")
    console.print("[dim]我会问你几个问题，帮你找到现阶段最该做的事。[/dim]\n")

    q1 = Prompt.ask("Q1: 你有明确的求职方向吗？", choices=["Yes", "No"], default="No")
    q2 = Prompt.ask("Q2: 你写过让自己满意的简历吗？", choices=["Yes", "No"], default="No")
    q3 = Prompt.ask("Q3: 你经历过技术/产品面试吗？", choices=["Yes", "No"], default="No")
    q4 = Prompt.ask("Q4: 你目前最大的短板是什么？",
                    choices=["岗位不了解", "简历不会写", "面试紧张", "项目不够好"],
                    default="岗位不了解")

    console.print("\n[bold green]=== 你的求职诊断结果 ===[/bold green]\n")
    result = buildConfusionDiagnosis([q1, q2, q3, q4])
    record_session(user_id, "confusion_diagnosis", result)
    _print_markdown(console, result)


def _cli_career_match(console, user_id):
    """🎯 岗位匹配度分析"""
    console.print("\n[bold cyan]🎯 岗位匹配度分析[/bold cyan]")
    console.print("[dim]描述你的背景，系统推荐最适合的3个岗位方向。[/dim]\n")

    # Check cache status
    import os
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_jobs.json")
    if os.path.exists(cache_path):
        try:
            import json
            with open(cache_path, "r", encoding="utf-8") as f:
                count = len(json.load(f))
            console.print(f"[dim]📋 已加载 {count} 个真实校招岗位（来自 campus_jobs.json）[/dim]\n")
        except Exception:
            console.print("[dim]📋 使用内置6个岗位模板[/dim]\n")
    else:
        console.print("[dim]📋 使用内置6个岗位模板（运行 python main.py fetch-jobs 查看如何爬取真实岗位）[/dim]\n")

    profile = _read_input(console, "你的背景（技能/项目/兴趣/学校/专业）")
    if not profile:
        return
    console.print("[dim]正在匹配...[/dim]\n")
    result = match_career(profile)
    record_session(user_id, "career_match", result)
    _print_markdown(console, result)


def _cli_group_interview(console, user_id):
    """👥 群面模拟 — 无领导小组讨论"""
    console.print("\n[bold cyan]👥 群面模拟 — 无领导小组讨论[/bold cyan]")
    console.print("[dim]你扮演一个角色，AI 扮演 2-3 个其他角色。5 轮讨论后给出分析。[/dim]\n")

    role = Prompt.ask("你的角色", default="产品经理")
    console.print("[dim]其他角色（逗号分隔，最多3个）[/dim]")
    others_input = Prompt.ask("其他角色", default="后端开发, 运营, 设计")
    other_roles = [r.strip() for r in others_input.split(",") if r.strip()][:3]
    topic = Prompt.ask("讨论主题", default="如何提升一款社交App的次日留存")

    console.print(f"\n[dim]你的角色: {role} | AI角色: {', '.join(other_roles)} | 主题: {topic}[/dim]\n")

    session = start_group_interview(role, other_roles, topic)
    opening = session.get("opening", f"讨论主题：{topic}\n参与者：{role}, {', '.join(other_roles)}\n请{role}先发表观点。")
    console.print(f"[bold yellow]=== 开场 ===[/bold yellow]")
    _print_markdown(console, {"markdown": opening})

    round_num = 0
    while round_num < session.get("max_rounds", 5):
        round_num += 1
        answer = Prompt.ask(f"\n[bold green]第{round_num}轮 — 你的发言[/bold green]")
        if answer.lower() in ("quit", "exit", "退出"):
            break

        console.print("[dim]其他角色思考中...[/dim]")
        resp = group_respond(session, answer)

        for r in resp.get("responses", []):
            console.print(f"\n[bold cyan]{r['role']}：[/bold cyan]{r['content']}")

        console.print(f"[dim]--- {resp.get('round_summary', '')} ---[/dim]")

        if resp.get("is_complete"):
            break

    # Evaluate
    if Prompt.ask("\n查看群面分析？", choices=["y", "n"], default="y") == "y":
        console.print("[dim]正在分析群面表现...[/dim]")
        eval_result = group_evaluate(session)
        record_session(user_id, "group_interview", eval_result)
        _print_markdown(console, eval_result)


def _cli_resume_interview(console, user_id, session: dict):
    """Resume a saved interview session."""
    console.print(f"\n[bold cyan]🔄 恢复面试[/bold cyan]")
    console.print(f"[dim]模式: {session.get('mode')} | 岗位: {session.get('target_role')} | 已进行 {len([m for m in session.get('chat_history', []) if m.get('role') == 'candidate'])} 轮[/dim]\n")

    history = session.get("chat_history", [])
    mode = session.get("mode", "高压")
    role = session.get("target_role", "产品经理")

    # Print last few messages for context
    for msg in history[-4:]:
        prefix = "面试官" if msg["role"] == "interviewer" else "你"
        console.print(f"[bold]{prefix}：[/bold]{msg['content']}\n")

    pressure = 50
    while True:
        answer = Prompt.ask("[bold green]你[/bold green]")
        if answer.lower() in ("quit", "exit", "退出", "结束面试"):
            break

        history.append({"role": "candidate", "content": answer})
        resp = respond(user_answer=answer, mode=mode, target_role=role, chat_history=history)
        msg = resp.get("interviewer_message", "") if isinstance(resp, dict) else str(resp)
        console.print(f"\n[bold red]面试官：[/bold red]{msg}\n")
        history.append({"role": "interviewer", "content": msg})

        if resp.get("is_complete") if isinstance(resp, dict) else False:
            break

    if Prompt.ask("查看评估？", choices=["y", "n"], default="y") == "y":
        eval_result = evaluate(history, mode, role)
        _print_markdown(console, eval_result)
        # Update saved session
        try:
            from modules.growth_tracker import save_interview_session
            save_interview_session(user_id, session["session_id"], history, [], eval_result, mode, role)
            console.print(f"[dim]面试已更新[/dim]")
        except Exception:
            pass


# ═══════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════

def _read_input(console, label: str) -> str:
    """Read input: single-line for file/URL, multi-line requires END."""
    console.print(f"[dim]{label}（文件路径/URL/直接粘贴，多行输入以 END 结束）：[/dim]")
    first = input()

    if first.strip().upper() == "END":
        return ""
    if first.strip().startswith(("http://", "https://", "E:", "D:", "C:", "/", ".")):
        return first.strip()
    if first.strip().endswith((".md", ".txt", ".MD", ".TXT")):
        return first.strip()

    lines = [first]
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _print_markdown(console, result: dict, key: str = ""):
    """Print result, preferring markdown field."""
    if not isinstance(result, dict):
        console.print(str(result))
        return

    md = result.get("markdown", "")
    if md:
        try:
            from rich.markdown import Markdown
            console.print(Markdown(md))
            return
        except Exception:
            pass

    # Fallback JSON
    display = {k: v for k, v in result.items() if k != "markdown"}
    console.print_json(json.dumps(display, ensure_ascii=False, indent=2))


# ═══════════════════════════════════════════════════
# v2 Self-Review & Delivery Summary
# ═══════════════════════════════════════════════════

def _print_v2_review():
    """Print the brutal v2 self-review."""
    print(get_self_review())


def _print_v2_summary():
    """Print v2 delivery summary card."""
    print(r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎯 ByteDance Offer Copilot v2                         ║
║   AI 互联网职业教练                                      ║
║                                                          ║
║   从「AI 校招工具」升级为「AI 互联网职业教练」            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

  不是帮你改简历。是让你获得真正的互联网感。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  v2 交付清单

  📦 项目规模
     12 个 Python 模块  |  4,480 行代码  |  零 Mock 数据

  🆕 新增 4 个模块
     📋 modules/interview_feedback.py    面评系统
     ⚡ modules/contradiction_engine.py  矛盾检测引擎
     🫧 modules/corporate_bs_detector.py 黑话检测器
     📈 modules/growth_tracker.py        成长追踪系统

  🔧 升级 5 个模块
     🔍 modules/jd_analyzer.py          支持文件/URL/文本三种输入
     📊 modules/offer_predictor.py      更犀利的评价语言
     🔥 modules/resume_rewriter.py      集成黑话检测
     🎤 modules/mock_interviewer.py     地狱模式 + 矛盾检测
     🗺️ modules/growth_advisor.py       集成成长追踪
     🧠 utils.py                       全新 P8 面试官人格 Prompt

  🎯 核心能力
     ✅ JD 拆解（文件/URL/文本）
     ✅ Offer 7 维概率预测
     ✅ 简历互联网化重构
     ✅ 温和 / 高压 / 地狱 三模式面试
     ✅ 真实字节面评格式
     ✅ 矛盾检测 + 精准追问
     ✅ 学生空话即时检测
     ✅ Offer 概率变化曲线
     ✅ 用户成长追踪

  🚀 运行方式
     python main.py cli      交互式 CLI
     python main.py web      Web UI (localhost:8000)
     python main.py full     一键全流程
     python main.py bs       黑话检测
     python main.py review   残酷自评
     python main.py summary  本页面

  💡 设计原则
     1. Prompt 是产品核心，不是代码
     2. 零 Mock — 所有输出由 LLM 实时生成
     3. JSON + Markdown 双输出
     4. 规则引擎 + LLM 双层架构
     5. 模块化纯函数，任何平台可嵌入

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ⚠️ 已知局限（来自自评）

     综合评分：6.5/10  有条件通过

     最致命的问题：没有数据闭环
     → 你不知道用户用完之后 Offer 概率有没有真的提升

     面试追问深度靠 prompt 而非技术
     → 超过 30 轮对话，上下文窗口溢出，矛盾检测会崩

     黑话检测规则硬编码
     → 无法自进化，新的空话模式检测不到

     差异化护城河弱
     → 任何会用 Trae Solo 的产品经理一个周末可复刻 80%

     如果 v3 只做一件事：做数据闭环。
     找 20 个真实用户，追踪投递结果。

     没有数据的产品建议，
     和自己嘴里说的「学生空话」没有本质区别。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ═══════════════════════════════════════════════════
# Web UI
# ═══════════════════════════════════════════════════

def _print_fetch_jobs_guide():
    """Print guide for crawling ByteDance campus jobs via Trae Solo."""
    import os
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_jobs.json")
    has_cache = os.path.exists(cache_path)

    print(f"""
  ByteDance Campus Jobs — 岗位缓存
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  缓存状态: {'已缓存' if has_cache else '未缓存'}  {cache_path}

  Trae Solo "More Than Coding" 爬取指南:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. 打开 Trae Solo 对话框
  2. 输入:
     "帮我爬取 https://jobs.bytedance.com/campus 的所有校招岗位，
      提取职位名称和岗位要求，
      保存为 campus_jobs.json 放在项目根目录"

  3. Trae Solo 会用内置浏览器能力抓取页面数据并写入文件
  4. 爬完后岗位匹配功能自动识别真实岗位

  数据格式（任意一种均可自动识别）:
  [
    {{"jobTitle": "...", "jobDescription": "..."}},
    {{"title": "...", "requirements": "..."}},
    {{"name": "...", "jd": "...", "department": "..."}}
  ]

  匹配时自动加载缓存岗位 > 没有缓存则用内置6个岗位模板
""")
    return


def _print_stats():
    """Print LLM performance statistics."""
    import os, json
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "performance.jsonl")
    if not os.path.exists(log_path):
        print("No performance data yet. Run at least one LLM call first.")
        return

    total = total_time = successes = failures = 0
    times = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            total += 1
            if entry.get("success"):
                successes += 1
                total_time += entry.get("response_time_ms", 0)
                times.append(entry["response_time_ms"])
            else:
                failures += 1

    if not times:
        print(f"Total calls: {total}, Success: {successes}, Failures: {failures}")
        return

    avg = total_time / len(times)
    sorted_times = sorted(times)
    p50 = sorted_times[len(sorted_times) // 2]
    p90 = sorted_times[min(int(len(sorted_times) * 0.9), len(sorted_times) - 1)]
    p99 = sorted_times[min(int(len(sorted_times) * 0.99), len(sorted_times) - 1)]

    print(f"""
LLM Performance Stats
━━━━━━━━━━━━━━━━━━━━━━━
Total calls: {total}
Success: {successes}  Failures: {failures}
Avg: {avg:.0f}ms  P50: {p50:.0f}ms  P90: {p90:.0f}ms  P99: {p99:.0f}ms
Min: {sorted_times[0]:.0f}ms  Max: {sorted_times[-1]:.0f}ms
""")

def run_web():
    try:
        from components.ui import app
        import uvicorn
        print("ByteDance Offer Copilot v2 — http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError:
        print("Web UI 需要: pip install fastapi uvicorn")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    if cmd == "web":
        run_web()
    elif cmd == "cli":
        run_cli()
    elif cmd == "full":
        from rich.console import Console
        _cli_full(Console(), "default_user")
    elif cmd == "bs":
        from rich.console import Console
        _cli_bs_detect(Console())
    elif cmd == "growth-report":
        from rich.console import Console
        _cli_growth_report(Console(), "default_user")
    elif cmd == "review":
        _print_v2_review()
    elif cmd == "stats":
        _print_stats()
    elif cmd == "fetch-jobs":
        _print_fetch_jobs_guide()
    elif cmd == "summary":
        _print_v2_summary()
    else:
        print(f"未知命令: {cmd}")
        print("可用: web / cli / full / bs / growth-report / review / stats / fetch-jobs / summary")


if __name__ == "__main__":
    main()
