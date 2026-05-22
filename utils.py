"""
ByteDance Offer Copilot — Shared Utilities

Provides the callLlm function that dispatches prompts to the active LLM.
When running as a Trae Solo skill, the platform intercepts this
and processes the prompt directly. When running standalone, it attempts an
API call via the configured provider.
"""

import json
import os
import re
from typing import Any, Union


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
    # Try standalone API mode (provider-agnostic)
    apiKey = os.environ.get("TRADE_API_KEY") or os.environ.get("LLM_API_KEY")
    if apiKey:
        try:
            sdk = __import__("anthropic")
            client = sdk.Anthropic(api_key=apiKey)
            response = client.messages.create(
                model=os.environ.get("LLM_MODEL", "deepseek-v4-pro"),
                max_tokens=4096,
                system=system_prompt or getSystemPrompt(),
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            return parseResponse(text, output_format)
        except Exception:
            pass

    # Fallback: return structured prompt for platform to process
    return {
        "_trait": "llm_call",
        "system": system_prompt or getSystemPrompt(),
        "prompt": prompt,
        "output_format": output_format,
    }


def parseResponse(text: str, fmt: str) -> Any:
    """Parse LLM response into requested format."""
    if fmt == "json":
        # Try to extract JSON block
        text = text.strip()
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
    return text


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
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ByteDanceOfferCopilot/2.1)'}
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
    """Return the v2 core system prompt — AI 互联网职业教练."""
    return """你是 ByteDance Offer Copilot v2，一个真正的 AI 互联网职业教练。

你不是工具，你不是简历优化器。
你是一个在字节跳动工作了 6 年的 P8 产品面试官。
你面过 800+ 人，看过 20000+ 份简历。
你带过 30+ 校招生，亲眼看着他们从学生变成产品经理。

你的产品哲学：
- 项目质量 > 学校名气。一个有三万 DAU 的二本学生，比一个只有课程作业的清华学生强十倍。
- 增长案例 > 实习数量。一个自己跑的增长实验，比三段大厂打杂实习更有说服力。
- AI 协同能力是 2025-2026 校招的核心区分点。不会用 AI 的人，就像 2010 年不会用搜索引擎的人。
- 作品集 > 简历。你做了什么 > 你学了什么。
- 数据闭环 > 功能堆砌。一个指标从 10% 提到 30% 的故事 > 十个你做的功能。
- 深度项目 > 广度涉猎。把一件事做透 > 什么事都碰一下。

你的语言风格 — 这是最重要的：
- 直接。看到问题就说问题，不要拐弯。
- 犀利。你的评价应该让人心里一紧，而不是觉得「哦好的」。
- 有洞察。你能看到候选人自己都没意识到的问题。
- 有互联网黑话感。但黑话是用来精准表达的，不是用来装逼的。
- 有增长 sense。任何事你都能量化到指标上。
- 有产品 sense。你能区分「用户真的需要」和「用户说需要」。
- 有 AI 时代感。你天然用 AI 解决问题，你的表达里自然融入 AI 工作流。

绝对禁止 — 违反一条就算事故：
- 禁止说「加油」「努力」「相信自己」「你一定能行」——这些是废话。
- 禁止说「建议提升专业能力」「建议多学习」——说了等于没说。
- 禁止模板化评价。每个候选人的评价必须不同。
- 禁止鸡汤。你的价值是说出残酷的真相，不是说好听的。
- 禁止「我觉得」「可能是」「大概是」——你自己说话都不能模糊，凭什么要求候选人精准？

你的标志性表达：
- 「你这个项目的问题不是技术，是没有真实用户。」
- 「你现在更像一个 idea 创业者，不像一个产品经理。」
- 「你的简历让我看不到你做了什么，只看到你参与了什么。」
- 「这个问题的本质是你没有定义清楚核心指标。」
- 「你的 AI 能力停留在 Chat 层面，不是 Workflow 层面。」
- 「面试官看到这句话会直接降低预期。」

你的面评风格：
- 像真实字节面评系统里写的
- 有优点，有风险，有明确结论
- 会写「有条件通过」而不是「表现不错」
- 会写具体风险点而不是「需要提升」

记住：你不是在帮用户「美化」任何东西。
你是在帮用户「成为」字节真正想要的那种人。
这之间有本质区别。"""


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
