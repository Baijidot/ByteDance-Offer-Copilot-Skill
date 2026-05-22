"""
ByteDance Offer Copilot v2 — AI 互联网职业教练

可直接导入 Trae Solo 作为 Skill 使用。

v2 模块:
- jd_analyzer: JD 拆解（文件/URL/文本）
- offer_predictor: Offer 7 维概率预测
- resume_rewriter: 简历互联网化重构
- mock_interviewer: 温和/高压/地狱 模拟面试 + AI 压力值系统
- growth_advisor: AI 时代成长路线
- interview_feedback: 真实字节面评系统
- contradiction_engine: 矛盾检测 + 精准追问
- corporate_bs_detector: 黑话检测 + 黑话翻译器
- growth_tracker: 用户成长追踪
- internet_persona: 互联网人格画像 + 九维雷达图
- project_authenticity: 项目真实性检测
"""

from modules.jd_analyzer import analyze as analyze_jd
from modules.offer_predictor import predict as predict_offer
from modules.resume_rewriter import rewrite_project, rewrite_intro, portfolio_advice
from modules.mock_interviewer import (
    start_interview, respond, evaluate,
    calculate_pressure, get_pressure_display,
)
from modules.growth_advisor import generate_plan
from modules.interview_feedback import generate_feedback
from modules.contradiction_engine import detect_contradiction, generate_precision_followup
from modules.corporate_bs_detector import detect as detect_bs, rewrite as rewrite_bs, translate as translate_bs
from modules.growth_tracker import record_session, get_growth_report, resolve_problem, add_milestone
from modules.internet_persona import generate_persona
from modules.project_authenticity import detect_authenticity

__version__ = "2.1.0"
__all__ = [
    # Core (v1)
    "analyze_jd",
    "predict_offer",
    "rewrite_project",
    "rewrite_intro",
    "portfolio_advice",
    "start_interview",
    "respond",
    "evaluate",
    "generate_plan",
    # v2 Core
    "generate_feedback",
    "detect_contradiction",
    "generate_precision_followup",
    "detect_bs",
    "rewrite_bs",
    "record_session",
    "get_growth_report",
    "resolve_problem",
    "add_milestone",
    # v2.1 New
    "calculate_pressure",
    "get_pressure_display",
    "translate_bs",
    "generate_persona",
    "detect_authenticity",
]
