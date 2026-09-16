"""
CSS Styles — Offer Copilot v3.2
Light minimal theme, referencing chatglm.cn / kimi.com:
white & warm-gray surfaces, one restrained blue accent, 1px borders,
large radii, pill buttons, generous whitespace.
"""

CSS = """
/* ===== Offer Copilot — Light Design System (GLM / Kimi style) ===== */

:root {
    --bg-page: #f7f7f8;
    --bg-sidebar: #f7f7f8;
    --bg-card: #ffffff;
    --bg-secondary: #f2f3f5;
    --bg-input: #ffffff;
    --bg-code: #f2f3f5;
    --bg-card-hover: #f7f7f8;
    --border-default: #e8e8ec;
    --border-hover: #d8d9e0;
    --text-primary: #17171c;
    --text-secondary: #55555f;
    --text-muted: #9a9aa3;
    --accent: #3b5bfd;
    --accent-hover: #2f4ce6;
    --accent-soft: #eef1ff;
    --text-accent: #3b5bfd;
    --success: #16a34a;
    --warning: #d97706;
    --danger: #dc2626;
    --info: #3b5bfd;
    --radius-sm: 10px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow-sm: 0 1px 2px rgba(23, 23, 28, 0.04);
    --shadow-md: 0 4px 16px rgba(23, 23, 28, 0.07);
    --shadow-lg: 0 12px 40px rgba(23, 23, 28, 0.14);
    --font-sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
}

* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    background: var(--bg-page);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

h1 { font-size: 26px; font-weight: 700; letter-spacing: -0.01em; }
h2 { font-size: 19px; font-weight: 600; }
h3 { font-size: 16px; font-weight: 600; }
hr { border: none; border-top: 1px solid var(--border-default); margin: 16px 0; }

/* ===== Layout ===== */

.app-container { max-width: 1080px; margin: 0 auto; padding: 0 24px 60px; }

/* ===== App shell (sidebar + main) ===== */

.shell {
    display: grid;
    grid-template-columns: 248px 1fr;
    min-height: 100vh;
}

.sidebar {
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-default);
    padding: 20px 14px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 17px;
    color: var(--text-primary);
    padding: 4px 8px;
    letter-spacing: -0.01em;
}

.brand .brand-ver { font-size: 11px; color: var(--text-muted); font-weight: 500; margin-left: auto; }

.profile-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    background: var(--bg-card);
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
}

.profile-chip:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.profile-chip .pc-name { font-size: 13px; font-weight: 600; color: var(--text-primary); line-height: 1.3; }
.profile-chip .pc-role { font-size: 11px; color: var(--text-muted); }
.profile-chip.empty { border-style: dashed; background: transparent; }
.profile-chip.empty .pc-name { color: var(--text-secondary); }

.ring {
    --p: 0;
    --c: var(--accent);
    width: 40px; height: 40px; flex: none;
    border-radius: 50%;
    background: conic-gradient(var(--c) calc(var(--p) * 1%), var(--bg-secondary) 0);
    display: grid; place-items: center;
    font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--text-primary);
    position: relative;
}
.ring::before { content: ""; position: absolute; width: 30px; height: 30px; border-radius: 50%; background: var(--bg-card); }
.ring span { position: relative; }
.ring.lg { width: 92px; height: 92px; font-size: 21px; }
.ring.lg::before { width: 72px; height: 72px; }
.ring.md { width: 56px; height: 56px; font-size: 14px; }
.ring.md::before { width: 42px; height: 42px; }
.ring.low { --c: var(--danger); }
.ring.mid { --c: var(--warning); }
.ring.high { --c: var(--success); }

.side-nav { display: flex; flex-direction: column; gap: 2px; }

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    font-size: 14px;
    cursor: pointer;
    border: none;
    background: transparent;
    text-align: left;
    width: 100%;
    font-family: var(--font-sans);
    transition: background 0.15s, color 0.15s;
}

.nav-item:hover { background: #ececf1; color: var(--text-primary); }
.nav-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.nav-item.locked { color: var(--text-muted); cursor: not-allowed; }
.nav-item.locked:hover { background: transparent; color: var(--text-muted); }
.nav-item .nav-lock { margin-left: auto; font-size: 12px; opacity: 0.7; }
.nav-item .nav-badge { margin-left: auto; font-size: 11px; background: var(--bg-card); padding: 1px 8px; border-radius: 10px; color: var(--text-muted); border: 1px solid var(--border-default); }
.nav-item.active .nav-badge { background: #fff; color: var(--accent); border-color: transparent; }
.nav-group { font-size: 11px; color: var(--text-muted); letter-spacing: 0.06em; padding: 12px 12px 4px; }

.sidebar-foot { margin-top: auto; font-size: 12px; color: var(--text-muted); padding: 8px 6px; display: flex; flex-direction: column; gap: 6px; }
.sidebar-foot .sf-row { display: flex; align-items: center; gap: 8px; }
.sidebar-foot a { color: var(--text-muted); }
.sidebar-foot a:hover { color: var(--accent); }

.ai-chip {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px; border-radius: var(--radius-sm);
    background: var(--bg-card); border: 1px solid var(--border-default);
    cursor: pointer; font-size: 12px; color: var(--text-secondary);
    transition: border-color 0.15s;
}
.ai-chip:hover { border-color: var(--border-hover); }
.ai-chip .ai-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--danger); flex: none; }
.ai-chip.on .ai-dot { background: var(--success); }

.main { padding: 28px 36px 60px; max-width: 1240px; width: 100%; }
.page { display: none; }
.page.active { display: block; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.page-head h1 { font-size: 24px; margin: 0 0 4px; }
.page-head p { color: var(--text-secondary); margin: 0; font-size: 14px; }
.page-head .head-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-main-side { display: grid; grid-template-columns: 1.6fr 1fr; gap: 16px; }
.dash-grid { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 16px; margin-bottom: 16px; }

/* ===== Cards ===== */

.card {
    background: var(--bg-card);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 20px;
    box-shadow: var(--shadow-sm);
}

.card h3 { margin-top: 0; font-size: 15px; }
.card .card-sub { color: var(--text-muted); font-size: 13px; margin-top: -6px; margin-bottom: 12px; }

/* ===== Forms ===== */

.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
.form-group { margin-bottom: 12px; }
.form-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.form-input, .form-textarea, .form-select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    background: var(--bg-input);
    color: var(--text-primary);
    font-size: 14px;
    font-family: var(--font-sans);
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.form-input:focus, .form-textarea:focus, .form-select:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
}
.form-textarea { resize: vertical; min-height: 90px; line-height: 1.6; }
.form-select { appearance: auto; }

/* ===== Buttons ===== */

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 9px 18px;
    border-radius: 999px;
    border: 1px solid transparent;
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
    font-family: var(--font-sans);
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
}
.btn:hover { background: #e9eaee; }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-primary {
    background: var(--text-primary);
    color: #fff;
}
.btn-primary:hover { background: #000; }

.btn-secondary {
    background: var(--bg-card);
    border-color: var(--border-default);
    color: var(--text-primary);
}
.btn-secondary:hover { border-color: var(--border-hover); background: var(--bg-card); box-shadow: var(--shadow-sm); }

.btn-danger {
    background: var(--bg-card);
    border-color: var(--border-default);
    color: var(--danger);
}
.btn-danger:hover { border-color: var(--danger); }

.btn-lg { padding: 12px 26px; font-size: 15px; }
.btn-block { width: 100%; }

/* ===== Alerts / tags / chips ===== */

.alert { padding: 12px 16px; border-radius: var(--radius-md); font-size: 13px; margin-bottom: 14px; display: flex; align-items: flex-start; gap: 8px; }
.alert-info { background: var(--accent-soft); color: var(--text-primary); }
.alert-warning { background: #fdf3e3; color: #8a5a00; }
.alert-danger { background: #fdeaea; color: var(--danger); }

.tag { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }
.tag-success { background: #e8f6ee; color: var(--success); }
.tag-warning { background: #fdf3e3; color: var(--warning); }
.tag-danger { background: #fdeaea; color: var(--danger); }
.tag-info { background: var(--accent-soft); color: var(--accent); }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 12px; padding: 3px 10px; border-radius: 999px; background: var(--bg-secondary); border: 1px solid var(--border-default); color: var(--text-secondary); }
.chip.ok { background: #e8f6ee; color: var(--success); border-color: transparent; }
.chip.miss { background: #fdeaea; color: var(--danger); border-color: transparent; }
.chip.warn { background: #fdf3e3; color: var(--warning); border-color: transparent; }

/* ===== Onboarding ===== */

.onboard { max-width: 860px; margin: 0 auto; }
.steps { display: flex; gap: 8px; margin: 8px 0 24px; }
.step { flex: 1; padding: 10px 12px; border-radius: var(--radius-md); background: var(--bg-secondary); border: 1px solid transparent; font-size: 13px; color: var(--text-muted); display: flex; gap: 8px; align-items: center; }
.step .step-n { width: 22px; height: 22px; border-radius: 50%; background: var(--bg-card); border: 1px solid var(--border-default); display: grid; place-items: center; font-size: 12px; font-weight: 700; flex: none; }
.step.active { border-color: var(--accent); color: var(--text-primary); }
.step.active .step-n { background: var(--accent); color: #fff; border-color: var(--accent); }
.step.done { color: var(--success); }
.step.done .step-n { background: var(--success); color: #fff; border-color: var(--success); }

.dropzone {
    border: 2px dashed var(--border-hover);
    border-radius: var(--radius-md);
    padding: 18px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    background: var(--bg-card);
    transition: border-color 0.15s, background 0.15s;
}
.dropzone:hover, .dropzone.over { border-color: var(--accent); background: var(--accent-soft); }
.dropzone input { display: none; }

.list-editor .le-item { border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 10px; margin-bottom: 8px; background: var(--bg-secondary); position: relative; }
.list-editor .le-item .form-input { margin-bottom: 6px; font-weight: 600; background: var(--bg-card); }
.list-editor .le-item .form-textarea { min-height: 70px; font-size: 13px; background: var(--bg-card); }
.list-editor .le-remove { position: absolute; top: 8px; right: 8px; background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; }
.list-editor .le-remove:hover { color: var(--danger); }

details.raw-toggle summary { cursor: pointer; color: var(--text-muted); font-size: 12px; margin: 8px 0; }
details.raw-toggle[open] summary { margin-bottom: 8px; }

/* ===== JD library ===== */

.jd-card { border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 14px; background: var(--bg-card); display: grid; grid-template-columns: 56px 1fr auto; gap: 14px; align-items: center; cursor: pointer; margin-bottom: 10px; transition: border-color 0.15s, box-shadow 0.15s; }
.jd-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.jd-card.active { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.jd-card .jd-title { font-weight: 600; color: var(--text-primary); font-size: 14px; }
.jd-card .jd-company { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.jd-card .jd-actions { display: flex; gap: 6px; }

.score-badge { display: inline-flex; align-items: center; justify-content: center; min-width: 40px; height: 26px; padding: 0 10px; border-radius: 999px; font-family: var(--font-mono); font-size: 13px; font-weight: 700; background: var(--bg-secondary); color: var(--text-secondary); }
.score-badge.high { background: #e8f6ee; color: var(--success); }
.score-badge.mid { background: #fdf3e3; color: var(--warning); }
.score-badge.low { background: #fdeaea; color: var(--danger); }

mark.kw { background: #eef1ff; color: var(--text-primary); border-radius: 3px; padding: 0 2px; }
mark.kw.hit { background: #e8f6ee; }
mark.kw.miss { background: #fdeaea; }
.jd-text { white-space: pre-wrap; font-size: 13px; line-height: 1.75; color: var(--text-secondary); max-height: 420px; overflow-y: auto; padding: 14px; background: var(--bg-secondary); border-radius: var(--radius-sm); }

/* ===== Dashboard ===== */

.next-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.next-list li { padding: 10px 12px; background: var(--bg-secondary); border-radius: var(--radius-sm); font-size: 13px; color: var(--text-secondary); border-left: 3px solid var(--border-hover); }
.next-list li.p0 { border-left-color: var(--danger); }
.next-list li.p1 { border-left-color: var(--warning); }
.next-list li.p2 { border-left-color: var(--success); }
.next-list li:hover { background: #ececf1; }

.stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 16px; }
.stat-box { background: var(--bg-secondary); border-radius: var(--radius-md); padding: 14px; text-align: center; }
.stat-box .sb-value { font-size: 24px; font-weight: 700; color: var(--text-primary); font-family: var(--font-mono); }
.stat-box .sb-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.funnel { display: flex; flex-direction: column; gap: 8px; margin: 12px 0 20px; }
.funnel-row { display: grid; grid-template-columns: 90px 1fr 110px; align-items: center; gap: 12px; font-size: 13px; }
.funnel-row .funnel-bar { height: 22px; background: var(--bg-secondary); border-radius: 999px; overflow: hidden; }
.funnel-row .funnel-fill { height: 100%; background: var(--accent); border-radius: 999px; transition: width 0.4s ease; }
.funnel-row .funnel-num { color: var(--text-secondary); text-align: right; font-family: var(--font-mono); font-size: 12px; }

/* ===== Kanban ===== */

.kanban { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 16px; }
.kanban-board { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; margin-top: 12px; }
.kanban-board .kanban-col { min-width: 224px; max-width: 260px; flex: 1 0 224px; }

.kanban-col { background: var(--bg-secondary); border: 1px solid transparent; border-radius: var(--radius-md); padding: 10px; min-height: 80px; }
.kanban-col.drag-over { border-color: var(--accent); background: var(--accent-soft); }
.kanban-col-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 0 4px; }
.kanban-col-title .col-count { background: var(--bg-card); padding: 0 8px; border-radius: 10px; font-size: 11px; color: var(--text-muted); }

.kanban-card { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 10px 12px; margin-bottom: 8px; font-size: 13px; transition: border-color 0.15s, box-shadow 0.15s; }
.kanban-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.kanban-card.stale { border-left: 3px solid var(--warning); }
.kanban-card.offer { border-left: 3px solid var(--success); }
.kanban-card.dead { opacity: 0.55; }
.kanban-card[draggable=true] { cursor: grab; }
.kanban-card.dragging { opacity: 0.4; }

.kanban-card .kc-title { font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.kanban-card .kc-meta { color: var(--text-muted); font-size: 12px; margin-bottom: 8px; line-height: 1.5; }
.kanban-card .kc-actions { display: flex; gap: 6px; align-items: center; }
.kanban-card .kc-actions select { flex: 1; font-size: 12px; padding: 4px 6px; border: 1px solid var(--border-default); border-radius: 8px; background: var(--bg-card); color: var(--text-secondary); font-family: var(--font-sans); }
.kanban-card .kc-actions button { font-size: 12px; padding: 4px 9px; }

/* ===== Prep / interview ===== */

.sub-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.sub-tab { padding: 7px 16px; border-radius: 999px; border: 1px solid var(--border-default); background: var(--bg-card); color: var(--text-secondary); font-size: 13px; cursor: pointer; font-family: var(--font-sans); transition: all 0.15s; }
.sub-tab:hover { border-color: var(--border-hover); }
.sub-tab.active { background: var(--text-primary); color: #fff; border-color: var(--text-primary); }

.chat-container { display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg); height: 520px; overflow: hidden; }
.chat-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; border-bottom: 1px solid var(--border-default); }
.chat-mode-badge { padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.chat-mode-badge.mild { background: #e8f6ee; color: var(--success); }
.chat-mode-badge.hard { background: #fdf3e3; color: var(--warning); }
.chat-mode-badge.hell { background: #fdeaea; color: var(--danger); }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.chat-message { display: flex; gap: 10px; max-width: 85%; }
.chat-message.interviewer { align-self: flex-start; }
.chat-message.candidate { align-self: flex-end; flex-direction: row-reverse; }
.chat-avatar { width: 34px; height: 34px; border-radius: 50%; background: var(--bg-secondary); display: grid; place-items: center; font-size: 16px; flex: none; }
.chat-bubble { padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.chat-message.interviewer .chat-bubble { background: var(--bg-secondary); color: var(--text-primary); border-top-left-radius: 4px; }
.chat-message.candidate .chat-bubble { background: var(--accent); color: #fff; border-top-right-radius: 4px; }
.chat-input-area { display: flex; gap: 10px; padding: 14px 16px; border-top: 1px solid var(--border-default); }
.chat-input { flex: 1; padding: 11px 16px; border: 1px solid var(--border-default); border-radius: 999px; font-size: 14px; outline: none; font-family: var(--font-sans); background: var(--bg-input); color: var(--text-primary); }
.chat-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }

/* ===== Result panel / markdown ===== */

.result-panel { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg); padding: 28px; margin-top: 24px; }
.result-panel.visible { display: block; }

.markdown-content { font-size: 14px; line-height: 1.75; color: var(--text-primary); }
.markdown-content h1 { font-size: 20px; margin: 20px 0 12px; }
.markdown-content h2 { font-size: 17px; margin: 18px 0 10px; }
.markdown-content h3 { font-size: 15px; margin: 14px 0 8px; }
.markdown-content p { margin: 8px 0; }
.markdown-content ul { padding-left: 20px; margin: 8px 0; }
.markdown-content li { margin: 4px 0; }
.markdown-content blockquote { margin: 10px 0; padding: 8px 14px; border-left: 3px solid var(--accent); background: var(--accent-soft); border-radius: 0 8px 8px 0; color: var(--text-primary); }
.markdown-content code { background: var(--bg-code); padding: 2px 6px; border-radius: 6px; font-family: var(--font-mono); font-size: 12.5px; }
.markdown-content strong { font-weight: 700; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
th, td { padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--border-default); }
th { font-weight: 600; color: var(--text-secondary); background: var(--bg-secondary); }
tr:hover td { background: var(--bg-card-hover); }

/* ===== Score / dimensions ===== */

.score-circle { width: 110px; height: 110px; border-radius: 50%; border: 3px solid; margin: 0 auto; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.score-value { font-size: 30px; font-weight: 700; font-family: var(--font-mono); }
.score-label { font-size: 12px; color: var(--text-muted); }

.dimension-list { display: flex; flex-direction: column; gap: 12px; }
.dimension-item { display: flex; align-items: center; gap: 12px; }
.dimension-name { width: 130px; font-size: 13px; color: var(--text-secondary); flex: none; }
.dimension-bar-wrap { flex: 1; height: 10px; background: var(--bg-secondary); border-radius: 999px; overflow: hidden; }
.dimension-bar-fill { height: 100%; border-radius: 999px; transition: width 0.3s; }
.dimension-score { font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary); flex: none; }

/* ===== Offer comparator ===== */

.offer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 16px; }
.offer-card { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 16px; position: relative; }
.offer-card:hover { box-shadow: var(--shadow-sm); }
.offer-card .oc-remove { position: absolute; top: 10px; right: 10px; background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 16px; }
.offer-card .oc-remove:hover { color: var(--danger); }
.offer-card .form-group { margin-bottom: 10px; }
.offer-card .form-label { font-size: 12px; }
.offer-card .form-input { padding: 8px 10px; font-size: 13px; }

.slider-row { display: grid; grid-template-columns: 90px 1fr 32px; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; }
.slider-row input[type=range] { width: 100%; accent-color: var(--accent); }
.slider-row .sr-val { text-align: right; font-family: var(--font-mono); color: var(--accent); }

.weight-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px 24px; margin: 8px 0 16px; }

.rank-list { display: flex; flex-direction: column; gap: 10px; margin: 16px 0 24px; }
.rank-row { display: grid; grid-template-columns: 36px 1fr 60px; align-items: center; gap: 12px; }
.rank-row .rank-medal { font-size: 20px; text-align: center; }
.rank-row .rank-bar { height: 30px; background: var(--bg-secondary); border-radius: 999px; overflow: hidden; position: relative; }
.rank-row .rank-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.rank-row .rank-name { position: absolute; left: 14px; top: 0; height: 100%; display: flex; align-items: center; font-size: 13px; font-weight: 600; color: var(--text-primary); }
.rank-row .rank-score { font-family: var(--font-mono); text-align: right; color: var(--accent); font-weight: 600; }

/* ===== Tools ===== */

.tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.tool-card { border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 16px; background: var(--bg-card); cursor: pointer; transition: all 0.15s; }
.tool-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.tool-card.active { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.tool-card .tc-title { font-weight: 600; font-size: 14px; color: var(--text-primary); }
.tool-card .tc-desc { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

/* ===== Misc ===== */

.emoji-icon { font-size: 18px; }
.hint { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
.empty-state { text-align: center; color: var(--text-muted); padding: 32px 16px; font-size: 13px; }
.empty-state b { color: var(--text-secondary); }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: var(--text-primary); color: #fff; padding: 10px 18px; border-radius: 999px; font-size: 13px; box-shadow: var(--shadow-lg); z-index: 2000; opacity: 0; transition: opacity 0.2s; pointer-events: none; }
.toast.show { opacity: 1; }

.loading { display: flex; align-items: center; justify-content: center; padding: 40px; color: var(--text-muted); gap: 10px; }
.loading-spinner { width: 20px; height: 20px; border: 2px solid var(--border-default); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== Settings modal ===== */

.modal-backdrop { position: fixed; inset: 0; background: rgba(23, 23, 28, 0.4); display: flex; align-items: center; justify-content: center; z-index: 3000; padding: 20px; }
.modal { background: var(--bg-card); border-radius: var(--radius-xl); border: 1px solid var(--border-default); box-shadow: var(--shadow-lg); width: 100%; max-width: 480px; padding: 24px; }
.modal h2 { margin: 0 0 4px; font-size: 18px; }
.modal .modal-sub { color: var(--text-muted); font-size: 13px; margin: 0 0 16px; }
.modal .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; flex-wrap: wrap; }
.modal .test-result { font-size: 12px; margin-top: 10px; min-height: 18px; }
.presets { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.preset-btn { font-size: 12px; padding: 4px 12px; border-radius: 999px; border: 1px solid var(--border-default); background: var(--bg-card); color: var(--text-secondary); cursor: pointer; font-family: var(--font-sans); }
.preset-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ===== Responsive ===== */

@media (max-width: 960px) {
    .shell { grid-template-columns: 1fr; }
    .sidebar { position: static; height: auto; flex-direction: row; flex-wrap: wrap; gap: 8px; padding: 12px; }
    .side-nav { flex-direction: row; flex-wrap: wrap; }
    .nav-group { display: none; }
    .sidebar-foot { display: none; }
    .main { padding: 16px; }
    .grid-2, .grid-3, .grid-main-side, .dash-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
    h1 { font-size: 20px; }
    .btn-lg { padding: 10px 20px; font-size: 14px; }
    .form-input, .form-textarea, .form-select { font-size: 13px; padding: 8px 10px; }
    .chat-container { height: calc(100vh - 160px); }
    h2 { font-size: 18px; }
    h3 { font-size: 15px; }
    .score-circle { width: 90px; height: 90px; }
    .score-value { font-size: 26px; }
    table { font-size: 12px; }
    th, td { padding: 6px 8px; }
    .dimension-item { flex-wrap: wrap; }
    .dimension-name { width: 100%; margin-bottom: 4px; }
}
"""
