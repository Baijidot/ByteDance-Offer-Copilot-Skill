"""
CSS Styles — ByteDance Offer Copilot
Dark theme, ByteDance-inspired design system.
"""

CSS = """
/* ===== ByteDance Offer Copilot — Design System ===== */

:root {
    --bg-primary: #0d0d0f;
    --bg-secondary: #141418;
    --bg-card: #1a1a20;
    --bg-card-hover: #1f1f28;
    --bg-input: #1a1a24;
    --bg-code: #0f0f14;

    --border-default: #2a2a35;
    --border-active: #3d3dff;
    --border-hover: #404055;

    --text-primary: #e8e8ed;
    --text-secondary: #9e9eaa;
    --text-muted: #6a6a75;
    --text-accent: #5b8eff;

    --accent: #3d3dff;
    --accent-hover: #5555ff;
    --accent-glow: rgba(61, 61, 255, 0.15);

    --success: #2dd4bf;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #60a5fa;

    --gradient-hero: linear-gradient(135deg, #3d3dff 0%, #8b5cf6 50%, #a78bfa 100%);
    --gradient-card: linear-gradient(135deg, rgba(61,61,255,0.08) 0%, rgba(139,92,246,0.04) 100%);

    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
    --radius-xl: 24px;

    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);

    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
}

/* ===== Reset & Base ===== */

*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-sans);
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    min-height: 100vh;
}

/* ===== Layout ===== */

.app-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}

/* ===== Header ===== */

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-default);
    margin-bottom: 32px;
}

.header-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    text-decoration: none;
}

.header-logo .logo-icon {
    width: 32px;
    height: 32px;
    background: var(--gradient-hero);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.header-nav {
    display: flex;
    gap: 8px;
}

.header-nav a {
    color: var(--text-secondary);
    text-decoration: none;
    padding: 6px 14px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    transition: all 0.15s;
}

.header-nav a:hover, .header-nav a.active {
    color: var(--text-primary);
    background: var(--bg-card);
}

/* ===== Hero Section ===== */

.hero {
    text-align: center;
    padding: 60px 0 40px;
}

.hero-badge {
    display: inline-block;
    padding: 4px 14px;
    background: var(--accent-glow);
    border: 1px solid rgba(61,61,255,0.3);
    border-radius: 20px;
    font-size: 13px;
    color: var(--text-accent);
    margin-bottom: 20px;
    font-weight: 500;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 12px;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 18px;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto 32px;
    line-height: 1.7;
}

.hero-stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 24px;
}

.hero-stat {
    text-align: center;
}

.hero-stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-accent);
}

.hero-stat-label {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ===== Tab Navigation ===== */

.tab-nav {
    display: flex;
    gap: 4px;
    padding: 4px;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    margin-bottom: 32px;
    overflow-x: auto;
}

.tab-btn {
    padding: 10px 20px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
    font-family: var(--font-sans);
}

.tab-btn:hover {
    color: var(--text-primary);
    background: var(--bg-card);
}

.tab-btn.active {
    color: var(--text-primary);
    background: var(--bg-card);
    box-shadow: var(--shadow-sm);
}

/* ===== Cards ===== */

.card {
    background: var(--bg-card);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 24px;
    transition: all 0.2s;
}

.card:hover {
    border-color: var(--border-hover);
    background: var(--bg-card-hover);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}

.card-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.card-title {
    font-size: 16px;
    font-weight: 600;
}

.card-body {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.7;
}

/* ===== Feature Grid ===== */

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}

/* ===== Form Elements ===== */

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-textarea {
    width: 100%;
    min-height: 120px;
    padding: 14px;
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
    line-height: 1.6;
    resize: vertical;
    transition: border-color 0.15s;
}

.form-textarea:focus {
    outline: none;
    border-color: var(--border-active);
    box-shadow: 0 0 0 3px var(--accent-glow);
}

.form-input {
    width: 100%;
    padding: 10px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
    transition: border-color 0.15s;
}

.form-input:focus {
    outline: none;
    border-color: var(--border-active);
    box-shadow: 0 0 0 3px var(--accent-glow);
}

.form-select {
    width: 100%;
    padding: 10px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%239e9eaa' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
}

.form-select:focus {
    outline: none;
    border-color: var(--border-active);
}

.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

/* ===== Buttons ===== */

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 24px;
    border: none;
    border-radius: var(--radius-md);
    font-family: var(--font-sans);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    text-decoration: none;
}

.btn-primary {
    background: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-hover);
    box-shadow: 0 4px 16px rgba(61, 61, 255, 0.4);
}

.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.btn-secondary:hover {
    border-color: var(--border-hover);
    background: var(--bg-card-hover);
}

.btn-danger {
    background: rgba(239, 68, 68, 0.15);
    color: var(--danger);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
    background: rgba(239, 68, 68, 0.25);
}

.btn-lg {
    padding: 14px 32px;
    font-size: 16px;
}

.btn-block {
    width: 100%;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* ===== Progress Bar ===== */

.progress-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

.progress-fill.high {
    background: linear-gradient(90deg, #2dd4bf, #22c55e);
}

.progress-fill.medium {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.progress-fill.low {
    background: linear-gradient(90deg, #ef4444, #f87171);
}

/* ===== Score Display ===== */

.score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 3px solid var(--accent);
    background: var(--accent-glow);
    margin: 0 auto;
}

.score-value {
    font-size: 36px;
    font-weight: 800;
    color: var(--text-accent);
}

.score-label {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
}

/* ===== Dimension Bars ===== */

.dimension-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.dimension-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.dimension-name {
    width: 120px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    flex-shrink: 0;
}

.dimension-bar-wrap {
    flex: 1;
    height: 6px;
    background: var(--bg-secondary);
    border-radius: 3px;
    overflow: hidden;
}

.dimension-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.dimension-score {
    width: 50px;
    text-align: right;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    flex-shrink: 0;
}

/* ===== Tags / Badges ===== */

.tag {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.tag-success {
    background: rgba(45, 212, 191, 0.12);
    color: var(--success);
}

.tag-warning {
    background: rgba(245, 158, 11, 0.12);
    color: var(--warning);
}

.tag-danger {
    background: rgba(239, 68, 68, 0.12);
    color: var(--danger);
}

.tag-info {
    background: rgba(96, 165, 250, 0.12);
    color: var(--info);
}

.tag-accent {
    background: var(--accent-glow);
    color: var(--text-accent);
}

/* ===== Interview Chat ===== */

.chat-container {
    display: flex;
    flex-direction: column;
    height: 500px;
    background: var(--bg-card);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.chat-mode-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.chat-mode-badge.mild {
    background: rgba(45,212,191,0.12);
    color: var(--success);
}

.chat-mode-badge.hard {
    background: rgba(245,158,11,0.12);
    color: var(--warning);
}

.chat-mode-badge.hell {
    background: rgba(239,68,68,0.12);
    color: var(--danger);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.chat-message {
    display: flex;
    gap: 12px;
    max-width: 85%;
}

.chat-message.interviewer {
    align-self: flex-start;
}

.chat-message.candidate {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.chat-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.chat-message.interviewer .chat-avatar {
    background: var(--accent-glow);
}

.chat-message.candidate .chat-avatar {
    background: var(--bg-secondary);
}

.chat-bubble {
    padding: 12px 16px;
    border-radius: var(--radius-md);
    font-size: 14px;
    line-height: 1.6;
}

.chat-message.interviewer .chat-bubble {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.chat-message.candidate .chat-bubble {
    background: var(--accent);
    color: white;
}

.chat-input-area {
    padding: 16px 20px;
    border-top: 1px solid var(--border-default);
    display: flex;
    gap: 12px;
}

.chat-input {
    flex: 1;
    padding: 10px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
}

.chat-input:focus {
    outline: none;
    border-color: var(--border-active);
}

/* ===== Table ===== */

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th {
    text-align: left;
    padding: 12px 16px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border-default);
}

td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-default);
    color: var(--text-secondary);
}

tr:hover td {
    background: rgba(255,255,255,0.02);
}

/* ===== Result Panel ===== */

.result-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 32px;
    margin-top: 24px;
    display: none;
}

.result-panel.visible {
    display: block;
}

.result-panel h2 {
    font-size: 20px;
    margin-bottom: 20px;
}

.result-panel h3 {
    font-size: 16px;
    margin-bottom: 12px;
    color: var(--text-accent);
}

/* ===== Loading ===== */

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    color: var(--text-muted);
    gap: 10px;
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-default);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== Alerts ===== */

.alert {
    padding: 14px 18px;
    border-radius: var(--radius-md);
    font-size: 14px;
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.6;
}

.alert-info {
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.25);
    color: var(--info);
}

.alert-warning {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: var(--warning);
}

.alert-danger {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    color: var(--danger);
}

/* ===== Radar Chart (SVG) ===== */

.radar-container {
    display: flex;
    justify-content: center;
    padding: 20px;
}

.radar-chart {
    max-width: 300px;
}

/* ===== Footer ===== */

.footer {
    text-align: center;
    padding: 40px 0;
    color: var(--text-muted);
    font-size: 13px;
    border-top: 1px solid var(--border-default);
    margin-top: 60px;
}

/* ===== Responsive ===== */

@media (max-width: 768px) {
    .hero h1 {
        font-size: 28px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .tab-nav {
        flex-wrap: nowrap;
    }

    .tab-btn {
        padding: 8px 14px;
        font-size: 13px;
    }

    .chat-container {
        height: 400px;
    }

    .chat-message {
        max-width: 90%;
    }
}

/* ===== Markdown Content ===== */

.markdown-content h2 {
    font-size: 18px;
    margin: 20px 0 12px;
    color: var(--text-primary);
}

.markdown-content h3 {
    font-size: 15px;
    margin: 16px 0 8px;
    color: var(--text-accent);
}

.markdown-content p {
    margin: 8px 0;
    line-height: 1.7;
}

.markdown-content ul {
    padding-left: 20px;
}

.markdown-content li {
    margin: 4px 0;
    color: var(--text-secondary);
}

.markdown-content blockquote {
    border-left: 3px solid var(--accent);
    padding: 8px 16px;
    margin: 12px 0;
    background: var(--accent-glow);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    color: var(--text-secondary);
    font-style: italic;
}

.markdown-content table {
    margin: 12px 0;
}

.markdown-content code {
    background: var(--bg-code);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--text-accent);
}

/* ===== Emoji Icons ===== */

.emoji-icon {
    font-size: 24px;
    line-height: 1;
}

/* ===== Scrollbar ===== */

::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--border-hover);
}

/* ===== Mobile Responsive ===== */

@media (max-width: 768px) {
    .app-container { padding: 0 12px; }
    .header { flex-direction: column; gap: 12px; align-items: flex-start; }
    .header-nav { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
    .header-nav a { font-size: 13px; }

    .hero { padding: 32px 0 24px; }
    .hero h1 { font-size: 24px; }
    .hero-subtitle { font-size: 14px; }
    .hero-stats { gap: 20px; }
    .hero-stat-value { font-size: 22px; }

    .feature-grid { grid-template-columns: 1fr; }
    .form-row { grid-template-columns: 1fr; }

    .tab-nav {
        flex-wrap: nowrap; overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding: 4px 2px; gap: 4px;
    }
    .tab-btn { padding: 8px 14px; font-size: 13px; flex-shrink: 0; white-space: nowrap; }

    .card { padding: 16px; border-radius: var(--radius-md); }
    .result-panel { padding: 16px; }

    .chat-container { height: calc(100vh - 200px); border-radius: 0; border: none; }
    .chat-message { max-width: 95%; }
    .chat-bubble { font-size: 13px; padding: 10px 12px; }
    .chat-input-area { padding: 12px; gap: 8px; flex-direction: column; }
    .chat-input-area .form-input { width: 100%; }

    .score-circle { width: 90px; height: 90px; }
    .score-value { font-size: 28px; }
    .dimension-item { flex-wrap: wrap; }
    .dimension-name { width: 100%; margin-bottom: 4px; }
    .dimension-score { width: auto; }

    table { font-size: 12px; }
    th, td { padding: 6px 8px; }

    .footer { padding: 24px 0; font-size: 12px; }

    .guide-card { max-width: 100%; width: calc(100% - 24px); padding: 20px; }

    .btn-lg { padding: 12px 24px; font-size: 14px; }
}

@media (max-width: 480px) {
    .hero h1 { font-size: 20px; }
    .hero-badge { font-size: 11px; }
    .tab-btn { padding: 6px 10px; font-size: 12px; }
    .btn-lg { padding: 10px 20px; font-size: 14px; }
    .form-input, .form-textarea, .form-select { font-size: 13px; padding: 8px 10px; }
    .chat-container { height: calc(100vh - 160px); }
    .chat-header { padding: 12px; }
    .chat-messages { padding: 12px; }
    h2 { font-size: 20px; }
    h3 { font-size: 16px; }
}
"""
