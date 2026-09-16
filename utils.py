"""
Offer Copilot — Shared Utilities

Provides the callLlm function that dispatches prompts to the active LLM.
When running as a Trae Solo skill, the platform intercepts this
and processes the prompt directly. When running standalone, it attempts an
API call via the configured provider.
"""

import json
import os
import re
import time
from typing import Any, Union


def getLlmSettingsPath() -> str:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data")
    return os.path.join(base, "settings.json")


def loadLlmSettings() -> dict:
    """读取 user_data/settings.json 里的 AI 配置（Web 端「AI 设置」写入）。"""
    path = getLlmSettingsPath()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def saveLlmSettings(settings: dict) -> dict:
    base = os.path.dirname(getLlmSettingsPath())
    os.makedirs(base, exist_ok=True)
    current = loadLlmSettings()
    for k in ("api_key", "base_url", "model"):
        if settings.get(k):
            current[k] = str(settings[k]).strip()
    if "api_key" in settings and not settings.get("api_key"):
        current.pop("api_key", None)  # 显式清空
    with open(getLlmSettingsPath(), "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current


def getLlmConfig() -> dict:
    """
    合成最终生效的 LLM 配置：设置文件 > 环境变量。
    返回 {"api_key", "base_url", "model"}；base_url 兼容「根地址」和「完整 chat/completions 地址」。
    """
    saved = loadLlmSettings()
    api_key = saved.get("api_key") or os.environ.get("TRADE_API_KEY") or os.environ.get("LLM_API_KEY") or ""
    base_url = saved.get("base_url") or os.environ.get("LLM_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4"
    model = saved.get("model") or os.environ.get("LLM_MODEL") or "glm-4.6"
    return {"api_key": api_key, "base_url": base_url, "model": model}


def maskKey(key: str) -> str:
    if not key:
        return ""
    return key[:6] + "****" + key[-4:] if len(key) > 12 else "****"


def callLlm(prompt: str, system_prompt: str = "", output_format: str = "json") -> Union[dict, str]:
    """
    Call the LLM with a prompt and return structured output.

    In Trae Solo context, this function serves as a semantic marker —
    the platform processes the prompt with the active model.

    In standalone mode, attempts to use TRADE_API_KEY from env.

    Args:
        prompt: The main prompt to send
        system_prompt: System-level instructions
        output_format: Expected format — 'json', 'markdown', or 'text'

    Returns:
        Parsed dict if output_format='json', otherwise a string
    """
    # Standalone API mode (OpenAI-compatible: GLM / Kimi / DeepSeek / OpenAI ...)
    cfg = getLlmConfig()
    if cfg.get("api_key"):
        start = time.time()
        import httpx
        url = cfg["base_url"].rstrip("/")
        if not url.endswith("/chat/completions"):
            url = url + "/chat/completions"
        messages = []
        messages.append({"role": "system", "content": system_prompt or getSystemPrompt()})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": cfg["model"], "messages": messages, "max_tokens": 16384, "temperature": 0.6}
        # 智谱推理模型（glm-5.x）默认开思考，长 prompt 时思考 token 会吃光上限导致正文为空；
        # 报告类任务显式关闭（仅对智谱端点生效，其他厂商不传此参数）
        if "bigmodel.cn" in cfg["base_url"]:
            payload["thinking"] = {"type": "disabled"}
        resp = httpx.post(
            url,
            headers={"Authorization": "Bearer " + cfg["api_key"]},
            json=payload,
            timeout=httpx.Timeout(240.0, connect=10.0),
        )
        elapsed = (time.time() - start) * 1000
        resp.raise_for_status()
        data = resp.json()
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        if not text.strip():
            finish = choice.get("finish_reason", "?")
            reasoning = (data.get("usage", {}).get("completion_tokens_details", {}) or {}).get("reasoning_tokens")
            raise RuntimeError(
                f"模型返回空内容（finish_reason={finish}"
                + (f"，思考消耗 {reasoning} tokens" if reasoning else "")
                + "）。可在「AI 设置」换一个非推理模型（如 glm-4.6）重试。"
            )
        _logPerformance(len(prompt), elapsed, True)
        return parseResponse(text, output_format)

    # Fallback: return structured prompt for platform to process
    return {
        "_trait": "llm_call",
        "system": system_prompt or getSystemPrompt(),
        "prompt": prompt,
        "output_format": output_format,
    }


def _logPerformance(prompt_len: int, response_ms: float, success: bool) -> None:
    """Log LLM call performance to JSONL file."""
    try:
        from datetime import datetime
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "performance.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_length": prompt_len,
            "response_time_ms": round(response_ms, 2),
            "success": success,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def safeCallLlm(prompt: str, system_prompt: str = "", output_format: str = "json",
                fallback: dict = None, timeout: int = 60) -> Union[dict, str]:
    """
    Call LLM with exception handling and structured fallback.

    On failure, returns a fallback dict with error info and friendly retry hint.
    In Trae Solo mode, delegates to callLlm directly (platform handles execution).
    """
    apiKey = os.environ.get("TRADE_API_KEY") or os.environ.get("LLM_API_KEY")

    try:
        result = callLlm(prompt, system_prompt, output_format)
    except Exception as e:
        result = None
        if fallback is not None:
            fallback["_error"] = str(e)
            fallback["_retry_hint"] = "AI 调用失败：请到「AI 设置」检查 Key / 模型，或稍后重试"
            return fallback
        if output_format != "json":
            return f"[错误] LLM调用失败: {str(e)}。请重试或输入更短的文本。"
        return {
            "error": str(e),
            "markdown": "> ⚠️ AI 调用失败：" + str(e) + "\n>\n> 请到 Web 端「AI 设置」检查 Key / 模型，或稍后重试。"
        }

    # callLlm returned _trait marker — no real LLM call happened (no API key, not in Trae Solo)
    if isinstance(result, dict) and "_trait" in result:
        if fallback is not None:
            fallback["_error"] = "LLM未配置"
            fallback["_retry_hint"] = "还没有配置 AI：打开侧栏「AI 设置」填入 API Key 即可"
            return fallback
        return {
            "error": "LLM未配置",
            "markdown": "> ⚠️ 还没有配置 AI\n>\n> 打开 Web 端侧栏的「AI 设置」，填入 API Key 即可使用全部 AI 功能（支持 GLM / Kimi / DeepSeek / OpenAI 等任何 OpenAI 兼容接口）。"
        }

    return result


def parseResponse(text: str, fmt: str) -> Any:
    """Parse LLM response into requested format."""
    if fmt == "json":
        text = text.strip()
        # 优先取 ```json / ``` 围栏块（容错：只有开头没有闭合时取到结尾）
        m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, flags=re.DOTALL)
        if m:
            text = m.group(1).strip()
        else:
            i, j = text.find("{"), text.rfind("}")
            if i != -1:
                text = text[i:j + 1] if j > i else text[i:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            repaired = _repairTruncatedJson(text)
            if repaired is not None:
                return repaired
            return {"raw": text}
    return text


def _repairTruncatedJson(text: str) -> Any:
    """
    修复被 max_tokens 截断的 JSON：找到最后一个完整值的位置，裁掉残尾，再补齐未闭合的括号。
    输出会缺最后半截字段，但整体结构可用（报告类输出可接受）。
    """
    if "{" not in text and "[" not in text:
        return None
    stack = []
    in_str = False
    esc = False
    last_safe = 0
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()
            last_safe = i + 1
        elif ch == ",":
            last_safe = i
    if not stack and not in_str:
        return None
    cut = text[:last_safe].rstrip().rstrip(",")
    closes = {"{": "}", "[": "]"}
    for b in reversed(stack):
        cut += closes.get(b, "")
    try:
        return json.loads(cut)
    except json.JSONDecodeError:
        return None


def fetchInput(source: str) -> tuple[str, str]:
    """
    智能输入识别 — 支持三种 JD 输入方式：

    1. MD 文件路径    → 读取文件内容
    2. 网站 URL        → 抓取网页文本
    3. 直接粘贴 JD 文本 → 原样返回

    Args:
        source: 用户输入（文件路径 / URL / JD 文本）

    Returns:
        (content, sourceType) — content 是提取的文本，sourceType 是 'file'/'url'/'text'
    """
    source = source.strip()

    # 1. Detect file path: ends with .md / .txt / .json
    if source.endswith(('.md', '.txt', '.json', '.MD', '.TXT', '.JSON')):
        try:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read().strip(), 'file'
        except FileNotFoundError:
            pass  # Fall through — might just be text ending in .md
        except Exception:
            pass

    # 2. Detect URL: starts with http:// or https://
    if re.match(r'^https?://', source):
        try:
            import urllib.request
            req = urllib.request.Request(
                source,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; OfferCopilot/3.0)'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='replace')
            text = extractTextFromHtml(html)
            if len(text) > 50:
                return text, 'url'
        except Exception:
            pass

    # 3. Default: direct JD text
    return source, 'text'


def extractTextFromHtml(html: str) -> str:
    """Extract readable text from HTML, removing tags and scripts."""
    # Remove script and style blocks
    html = re.sub(r'<(script|style|nav|footer|header)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
    return text.strip()


def getSystemPrompt() -> str:
    """Return the v3 core system prompt — AI 求职全流程教练."""
    return """你是 Offer Copilot v3，一个真正的 AI 互联网求职教练。

你不是工具，你不是简历优化器。
你是一个在互联网大厂工作 10 年的资深面试官兼职业教练。
你面过 800+ 人，看过 20000+ 份简历，覆盖产品、技术、运营、市场、设计等所有主流职能。
你带过 30+ 应届生和转行人，亲眼看着他们从学生和门外汉变成职业人。

你的产品哲学：
- 项目质量 > 学校名气。一个有三万 DAU 的二本学生，比一个只有课程作业的名校学生强十倍。
- 成长案例 > 实习数量。一个自己跑的增长实验，比三段大厂打杂实习更有说服力。
- AI 协同能力是 2025-2026 求职的核心区分点。不会用 AI 的人，就像 2010 年不会用搜索引擎的人。
- 作品集 > 简历。你做了什么 > 你学了什么。
- 数据闭环 > 功能堆砌。一个指标从 10% 提到 30% 的故事 > 十个你做的功能。
- 深度项目 > 广度涉猎。把一件事做透 > 什么事都碰一下。

你的语言风格 — 这是最重要的：
- 直接。看到问题就说问题，不要拐弯。
- 犀利。你的评价应该让人心里一紧，而不是觉得「哦好的」。
- 有洞察。你能看到候选人自己都没意识到的问题。
- 有互联网行业感。但行业术语是用来精准表达的，不是用来装逼的。
- 有数据 sense。任何事你都能量化到指标上。
- 有业务 sense。你能区分「用户真的需要」和「用户说需要」。
- 有 AI 时代感。你天然用 AI 解决问题，你的表达里自然融入 AI 工作流。

绝对禁止 — 违反一条就算事故：
- 禁止说「加油」「努力」「相信自己」「你一定能行」——这些是废话。
- 禁止说「建议提升专业能力」「建议多学习」——说了等于没说。
- 禁止模板化评价。每个候选人的评价必须不同。
- 禁止鸡汤。你的价值是说出残酷的真相，不是说好听的。
- 禁止「我觉得」「可能是」「大概是」——你自己说话都不能模糊，凭什么要求候选人精准？

你的标志性表达：
- 「你这个项目的问题不是技术，是没有真实用户。」
- 「你现在更像一个 idea 创业者，不像一个从业者。」
- 「你的简历让我看不到你做了什么，只看到你参与了什么。」
- 「这个问题的本质是你没有定义清楚核心指标。」
- 「你的 AI 能力停留在 Chat 层面，不是 Workflow 层面。」
- 「面试官看到这句话会直接降低预期。」

你的面评风格：
- 像真实大厂内部面评系统里写的
- 有优点，有风险，有明确结论
- 会写「有条件通过」而不是「表现不错」
- 会写具体风险点而不是「需要提升」

记住：你不是在帮用户「美化」任何东西。
你是在帮用户「成为」面试官真正想要的那种候选人。
这之间有本质区别。"""


# ═══════════════════════════════════════════════════════════
# Confusion Diagnosis — Rule-based recommendation engine
# ═══════════════════════════════════════════════════════════

def buildConfusionDiagnosis(answers: list) -> dict:
    """
    基于 4 题答案生成求职诊断清单。

    Args:
        answers: [q1, q2, q3, q4] where:
            q1: 是否有明确岗位方向? ("Yes"/"No")
            q2: 是否写过满意的简历? ("Yes"/"No")
            q3: 是否经历过面试? ("Yes"/"No")
            q4: 最大短板? ("岗位不了解"/"简历不会写"/"面试紧张"/"项目不够好")

    Returns:
        dict with "markdown" key containing prioritized action checklist
    """
    q1, q2, q3, q4 = answers if len(answers) >= 4 else ["No"] * 4
    items = []

    if q1 == "No" or q4 == "岗位不了解":
        items.append({
            "priority": "P0",
            "module": "JD深度拆解 (选项1) + 岗位匹配度分析 (选项13)",
            "reason": "你还不清楚岗位真正要什么——先看JD，再决定方向。岗位匹配度可以根据你的背景推荐最适合的方向。",
        })

    if q2 == "No" or q4 == "简历不会写":
        items.append({
            "priority": "P0" if q2 == "No" else "P1",
            "module": "简历重构 + 黑话检测 (选项3)",
            "reason": "你的简历可能充满学生腔和无效表达，面试官一眼就刷掉。黑话检测能帮你发现学生腔。",
        })

    if q3 == "No" or q4 == "面试紧张":
        items.append({
            "priority": "P0" if q3 == "No" else "P1",
            "module": "模拟面试 - 温和模式 或 暖心模式 (选项4)",
            "reason": "没面过就先练。温和模式帮你适应面试节奏，暖心模式给你信心和具体反馈。",
        })

    if q4 == "项目不够好":
        items.append({
            "priority": "P0",
            "module": "项目真实性检测 (选项10) + 成长路线 (选项5)",
            "reason": "你的项目可能缺两个核心东西：真实用户和数据闭环。先用项目检测找问题，再用成长路线补课。",
        })

    # Always recommend
    items.append({
        "priority": "P2",
        "module": "互联网人格画像 (选项9)",
        "reason": "做完上述步骤后，用人格画像了解你的九维能力雷达图，知道哪里还需要补。",
    })
    items.append({
        "priority": "P2",
        "module": "投递看板 (选项15)",
        "reason": "从今天起每一次投递都记下来。求职是漏斗，不记录就永远不知道自己卡在哪一层。",
    })

    lines = [
        "# 🧭 求职迷茫诊断报告",
        "",
        "根据你的回答，以下是现阶段优先级最高的行动清单：",
        "",
        "| 优先级 | 建议使用的功能 | 原因 |",
        "|--------|---------------|------|",
    ]
    for item in sorted(items, key=lambda x: {"P0": 0, "P1": 1, "P2": 2}[x["priority"]]):
        emoji = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}[item["priority"]]
        lines.append(f"| {emoji} {item['priority']} | {item['module']} | {item['reason']} |")

    lines.extend([
        "",
        "> 按从上到下的顺序使用这些功能。每个功能的结果会自动保存到你的成长档案中。",
        "",
        "### 💡 下一步",
        "在 CLI 菜单输入对应的数字，或切换到对应的页面标签。",
        "",
    ])
    return {"markdown": "\n".join(lines)}


# ═══════════════════════════════════════════════════════════
# Growth Tracker Storage
# ═══════════════════════════════════════════════════════════

def getGrowthDataPath() -> str:
    """Get path for growth tracker storage file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "growth_data.json")


def loadGrowthData() -> dict:
    """Load persisted growth tracking data."""
    path = getGrowthDataPath()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": [], "users": {}}


def saveGrowthData(data: dict) -> None:
    """Persist growth tracking data."""
    try:
        with open(getGrowthDataPath(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
