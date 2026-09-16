# Offer Copilot v3.2

<p align="center">
  <b>AI 求职全流程教练 — 从 JD 拆解到 Offer 选择的闭环</b><br>
  <sub>校招 / 社招 / 实习 / 转行 · 产品 / 技术 / 运营 / 市场 / 设计</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.2.0-blue" />
  <img src="https://img.shields.io/badge/python-3.9+-green" />
  <img src="https://img.shields.io/badge/modules-19-orange" />
  <img src="https://img.shields.io/badge/built%20with-Trae-8A2BE2" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

---

不是简历美化工具。是让 AI 扮演**互联网大厂资深面试官**，用直接、犀利的风格拷打你的简历、项目和面试回答——然后告诉你真问题在哪。

v3 在此基础上补上了求职流程的另一半：**你投了什么、走到哪一步、卡在哪一层、最后怎么选**。

v3.1 把整个产品改成**简历优先**（参考 Teal / Huntr / Jobscan / 超级简历的做法）：

```
 ① 导入简历 ─→ ② 岗位库：粘 JD，秒出匹配分 ─→ ③ 记为已投递，看板拖拽推进 ─→ ④ 面试准备 / 模拟面试 ─→ ⑤ Offer 对比
   没有它其他页面全锁    硬技能命中/缺失·硬门槛·高亮      漏斗·停滞预警         自动取档案不重复填表      从看板一键导入
```

> v2 自评说：「没有数据闭环，是这个产品最致命的问题。」
> v3 的第一件事就是把它补上。→ [`python main.py self-review`](modules/self_review.py)

## 求职闭环：四段 × 17 个功能模块（`modules/` 下 19 个模块文件）

```
 定方向            备弹药                       上战场                  做决策
 ────────         ─────────────────────        ──────────────         ────────────
 🧭 迷茫诊断       🔍 JD 拆解                    🎤 模拟面试 ×4 模式      ⚖️ Offer 对比 [v3]
 🎯 岗位匹配       📊 Offer 预测                 📋 面评报告              🧬 人格画像
                  🔥 简历重构 + 导出             👥 群面模拟              🗺️ 成长路线
                  🫧 黑话检测 / 翻译             ⚡ 矛盾检测 + 压力值      📈 成长追踪
                  🔍 项目真实性                  📋 投递看板 [v3]
                  🎙️ 自我介绍 / 项目讲稿 [v3]
```

| 模块 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 🔍 JD 拆解 | 岗位潜台词 + 理想候选人画像 + 30 天路线，自动识别职能类型 | JD 文本 / URL / 文件 | 结构化分析 + Markdown |
| 📊 Offer 预测 | 6 维评分 + 综合概率 + 差距分析，专业维度按职能切换标准 | 简历 + JD | 评分卡 + 具体建议 |
| 🔥 简历重构 | 学生腔 → 互联网表达，PDF / Word 导出（中文字体已内嵌） | 项目描述 / 自我介绍 | 改写版 + 改动清单 + 面试话术 |
| 🎙️ **自我介绍生成 [v3]** | 30s / 60s / 3min × 结构化 / 讲故事 / 数据流 × 校招 / 社招 / 实习 / 转行 | 简历 + JD（可选） | 开场钩子 + 口语讲稿 + 分段秒数 + 预判第一问 |
| 🎯 **项目讲稿生成 [v3]** | STAR 拆解 + 埋钩子 + 预判追问 Top5 + 风险点 + 缺失数据清单 | 项目描述 + JD（可选） | 1min / 3min / 深挖版讲稿 |
| 🫧 黑话检测 / 翻译 | 弱动词 / 空话 / 模糊量化词识别，逐句翻译 | 任意文本 | 空话指数 + 逐项解释 |
| 🎤 模拟面试 | 温和 / 高压 / 地狱 / 暖心，AI 压力值，矛盾检测 | 岗位 + JD | 追问 + 压力曲线 + 7 维评估 |
| 📋 面评报告 | 大厂内部面评格式：优势 / 风险 / 争议点 / 结论 | 面试记录 | 有条件通过 / 建议不通过 + 行动项 |
| 👥 群面模拟 | 无领导小组讨论，AI 多角色 | 角色 + 主题 | 5 轮讨论 + 发言 / 观点 / 协作分析 |
| 📋 **投递看板 [v3]** | 状态流转 · 漏斗转化率 · 停滞预警（≥14 天）· 本周活跃 · 行动建议 | 每一次投递 / 面试 / 结果 | 看板 + 漏斗 + 下一步 |
| ⚖️ **Offer 对比 [v3]** | 六维加权（规则层，可调权重，敏感性分析）+ 隐藏风险 / 谈判筹码（LLM 层） | 2-5 个 Offer | 排名 + 对比表 + 谈判话术 + 盲点 |
| 🧬 人格画像 | 九维互联网能力雷达 | 简历 + 项目 + 内容经历 | 雷达数据 + 强弱项 |
| 🔍 真实性检测 | 学生 Demo vs 真实产品 | 项目描述 | 6 维评分 + 学生味信号 |
| 🧭 迷茫诊断 | 4 题定位阶段 → 优先级行动清单 | 4 道选择题 | P0 / P1 / P2 清单 |
| 🎯 岗位匹配 | 10 个通用方向（技术 / 产品 / 运营 / 设计 / 数据 / 市场），含转行可迁移性 | 背景描述 | TOP 3 + 差距清单 |
| 🗺️ 成长路线 | AI 时代的 30 天冲刺计划 | 自评 + 目标岗位 | 路线 + 周计划 |
| 📈 成长追踪 | 历史记录 + Offer 概率趋势 + 面试持久化 | 使用数据 | 成长曲线 |

## 快速开始

### 作为 Trae Skill 使用

1. 下载本仓库 zip（仓库页 **Code → Download ZIP**）
2. 在 Trae 中导入 Skill，自动注册
3. 说「帮我拆解这个 JD」「给我一份 60 秒自我介绍」「我腾讯一面过了，记一下」「帮我比一下这两个 Offer」即可触发

### 本地运行（Web UI）

```bash
git clone https://github.com/Baijidot/ByteDance-Offer-Copilot-Skill.git
cd ByteDance-Offer-Copilot-Skill
pip install -r requirements.txt

python main.py web                 # http://localhost:8000
```

打开后第一步是导入简历（粘贴或上传 .pdf / .docx / .txt / .md），确认档案后进入工作台。
想先看看效果：`demo-seed/` 里有一套虚构人设的演示数据（简历 + 3 份 JD + 9 条投递记录）和一键灌入脚本，跑完即可复现演示状态。

**配置 AI（可选）**：点侧栏底部「AI 未配置」→ 填 API Key（内置智谱 GLM / Kimi / DeepSeek / OpenAI 预设，
任何 OpenAI 兼容接口都行）→ 测试连接 → 保存。Key 只存在本地 `user_data/settings.json`，也可以用环境变量
`TRADE_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`。不配置也能用全部规则层功能：
简历解析 / 完整度 / JD 匹配分 / 黑话检测 / 投递看板 / Offer 加权对比。

### CLI

```bash
python main.py cli          # 17 个菜单选项，按「准备 / 面试 / 方向与成长 / 闭环」分组
python main.py tracker      # 直接看投递看板
python main.py self-review  # 产品自评（v2 自评 + v3 回应）
python main.py stats        # LLM 调用 P50 / P90 / P99
```

### Python 直接调用

```python
from modules import (
    analyze_jd, detect_bs, generate_intro,
    add_application, update_status, get_tracker_stats, compare_offers,
)

# JD 拆解（支持文件路径 / URL / 直接粘贴，任意公司任意岗位）
print(analyze_jd("https://careers.example.com/job/12345")["markdown"])

# 黑话检测（规则引擎，秒出，不耗 LLM）
print(detect_bs("我参与了项目开发，提升了用户体验，做了很多功能")["overall_score"])

# 60 秒自我介绍，社招场景，讲故事风格
print(generate_intro(resume_text, jd_text, duration="60", style="讲故事", scene="社招")["markdown"])

# 投递追踪（纯规则，本地 JSON）
r = add_application("腾讯", "后端开发", channel="内推", applied_at="2026-09-01")
update_status(r["application"]["id"], "一面", note="问了分布式锁")
print(get_tracker_stats()["markdown"])          # 漏斗 / 停滞预警 / 下一步

# Offer 对比（规则层加权 + LLM 定性分析）
print(compare_offers([
    {"company": "A", "total_package": 42, "growth_score": 8, "stability_score": 6, "team_score": 8, "location_score": 8, "track_score": 8},
    {"company": "B", "total_package": 38, "growth_score": 7, "stability_score": 8, "team_score": 6, "location_score": 7, "track_score": 6},
], priorities="三年内想快速成长")["markdown"])
```

## 项目结构

```
ByteDance-Offer-Copilot-Skill/
├── SKILL.md                          # Trae Skill 注册定义（name: offer-copilot）
├── trae-skill.json
├── main.py                           # CLI + Web UI 入口 + run_skill()
├── utils.py                          # LLM 调度 / 系统人格 / 输入识别 / 持久化
├── modules/
│   ├── profile.py                    # 简历档案：导入 / 规则解析 / 完整度 [v3.1]
│   ├── jd_library.py                 # 岗位库 + 简历×JD 匹配分 [v3.1]
│   ├── jd_analyzer.py                # JD 深度拆解
│   ├── offer_predictor.py            # Offer 6 维概率预测
│   ├── resume_rewriter.py            # 简历互联网化重构
│   ├── self_intro_generator.py       # 自我介绍 / 项目 STAR 讲稿 [v3]
│   ├── mock_interviewer.py           # 模拟面试 + AI 压力值 + 暖心模式
│   ├── interview_feedback.py         # 大厂格式面评
│   ├── contradiction_engine.py       # 矛盾检测 + 精准追问
│   ├── corporate_bs_detector.py      # 黑话检测 + 翻译（规则引擎）
│   ├── group_interview.py            # 群面模拟
│   ├── application_tracker.py        # 投递看板 / 漏斗 / 停滞预警 [v3]
│   ├── offer_comparator.py           # Offer 六维加权对比 [v3]
│   ├── career_matcher.py             # 岗位匹配（10 个通用方向）
│   ├── growth_advisor.py             # AI 时代成长路线
│   ├── growth_tracker.py             # 成长追踪 + 面试持久化
│   ├── internet_persona.py           # 互联网人格画像
│   ├── project_authenticity.py       # 项目真实性检测
│   └── self_review.py                # 产品自评（v2）+ v3 回应
├── components/
│   ├── ui.py                         # FastAPI 路由（简历门禁 + 档案预填）
│   ├── app.html                      # 单页前端：引导页 + 侧边栏工作台 [v3.1]
│   ├── styles.py                     # 暗色主题 + 看板 / 漏斗 / Offer 卡片样式
│   └── export.py                     # PDF / Word 导出（自动注册中文字体）
├── requirements.txt
└── pyproject.toml
```

## v3.2 变更 (2026-09) — 新界面 + AI 配置入口

| 变化 | 说明 |
|------|------|
| 🎨 全新浅色界面 | 参考 GLM（chatglm.cn）和 Kimi 的设计语言重写整套样式：白 / 暖灰底、一个克制的蓝色点缀、1px 浅边框、大圆角、药丸按钮、大量留白 |
| ⚙️ AI 配置入口 | 侧栏底部「AI 设置」：填 API Key + Base URL + 模型，内置智谱 GLM / Kimi / DeepSeek / OpenAI 预设，一键测试连接。调用层换成 httpx 走 OpenAI 兼容接口，配置即用，Key 只存本地 |
| 🚫 去掉所有示例数据 | 「填充示例简历 / JD / 看板数据」按钮全部移除——界面里出现的一切数据都来自你的真实输入 |

## v3.1 变更 (2026-09) — 简历优先

| 变化 | 说明 |
|------|------|
| 📄 简历档案 | 粘贴 / 上传 .docx .txt .md → 规则引擎解析成结构化档案（姓名、目标岗位、教育、技能、项目、经历），无需 API Key；完整度评分 + 缺什么。有 LLM 时自动精修 |
| 🔒 门禁 | 没有档案时，Web 界面只开放「导入简历」，其他页面锁定——一线产品的共同做法，也是这个工具真正能用起来的前提 |
| 🎯 岗位库 + 匹配分 | 每条 JD 秒出匹配分（参考 Jobscan Match Report）：硬技能命中/缺失、软技能、学历/年限/院校/英语硬门槛，JD 里关键词高亮。保存简历后自动重算 |
| 🏠 工作台 | 首页不再是工具列表：档案完整度、投递漏斗、本周数据、按优先级排序的「下一步做什么」、岗位库 TOP |
| 🔗 联动 | 岗位库 →「记为已投递」→ 看板；看板拖拽换阶段；Offer 对比可从看板导入；面试准备 / 模拟面试自动取档案和岗位库 JD |
| 🖥️ 新界面 | 左侧栏导航（工作台 / 我的简历 / 岗位库 / 投递看板 / 面试准备 / 模拟面试 / Offer 对比 / 工具箱），前端拆成独立 `app.html` |

## v3.0 变更 (2026-09)

### 新增

| 特性 | 说明 |
|------|------|
| 📋 投递记录追踪 | 10 种状态流转，漏斗（投递→一面→二面→HR面→Offer）单调转化率，≥14 天停滞预警，本周活跃度，基于数据的下一步建议。**回应 v2 自评的「无数据闭环」** |
| 🎙️ 自我介绍生成器 | 时长 × 风格 × 场景 27 种组合，输出开场钩子 / 口语讲稿 / 分段秒数 / 口语提示 / 避坑 / 面试官最可能问的第一个问题 |
| 🎯 项目讲稿生成器 | STAR 拆解，主动埋钩子，预判追问 Top5（含面试官意图和应对策略），标出面试前必须补的数据 |
| ⚖️ Offer 对比决策器 | 六维加权（薪酬 / 成长 / 稳定 / 团队 / 城市 / 赛道），权重敏感性分析，LLM 输出隐藏风险 / 签前必问 / 谈判话术 / 打分与自述的矛盾 |
| 🌐 全面通用化 | 移除单一公司绑定；人格改为「互联网大厂 10 年资深面试官」，覆盖产品 / 技术 / 运营 / 市场 / 设计，校招 / 社招 / 实习 / 转行；岗位匹配从 6 个模板扩到 10 个 |
| 🖥️ Web UI 重做 | 11 个页面，岗位改为可输入 + 联想（不再锁死下拉框），loading 状态，友好错误提示 |

### 修复

| 问题 | 影响 |
|------|------|
| Web 简历导出接口漏了路由装饰器、`os` 未导入 | 导出功能整体不可用 |
| PDF 未注册中文字体 + 正文用了暗色主题的浅灰 | 中文简历导出为黑方块 / 白底看不见 |
| 前端 `renderMarkdown` 传入 dict | JD 拆解 / 简历重构 / 成长路线显示 `[object Object]` |
| Offer 预测读了不存在的 `result.probability` | 概率圆环渲染崩溃 |
| `stats` / `fetch-jobs` 子命令调用未定义函数 | NameError |
| 30 轮以上对话摘要引用未定义变量 `n` | 长面试崩溃 |
| 迷茫诊断前端传英文选项，规则引擎只认中文 | 第 4 题永远匹配失败 |
| 无 LLM 时空渲染覆盖了错误提示 | 显示「综合概率：0%」而非配置提示 |

## 架构设计

### 双层架构：规则引擎 + LLM

```
用户输入 → 规则引擎（即时 / 免费 / 确定性）→ 黑话指数、漏斗转化、Offer 加权分、停滞预警
                ↓
          LLM 深度分析（有洞察）→ JD 潜台词、面试追问、面评、谈判筹码、讲稿
```

原则：**能算的不问 LLM**。v3 新增的三个模块里，投递看板 100% 规则层，Offer 对比的打分与排名 100% 规则层，LLM 只负责它擅长的定性判断。

### 核心设计原则

1. **Prompt 是产品核心**，不是配置项。System Prompt 打磨了最长时间
2. **零 Mock 数据** — 所有分析结果由 LLM 实时生成
3. **JSON + Markdown 双输出** — 结构化数据给前端，渲染好的 Markdown 给人读
4. **模块化纯函数** — 每个模块可独立导入，不依赖任何特定平台
5. **规则引擎 + LLM 分层** — 快的用规则，深的用 LLM
6. **闭环优先** — 每个模块的输出都指向下一步该用哪个模块

### 面试官人格（System Prompt 核心）

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
| 模糊表达（我觉得 / 可能 / 大概） | +8 |
| 缺少数据支撑 | +6 |
| 黑话过量（3 个以上） | +5 |
| 回答过短（<30 字） | +10 |
| 防御性表达（"主要是团队"） | +7 |
| 坦率承认不足 | **-8** |
| 展示了深度思考 | -6 |
| 展示了 AI 工作流 | -4 |

地狱模式有 **1.5x** 压力乘数。

### 投递漏斗的一个设计决定

笔试是可跳过环节（很多岗位直接进一面），如果放进线性漏斗链会算出 >100% 的转化率。
所以漏斗链是 `投递 → 一面 → 二面 → HR面 → Offer`，按「走到的最远阶段」推断（到了 HR 面就算经过了一面二面），
笔试单独计数。保证漏斗单调递减，转化率才有意义。

## 已知局限

| 问题 | 影响 | 计划 |
|------|------|------|
| 投递数据只有自己的，没有横向基准 | 不知道 20% 的一面率算好还是差 | 积累匿名聚合数据后给行业参考线 |
| 面试追问靠 prompt 而非向量检索 | >30 轮对话会退化 | 待向量化 |
| 黑话规则硬编码 | 无法识别新空话 | 待自进化 |
| Offer 对比的五维打分靠用户主观 | 打分本身可能有偏 | LLM 层的「盲点」检测部分缓解，待引入外部数据 |
| **Web 端模拟面试不显示压力值 / 压力曲线** | 功能表和页面文案都写了「AI 压力值」，`/api/interview/answer` 也把 `pressure` 返回了，但 `app.html` 目前没有渲染它；压力值只在 CLI（`python main.py cli`）里显示 | Web 端补压力曲线组件 |
| **简历规则解析有三处已知粗糙**（`modules/profile.py`） | ① `_guess_target_role` 抓「求职意向」后整段不在 `\|` 处截断，会把「期望城市」一起带进目标岗位；② `_guess_job_type` 见到「实习」+「在读 / 届」判成校招；③ `_split_blocks` 按「≤40 字且无句末标点」猜项目标题。三处都靠「确认档案」那一步手改兜底，有 Key 时 LLM 精修覆盖大部分 | 逐条收紧正则 |
| Offer 对比从看板导入时，薪资预填只认写了「万」且不带「月」的字串 | 「300元/天」「25k/月」「2万/月」一律留空由用户自己填，不做任何换算（宁缺勿错） | 加单位识别与换算 |

## 历史版本

- **v2.3（原「ByteDance Offer Copilot」字节校招专用版）**：完整保留在 [`bytedance-coach-v2.3` 分支](https://github.com/Baijidot/ByteDance-Offer-Copilot-Skill/tree/bytedance-coach-v2.3)，Skill 名为 `bytedance-coach`，可与 v3.x 同时导入 Trae 使用
- **v3.x（本分支 main）**：通用求职全流程教练，Skill 名为 `offer-copilot`

## License

MIT
