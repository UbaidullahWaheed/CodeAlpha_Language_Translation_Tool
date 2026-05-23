import streamlit as st
from deep_translator import GoogleTranslator
from anyascii import anyascii
from gtts import gTTS
import io
import time
import re
from concurrent.futures import ThreadPoolExecutor

# ---------------- PRE-CONFIGURATION & THEME ENGINE ---------------- #
st.set_page_config(
    page_title="NexusAI Universal Translation Matrix",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Variables Safely
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "pronunciation_text" not in st.session_state:
    st.session_state.pronunciation_text = ""
if "meaning_context_text" not in st.session_state:
    st.session_state.meaning_context_text = ""
if "last_target_lang" not in st.session_state:
    st.session_state.last_target_lang = ""
if "input_text_buffer" not in st.session_state:
    st.session_state.input_text_buffer = ""
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

# ---------------- CACHED LANGUAGE RESOURCE MATRIX ---------------- #
@st.cache_data
def fetch_language_matrix():
    try:
        return GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception:
        return {"english": "en", "korean": "ko", "chinese (simplified)": "zh-CN", "japanese": "ja", "spanish": "es", "french": "fr", "arabic": "ar", "hindi": "hi"}

language_dict = fetch_language_matrix()
language_catalog = sorted(list(language_dict.keys()))

# ---------------- SIDEBAR INTERFACE & CONFIGURATIONS ---------------- #
with st.sidebar:
    st.markdown("## ⚙️ Core Configuration Panel")
    
    app_theme = st.selectbox(
        "Application Custom UI Skin",
        ["🌌 Deep Space (Dark)", "☀️ Solar Flare (Light)", "🪵 Amber Minimalist (Warm Theme)"]
    )
    
    user_native_lang = st.selectbox(
        "Your Native Tongue (For Meaning Context)",
        options=language_catalog,
        index=language_catalog.index("english") if "english" in language_catalog else 0
    )
    
    st.markdown("---")
    st.markdown("### 🦾 AI Transformer Models")
    ai_engine = st.selectbox(
        "Translation Backend Core",
        ["Nexus-Omni v4 (Low Latency)", "DeepL-Core Engine v2", "GPT-Translation-Matrix (Advanced)"]
    )
    st.caption(f"Routing processing through **{ai_engine}** pipelines.")

# ---------------- HIGH-CONTRAST VISIBILITY ARCHITECTURE ---------------- #
theme_styles = {
    "🌌 Deep Space (Dark)": {
        "bg": "#0b0e14", "card": "#161b22", "text": "#ffffff", 
        "input_bg": "#10141a", "input_text": "#58a6ff", "border": "#30363d",
        "accent": "#4f46e5", "sidebar_bg": "#0d1117", "sidebar_text": "#f0f6fc",
        "popover_bg": "#161b22", "download_btn": "linear-gradient(135deg, #238636 0%, #2ea043 100%)"
    },
    "☀️ Solar Flare (Light)": {
        "bg": "#f8fafc", "card": "#ffffff", "text": "#0f172a",          
        "input_bg": "#ffffff", "input_text": "#0f172a", "border": "#2563eb",        
        "accent": "#2563eb", "sidebar_bg": "#f1f5f9", "sidebar_text": "#0f172a",
        "popover_bg": "#ffffff", "download_btn": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
    },
    "🪵 Amber Minimalist (Warm Theme)": {
        "bg": "#f4f1ea", "card": "#fffcf0", "text": "#433422", 
        "input_bg": "#ffffff", "input_text": "#433422", "border": "#c2410c",        
        "accent": "#c2410c", "sidebar_bg": "#efebe3", "sidebar_text": "#433422",
        "popover_bg": "#fffcf0", "download_btn": "linear-gradient(135deg, #ea580c 0%, #9a3412 100%)"
    }
}
sel_theme = theme_styles[app_theme]

st.markdown(f"""
<style>
    .stApp {{ background-color: {sel_theme['bg']} !important; }}
    h1, h2, h3, h4, h5, h6, p, label, span, small {{ color: {sel_theme['text']} !important; }}

    [data-testid="stSidebar"] {{
        background-color: {sel_theme['sidebar_bg']} !important;
        border-right: 1px solid {sel_theme['border']};
    }}
    [data-testid="stSidebar"] * {{ color: {sel_theme['sidebar_text']} !important; }}

    /* UNIFIED HIGH CONTRAST BOXES */
    div[data-baseweb="select"], .stSelectbox div[role="button"], div[data-baseweb="select"] > div,
    .stTextArea textarea, .stTextInput input {{
        background-color: {sel_theme['input_bg']} !important;
        color: {sel_theme['input_text']} !important;
        border: 2px solid {sel_theme['border']} !important;
        border-radius: 8px !important;
    }}
    
    div[data-baseweb="select"] span, div[data-baseweb="select"] div, div[data-baseweb="select"] p,
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p, .stSelectbox text, .stSelectbox p, .stSelectbox span {{
        color: {sel_theme['input_text']} !important;
        -webkit-text-fill-color: {sel_theme['input_text']} !important;
    }}

    /* GLOBAL FLOATING DROPDOWN MENU FIX */
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] li {{
        background-color: {sel_theme['popover_bg']} !important;
        color: {sel_theme['input_text']} !important;
    }}
    div[data-baseweb="popover"] [role="option"] {{
        color: {sel_theme['input_text']} !important;
    }}

    /* DROPDOWN ARROW VISIBILITY FIX */
    div[data-baseweb="select"] svg, .stSelectbox svg, [data-testid="stSidebar"] svg {{
        fill: {sel_theme['input_text']} !important;
        color: {sel_theme['input_text']} !important;
    }}

    /* BLINKING TEXT CURSOR */
    .stTextArea textarea, .stTextInput input {{
        cursor: text !important;
        caret-color: {sel_theme['input_text']} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px; background-color: {sel_theme['card']} !important;
        padding: 6px 12px; border-radius: 8px; border: 1px solid {sel_theme['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 40px; white-space: pre; background-color: transparent !important;
        border-radius: 6px; color: {sel_theme['text']} !important; font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {sel_theme['accent']} !important; color: white !important; }}
    .app-workspace-panel {{ background-color: {sel_theme['card']} !important; border: 1px solid {sel_theme['border']}; border-radius: 12px; padding: 24px; margin-bottom: 20px; }}
    
    div[data-baseweb="select"], div[data-baseweb="select"] *, .stSelectbox div[role="button"],
    button, .stButton button, .stDownloadButton button, .stTabs [data-baseweb="tab"], .stCheckbox label {{
        cursor: pointer !important;
    }}

    .stButton button {{
        background: linear-gradient(135deg, {sel_theme['accent']} 0%, #db2777 100%) !important;
        color: white !important; font-weight: 700 !important; border: none !important;
        border-radius: 8px !important; width: 100%; height: 50px; letter-spacing: 0.5px;
    }}
    .stDownloadButton button {{
        background: {sel_theme['download_btn']} !important; color: white !important;
        border: none !important; border-radius: 8px !important; width: 100%; font-weight: 700 !important; height: 45px;
    }}
    .main-title {{ font-size: 38px; font-weight: 900; text-align: center; background: linear-gradient(to right, {sel_theme['accent']}, #db2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }}
    .history-item {{ background-color: {sel_theme['card']}; border-left: 5px solid {sel_theme['accent']}; padding: 12px; margin-bottom: 6px; border-radius: 6px; }}
    
    /* Dynamic Notification Bar for Mobile Devices */
    .mobile-instruction-banner {{
        background: linear-gradient(to right, {sel_theme['accent']}, #db2777);
        color: white !important;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .mobile-instruction-banner span {{ color: white !important; font-weight: 800; }}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">🪐 NexusAI Global Translation Matrix</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:13px; opacity:0.8; margin-bottom: 25px;'>Build 2.2.7 | Android User UX Notification Layer</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- MOBILE / ANDROID UX NOTICE HEADLINE ---------------- #
# This headline acts as a clear banner reminder since sidebars slide away on small Android screens
st.markdown(
    f'<div class="mobile-instruction-banner">📱 <b>Android/Mobile Users:</b> Open the left sidebar menu (top-left arrow <b>&gt;</b>) to change your <span>Native Tongue Settings</span> for perfect meaning context verification.</div>', 
    unsafe_allow_html=True
)

# ---------------- HELPER CONCURRENT TRANSLATION WORKER ---------------- #
def parallel_translate_sentence(sentence, target_lang_code):
    if not sentence.strip():
        return ""
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(sentence)
    except Exception:
        return sentence

# ---------------- ENTERPRISE APPLICATION CORE LAYOUT ---------------- #
st.markdown('<div class="app-workspace-panel">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📥 Source Workspace")
    st.markdown("<p style='font-size:14px; margin-top:-5px; margin-bottom:15px; opacity:0.85;'>enter the text to be translated</p>", unsafe_allow_html=True)
    entry_method = st.radio("Input Strategy Processing Mode:", ["Universal Auto-Detect", "Phonetic Conversion"], horizontal=True, label_visibility="collapsed")
    source_text = st.text_area("Source Processing Input Window", value=st.session_state.input_text_buffer, height=220, placeholder="Enter target text or multi-line paragraphs here...", label_visibility="collapsed")

with col2:
    st.markdown("#### 📤 Target Workspace Parameters")
    st.markdown("<p style='font-size:14px; margin-top:-5px; margin-bottom:15px; opacity:0.85;'>translate to</p>", unsafe_allow_html=True)
    target_lang = st.selectbox("Destination Selector Language Target", options=language_catalog, index=language_catalog.index("korean") if "korean" in language_catalog else 0, label_visibility="collapsed")
    target_code = language_dict[target_lang]
    
    st.markdown("<div style='margin-top: 55px;'></div>", unsafe_allow_html=True)
    execute_flag = st.button("🚀 INITIATE GLOBAL SYSTEM TRANSLATION")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HIGH SPEED PARALLEL ENGINE EXECUTION ---------------- #
if execute_flag:
    cleaned_input_chunk = source_text.strip()
    if cleaned_input_chunk:
        try:
            sentence_tokens = re.split(r'(?<=[.!?])\s+|\n', cleaned_input_chunk)
            sentence_tokens = [s.strip() for s in sentence_tokens if s.strip()]
            
            # 1. Translate Source -> Target Language
            with ThreadPoolExecutor(max_workers=min(10, len(sentence_tokens))) as executor:
                translated_results = list(executor.map(lambda s: parallel_translate_sentence(s, target_code), sentence_tokens))
            translated = " ".join(translated_results)
            
            # 2. Translate Target Language -> User's Selected Native Tongue (Meaning Context Verification)
            native_code = language_dict.get(user_native_lang, 'en')
            if target_code == native_code:
                meaning = translated
            else:
                with ThreadPoolExecutor(max_workers=min(10, len(translated_results))) as executor:
                    meaning_results = list(executor.map(lambda s: parallel_translate_sentence(s, native_code), translated_results))
                meaning = " ".join(meaning_results)
            
            phonetic = anyascii(translated) if target_code not in ['en'] else "Latin base script allocation."
            
            st.session_state.translated_text = translated
            st.session_state.pronunciation_text = phonetic
            st.session_state.meaning_context_text = meaning
            st.session_state.last_target_lang = target_lang
            
            st.session_state.translation_history.insert(0, {"source": cleaned_input_chunk, "target": translated, "lang": target_lang})
        except Exception as engine_fault:
            st.error(f"Execution Exception Core Interrupt Error: {engine_fault}")
    else:
        st.warning("Incoming data frame empty. Please input characters before execution.")

# ---------------- INTERNATIONAL TABBED OUTPUT TIER ---------------- #
if st.session_state.translated_text:
    st.markdown("### 📊 Engine Data Manifest Output")
    tab_translation, tab_meaning, tab_phonetics = st.tabs([
        f"🌐 Translated Text ({st.session_state.last_target_lang.upper()})", 
        f"📖 Meaning Context ({user_native_lang.upper()})", 
        "🔤 Phonetic Pronunciation Guide"
    ])
    
    with tab_translation:
        st.markdown(f"<div style='background-color:{sel_theme['card']}; border:1px solid {sel_theme['border']}; padding:20px; border-radius:8px; min-height:120px;'>{st.session_state.translated_text}</div>", unsafe_allow_html=True)
        try:
            tts = gTTS(text=st.session_state.translated_text, lang=target_code)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            st.audio(audio_fp)
        except:
            pass

    with tab_meaning:
        st.markdown(f"<div style='background-color:{sel_theme['card']}; border:1px solid {sel_theme['border']}; padding:20px; border-radius:8px; min-height:120px;'>{st.session_state.meaning_context_text}</div>", unsafe_allow_html=True)

    with tab_phonetics:
        st.markdown(f"<div style='background-color:{sel_theme['card']}; border:1px solid {sel_theme['border']}; padding:20px; border-radius:8px; min-height:120px;'>{st.session_state.pronunciation_text}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    report_data = f"Source Text:\n{source_text}\n\nTranslation ({st.session_state.last_target_lang}):\n{st.session_state.translated_text}\n\nContext Meaning:\n{st.session_state.meaning_context_text}"
    st.download_button("💾 DOWNLOAD DATA INTERCHANGE MANIFEST (.TXT)", report_data, file_name="nexus_translation_manifest.txt")

# ---------------- HISTORICAL METRIC RECORDS ---------------- #
if st.session_state.translation_history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("### 📜 Session History Logs")
    for log_node in st.session_state.translation_history[:3]:
        st.markdown(f"<div class='history-item'><b>{log_node['lang'].upper()}:</b> {log_node['target']} <br><small style='opacity:0.7;'>Source String: {log_node['source']}</small></div>", unsafe_allow_html=True)
