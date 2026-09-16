"""
Career Matcher — 岗位匹配度分析。

Takes candidate background description and matches to top 3 job directions.
Uses 10 built-in role templates (covering 技术/产品/运营/设计/数据/市场)
unless the caller passes its own JD list.
"""

import json
import os
from typing import Optional
from utils import callLlm, safeCallLlm

SYSTEM_PROMPT = """你是互联网行业的岗位匹配专家，服务对象覆盖校招、社招和转行人群。
你深刻理解各个技术/产品/运营/设计/数据/市场岗位的真实要求，能精准判断候选人与岗位的匹配度。

你的原则：
- 项目质量 > 学校名气
- 技术深度 > 技术广度（对技术岗）
- 用户/数据意识 > 功能堆砌经验（对产品岗）
- 可量化结果 > 岗位头衔（对运营/市场岗）
- AI 协同能力是加分项
- 转行候选人：重点评估可迁移能力，而不是简单否定
- 不要给虚假希望 — 差距就是差距
- 匹配分必须严格，大部分候选人应该在 40-70 分区间"""

BUILT_IN_ROLES = [
    {
        "title": "后端开发",
        "技术要求": "Go/Java/C++中至少一门, 分布式系统基础, MySQL/Redis, 消息队列, 微服务架构",
        "项目要求": "高并发或分布式项目经验, 性能优化案例, 系统设计能力, 线上问题排查经验",
        "学历门槛": "本科及以上, 计算机/软件工程相关专业优先",
        "加分项": "开源贡献, 系统设计竞赛获奖, 云原生经验(K8s/Docker), 源码阅读习惯"
    },
    {
        "title": "前端开发",
        "技术要求": "JavaScript/TypeScript, React或Vue框架, HTML/CSS, 浏览器原理, 网络协议",
        "项目要求": "复杂前端项目(SPA/SSR), 组件库或工具开发, 性能优化(首屏/渲染), 跨端经验",
        "学历门槛": "本科及以上, 计算机相关专业优先",
        "加分项": "开源UI库贡献, 跨端开发(Flutter/RN), WebAssembly, Node.js全栈能力"
    },
    {
        "title": "客户端开发",
        "技术要求": "Swift/Kotlin/Objective-C, iOS/Android系统原理, 性能与内存优化, 网络与存储",
        "项目要求": "上架应用或复杂客户端模块, 启动/卡顿/包体优化案例, 跨端框架实践",
        "学历门槛": "本科及以上, 计算机相关专业优先",
        "加分项": "个人App有真实用户, 鸿蒙/Flutter经验, 音视频或图形渲染经验"
    },
    {
        "title": "算法工程师",
        "技术要求": "Python/C++, 机器学习/深度学习框架(PyTorch/TF), 数学基础(概率/线性代数/优化), 论文阅读与复现能力",
        "项目要求": "Kaggle竞赛名次(前10%), 论文发表(一作), 实际业务落地项目(非Demo), 数据处理全流程经验",
        "学历门槛": "硕士及以上, 数学/统计/CS相关专业, 顶会论文强烈加分",
        "加分项": "一作顶会论文, 工业级模型部署经验, 大模型训练/微调经验, 开源ML项目维护者"
    },
    {
        "title": "测试开发",
        "技术要求": "Python/Java, 自动化测试框架(Selenium/Appium/pytest), CI/CD流程, Linux基础, 网络协议",
        "项目要求": "自动化测试平台或框架搭建, 测试效率量化提升数据, 性能/压力测试实践",
        "学历门槛": "本科及以上, 计算机相关专业",
        "加分项": "测试工具开源项目, 性能/安全测试经验, 持续集成实践经验, 质量度量体系搭建"
    },
    {
        "title": "产品经理",
        "技术要求": "数据分析(SQL必备), 原型工具(Figma/Sketch), A/B测试方法论, 用户研究基础",
        "项目要求": "从0到1的产品或功能, 真实用户(非课程项目), 数据驱动的决策案例, 用户反馈闭环",
        "学历门槛": "本科及以上, 专业不限但偏好CS/设计/心理学/社会学",
        "加分项": "个人产品有DAU, 内容账号有粉丝, AI工具深度使用, 增长实验经验"
    },
    {
        "title": "数据分析",
        "技术要求": "SQL精通, Python/R数据处理, 统计学基础, BI工具(Tableau/PowerBI), A/B测试与因果推断",
        "项目要求": "完整的数据分析项目(问题定义→取数→分析→结论→落地), 业务指标体系搭建, 数据驱动的决策案例",
        "学历门槛": "本科及以上, 统计/数学/经济/CS相关专业优先",
        "加分项": "数据竞赛名次, 建过数据看板, 埋点设计经验, 业务方能听懂的汇报能力"
    },
    {
        "title": "运营",
        "技术要求": "数据分析(Excel/SQL), 内容创作能力, 活动策划执行, 社群管理, 用户调研",
        "项目要求": "真实运营案例(线上活动/内容/社群), 可量化的增长数据, 用户洞察与策略调整",
        "学历门槛": "本科及以上, 专业不限",
        "加分项": "个人账号运营(有粉丝量), 爆款内容案例, A/B增长实验, 用户生命周期管理经验"
    },
    {
        "title": "市场营销",
        "技术要求": "品牌与投放基础, 内容策划, 数据分析(ROI/CAC/LTV), 渠道管理, 市场调研",
        "项目要求": "完整的营销活动案例(目标→策略→执行→复盘), 可量化的投放或增长结果, 跨部门协作经验",
        "学历门槛": "本科及以上, 专业不限",
        "加分项": "爆款营销案例, 投放账户实操经验, 品牌从0到1经验, 自媒体影响力"
    },
    {
        "title": "UI/UX 设计",
        "技术要求": "Figma/Sketch精通, 设计系统与组件规范, 交互原型, 基础动效, 用户研究方法",
        "项目要求": "完整的产品设计案例(需求→方案→验证→迭代), 设计改版带来的数据变化, 作品集",
        "学历门槛": "本科及以上, 设计/艺术/HCI相关专业优先",
        "加分项": "作品集有上线产品, 设计系统搭建经验, AI设计工具工作流, 数据驱动设计案例"
    },
]


def match_career(student_profile: str, available_jd_list: list = None) -> dict:
    """
    匹配候选人背景到最适合的岗位方向。

    Args:
        student_profile: 候选人背景描述（技能/项目/兴趣/学校/专业/工作经历等）
        available_jd_list: 可选的真实JD列表 [{"title": str, "requirements": str}, ...]
                           如果为None，使用内置 10 个岗位模板

    Returns:
        {
            "matches": [{"role": str, "match_score": int, "strengths": [...], "gaps": [...], "gap_checklist": [...]}],
            "overall_recommendation": str,
            "markdown": str
        }
    """
    roles = available_jd_list if available_jd_list else BUILT_IN_ROLES

    prompt = f"""请基于以下候选人背景，匹配最适合的岗位方向。

【候选人背景】
{student_profile[:4000]}

【可选岗位模板】
{json.dumps(roles, ensure_ascii=False, indent=2)[:4000]}

请分析每个岗位的匹配度，选出 TOP 3 并给出详细分析。

匹配原则：
- 技术岗看技术栈匹配度和项目复杂度
- 产品岗看用户意识和数据 sense
- 运营/市场岗看可量化的结果和用户洞察
- 转行候选人重点看可迁移能力
- 不要只看学历 — 项目经验和动手能力更重要
- AI 能力对所有岗位都是加分项

输出 JSON：
```json
{{
  "matches": [
    {{
      "role": "岗位名称（必须与模板中的title一致）",
      "match_score": 72,
      "strengths": ["候选人的具体优势1（引用背景中的内容）", "优势2"],
      "gaps": ["具体差距1", "差距2"],
      "gap_checklist": [
        {{"item": "需要补充的具体技能或经验", "priority": "high"}},
        {{"item": "建议做的项目或练习", "priority": "medium"}},
        {{"item": "加分项建议", "priority": "low"}}
      ]
    }}
  ],
  "overall_recommendation": "综合建议 — 最推荐哪个方向、为什么、下一步最该做什么（100字以内）"
}}
```

要求：
- matches 必须恰好 3 个
- match_score 严格评分（大部分候选人应在 40-70 区间）
- strengths 和 gaps 必须引用候选人背景中的具体内容
- gap_checklist 必须可执行（不是说"多学习"）
- overall_recommendation 必须给出明确方向选择建议"""

    result = safeCallLlm(prompt, SYSTEM_PROMPT, output_format="json",
                         fallback={"matches": [], "overall_recommendation": "分析暂时不可用，请重试", "error": ""})

    if isinstance(result, dict) and "_trait" not in result and not result.get("error") and not result.get("_error"):
        result["markdown"] = _render_markdown(result)

    return result


def _render_markdown(data: dict) -> str:
    """Render career match results as Markdown."""
    lines = [
        "# 🎯 岗位匹配度分析",
        "",
    ]

    matches = data.get("matches", [])
    if not matches:
        lines.append("> 暂无匹配结果，请重试。")
        return "\n".join(lines)

    for i, m in enumerate(matches):
        score = m.get("match_score", 0)
        if score >= 75:
            emoji, color = "🟢", "高匹配"
        elif score >= 50:
            emoji, color = "🟡", "中等匹配"
        else:
            emoji, color = "🔴", "低匹配"

        bar_filled = score // 5
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        lines.append(f"## {i+1}. {m.get('role', '')} — {score}/100 {emoji}")
        lines.append(f"`{bar}`")
        lines.append("")

        if m.get("strengths"):
            lines.append("**✅ 你的优势**")
            for s in m["strengths"]:
                lines.append(f"- {s}")
            lines.append("")

        if m.get("gaps"):
            lines.append("**⚠️ 存在的差距**")
            for g in m["gaps"]:
                lines.append(f"- {g}")
            lines.append("")

        if m.get("gap_checklist"):
            lines.append("**📋 补强清单**")
            lines.append("| 优先级 | 行动项 |")
            lines.append("|--------|--------|")
            for item in m["gap_checklist"]:
                p_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.get("priority", "medium"), "⚪")
                lines.append(f"| {p_emoji} {item.get('priority', 'medium')} | {item.get('item', '')} |")
            lines.append("")

    if data.get("overall_recommendation"):
        lines.append("## 💡 综合建议")
        lines.append(f"> {data['overall_recommendation']}")
        lines.append("")

    return "\n".join(lines)
