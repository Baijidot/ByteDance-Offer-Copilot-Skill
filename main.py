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
    generate_persona, detect_authenticity,
)
from modules.self_review import get_self_review


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

    while True:
        console.print("\n[bold]⚡ v2 功能菜单：[/bold]")
        console.print("  1. 🔍 JD 深度拆解（支持文件/URL/文本）")
        console.print("  2. 📊 Offer 概率预测")
        console.print("  3. 🔥 简历重构 + 黑话检测")
        console.print("  4. 🎤 模拟面试（温和/高压/地狱 + 压力值）")
        console.print("  5. 🗺️ 成长路线")
        console.print("  6. 🫧 黑话检测 + 翻译")
        console.print("  7. 📋 生成面评报告")
        console.print("  8. 📈 查看成长轨迹")
        console.print("  9. 🧬 互联网人格画像")
        console.print("  10. 🔍 项目真实性检测")
        console.print("  11. 🚀 一键全流程 v2.1")
        console.print("  0. 退出")

        choice = Prompt.ask("选项", choices=[str(i) for i in range(12)])

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


def _cli_interview(console, user_id):
    console.print("\n[bold cyan]🎤 模拟面试[/bold cyan]\n")
    mode = Prompt.ask("面试模式", choices=["温和", "高压", "地狱"], default="地狱")
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
    elif cmd == "summary":
        _print_v2_summary()
    else:
        print(f"未知命令: {cmd}")
        print("可用: web / cli / full / bs / growth-report / review / summary")


if __name__ == "__main__":
    main()
