"""
Offer Copilot v3 — AI 求职全流程教练

可直接导入 Trae Solo 作为 Skill 使用。

v2 模块:
- jd_analyzer: JD 拆解（文件/URL/文本）
- offer_predictor: Offer 6 维概率预测
- resume_rewriter: 简历互联网化重构
- mock_interviewer: 温和/高压/地狱/暖心 模拟面试 + AI 压力值系统
- growth_advisor: AI 时代成长路线
- interview_feedback: 真实大厂面评系统
- contradiction_engine: 矛盾检测 + 精准追问
- corporate_bs_detector: 黑话检测 + 黑话翻译器
- growth_tracker: 用户成长追踪
- internet_persona: 互联网人格画像 + 九维雷达图
- project_authenticity: 项目真实性检测
- career_matcher: 岗位匹配度分析
- group_interview: 群面模拟

v3 模块:
- application_tracker: 投递记录追踪 + 漏斗 + 停滞预警（数据闭环）
- self_intro_generator: 自我介绍 / 项目 STAR 讲稿 + 追问预判
- offer_comparator: Offer 六维加权对比 + 谈判要点

v3.1 模块（简历优先）:
- profile: 简历档案 — 导入 / 规则解析 / 完整度，所有功能的入口
- jd_library: 岗位库 + 简历×JD 匹配分（硬技能/软技能/硬门槛）
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
from modules.growth_tracker import record_session, get_growth_report, resolve_problem, add_milestone, save_interview_session, load_interview_session, list_interview_sessions
from modules.internet_persona import generate_persona
from modules.project_authenticity import detect_authenticity
from modules.career_matcher import match_career
from modules.group_interview import start_group_interview, group_respond, group_evaluate
from modules.application_tracker import (
    add_application, update_status, update_application, delete_application,
    list_applications, get_tracker_stats, get_dashboard,
)
from modules.self_intro_generator import generate_intro, generate_project_pitch
from modules.offer_comparator import compare_offers
from modules.profile import (
    get_profile, save_profile, delete_profile, parse_resume, parse_resume_rules,
    completeness, with_completeness, extract_text_from_upload, profile_as_resume_text,
)
from modules.jd_library import add_jd, list_jds, get_jd, delete_jd, match_jd_rules, rematch_all, save_deep_analysis

__version__ = "3.2.0"
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
    "match_career",
    "save_interview_session",
    "load_interview_session",
    "list_interview_sessions",
    "start_group_interview",
    "group_respond",
    "group_evaluate",
    # v3 New
    "add_application",
    "update_status",
    "update_application",
    "delete_application",
    "list_applications",
    "get_tracker_stats",
    "get_dashboard",
    "generate_intro",
    "generate_project_pitch",
    "compare_offers",
    # v3.1 Profile-first
    "get_profile",
    "save_profile",
    "delete_profile",
    "parse_resume",
    "parse_resume_rules",
    "completeness",
    "with_completeness",
    "extract_text_from_upload",
    "profile_as_resume_text",
    "add_jd",
    "list_jds",
    "get_jd",
    "delete_jd",
    "match_jd_rules",
    "rematch_all",
    "save_deep_analysis",
]
