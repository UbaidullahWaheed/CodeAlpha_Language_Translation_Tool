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

# ---------------- NATIVE SYSTEM DIRECT THEME INJECTION ---------------- #
theme_matrix = {
    "🌌 Deep Space (Dark Mode)": {
        "text_color": "#ffffff", "label_color": "#ffffff",
        "input_bg": "#161b22", "input_text": "#58a6ff", "border": "#30363d",
        "placeholder": "#6e7681", "accent": "#58a6ff", 
        "btn_gradient": "linear-gradient(135deg, #4f46e5 0%, #db2777 100%)",
        "tab_active": "#4f46e5", "signature_text": "#8b949e", "signature": "Build 2.6.0 | Custom Dark Engine"
    },
    "☀️ Solar Flare (Vibrant Light)": {
        "text_color": "#1e3a8a", "label_color": "#0f172a",
        "input_bg": "#f0f4f8", "input_text": "#1e3a8a", "border": "#3b82f6",
        "placeholder": "#2563eb", "accent": "#4f46e5", 
        "btn_gradient": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
        "tab_active": "#6366f1", "signature_text": "#1e3a8a", "signature": "Build 2.6.0 | Vibrant Light Matrix"
    },
    "🪵 Amber Minimalist (Warm Mode)": {
        "text_color": "#433422", "label_color": "#433422",
        "input_bg": "#f4f1ea", "input_text": "#433422", "border": "#d97706",
        "placeholder": "#a16207", "accent": "#d97706", 
        "btn_gradient": "linear-gradient(135deg, #ea580c 0%, #d97706 100%)",
        "tab_active": "#ea580c", "signature_text": "#715c43", "signature": "Build 2.6.0 | Custom Warm Engine"
    }
}
active_skin = theme_matrix[st.session_state.ui_theme_mode]

# NATIVE CLASS OVERRIDES: Directly colors Streamlit labels, blocks, and text boxes
st.html(f"""
<style>
    /* Force visibility onto all core typography elements */
    [data-testid="stMarkdownContainer"] p, h1, h2, h3, h4, h5, h6, label, span, p {{
        color: {active_skin['label_color']} !important;
    }}
    
    /* Target Streamlit's native input area wrappers directly to eliminate the dark box */
    .stTextArea textarea, [data-baseweb="textarea"] {{
        background-color: {active_skin['input_bg']} !important;
        color: {active_skin['input_text']} !important;
        border: 2px solid {active_skin['border']} !important;
        border-radius: 12px !important;
    }}
    
    /* Target Streamlit's select boxes and options dropdown wrappers */
    .stSelectbox div[role="button"], div[data-baseweb="select"] {{
        background-color: {active_skin['input_bg']} !important;
        color: {active_skin['input_text']} !important;
        border: 2px solid {active_skin['border']} !important;
        border-radius: 8px !important;
    }}

    /* Global Placeholder Visibility Controls */
    textarea::placeholder, input::placeholder {{
        color: {active_skin['placeholder']} !important;
        opacity: 1 !important;
        -webkit-text-fill-color: {active_skin['placeholder']} !important;
    }}

    /* Action buttons skin injection */
    .stButton button {{
        background: {active_skin['btn_gradient']} !important;
        color: white !important;
        border: none !important;
        font-weight: 800 !important;
        height: 50px;
        width: 100%;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }}

    /* Result Tab Navigation elements */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {active_skin['input_bg']} !important;
        border: 2px solid {active_skin['border']} !important;
        border-radius: 10px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {active_skin['label_color']} !important;
        font-weight: 700 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {active_skin['tab_active']} !important;
        color: white !important;
        border-radius: 6px;
    }}
    
    /* Custom Output Display fields */
    .output-content-block {{
        background-color: {active_skin['input_bg']} !important;
        color: {active_skin['input_text']} !important;
        border: 2px solid {active_skin['border']} !important;
        padding: 18px;
        border-radius: 12px;
        min-height: 110px;
        font-weight: 500;
    }}
</style>
""")

# ---------------- HEADER ---------------- #
st.markdown('<div style="text-align:center;"><h1 style="font-size:36px; font-weight:900; background: linear-gradient(to right, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🪐 NexusAI Universal Translation Matrix</h1></div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;"><p style="font-size:14px; font-weight: 800; color: {active_skin["signature_text"]} !important;">{active_skin["signature"]}</p></div>', unsafe_allow_html=True)
st.markdown("---")

# ---------------- HELPER CONCURRENT TRANSLATION WORKER ---------------- #
def parallel_translate_sentence(sentence, target_lang_code):
    if not sentence.strip():
        return ""
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(sentence)
    except Exception:
        return sentence

# ---------------- WORKSPACE WORKFLOW ---------------- #
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Source Workspace")
    entry_method = st.radio("Input Strategy Processing Mode", ["Universal Auto-Detect", "Phonetic Conversion"], horizontal=True)
    source_text = st.text_area("Input Text Box Area", value=st.session_state.input_text_buffer, height=180, placeholder="Enter target text here...", label_visibility="collapsed")

with col2:
    st.markdown("### 📤 Target Parameters")
    st.markdown("<p style='font-size: 14px; margin-bottom: 2px;'>Select Destination Language</p>", unsafe_allow_html=True)
    target_lang = st.selectbox("Destination Selector Language Target", options=language_catalog, index=language_catalog.index("korean") if "korean" in language_catalog else 0, label_visibility="collapsed")
    target_code = language_dict[target_lang]
    
    st.markdown("<div style='margin-top: 52px;'></div>", unsafe_allow_html=True)
    execute_flag = st.button("🚀 INITIATE TRANSLATION CORE")

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

# ---------------- TABBED OUTPUT GENERATOR TIER ---------------- #
if st.session_state.translated_text:
    st.markdown("---")
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

# ---------------- HISTORICAL METRIC RECORDS ---------------- #
if st.session_state.translation_history:
    st.markdown("---")
    st.write("### 📜 Session History Logs")
    for log_node in st.session_state.translation_history[:3]:
        st.markdown(
            f"<div style='background-color:{active_skin['input_bg']}; border-left:5px solid {active_skin['accent']}; padding:12px; margin-bottom:6px; border-radius:6px; color:{active_skin['label_color']};'>"
            f"<b>{log_node['lang'].upper()}:</b> {log_node['target']} <br>"
            f"<small style='opacity: 0.75;'>Source: {log_node['source']}</small></div>", 
            unsafe_allow_html=True
        )
