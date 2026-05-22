# ByteDance Offer Copilot v2.1

<p align="center">
  <b>AI 互联网职业教练 — 专治学生空话和简历注水</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-blue" />
  <img src="https://img.shields.io/badge/python-3.9+-green" />
  <img src="https://img.shields.io/badge/modules-12-orange" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

---

不是简历美化工具。是直接扮演**字节跳动 P8 面试官**，用毒舌、犀利的风格拷打你的简历、项目、面试回答——然后告诉你真问题在哪。

## 能力总览

| 模块 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 🔍 JD 拆解 | 岗位潜台词解读 + 理想候选人画像 + 30天路线 | JD文本/URL/文件 | 结构化分析 + Markdown |
| 📊 Offer 预测 | 7 维评分 + 综合概率 + 差距分析 | 简历 + JD | 评分卡 + 具体建议 |
| 🔥 简历重构 | 学生腔 → 互联网表达 | 项目描述/自我介绍 | 改写版 + 改动清单 |
| 🫧 黑话检测 | 弱动词/空话/模糊量化词识别 | 任意文本 | 空话指数 + 逐项解释 |
| 🌐 黑话翻译 | 学生空话 → 互联网表达 | 任意文本 | 逐句翻译 + 笔记 |
| 🎤 模拟面试 | 温和/高压/地狱三模式 | 岗位 + JD | 追问 + 压力值 + 评估 |
| 📋 面评报告 | 真实字节面评格式 | 面试对话记录 | 优势/风险/结论/行动项 |
| ⚡ 矛盾检测 | 跨轮次逻辑矛盾识别 | 历史对话 + 最新回答 | 矛盾标记 + 精准追问 |
| 🔥 AI 压力值 | 基于回答质量的动态压力计算 | 面试回答 + 历史 | 0-100 压力值 + 变化原因 |
| 🧬 人格画像 | 九维互联网能力雷达 | 简历 + 项目 + 内容经历 | 雷达数据 + 强弱项分析 |
| 🔍 真实性检测 | 学生Demo vs 真实产品 | 项目描述 | 6维度评分 + 学生味信号 |
| 📈 成长追踪 | 历史记录 + 成长曲线 | 使用数据 | 趋势图 + 评分 |

## 快速开始

### 作为 Trae Solo Skill 使用

1. 下载 `bytedance-coach.zip`（见 [Releases](https://github.com/Baijidot/ByteDance-Offer-Copilot-Skill/releases)）
2. 在 Trae Solo 中导入 Skill
3. 自动注册，关键词触发

### Python 直接调用

```bash
git clone https://github.com/Baijidot/ByteDance-Offer-Copilot-Skill.git
cd ByteDance-Offer-Copilot-Skill
pip install -r requirements.txt
```

```python
from modules import analyze_jd, detect_bs, predict_offer, start_interview

# JD 拆解（支持文件路径 / URL / 直接粘贴）
result = analyze_jd("https://jobs.bytedance.com/xxx")
print(result["markdown"])

# 黑话检测（规则引擎，秒出，不耗 LLM）
result = detect_bs("我参与了项目开发，提升了用户体验，做了很多功能")
print(f"空话指数：{result['overall_score']}/100")

# 地狱面试
session = start_interview(mode="地狱", target_role="产品经理")
print(session["opening"])
```

### CLI 交互界面

```bash
python main.py cli
# 12 个菜单选项：JD拆解 / Offer预测 / 简历重构+黑话 / 模拟面试+压力值 /
# 成长路线 / 黑话检测+翻译 / 面评报告 / 成长轨迹 / 人格画像 / 项目真实性 / 一键全流程
```

## 项目结构

```
ByteDance-Offer-Copilot-Skill/
├── SKILL.md                          # Trae Solo Skill 注册定义
├── main.py                           # CLI + Web UI 入口
├── utils.py                          # LLM 调度 + 输入识别 + 持久化
├── modules/
│   ├── jd_analyzer.py                # JD 深度拆解
│   ├── offer_predictor.py            # Offer 7维概率预测
│   ├── resume_rewriter.py            # 简历互联网化重构
│   ├── mock_interviewer.py           # 模拟面试 + AI 压力值
│   ├── interview_feedback.py         # 字节格式面评
│   ├── contradiction_engine.py       # 矛盾检测 + 精准追问
│   ├── corporate_bs_detector.py      # 黑话检测 + 黑话翻译
│   ├── growth_advisor.py             # AI 时代成长路线
│   ├── growth_tracker.py             # 用户成长追踪
│   ├── internet_persona.py           # 互联网人格画像
│   ├── project_authenticity.py       # 项目真实性检测
│   └── self_review.py                # 残酷自评
├── components/
│   ├── ui.py                         # FastAPI Web 界面
│   └── styles.py                     # 暗色 CSS 主题
├── requirements.txt
└── pyproject.toml
```

## 架构设计

### 双层架构：规则引擎 + LLM

```
用户输入 → 规则引擎（即时/免费）→ 快速检测（秒出）
                ↓
          LLM 深度分析 → 结构化报告（有洞察）
```

- **规则层**：黑话检测、真实性检测的规则信号——不需要调 LLM，即时反馈
- **LLM 层**：JD 拆解、面试追问、面评生成——由 LLM 实时生成，零 Mock 数据

### 核心设计原则

1. **Prompt 是产品核心**，不是配置项。System Prompt 打磨了最长时间
2. **零 Mock 数据** — 所有分析结果由 LLM 实时生成
3. **JSON + Markdown 双输出** — 结构化数据给前端，渲染好的 Markdown 给人读
4. **模块化纯函数** — 每个模块可独立导入，不依赖任何特定平台
5. **规则引擎 + LLM 分层** — 快的用规则（免费即时），深的用 LLM（高质量有洞察）

### P8 面试官人格（System Prompt 核心）

```
禁止说：加油、努力、相信自己、提升专业能力
禁止模板化评价
禁止鸡汤

标志性表达：
- 「你的项目问题不是技术，是没有真实用户」
- 「你的 AI 停留在 Chat 层面，不是 Workflow 层面」
- 「面试官看到这句话会直接降低预期」
```

### 地狱面试模式 + 压力值系统

面试中的压力值不是随机数，是根据回答质量动态计算：

| 信号 | 压力变化 |
|------|---------|
| 模糊表达（我觉得/可能/大概） | +8 |
| 缺少数据支撑 | +6 |
| 黑话过量（3个以上） | +5 |
| 回答过短（<30字） | +10 |
| 防御性表达（"主要是团队"） | +7 |
| 坦率承认不足 | **-8** |
| 展示了深度思考 | -6 |
| 展示了 AI 工作流 | -4 |

地狱模式有 **1.5x** 压力乘数。

## 已知局限

| 问题 | 影响 | 计划 |
|------|------|------|
| 没有数据闭环 | 无法证明建议有效 | v3 最高优先级 |
| 面试追问靠 prompt 而非向量检索 | >30轮对话会退化 | 待向量化 |
| 黑话规则硬编码 | 无法识别新空话 | 待自进化 |
| 差异化护城河弱 | 复制成本低 | 需数据壁垒 |

## License

MIT
