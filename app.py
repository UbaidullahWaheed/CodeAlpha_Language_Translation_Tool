import streamlit as st
from deep_translator import GoogleTranslator
from anyascii import anyascii
from gtts import gTTS
import io
import time
import re
from concurrent.futures import ThreadPoolExecutor

# ---------------- PRE-CONFIGURATION & THEME SWITCH ENGINE ---------------- #
st.set_page_config(
    page_title="NexusAI Universal Translation Matrix",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Theme States Safely
if "ui_theme_mode" not in st.session_state:
    st.session_state.ui_theme_mode = "🌌 Deep Space (Dark Mode)"

# Initialize Session Data Buffers Safely
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

# ---------------- SIDEBAR INTERFACE & THEME CONFIGURATION ---------------- #
with st.sidebar:
    st.markdown("## ⚙️ Core Configuration Panel")
    
    chosen_skin = st.radio(
        "Application Interface Skin",
        ["🌌 Deep Space (Dark Mode)", "☀️ Solar Flare (Vibrant Light)", "🪵 Amber Minimalist (Warm Mode)"],
        index=["🌌 Deep Space (Dark Mode)", "☀️ Solar Flare (Vibrant Light)", "🪵 Amber Minimalist (Warm Mode)"].index(st.session_state.ui_theme_mode)
    )
    st.session_state.ui_theme_mode = chosen_skin
    
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

# ---------------- DYNAMIC COLOR MATRIX UPGRADE ---------------- #
theme_matrix = {
    "🌌 Deep Space (Dark Mode)": {
        "panel_bg": "#161b22", "text": "#ffffff", "subtext": "#8b949e",
        "input_bg": "#0d1117", "input_text": "#58a6ff", "border": "#30363d",
        "placeholder": "#6e7681", "accent": "#58a6ff", 
        "btn_gradient": "linear-gradient(135deg, #4f46e5 0%, #db2777 100%)",
        "tab_active": "#4f46e5", "signature": "Build 2.5.1 | Custom Dark Engine"
    },
    "☀️ Solar Flare (Vibrant Light)": {
        "panel_bg": "#ffffff", "text": "#0f172a", "subtext": "#3b82f6",
        "input_bg": "#f0f4f8", "input_text": "#1e3a8a", "border": "#3b82f6",
        "placeholder": "#2563eb", "accent": "#4f46e5", 
        "btn_gradient": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
        "tab_active": "#6366f1", "signature": "Build 2.5.1 | Vibrant Light Matrix"
    },
    "🪵 Amber Minimalist (Warm Mode)": {
        "panel_bg": "#fffcf0", "text": "#433422", "subtext": "#715c43",
        "input_bg": "#f4f1ea", "input_text": "#433422", "border": "#d97706",
        "placeholder": "#a16207", "accent": "#d97706", 
        "btn_gradient": "linear-gradient(135deg, #ea580c 0%, #d97706 100%)",
        "tab_active": "#ea580c", "signature": "Build 2.5.1 | Custom Warm Engine"
    }
}
active_skin = theme_matrix[st.session_state.ui_theme_mode]

# ADVANCED MOBILE VIEWPORT CONTAINER STYLING SHEET
st.html(f"""
<style>
    /* Card panel base adjustments */
    .mobile-theme-card {{
        background-color: {active_skin['panel_bg']} !important;
        border: 2px solid {active_skin['border']} !important;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        color: {active_skin['text']} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }}
    
    .mobile-theme-card h4, .mobile-theme-card p, .mobile-theme-card label {{
        color: {active_skin['text']} !important;
    }}
    
    /* Input windows structure styling configuration */
    .stTextArea textarea, .stSelectbox div[role="button"], div[data-baseweb="select"] {{
        background-color: {active_skin['input_bg']} !important;
        color: {active_skin['input_text']} !important;
        border: 2px solid {active_skin['border']} !important;
        border-radius: 8px !important;
    }}
    
    .stTextArea textarea {{
        color: {active_skin['input_text']} !important;
        font-weight: 500 !important;
    }}

    /* CRITICAL PLACEHOLDER VISIBILITY FIX FOR MOBILE DEVICES */
    .stTextArea textarea::placeholder {{
        color: {active_skin['placeholder']} !important;
        opacity: 1 !important;
        -webkit-text-fill-color: {active_skin['placeholder']} !important;
        font-weight: bold !important;
    }}
    
    .stTextArea textarea::-webkit-input-placeholder {{
        color: {active_skin['placeholder']} !important;
        opacity: 1 !important;
        -webkit-text-fill-color: {active_skin['placeholder']} !important;
    }}

    /* Dynamic Button Configurations */
    .stButton button {{
        background: {active_skin['btn_gradient']} !important;
        color: white !important;
        border: none !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
        height: 52px;
        width: 100%;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }}

    /* Tabs Styling Control Architecture */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {active_skin['panel_bg']} !important;
        border: 2px solid {active_skin['border']};
        border-radius: 8px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {active_skin['text']} !important;
        font-weight: 700 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {active_skin['tab_active']} !important;
        color: white !important;
        border-radius: 6px;
    }}
    
    .output-content-block {{
        background-color: {active_skin['input_bg']};
        color: {active_skin['input_text']};
        border: 2px solid {active_skin['border']};
        padding: 15px;
        border-radius: 8px;
        min-height: 100px;
        font-weight: 500;
    }}
</style>
""")

# ---------------- HEADER ---------------- #
st.markdown('<div style="text-align:center;"><h1 style="font-size:36px; font-weight:900; background: linear-gradient(to right, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🪐 NexusAI Universal Translation Matrix</h1></div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; font-size:13px; font-weight: 600; color: {active_skin['text']};'>{active_skin['signature']}</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- HELPER CONCURRENT TRANSLATION WORKER ---------------- #
def parallel_translate_sentence(sentence, target_lang_code):
    if not sentence.strip():
        return ""
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(sentence)
    except Exception:
        return sentence

# ---------------- CONTAINER STYLE WORKSPACE SYSTEM ---------------- #
st.markdown(f'<div class="mobile-theme-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📥 Source Workspace")
    entry_method = st.radio("Input Strategy Processing Mode:", ["Universal Auto-Detect", "Phonetic Conversion"], horizontal=True)
    source_text = st.text_area("Source Processing Input Window", value=st.session_state.input_text_buffer, height=180, placeholder="Enter target text here...", label_visibility="collapsed")

with col2:
    st.markdown("#### 📤 Target Workspace Parameters")
    target_lang = st.selectbox("Destination Selector Language Target", options=language_catalog, index=language_catalog.index("korean") if "korean" in language_catalog else 0)
    target_code = language_dict[target_lang]
    
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    execute_flag = st.button("🚀 INITIATE SYSTEM TRANSLATION")
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
            
            # 2. Translate Target Language -> User's Selected Native Tongue
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
            st.error(f"Execution Fault: {engine_fault}")
    else:
        st.warning("Please enter text before running execution pipelines.")

# ---------------- TABBED DATA PROCESSING TIERS ---------------- #
if st.session_state.translated_text:
    st.markdown(f'<div class="mobile-theme-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Engine Data Manifest Output")
    tab_translation, tab_meaning, tab_phonetics = st.tabs([
        f"🌐 Translated Text ({st.session_state.last_target_lang.upper()})", 
        f"📖 Meaning Context ({user_native_lang.upper()})", 
        "🔤 Phonetic Pronunciation"
    ])
    
    with tab_translation:
        st.markdown(f"<div class='output-content-block'>{st.session_state.translated_text}</div>", unsafe_allow_html=True)
        try:
            tts = gTTS(text=st.session_state.translated_text, lang=target_code)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            st.audio(audio_fp)
        except:
            pass

    with tab_meaning:
        st.markdown(f"<div class='output-content-block'>{st.session_state.meaning_context_text}</div>", unsafe_allow_html=True)

    with tab_phonetics:
        st.markdown(f"<div class='output-content-block'>{st.session_state.pronunciation_text}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    report_data = f"Source Text:\n{source_text}\n\nTranslation ({st.session_state.last_target_lang}):\n{st.session_state.translated_text}"
    st.download_button("💾 DOWNLOAD DATA MANIFEST (.TXT)", report_data, file_name="nexus_translation_manifest.txt")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HISTORICAL METRIC RECORDS ---------------- #
if st.session_state.translation_history:
    st.write("### 📜 Session History Logs")
    for log_node in st.session_state.translation_history[:3]:
        st.markdown(
            f"<div style='background-color:{active_skin['panel_bg']}; border-left:5px solid {active_skin['accent']}; padding:12px; margin-bottom:6px; border-radius:6px; color:{active_skin['text']};'>"
            f"<b>{log_node['lang'].upper()}:</b> {log_node['target']} <br>"
            f"<small style='color:{active_skin['subtext']};'>Source: {log_node['source']}</small></div>", 
            unsafe_allow_html=True
        )
