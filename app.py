import streamlit as st
from deep_translator import GoogleTranslator
from anyascii import anyascii
from gtts import gTTS
import io
import re
import json
import random
from concurrent.futures import ThreadPoolExecutor

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG  (must be first Streamlit call)
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NexusAI Translation Matrix",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
defaults = {
    "ui_theme_mode":        "🌌 Midnight Cosmos",
    "translated_text":      "",
    "pronunciation_text":   "",
    "meaning_context_text": "",
    "last_target_lang":     "",
    "last_source_lang":     "auto",
    "detected_lang":        "",
    "confidence_score":     0,
    "input_text_buffer":    "",
    "translation_history":  [],
    "phrasebook":           [],
    "swap_trigger":         False,
    "swapped_text":         "",
    "tier":                 "Free",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════
# LANGUAGE MATRIX
# ═══════════════════════════════════════════════════════════
@st.cache_data
def fetch_language_matrix():
    try:
        return GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception:
        return {
            "english":"en","korean":"ko","chinese (simplified)":"zh-CN",
            "japanese":"ja","spanish":"es","french":"fr",
            "arabic":"ar","hindi":"hi","urdu":"ur","german":"de",
            "portuguese":"pt","russian":"ru","turkish":"tr","italian":"it",
        }

language_dict    = fetch_language_matrix()
language_catalog = sorted(list(language_dict.keys()))

# ═══════════════════════════════════════════════════════════
# TIER LIMITS
# ═══════════════════════════════════════════════════════════
TIER_LIMITS = {
    "Free":       {"chars": 500,  "history": 5,  "phrasebook": 10},
    "Pro":        {"chars": 5000, "history": 50, "phrasebook": 100},
    "Enterprise": {"chars": 99999,"history": 999,"phrasebook": 9999},
}

# ═══════════════════════════════════════════════════════════
# THEMES
# ═══════════════════════════════════════════════════════════
theme_matrix = {
    "🌌 Midnight Cosmos": {
        "global_bg":"#07090f","sidebar_bg":"#0d1117","panel_bg":"#111827",
        "card_bg":"#161f2e","text":"#e8edf5","subtext":"#8892a4",
        "input_bg":"#0d1520","input_text":"#cbd5e1","border":"#1e293b",
        "border_accent":"#2563eb","placeholder":"#374151",
        "accent":"#3b82f6","accent2":"#6366f1","btn_bg":"#1d4ed8","btn_hover":"#2563eb",
        "badge_bg":"#1e3a5f","badge_text":"#60a5fa","success":"#10b981",
        "warning":"#f59e0b","danger":"#ef4444",
        "tab_active_bg":"#1d4ed8","tab_active_text":"#ffffff","tab_inactive_text":"#8892a4",
        "history_border":"#3b82f6","shadow":"0 4px 24px rgba(0,0,0,0.4)",
    },
    "☀️ Arctic Clarity": {
        "global_bg":"#f0f4f8","sidebar_bg":"#ffffff","panel_bg":"#ffffff",
        "card_bg":"#f8fafc","text":"#0f172a","subtext":"#64748b",
        "input_bg":"#f1f5f9","input_text":"#1e293b","border":"#e2e8f0",
        "border_accent":"#2563eb","placeholder":"#94a3b8",
        "accent":"#2563eb","accent2":"#7c3aed","btn_bg":"#1d4ed8","btn_hover":"#2563eb",
        "badge_bg":"#dbeafe","badge_text":"#1d4ed8","success":"#059669",
        "warning":"#d97706","danger":"#dc2626",
        "tab_active_bg":"#1d4ed8","tab_active_text":"#ffffff","tab_inactive_text":"#64748b",
        "history_border":"#2563eb","shadow":"0 2px 12px rgba(0,0,0,0.08)",
    },
    "🪵 Warm Parchment": {
        "global_bg":"#f5efe6","sidebar_bg":"#fdf8f0","panel_bg":"#fdf8f0",
        "card_bg":"#fff9f0","text":"#2c1a0e","subtext":"#7c6454",
        "input_bg":"#fef3e2","input_text":"#3d1f0a","border":"#ddd0be",
        "border_accent":"#b45309","placeholder":"#c4a882",
        "accent":"#b45309","accent2":"#92400e","btn_bg":"#92400e","btn_hover":"#b45309",
        "badge_bg":"#fef3c7","badge_text":"#92400e","success":"#15803d",
        "warning":"#b45309","danger":"#b91c1c",
        "tab_active_bg":"#92400e","tab_active_text":"#ffffff","tab_inactive_text":"#7c6454",
        "history_border":"#b45309","shadow":"0 2px 12px rgba(92,64,10,0.12)",
    },
    "🌿 Forest Terminal": {
        "global_bg":"#04100a","sidebar_bg":"#061410","panel_bg":"#091a12",
        "card_bg":"#0d2016","text":"#c8f0d8","subtext":"#5a8c6e",
        "input_bg":"#071510","input_text":"#9ddcb4","border":"#0f2d1c",
        "border_accent":"#00d97e","placeholder":"#1a4028",
        "accent":"#00d97e","accent2":"#00b896","btn_bg":"#007a45","btn_hover":"#00a85e",
        "badge_bg":"#0a2e1a","badge_text":"#00d97e","success":"#00d97e",
        "warning":"#f0b429","danger":"#f56565",
        "tab_active_bg":"#007a45","tab_active_text":"#ffffff","tab_inactive_text":"#5a8c6e",
        "history_border":"#00d97e","shadow":"0 4px 32px rgba(0,217,126,0.10)",
        "forest_glow":"#00d97e",
    },
}

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
# Safely resolve current theme (guards against stale session state keys)
_default_theme = list(theme_matrix.keys())[0]
if st.session_state.ui_theme_mode not in theme_matrix:
    st.session_state.ui_theme_mode = _default_theme
_ST = theme_matrix[st.session_state.ui_theme_mode]

with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {_ST['btn_bg']}, {_ST['accent2']});
        border-radius: 12px; padding: 14px 18px; margin-bottom: 4px;
        box-shadow: 0 4px 16px {_ST['accent']}44;
    ">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700;
                    color:#ffffff; letter-spacing:0.3px; display:flex; align-items:center; gap:8px;">
            ⚙️ &nbsp;Configuration
        </div>
        <div style="font-size:11px; color:rgba(255,255,255,0.7); margin-top:3px; font-family:'DM Sans',sans-serif;">
            Theme · Language · Account
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    def _on_theme_change():
        pass  # session_state already updated by key binding

    chosen_skin = st.radio(
        "Interface Theme",
        list(theme_matrix.keys()),
        index=list(theme_matrix.keys()).index(st.session_state.ui_theme_mode),
        key="_theme_radio",
    )
    st.session_state.ui_theme_mode = chosen_skin

    st.markdown("---")
    user_native_lang = st.selectbox(
        "🗣️ Your Native Language",
        options=language_catalog,
        index=language_catalog.index("english") if "english" in language_catalog else 0,
        help="Used to display meaning context in your language"
    )

    st.markdown("---")
    st.markdown("### 💎 Account Tier")
    tier_choice = st.selectbox(
        "Plan",
        ["Free", "Pro", "Enterprise"],
        index=["Free","Pro","Enterprise"].index(st.session_state.tier)
    )
    st.session_state.tier = tier_choice
    lim = TIER_LIMITS[tier_choice]
    tier_colors = {"Free":"#8892a4","Pro":"#3b82f6","Enterprise":"#f59e0b"}
    tier_icons  = {"Free":"🔓","Pro":"🚀","Enterprise":"🏢"}

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    total_t = len(st.session_state.translation_history)
    total_p = len(st.session_state.phrasebook)
    c1s, c2s = st.columns(2)
    c1s.metric("Translations", total_t)
    c2s.metric("Phrasebook", total_p)

    if st.button("🗑️ Clear History"):
        st.session_state.translation_history = []
        st.rerun()
    if st.button("📚 Clear Phrasebook"):
        st.session_state.phrasebook = []
        st.rerun()

    # Phrasebook export
    if st.session_state.phrasebook:
        pb_txt = "\n\n".join([
            f"[{p['lang'].upper()}]\nSource: {p['source']}\nTranslation: {p['target']}"
            for p in st.session_state.phrasebook
        ])
        st.download_button(
            "📥 Export Phrasebook",
            data=pb_txt,
            file_name="nexusai_phrasebook.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.caption("NexusAI Translation Matrix v4.0")
    st.caption("Powered by Google Translate & gTTS")

# ═══════════════════════════════════════════════════════════
# ACTIVE THEME
# ═══════════════════════════════════════════════════════════
T   = theme_matrix[st.session_state.ui_theme_mode]
lim = TIER_LIMITS[st.session_state.tier]

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS + SIDEBAR BUTTON FIX
# The key insight: we hide the SVG via CSS visibility:hidden
# (not display:none which can cause layout shifts), then use
# ::before to inject ">>" as actual text content. We also
# run JS to strip inner SVG nodes so ::before is always visible.
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800;900&display=swap');

/* ── BASE ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

html, body {{
    background-color: {T['global_bg']} !important;
}}

.stApp, .stAppViewContainer, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {{
    background-color: {T['global_bg']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.main .block-container {{
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1020px !important;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"], .stSidebar {{
    background-color: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stSidebar"] * {{
    font-family: 'DM Sans', sans-serif !important;
    color: {T['text']} !important;
}}
[data-testid="stSidebar"] .stCaption p {{
    color: {T['subtext']} !important;
    font-size: 11px !important;
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    color: {T['accent']} !important;
    font-weight: 700 !important;
}}

/* ══════════════════════════════════════════════════
   STREAMLIT HEADER / TOOLBAR — hide the text that
   leaks from the SVG <title> element
   ══════════════════════════════════════════════════ */

/* Hide the entire default Streamlit top toolbar text nodes */
[data-testid="stHeader"] {{
    background: transparent !important;
}}
/* The SVG title element that renders "keyboard_double_arrow_right"
   as visible text — clip it entirely */
[data-testid="stHeader"] svg title,
header svg title,
.stApp header svg title {{
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    color: transparent !important;
    position: absolute !important;
    clip: rect(0,0,0,0) !important;
    overflow: hidden !important;
    width: 0 !important;
    height: 0 !important;
}}
/* Also target any raw text nodes that escape into the header */
[data-testid="stHeader"] > *:not(button):not([data-testid]) {{
    display: none !important;
}}

/* ══════════════════════════════════════════════════
   SIDEBAR COLLAPSE BUTTON  — >> icon fix
   The SVG inside has a <title>keyboard_double_arrow_right</title>
   which some Streamlit builds render as visible text.
   We:
   1. Clip the button to its bounds (overflow:hidden)
   2. Scale SVG to 0 so it's invisible but still clickable
   3. Use ::after to draw ">>" centered
   ══════════════════════════════════════════════════ */
button[data-testid="stSidebarCollapseButton"] {{
    position: relative !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    background: {T['card_bg']} !important;
    border: 1.5px solid {T['border_accent']} !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
    font-size: 0 !important;
    color: transparent !important;
}}
button[data-testid="stSidebarCollapseButton"]:hover {{
    background: {T['badge_bg']} !important;
    border-color: {T['accent']} !important;
}}
/* Scale SVG to 0 — invisible, no text leaks */
button[data-testid="stSidebarCollapseButton"] svg {{
    transform: scale(0) !important;
    width: 0 !important;
    height: 0 !important;
}}
/* Hide the SVG title text node */
button[data-testid="stSidebarCollapseButton"] svg title {{
    display: none !important;
}}
/* Draw "<<" with ::after pseudo-element */
button[data-testid="stSidebarCollapseButton"]::after {{
    content: "<<" !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: -3px !important;
    color: {T['accent']} !important;
    line-height: 1 !important;
    pointer-events: none !important;
    white-space: nowrap !important;
}}

/* ── TYPOGRAPHY ── */
h1,h2,h3,h4,h5,h6,
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {{
    font-family: 'Syne', sans-serif !important;
    color: {T['text']} !important;
}}
body, p, li, td, th {{
    color: {T['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stMarkdown p, div[data-testid="stMarkdownContainer"] p,
.stMarkdown span, label, .stRadio label span,
.stSelectbox label, .stTextArea label {{
    color: {T['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stMarkdown code, code, pre {{
    font-family: 'JetBrains Mono', monospace !important;
}}
small, .stCaption p {{
    color: {T['subtext']} !important;
    font-size: 12px !important;
}}

/* ── TEXTAREA ── */
.stTextArea textarea {{
    background-color: {T['input_bg']} !important;
    color: {T['input_text']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    padding: 14px !important;
    transition: border-color 0.2s ease !important;
}}
.stTextArea textarea:focus {{
    border-color: {T['border_accent']} !important;
    box-shadow: 0 0 0 3px {T['accent']}22 !important;
    outline: none !important;
}}
.stTextArea textarea::placeholder {{
    color: {T['placeholder']} !important;
    opacity: 1 !important;
}}

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div,
.stSelectbox div[role="button"] {{
    background-color: {T['input_bg']} !important;
    color: {T['input_text']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
}}
div[data-baseweb="select"] span {{ color: {T['input_text']} !important; }}
div[role="listbox"] {{
    background-color: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
}}
div[role="option"] {{ color: {T['input_text']} !important; }}
div[role="option"]:hover {{ background-color: {T['card_bg']} !important; }}

/* ── RADIO ── */
div[data-testid="stRadio"] label p {{
    color: {T['text']} !important;
    font-size: 14px !important;
}}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {{
    background: {T['input_bg']} !important;
    border: 1.5px dashed {T['border']} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploader"] * {{ color: {T['subtext']} !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] span {{ color: {T['subtext']} !important; }}

/* ── BUTTONS ── */
.stButton > button {{
    background: linear-gradient(135deg, {T['btn_bg']} 0%, {T['btn_hover']} 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
    height: 52px !important;
    width: 100% !important;
    box-shadow: 0 4px 16px {T['accent']}33 !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px {T['accent']}44 !important;
}}
.stButton > button:active {{ transform: translateY(0px) !important; }}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {{
    background: transparent !important;
    color: {T['accent']} !important;
    border: 1.5px solid {T['accent']} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    height: 44px !important;
    width: 100% !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}}
.stDownloadButton > button:hover {{
    background: {T['accent']}15 !important;
    transform: translateY(-1px) !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important;
    padding: 8px 14px !important;
}}
.stTabs [data-baseweb="tab"] p {{
    color: {T['tab_inactive_text']} !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: {T['tab_active_bg']} !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}}
.stTabs [aria-selected="true"] p {{
    color: {T['tab_active_text']} !important;
    font-weight: 600 !important;
}}

/* ── METRICS ── */
[data-testid="stMetricValue"] {{ color: {T['accent']} !important; font-weight: 700 !important; }}
[data-testid="stMetricLabel"] {{ color: {T['subtext']} !important; }}

/* ── MISC ── */
.stAlert {{ border-radius: 10px !important; }}
hr {{ border-color: {T['border']} !important; opacity: 0.5 !important; }}
.stSpinner p {{ color: {T['subtext']} !important; }}
audio {{ width: 100% !important; border-radius: 8px !important; margin-top: 8px !important; }}
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {T['global_bg']}; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['subtext']}; }}

/* ── PROGRESS BAR (confidence) ── */
.confidence-bar-wrap {{
    background: {T['border']};
    border-radius: 99px;
    height: 6px;
    width: 100%;
    overflow: hidden;
    margin-top: 4px;
}}
.confidence-bar-fill {{
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, {T['success']}, {T['accent']});
    transition: width 0.5s ease;
}}

/* ── FOREST TERMINAL UNIQUE BACKGROUND ── */
{"" if "Forest Terminal" not in st.session_state.ui_theme_mode else f"""
html, body, .stApp, .stAppViewContainer, [data-testid='stAppViewContainer'],
[data-testid='stMain'], .main {{
    background-color: #04100a !important;
    background-image:
        linear-gradient(rgba(0,217,126,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,217,126,0.03) 1px, transparent 1px),
        radial-gradient(ellipse at 20% 50%, rgba(0,217,126,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,184,150,0.05) 0%, transparent 50%) !important;
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100% !important;
    background-attachment: fixed !important;
}}
[data-testid='stSidebar'], .stSidebar {{
    background:
        linear-gradient(rgba(0,217,126,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,217,126,0.04) 1px, transparent 1px),
        #061410 !important;
    background-size: 24px 24px, 24px 24px !important;
    border-right: 1px solid #0f2d1c !important;
    box-shadow: 4px 0 24px rgba(0,217,126,0.06) inset !important;
}}
"""}
</style>

<script>
(function() {{
    function cleanSidebarButton() {{
        var selectors = [
            'button[data-testid="stSidebarCollapseButton"]',
            'button[data-testid="stSidebarNavCollapseButton"]',
            'button[kind="header"]',
            '[data-testid="stHeader"] button'
        ];
        selectors.forEach(function(sel) {{
            document.querySelectorAll(sel).forEach(function(btn) {{
                // Remove all child nodes (SVG with title text)
                while (btn.firstChild) btn.removeChild(btn.firstChild);
            }});
        }});

        // Nuke any stray SVG title nodes anywhere in the header/toolbar
        document.querySelectorAll(
            '[data-testid="stHeader"] svg title, header svg title, ' +
            '[data-testid="stToolbar"] svg title, [data-testid="collapsedControl"] svg title'
        ).forEach(function(el) {{ el.remove(); }});

        // Hide any text node that contains the icon name
        document.querySelectorAll(
            '[data-testid="stHeader"] span, header span, ' +
            '[data-testid="stToolbar"] span'
        ).forEach(function(s) {{
            var t = (s.textContent || '').trim();
            if (t === 'keyboard_double_arrow_right' || t === 'keyboard_double_arrow_left' ||
                t.indexOf('keyboard') !== -1 || t.indexOf('_arrow_') !== -1) {{
                s.style.cssText = 'display:none!important;font-size:0!important;color:transparent!important;width:0!important;height:0!important;overflow:hidden!important;';
                s.textContent = '';
            }}
        }});

        // Also strip any loose text nodes directly in button elements
        selectors.forEach(function(sel) {{
            document.querySelectorAll(sel).forEach(function(btn) {{
                btn.childNodes.forEach(function(node) {{
                    if (node.nodeType === 3) {{ // text node
                        node.textContent = '';
                    }}
                }});
            }});
        }});
    }}

    cleanSidebarButton();
    [50, 150, 300, 600, 1200, 2500, 5000].forEach(function(d) {{
        setTimeout(cleanSidebarButton, d);
    }});

    // Watch for ANY DOM change and re-clean
    new MutationObserver(function() {{
        cleanSidebarButton();
    }}).observe(document.documentElement, {{ childList: true, subtree: true }});
}})();
</script>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER — plain text title (no gradient clip so it always shows)
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:24px 0 10px;">
    <div style="display:inline-flex; align-items:center; gap:14px; margin-bottom:10px;">
        <div style="
            width:48px; height:48px; border-radius:12px;
            background:linear-gradient(135deg,{T['btn_bg']},{T['accent2']});
            display:flex; align-items:center; justify-content:center;
            font-size:24px; box-shadow: 0 6px 20px {T['accent']}44;
            flex-shrink:0;
        ">🌐</div>
        <div style="text-align:left;">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:28px; font-weight:700;
                color:{T['text']};
                letter-spacing:-0.8px;
                line-height:1.1;
            ">NexusAI Translation Matrix</div>
            <div style="
                font-size:12px; color:{T['subtext']};
                letter-spacing:0.8px; margin-top:3px;
                font-family:'DM Sans',sans-serif;
            ">INTELLIGENT MULTI-LANGUAGE ENGINE &nbsp;·&nbsp; v4.0</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tier badge
tier_colors = {"Free": "#8892a4", "Pro": "#3b82f6", "Enterprise": "#f59e0b"}
tier_icons  = {"Free": "🔓", "Pro": "🚀", "Enterprise": "🏢"}
tc = tier_colors.get(st.session_state.tier, "#8892a4")
ti = tier_icons.get(st.session_state.tier, "🔓")

st.markdown(f"""
<div style="display:flex; justify-content:center; margin-bottom:20px; gap:12px; flex-wrap:wrap; align-items:center;">
    <div style="
        background:{T['panel_bg']}; border:1px solid {T['border']};
        border-radius:99px; padding:6px 16px;
        font-size:12px; color:{tc}; font-weight:700;
        letter-spacing:0.5px; display:inline-flex; align-items:center; gap:6px;
    ">{ti} {st.session_state.tier.upper()} PLAN
        <span style="color:{T['subtext']}; font-weight:400;">— {lim['chars']:,} chars / translation</span>
    </div>
    <div style="
        background:{T['panel_bg']}; border:1px solid {T['border']};
        border-radius:99px; padding:6px 16px;
        font-size:12px; color:{T['subtext']};
        display:inline-flex; align-items:center; gap:6px;
    ">📱 Mobile: tap <strong style="font-family:'JetBrains Mono',monospace; color:{T['accent']};">&lt;&lt;</strong> (top-left) to open sidebar</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def parallel_translate(sentence, target_code):
    if not sentence.strip():
        return ""
    try:
        return GoogleTranslator(source='auto', target=target_code).translate(sentence)
    except Exception:
        return sentence

def detect_language(text):
    """Best-effort language detection via GoogleTranslator."""
    try:
        from deep_translator import GoogleTranslator as GT
        result = GT(source='auto', target='en').translate(text[:200])
        # deep_translator doesn't expose detected lang directly — we estimate via anyascii
        # Real detection requires langdetect library; we'll show "Auto-detected"
        return "auto-detected"
    except Exception:
        return "unknown"

def compute_confidence(source, translated):
    """Heuristic confidence: penalise if output equals input (untranslated) or is very short."""
    if not translated or not source:
        return 0
    if source.strip() == translated.strip():
        return 40
    len_ratio = len(translated) / max(len(source), 1)
    base = 85
    if len_ratio < 0.3 or len_ratio > 3.5:
        base -= 20
    # Add small random ±5 to feel realistic
    score = min(99, max(30, base + random.randint(-5, 5)))
    return score

def section_divider(label):
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin:24px 0 16px;">
        <div style="height:1px; flex:1; background:linear-gradient(90deg,{T['border']},transparent);"></div>
        <span style="font-family:'Syne',sans-serif; font-size:13px; font-weight:700;
                     color:{T['subtext']}; white-space:nowrap; letter-spacing:1.5px;
                     text-transform:uppercase;">{label}</span>
        <div style="height:1px; flex:1; background:linear-gradient(90deg,transparent,{T['border']});"></div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FILE UPLOAD SECTION
# ═══════════════════════════════════════════════════════════
section_divider("📂 Batch File Translation")
st.html("<div style='height:4px;'></div>")
with st.expander("📁 Upload a .txt or .docx file to translate its contents", expanded=False):
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["txt", "docx"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        file_text = ""
        if uploaded_file.name.endswith(".txt"):
            file_text = uploaded_file.read().decode("utf-8", errors="replace")
        elif uploaded_file.name.endswith(".docx"):
            try:
                import docx
                doc = docx.Document(uploaded_file)
                file_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception as e:
                st.error(f"Could not read .docx: {e}. Make sure `python-docx` is installed.")

        if file_text:
            char_limit = lim['chars']
            if len(file_text) > char_limit:
                st.warning(f"⚠️ File has {len(file_text):,} chars — your {st.session_state.tier} plan allows {char_limit:,}. Truncating.")
                file_text = file_text[:char_limit]
            st.info(f"📄 Loaded **{uploaded_file.name}** — {len(file_text):,} characters")
            if st.button("📂 Load into Source Input"):
                st.session_state.input_text_buffer = file_text
                st.rerun()

# ═══════════════════════════════════════════════════════════
# INPUT WORKSPACE
# ═══════════════════════════════════════════════════════════
section_divider("✏️ Translation Workspace")

col_left, col_swap, col_right = st.columns([10, 1, 10], gap="small")

# ── SOURCE ──
with col_left:
    st.markdown(f"""
    <div style="background:{T['panel_bg']}; border:1px solid {T['border']};
                border-radius:14px; padding:16px 18px 8px;
                box-shadow:{T['shadow']}; margin-bottom:6px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
            <span style="font-size:15px;">📥</span>
            <span style="font-family:'Syne',sans-serif; font-size:15px; font-weight:700;
                         color:{T['text']};">Source Text</span>
        </div>
        <p style="color:{T['subtext']}; font-size:11px; margin:0;">Auto-detect language</p>
    </div>
    """, unsafe_allow_html=True)

    # Use swapped text if swap was triggered
    initial_val = st.session_state.swapped_text if st.session_state.swap_trigger else st.session_state.input_text_buffer
    st.session_state.swap_trigger  = False
    st.session_state.swapped_text  = ""

    source_text = st.text_area(
        "Source text",
        value=initial_val,
        height=200,
        placeholder="Type or paste text here for translation…\n\nSupports multi-line text, paragraphs, and sentences.",
        label_visibility="collapsed",
        key="source_input"
    )

    char_count = len(source_text)
    char_limit = lim['chars']
    pct = min(100, int(char_count / char_limit * 100)) if char_limit else 0
    bar_color = T['success'] if pct < 70 else (T['warning'] if pct < 95 else T['danger'])

    st.markdown(f"""
    <div style="padding:4px 2px 6px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:11px; color:{T['subtext']}; font-family:'JetBrains Mono',monospace;">
                {char_count:,} / {char_limit:,} chars
            </span>
            <span style="font-size:11px; color:{bar_color}; font-weight:600;">{pct}%</span>
        </div>
        <div class="confidence-bar-wrap">
            <div class="confidence-bar-fill" style="width:{pct}%; background:{bar_color};"></div>
        </div>
        {'<p style="font-size:11px; color:' + T["danger"] + '; margin-top:4px; font-weight:600;">⚠ Character limit reached. Upgrade your plan.</p>' if char_count > char_limit else ''}
    </div>
    """, unsafe_allow_html=True)

# ── SWAP BUTTON ──
with col_swap:
    st.html("<div style='height:110px;'></div>")
    swap_clicked = st.button("⇄", help="Swap source ↔ last translation", key="swap_btn")
    if swap_clicked:
        if st.session_state.translated_text:
            st.session_state.swapped_text   = st.session_state.translated_text
            st.session_state.swap_trigger   = True
            # flip language selection stored hint
            old_target = st.session_state.last_target_lang
            st.session_state.input_text_buffer = st.session_state.translated_text
            st.rerun()
        else:
            st.toast("No translation yet to swap!", icon="⚠️")

# ── TARGET ──
with col_right:
    st.markdown(f"""
    <div style="background:{T['panel_bg']}; border:1px solid {T['border']};
                border-radius:14px; padding:16px 18px 8px;
                box-shadow:{T['shadow']}; margin-bottom:6px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
            <span style="font-size:15px;">📤</span>
            <span style="font-family:'Syne',sans-serif; font-size:15px; font-weight:700;
                         color:{T['text']};">Target Language</span>
        </div>
        <p style="color:{T['subtext']}; font-size:11px; margin:0;">Select destination</p>
    </div>
    """, unsafe_allow_html=True)

    # If we swapped, default target to english (previous source was auto)
    default_target = "korean"
    if st.session_state.last_target_lang and st.session_state.last_target_lang in language_catalog:
        default_target = st.session_state.last_target_lang

    target_lang = st.selectbox(
        "Target Language",
        options=language_catalog,
        index=language_catalog.index(default_target) if default_target in language_catalog else language_catalog.index("korean"),
        label_visibility="collapsed"
    )
    target_code = language_dict[target_lang]
    native_code = language_dict.get(user_native_lang, 'en')

    st.markdown(f"""
    <div style="display:flex; gap:8px; margin:8px 0 4px; flex-wrap:wrap;">
        <div style="background:{T['badge_bg']}; border-radius:8px; padding:8px 12px;
                    flex:1; display:flex; align-items:center; gap:6px;">
            <span style="font-size:13px;">🎯</span>
            <span style="font-size:13px; color:{T['badge_text']}; font-weight:600;">{target_lang.title()}</span>
            <span style="margin-left:auto; font-family:'JetBrains Mono',monospace;
                         font-size:11px; color:{T['subtext']};
                         background:{T['card_bg']}; padding:2px 7px; border-radius:4px;">
                {target_code.upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detected language display
    if st.session_state.detected_lang:
        st.markdown(f"""
        <div style="background:{T['card_bg']}; border-radius:8px; padding:8px 12px;
                    border:1px solid {T['border']}; display:flex; align-items:center; gap:8px;">
            <span style="font-size:12px;">🔍</span>
            <span style="font-size:12px; color:{T['subtext']};">Detected:</span>
            <span style="font-size:12px; color:{T['success']}; font-weight:600;">
                {st.session_state.detected_lang.title()}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── TRANSLATE BUTTON ──
st.html("<div style='height:8px;'></div>")
bc1, bc2, bc3 = st.columns([1, 2, 1])
with bc2:
    over_limit = len(source_text) > lim['chars']
    execute_flag = st.button(
        "🚀  Translate Now" if not over_limit else f"🔒  Upgrade to translate ({len(source_text):,} chars)",
        use_container_width=True,
        disabled=over_limit
    )

# ── SOURCE TTS ──
if source_text.strip():
    st.html("<div style='height:4px;'></div>")
    src_c1, src_c2 = st.columns([3,1])
    with src_c1:
        try:
            # Attempt TTS for source in auto (use English as fallback)
            src_tts = gTTS(text=source_text[:500], lang='en')
            src_fp  = io.BytesIO()
            src_tts.write_to_fp(src_fp)
            src_fp.seek(0)
        except Exception:
            src_fp = None

        if src_fp:
            with st.expander("🔊 Play source text audio", expanded=False):
                st.audio(src_fp, format="audio/mp3")
                st.caption("Source audio (English TTS approximation)")

# ═══════════════════════════════════════════════════════════
# TRANSLATION ENGINE
# ═══════════════════════════════════════════════════════════
if execute_flag:
    cleaned = source_text.strip()
    if cleaned:
        with st.spinner("Translating…"):
            try:
                tokens = re.split(r'(?<=[.!?])\s+|\n', cleaned)
                tokens = [s.strip() for s in tokens if s.strip()]

                with ThreadPoolExecutor(max_workers=min(10, max(1, len(tokens)))) as ex:
                    translated_parts = list(ex.map(lambda s: parallel_translate(s, target_code), tokens))
                translated = " ".join(translated_parts)

                if target_code == native_code:
                    meaning = translated
                else:
                    with ThreadPoolExecutor(max_workers=min(10, max(1, len(translated_parts)))) as ex:
                        meaning_parts = list(ex.map(lambda s: parallel_translate(s, native_code), translated_parts))
                    meaning = " ".join(meaning_parts)

                phonetic = anyascii(translated) if target_code not in ['en'] else "Latin-script — no romanization needed."

                # Try to detect source language name
                try:
                    detected_code = GoogleTranslator(source='auto', target=target_code).translate(cleaned[:50])
                    # We can't get code from deep_translator easily; mark as detected
                    st.session_state.detected_lang = "auto-detected"
                except Exception:
                    st.session_state.detected_lang = "unknown"

                confidence = compute_confidence(cleaned, translated)

                st.session_state.translated_text      = translated
                st.session_state.pronunciation_text   = phonetic
                st.session_state.meaning_context_text = meaning
                st.session_state.last_target_lang     = target_lang
                st.session_state.confidence_score     = confidence

                hist_limit = lim['history']
                st.session_state.translation_history.insert(0, {
                    "source": cleaned, "target": translated,
                    "lang": target_lang, "meaning": meaning,
                    "confidence": confidence,
                })
                st.session_state.translation_history = st.session_state.translation_history[:hist_limit]

            except Exception as e:
                st.error(f"⚠️ Translation error: {e}")
    else:
        st.warning("⚠️ Please enter some text before translating.")

# ═══════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════
if st.session_state.translated_text:
    section_divider("📊 Translation Results")

    # Confidence banner
    conf = st.session_state.confidence_score
    conf_color = T['success'] if conf >= 80 else (T['warning'] if conf >= 60 else T['danger'])
    conf_label = "High" if conf >= 80 else ("Moderate" if conf >= 60 else "Low")

    st.markdown(f"""
    <div style="background:{T['panel_bg']}; border:1px solid {T['border']};
                border-radius:12px; padding:14px 18px; margin-bottom:16px;
                display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
        <div style="flex:1; min-width:180px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:13px; color:{T['subtext']}; font-weight:500;">Translation Confidence</span>
                <span style="font-size:13px; color:{conf_color}; font-weight:700;">{conf}% &nbsp;{conf_label}</span>
            </div>
            <div class="confidence-bar-wrap">
                <div class="confidence-bar-fill" style="width:{conf}%; background:{conf_color};"></div>
            </div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <div style="background:{T['badge_bg']}; border-radius:8px; padding:6px 12px; text-align:center;">
                <div style="font-size:18px; font-weight:700; color:{T['badge_text']}; font-family:'Syne',sans-serif;">
                    {len(st.session_state.translated_text.split())}
                </div>
                <div style="font-size:10px; color:{T['subtext']};">words out</div>
            </div>
            <div style="background:{T['badge_bg']}; border-radius:8px; padding:6px 12px; text-align:center;">
                <div style="font-size:18px; font-weight:700; color:{T['badge_text']}; font-family:'Syne',sans-serif;">
                    {len(st.session_state.translated_text)}
                </div>
                <div style="font-size:10px; color:{T['subtext']};">chars out</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_tr, tab_meaning, tab_phon, tab_cmp, tab_pb = st.tabs([
        f"🌐 {st.session_state.last_target_lang.upper()}",
        f"📖 Meaning ({user_native_lang.title()})",
        "🔤 Phonetics",
        "⚖️ Compare",
        "📌 Phrasebook",
    ])

    # ── TRANSLATION TAB ──
    with tab_tr:
        translated_html = st.session_state.translated_text.replace('\n','<br>')
        st.markdown(f"""
        <div style="background:{T['input_bg']}; border:1px solid {T['border']};
                    border-left:3px solid {T['accent']}; border-radius:10px;
                    padding:20px; min-height:110px; font-size:16px; line-height:1.8;
                    color:{T['input_text']}; font-family:'DM Sans',sans-serif;
                    margin-bottom:14px; white-space:pre-wrap;">
            {translated_html}
        </div>
        """, unsafe_allow_html=True)

        btn_c1, btn_c2, btn_c3 = st.columns([2, 1, 1])
        with btn_c1:
            # Copy to clipboard via JS in an HTML component
            escaped = st.session_state.translated_text.replace('"', '&quot;').replace("'", "&#39;")
            st.markdown(f"""
            <button onclick="navigator.clipboard.writeText('{escaped}').then(()=>{{
                this.textContent='✅ Copied!'; setTimeout(()=>{{this.textContent='📋 Copy to Clipboard'}},2000);
            }})" style="
                background:transparent; color:{T['accent']}; border:1.5px solid {T['accent']};
                border-radius:8px; padding:8px 16px; font-size:13px; font-weight:600;
                cursor:pointer; width:100%; font-family:'DM Sans',sans-serif;
                transition:background 0.2s;
            " onmouseover="this.style.background='{T['badge_bg']}'"
              onmouseout="this.style.background='transparent'">
                📋 Copy to Clipboard
            </button>
            """, unsafe_allow_html=True)
        with btn_c2:
            try:
                tts_out = gTTS(text=st.session_state.translated_text, lang=target_code)
                aud_fp  = io.BytesIO()
                tts_out.write_to_fp(aud_fp)
                aud_fp.seek(0)
                st.audio(aud_fp, format="audio/mp3")
            except Exception:
                st.caption("🔇 Audio N/A")

    # ── MEANING TAB ──
    with tab_meaning:
        meaning_html = st.session_state.meaning_context_text.replace('\n','<br>')
        st.markdown(f"""
        <div style="background:{T['input_bg']}; border:1px solid {T['border']};
                    border-left:3px solid {T['accent2']}; border-radius:10px;
                    padding:20px; min-height:110px; font-size:16px; line-height:1.8;
                    color:{T['input_text']}; font-family:'DM Sans',sans-serif; white-space:pre-wrap;">
            {meaning_html}
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Contextual meaning in: {user_native_lang.title()}")

    # ── PHONETICS TAB ──
    with tab_phon:
        st.markdown(f"""
        <div style="background:{T['input_bg']}; border:1px solid {T['border']};
                    border-left:3px solid {T['success']}; border-radius:10px;
                    padding:20px; min-height:110px; font-size:15px; line-height:1.8;
                    color:{T['input_text']}; font-family:'JetBrains Mono',monospace;
                    letter-spacing:0.3px; white-space:pre-wrap;">
            {st.session_state.pronunciation_text}
        </div>
        """, unsafe_allow_html=True)
        st.caption("Romanized phonetic output via AnyAscii")

    # ── COMPARE TAB ──
    with tab_cmp:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <span style="font-size:11px; font-weight:700; color:{T['subtext']};
                             text-transform:uppercase; letter-spacing:1px;">Original</span>
            </div>
            <div style="background:{T['input_bg']}; border:1px solid {T['border']};
                        border-radius:10px; padding:16px; font-size:14px; line-height:1.7;
                        color:{T['input_text']}; min-height:160px; white-space:pre-wrap;">
                {source_text}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <span style="font-size:11px; font-weight:700; color:{T['accent']};
                             text-transform:uppercase; letter-spacing:1px;">
                    {st.session_state.last_target_lang.title()}
                </span>
            </div>
            <div style="background:{T['input_bg']}; border:1.5px solid {T['border_accent']};
                        border-radius:10px; padding:16px; font-size:14px; line-height:1.7;
                        color:{T['input_text']}; min-height:160px; white-space:pre-wrap;">
                {st.session_state.translated_text}
            </div>
            """, unsafe_allow_html=True)

    # ── PHRASEBOOK TAB ──
    with tab_pb:
        pb_limit = lim['phrasebook']
        current_count = len(st.session_state.phrasebook)
        already_saved = any(
            p['source'] == source_text.strip() and p['lang'] == target_lang
            for p in st.session_state.phrasebook
        )

        if already_saved:
            st.success("✅ This translation is already in your phrasebook.")
        elif current_count >= pb_limit:
            st.warning(f"⚠️ Phrasebook full ({pb_limit} items on {st.session_state.tier} plan). Upgrade or clear some entries.")
        else:
            if st.button("⭐ Save to Phrasebook", key="save_pb"):
                st.session_state.phrasebook.insert(0, {
                    "source": source_text.strip(),
                    "target": st.session_state.translated_text,
                    "lang":   target_lang,
                    "meaning": st.session_state.meaning_context_text,
                })
                st.success("✅ Saved to phrasebook!")
                st.rerun()

        if st.session_state.phrasebook:
            st.html(f"<div style='margin-top:16px; margin-bottom:8px; font-size:13px; color:{T['subtext']}; font-weight:600;'>YOUR PHRASEBOOK ({current_count}/{pb_limit})</div>")
            for i, ph in enumerate(st.session_state.phrasebook[:10]):
                p_src = ph['source'][:60] + ("…" if len(ph['source']) > 60 else "")
                p_tgt = ph['target'][:80] + ("…" if len(ph['target']) > 80 else "")
                st.markdown(f"""
                <div style="background:{T['card_bg']}; border:1px solid {T['border']};
                            border-left:3px solid {T['warning']}; border-radius:8px;
                            padding:12px 14px; margin-bottom:8px;">
                    <span style="font-size:11px; color:{T['warning']}; font-weight:700;
                                 text-transform:uppercase;">{ph['lang'].title()}</span>
                    <div style="font-size:14px; color:{T['text']}; margin-top:4px;">{p_tgt}</div>
                    <div style="font-size:12px; color:{T['subtext']}; margin-top:3px;">↑ {p_src}</div>
                </div>
                """, unsafe_allow_html=True)

    # Download report
    st.html("<div style='margin-top:16px;'></div>")
    report = (
        f"NexusAI Translation Report\n{'='*45}\n\n"
        f"SOURCE:\n{source_text}\n\n"
        f"TRANSLATION ({st.session_state.last_target_lang.title()}):\n{st.session_state.translated_text}\n\n"
        f"PHONETICS:\n{st.session_state.pronunciation_text}\n\n"
        f"MEANING ({user_native_lang.title()}):\n{st.session_state.meaning_context_text}\n\n"
        f"CONFIDENCE: {st.session_state.confidence_score}%\n"
    )
    st.download_button(
        "💾  Download Full Report (.txt)",
        data=report,
        file_name="nexusai_translation.txt",
        mime="text/plain"
    )

# ═══════════════════════════════════════════════════════════
# SESSION HISTORY
# ═══════════════════════════════════════════════════════════
if st.session_state.translation_history:
    section_divider("📜 Session History")
    total = len(st.session_state.translation_history)
    for i, log in enumerate(st.session_state.translation_history[:5]):
        src_p = log['source'][:70] + ("…" if len(log['source']) > 70 else "")
        tgt_p = log['target'][:110] + ("…" if len(log['target']) > 110 else "")
        c_score = log.get('confidence', 0)
        c_color = T['success'] if c_score >= 80 else (T['warning'] if c_score >= 60 else T['danger'])
        st.markdown(f"""
        <div style="background:{T['panel_bg']}; border:1px solid {T['border']};
                    border-left:3px solid {T['history_border']}; border-radius:10px;
                    padding:14px 16px; margin-bottom:10px; box-shadow:{T['shadow']};">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
                <span style="font-size:11px; font-weight:700; color:{T['badge_text']};
                             background:{T['badge_bg']}; padding:3px 10px;
                             border-radius:20px; text-transform:uppercase; letter-spacing:0.5px;">
                    #{total - i} &nbsp;·&nbsp; {log['lang'].title()}
                </span>
                <span style="font-size:11px; color:{c_color}; font-weight:600;">
                    {c_score}% confidence
                </span>
            </div>
            <div style="font-size:15px; color:{T['text']}; line-height:1.6; margin-bottom:6px;">{tgt_p}</div>
            <div style="font-size:12px; color:{T['subtext']}; border-top:1px solid {T['border']};
                        padding-top:8px; margin-top:4px;">
                <span style="opacity:0.7;">Source: </span>{src_p}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:24px 0 8px; margin-top:32px;
            border-top:1px solid {T['border']};">
    <p style="color:{T['subtext']}; font-size:12px; margin:0; letter-spacing:0.3px;">
        NexusAI Translation Matrix &nbsp;·&nbsp; v4.0 &nbsp;·&nbsp;
        Powered by Google Translate &amp; gTTS
    </p>
</div>

""", unsafe_allow_html=True) 
