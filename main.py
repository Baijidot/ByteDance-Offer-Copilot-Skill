#!/usr/bin/env python3
"""
Offer Copilot v3 — AI 求职全流程教练

不是工具，不是一个简历优化器。
是一个真正的 AI 面试官 + 职业教练，从 JD 拆解到 Offer 选择的闭环。
覆盖产品 / 技术 / 运营 / 市场 / 设计，校招 / 社招 / 实习 / 转行。

Usage:
    # Skill import
    from modules import analyze_jd, detect_bs, start_interview, generate_feedback, get_growth_report
    from modules import add_application, get_dashboard, generate_intro, compare_offers

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
    add_application, update_status, delete_application, list_applications, get_tracker_stats, get_dashboard,
    generate_intro, generate_project_pitch,
    compare_offers,
)
from modules.application_tracker import ALL_STATUSES, CHANNELS
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
    target_role: str = "",
    user_id: str = "default_user",
    offers: list = None,
    intro_duration: str = "60",
    intro_scene: str = "校招",
) -> dict:
    """
    v3 Skill 主入口 — 一键运行全部分析 + 成长追踪。

    Args:
        mode: "full" | "jd" | "predict" | "rewrite" | "interview" | "growth" | "bs_check"
              | "intro"（自我介绍）| "pitch"（项目讲稿，resume_text 视为项目描述）
              | "track"（投递看板）| "compare"（Offer 对比，需传 offers）
        jd_text: 岗位 JD（文本/文件路径/URL）
        resume_text: 简历文本
        interview_mode: 温和 / 高压 / 地狱 / 暖心
        target_role: 目标岗位（可留空，自动判断）
        user_id: 用户标识（用于成长追踪）
        offers: Offer 列表（mode="compare" 时使用，结构见 modules.offer_comparator）
        intro_duration: 自我介绍时长 "30" | "60" | "180"
        intro_scene: 校招 / 社招 / 实习 / 转行

    Returns:
        Dict with all analysis results.
    """
    results = {"_meta": {"version": "3.0.0", "mode": mode, "user_id": user_id}}

    # Step 1: JD Analysis
    if mode in ("full", "jd") and jd_text:
        jd_result = analyze_jd(jd_text, job_title=target_role)
        results["jd_analysis"] = jd_result
        record_session(user_id, "jd_analysis", jd_result)

    # Step 1.5: BS Detection (always run if resume provided)
    if resume_text and mode not in ("track", "compare"):
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

    # Step 3.5 (v3): Self intro / project pitch
    if mode in ("full", "intro") and resume_text:
        intro_result = generate_intro(resume_text, jd_text, duration=intro_duration, scene=intro_scene, target_role=target_role)
        results["self_intro"] = intro_result
        record_session(user_id, "self_intro", intro_result)
    if mode == "pitch" and resume_text:
        pitch_result = generate_project_pitch(resume_text, jd_text, target_role=target_role)
        results["project_pitch"] = pitch_result
        record_session(user_id, "project_pitch", pitch_result)

    # Step 4: Interview Start
    if mode in ("full", "interview"):
        interview_result = start_interview(mode=interview_mode, target_role=target_role, jd_text=jd_text)
        results["interview_start"] = interview_result

    # Step 5: Growth Plan
    if mode in ("full", "growth"):
        growth_result = generate_plan(resume_text=resume_text, jd_text=jd_text, target_role=target_role)
        results["growth_plan"] = growth_result
        record_session(user_id, "growth_plan", growth_result)

    # Step 6 (v3): Application tracker dashboard
    if mode in ("full", "track"):
        results["tracker"] = get_dashboard(user_id)

    # Step 7 (v3): Offer comparison
    if mode == "compare" and offers:
        compare_result = compare_offers(offers)
        results["offer_compare"] = compare_result
        record_session(user_id, "offer_compare", compare_result)

    # Step 8: Growth Report
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
        "[bold cyan]Offer Copilot v3[/bold cyan]\n"
        "[dim]AI 求职全流程教练 — 从 JD 拆解到 Offer 选择的闭环[/dim]",
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
            "[bold]🎯 欢迎来到 Offer Copilot！[/bold]\n\n"
            "这是一个 AI 求职全流程教练，不是简历美化工具。适用于校招 / 社招 / 实习 / 转行。\n\n"
            "[bold]推荐路径：[/bold]\n"
            "1. 定方向 —「🧭 迷茫诊断」(12) +「🎯 岗位匹配」(13)\n"
            "2. 备弹药 —「🔍 JD拆解」(1) →「🔥 简历重构」(3) →「🎙️ 自我介绍」(16) →「📊 Offer预测」(2)\n"
            "3. 上战场 —「🎤 模拟面试」(4) /「👥 群面」(14)，每一次真实投递记进「📋 投递看板」(15)\n"
            "4. 做决策 — 拿到多个 Offer 后用「⚖️ Offer 对比」(17)，别靠感觉选\n\n"
            "[dim]提示: 你的所有数据会保存在成长档案中，输入 0 退出。[/dim]",
            title="欢迎",
            border_style="cyan",
        ))

    while True:
        console.print("\n[bold]⚡ 功能菜单：[/bold]")
        console.print("  [dim]── 准备 ──[/dim]")
        console.print("  1. 🔍 JD 深度拆解（支持文件/URL/文本）")
        console.print("  2. 📊 Offer 概率预测")
        console.print("  3. 🔥 简历重构 + 黑话检测")
        console.print("  6. 🫧 黑话检测 + 翻译")
        console.print("  10. 🔍 项目真实性检测")
        console.print("  16. 🎙️ 自我介绍 / 项目讲稿生成  [cyan]v3[/cyan]")
        console.print("  [dim]── 面试 ──[/dim]")
        console.print("  4. 🎤 模拟面试（温和/高压/地狱/暖心 + 压力值）")
        console.print("  7. 📋 生成面评报告")
        console.print("  14. 👥 群面模拟")
        console.print("  [dim]── 方向与成长 ──[/dim]")
        console.print("  5. 🗺️ 成长路线")
        console.print("  8. 📈 查看成长轨迹")
        console.print("  9. 🧬 互联网人格画像")
        console.print("  12. 🧭 求职迷茫诊断")
        console.print("  13. 🎯 岗位匹配度分析")
        console.print("  [dim]── 闭环 ──[/dim]")
        console.print("  15. 📋 投递看板（漏斗 / 停滞预警）  [cyan]v3[/cyan]")
        console.print("  17. ⚖️ Offer 对比决策器  [cyan]v3[/cyan]")
        console.print("  11. 🚀 一键全流程")
        console.print("  0. 退出")

        choice = Prompt.ask("选项", choices=[str(i) for i in range(18)])

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
        elif choice == "15":
            _cli_tracker(console, user_id)
        elif choice == "16":
            _cli_intro(console, user_id)
        elif choice == "17":
            _cli_compare(console, user_id)


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
    role = Prompt.ask("目标岗位（如：后端开发 / 产品经理，可留空）", default="")

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
    role = Prompt.ask("目标岗位（可留空）", default="")
    grade = Prompt.ask("当前阶段（大三/大四/研二/已毕业/在职/转行中）", default="大三")
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
    console.print("[dim]像一个真实的大厂技术评审一样审查你的项目...[/dim]\n")
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

    role = Prompt.ask("目标岗位（可留空）", default="")
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
    console.print("[dim]描述你的背景，系统从 10 个内置岗位方向（技术/产品/运营/设计/数据/市场）里推荐最适合的 3 个。[/dim]\n")

    profile = _read_input(console, "你的背景（技能/项目/实习或工作/学校/专业/兴趣）")
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
    role = session.get("target_role", "")

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
# v3: Tracker / Intro / Offer Compare
# ═══════════════════════════════════════════════════

def _cli_tracker(console, user_id):
    """📋 投递看板 — 漏斗 / 停滞预警 / 状态流转"""
    from rich.prompt import Prompt
    from datetime import date

    while True:
        console.print("\n[bold cyan]📋 投递看板[/bold cyan]")
        _print_markdown(console, get_dashboard(user_id))

        console.print("\n  a. 新增投递    s. 更新状态    d. 删除记录    0. 返回主菜单")
        op = Prompt.ask("操作", choices=["a", "s", "d", "0"], default="0")
        if op == "0":
            return

        if op == "a":
            company = Prompt.ask("公司")
            position = Prompt.ask("岗位")
            channel = Prompt.ask("渠道", choices=CHANNELS, default="官网")
            city = Prompt.ask("城市（可留空）", default="")
            salary = Prompt.ask("薪资（可留空，如 25k×16）", default="")
            applied_at = Prompt.ask("投递日期", default=date.today().isoformat())
            next_action = Prompt.ask("下一步行动（可留空）", default="")
            next_date = Prompt.ask("行动日期（可留空）", default="") if next_action else ""
            notes = Prompt.ask("备注（可留空）", default="")
            result = add_application(
                company, position, channel=channel, salary=salary, city=city,
                applied_at=applied_at, next_action=next_action, next_action_date=next_date,
                notes=notes, user_id=user_id,
            )
            _print_markdown(console, result)

        elif op == "s":
            app_id = Prompt.ask("记录 ID（看板里的 ID，输入前几位即可）")
            new_status = Prompt.ask("新状态", choices=ALL_STATUSES)
            note = Prompt.ask("备注（如：面试官问了什么 / 挂在哪里）", default="")
            next_action = ""
            next_date = ""
            if new_status not in ("Offer", "已入职", "已挂", "已放弃"):
                next_action = Prompt.ask("下一步行动（可留空）", default="")
                if next_action:
                    next_date = Prompt.ask("行动日期（可留空）", default="")
            result = update_status(app_id, new_status, note=note,
                                   next_action=next_action, next_action_date=next_date, user_id=user_id)
            _print_markdown(console, result)

        elif op == "d":
            app_id = Prompt.ask("记录 ID")
            if Prompt.ask(f"确认删除 {app_id}？", choices=["y", "n"], default="n") == "y":
                _print_markdown(console, delete_application(app_id, user_id=user_id))


def _cli_intro(console, user_id):
    """🎙️ 自我介绍 / 项目讲稿生成"""
    from rich.prompt import Prompt

    console.print("\n[bold cyan]🎙️ 自我介绍 / 项目讲稿生成器[/bold cyan]")
    console.print("[dim]先给你能直接开口念的稿子，再去模拟面试里被拷打。[/dim]\n")
    kind = Prompt.ask("生成什么", choices=["自我介绍", "项目讲稿"], default="自我介绍")

    if kind == "自我介绍":
        resume = _read_input(console, "简历 / 个人背景")
        if not resume:
            return
        jd = _read_input(console, "目标 JD（可选，直接 END 跳过）")
        duration = Prompt.ask("时长（秒）", choices=["30", "60", "180"], default="60")
        style = Prompt.ask("风格", choices=["结构化", "讲故事", "数据流"], default="结构化")
        scene = Prompt.ask("场景", choices=["校招", "社招", "实习", "转行"], default="校招")
        role = Prompt.ask("目标岗位（可留空）", default="")
        company = Prompt.ask("目标公司（可留空）", default="")
        console.print("[dim]生成中...[/dim]\n")
        result = generate_intro(resume, jd, duration=duration, style=style, scene=scene,
                                target_role=role, company=company)
        record_session(user_id, "self_intro", result)
    else:
        project = _read_input(console, "项目描述（简历原文即可）")
        if not project:
            return
        jd = _read_input(console, "目标 JD（可选，直接 END 跳过）")
        depth = Prompt.ask("版本", choices=["1min", "3min", "deep"], default="3min")
        role = Prompt.ask("目标岗位（可留空）", default="")
        console.print("[dim]生成中...[/dim]\n")
        result = generate_project_pitch(project, jd, depth=depth, target_role=role)
        record_session(user_id, "project_pitch", result)

    _print_markdown(console, result)


def _cli_compare(console, user_id):
    """⚖️ Offer 对比决策器"""
    from rich.prompt import Prompt, FloatPrompt, IntPrompt
    from modules.offer_comparator import DIMENSIONS

    console.print("\n[bold cyan]⚖️ Offer 对比决策器[/bold cyan]")
    console.print("[dim]逐个录入 Offer（至少 2 个，最多 5 个）。薪资单位：万/年；五维打分 1-10，不确定就填 5。[/dim]\n")

    offers = []
    while len(offers) < 5:
        i = len(offers) + 1
        company = Prompt.ask(f"Offer {i} · 公司（留空结束录入）", default="")
        if not company:
            if len(offers) >= 2:
                break
            console.print("[yellow]至少需要 2 个 Offer 才能对比[/yellow]")
            continue
        offer = {"company": company}
        offer["position"] = Prompt.ask("  岗位", default="")
        offer["city"] = Prompt.ask("  城市", default="")
        offer["total_package"] = FloatPrompt.ask("  年总包（万，不确定填 0）", default=0.0)
        offer["base_salary"] = FloatPrompt.ask("  年 base（万，不确定填 0）", default=0.0)
        for key, name, _, desc in DIMENSIONS:
            if key == "salary":
                continue
            offer[f"{key}_score"] = IntPrompt.ask(f"  {name}（1-10）[dim]{desc}[/dim]", default=5)
        offer["notes"] = Prompt.ask("  备注（股票兑现 / leader / 加班情况等，可留空）", default="")
        offers.append(offer)
        console.print()

    weights = None
    if Prompt.ask("是否调整六维权重？（默认 薪酬30/成长25/稳定15/团队15/城市10/赛道5）", choices=["y", "n"], default="n") == "y":
        weights = {}
        for key, name, default_w, _ in DIMENSIONS:
            weights[key] = IntPrompt.ask(f"  {name} 权重", default=default_w)

    priorities = Prompt.ask("你现阶段最看重什么？（给 AI 的定性分析参考，可留空）", default="")
    console.print("[dim]计算中...[/dim]\n")
    result = compare_offers(offers, weights=weights, priorities=priorities)
    record_session(user_id, "offer_compare", result)
    _print_markdown(console, result)


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
# Delivery Summary / Stats
# ═══════════════════════════════════════════════════


def _print_summary():
    """Print v3.0 delivery summary card."""
    print(r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎯 Offer Copilot v3.0                                  ║
║   AI 求职全流程教练                                      ║
║                                                          ║
║   Built with Trae — More Than Coding                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

  不是帮你改简历。是从 JD 拆解到 Offer 选择，把求职做成闭环。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  v3.0 交付清单

  📦 项目规模
     17 个功能模块  |  规则引擎 + LLM 双层  |  零 Mock 数据

  🆕 v2.3 → v3.0 新增
     📋 投递记录追踪          看板 / 漏斗转化率 / 停滞预警 / 行动建议（数据闭环）
     🎙️ 自我介绍生成器        30s/60s/3min × 结构化/讲故事/数据流 × 校招/社招/实习/转行
     🎯 项目讲稿生成器        STAR 拆解 + 预判追问 Top5 + 风险点 + 缺失数据清单
     ⚖️ Offer 对比决策器      六维加权（规则层）+ 隐藏风险 / 谈判筹码（LLM 层）
     🌐 全面通用化            去除单一公司绑定；产品/技术/运营/市场/设计全职能
     🐛 Bug 修复              导出路由未注册、PDF 中文黑方块、前端渲染 [object Object]、
                              stats/fetch-jobs NameError、30 轮对话摘要崩溃、漏斗 >100%

  🎯 核心能力（完整 17 模块）
     ── 准备 ──
     ✅ JD 拆解（文件/URL/文本）          ✅ Offer 6 维概率预测
     ✅ 简历互联网化重构 + PDF/Word 导出   ✅ 学生空话即时检测 + 翻译
     ✅ 项目真实性检测                    ✅ 自我介绍 / 项目讲稿生成 [v3]
     ── 面试 ──
     ✅ 温和/高压/地狱/暖心 四模式面试     ✅ AI 压力值 + 矛盾检测 + 精准追问
     ✅ 大厂内部格式面评                  ✅ 群面模拟（无领导小组讨论）
     ── 方向与成长 ──
     ✅ 求职迷茫诊断                      ✅ 岗位匹配度分析（10 个通用方向）
     ✅ 互联网人格画像（九维雷达）         ✅ AI 时代成长路线
     ✅ 用户成长追踪 + 面试持久化
     ── 闭环 ──
     ✅ 投递看板 + 漏斗 + 停滞预警 [v3]    ✅ Offer 六维加权对比 [v3]

  🚀 运行方式
     python main.py cli          交互式 CLI（17 个菜单选项）
     python main.py web          Web UI (localhost:8000, 11 个页面)
     python main.py stats        LLM 性能统计（P50/P90/P99）
     python main.py bs           黑话检测
     python main.py self-review  产品自评（v2 自评 + v3 回应）
     python main.py summary      本页面

  💡 设计原则
     1. Prompt 是产品核心，不是代码
     2. 零 Mock — 所有输出由 LLM 实时生成
     3. JSON + Markdown 双输出
     4. 规则引擎 + LLM 双层架构（能算的不问 LLM）
     5. 模块化纯函数，任何平台可嵌入
     6. Trae 原生 Skill，关键词触发即用

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def _print_stats():
    """LLM 调用性能统计（读取 logs/performance.jsonl）。"""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "performance.jsonl")
    if not os.path.exists(log_path):
        print("暂无性能日志。只有在配置 TRADE_API_KEY / LLM_API_KEY 走独立 API 模式时才会记录。")
        return

    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("性能日志为空。")
        return

    times = sorted(e.get("response_time_ms", 0) for e in entries)
    success = sum(1 for e in entries if e.get("success"))
    avg_prompt = sum(e.get("prompt_length", 0) for e in entries) / len(entries)

    def pct(p):
        idx = min(len(times) - 1, int(round(p / 100 * (len(times) - 1))))
        return times[idx]

    print(f"""
📊 LLM 调用性能统计

  调用次数      {len(entries)}
  成功率        {success / len(entries) * 100:.1f}%
  平均 prompt   {avg_prompt:.0f} 字符

  响应时间（ms）
    P50   {pct(50):.0f}
    P90   {pct(90):.0f}
    P99   {pct(99):.0f}
    最大  {times[-1]:.0f}
    最小  {times[0]:.0f}

  日志：{log_path}
""")


def run_web():
    try:
        from components.ui import app
        import uvicorn
        print("Offer Copilot v3 — http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError as e:
        print(f"Web UI 需要: pip install fastapi uvicorn python-multipart  （{e}）")


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
    elif cmd == "tracker":
        from rich.console import Console
        _print_markdown(Console(), get_dashboard("default_user"))
    elif cmd in ("review", "summary"):
        _print_summary()
    elif cmd == "stats":
        _print_stats()
    elif cmd == "self-review":
        from rich.console import Console
        _print_markdown(Console(), {"markdown": get_self_review("all")})
    else:
        print(f"未知命令: {cmd}")
        print("可用: web / cli / full / bs / tracker / growth-report / summary / stats / self-review")


if __name__ == "__main__":
    main()
