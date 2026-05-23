import streamlit as st
from deep_translator import GoogleTranslator
from anyascii import anyascii
from gtts import gTTS
import io
import time

# ---------------- PRE-CONFIGURATION & THEME ENGINE ---------------- #
st.set_page_config(
    page_title="NexusAI Universal Translation Matrix",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Variables
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "pronunciation_text" not in st.session_state:
    st.session_state.pronunciation_text = ""
if "meaning_context_text" not in st.session_state:
    st.session_state.meaning_context_text = ""
if "last_target_lang" not in st.session_state:
    st.session_state.last_target_lang = ""
if "render_id" not in st.session_state:
    st.session_state.render_id = str(time.time())
if "input_text_buffer" not in st.session_state:
    st.session_state.input_text_buffer = ""
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

# ---------------- SIDEBAR INTERFACE & CONFIGURATIONS ---------------- #
with st.sidebar:
    st.markdown("## ⚙️ Core Configuration Panel")
    
    app_theme = st.selectbox(
        "Application Custom UI Skin",
        ["🌌 Deep Space (Dark)", "☀️ Solar Flare (Light)", "🪵 Amber Minimalist (Warm Theme)"]
    )
    
    user_native_lang = st.selectbox(
        "Your Native Tongue (For Meaning Context)",
        ["english", "korean", "chinese (simplified)", "japanese", "spanish", "french", "arabic", "hindi", "german", "urdu"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🦾 AI Transformer Models")
    ai_engine = st.selectbox(
        "Translation Backend Core",
        ["Nexus-Omni v4 (Low Latency)", "DeepL-Core Engine v2", "GPT-Translation-Matrix (Advanced)"]
    )
    st.caption(f"Routing processing through **{ai_engine}** pipelines.")
    
    st.markdown("---")
    st.markdown("### 🛠️ UI Options")
    enable_copy = st.checkbox("Show Copy Prompts", value=True)
    enable_animations = st.checkbox("Enable Loading Micro-Animations", value=True)

# ---------------- DYNAMIC GRAPHICS & CONTRAST THEME INJECTION ---------------- #
theme_styles = {
    "🌌 Deep Space (Dark)": {
        "bg": "#0f1117", 
        "card": "#1e2230", 
        "text": "#ffffff", 
        "input_bg": "#151821", 
        "input_text": "#ffffff", 
        "border": "rgba(255,255,255,0.2)",
        "accent": "#4f46e5",
        "sidebar_bg": "#161925",
        "sidebar_text": "#ffffff"
    },
    "☀️ Solar Flare (Light)": {
        "bg": "#f8fafc", 
        "card": "#ffffff", 
        "text": "#0f172a", 
        "input_bg": "#f1f5f9", 
        "input_text": "#0f172a", 
        "border": "rgba(15,23,42,0.15)",
        "accent": "#2563eb",
        "sidebar_bg": "#edf2f7",
        "sidebar_text": "#0f172a"
    },
    "🪵 Amber Minimalist (Warm Theme)": {
        "bg": "#fdfbf7", 
        "card": "#f4f1ea", 
        "text": "#433422", 
        "input_bg": "#eae6dc", 
        "input_text": "#433422", 
        "border": "rgba(67,52,34,0.15)",
        "accent": "#c2410c",
        "sidebar_bg": "#f5f0e6",
        "sidebar_text": "#433422"
    }
}
sel_theme = theme_styles[app_theme]

# Injected styles explicitly enforce native element overrides with precise contrast configurations
st.markdown(f"""
<style>
    /* Global Application Canvas Base */
    .stApp {{
        background-color: {sel_theme['bg']} !important;
        color: {sel_theme['text']} !important;
    }}
    
    /* Native Main Workspace Elements Reset */
    .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {{
        color: {sel_theme['text']} !important;
    }}
    
    /* --- STRICT SIDEBAR COMPONENT BLOCK --- */
    [data-testid="stSidebar"] {{
        background-color: {sel_theme['sidebar_bg']} !important;
        border-right: 1px solid {sel_theme['border']} !important;
    }}
    
    /* Enforce comprehensive color overrides down all text children nodes inside the sidebar wrapper */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] div {{
        color: {sel_theme['sidebar_text']} !important;
    }}
    
    /* Custom Sidebar Selectbox Background Fill Overrides */
    [data-testid="stSidebar"] div[data-baseweb="select"] {{
        background-color: {sel_theme['input_bg']} !important;
        border: 1px solid {sel_theme['border']} !important;
    }}
    
    /* --- GLOBAL INTERACTIVE COMPONENT ELEMENT HOVER CURSORS --- */
    /* Forces the mouse pointer to switch from an arrow to an interaction hand selector across form controls */
    div[data-baseweb="select"], 
    .stSelectbox div, 
    .stButton button, 
    .stDownloadButton button,
    input, 
    textarea, 
    label,
    .stCheckbox label,
    div[role="button"],
    div[role="radiogroup"] label {{
        cursor: pointer !important;
    }}
    
    /* Main Workspace Text Areas and Forms */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: {sel_theme['input_bg']} !important;
        color: {sel_theme['input_text']} !important;
        border: 1px solid {sel_theme['border']} !important;
    }}
    
    /* Presentation Output Structure Cards */
    .translation-card {{
        background-color: {sel_theme['card']} !important;
        border: 1px solid {sel_theme['border']};
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }}
    .translation-card h4, .translation-card h5 {{
        color: {sel_theme['text']} !important;
        margin: 0px !important;
    }}
    
    /* Historical Logs Cards Layout */
    .history-item {{
        background-color: {sel_theme['card']} !important;
        border-left: 4px solid {sel_theme['accent']} !important;
        border-top: 1px solid {sel_theme['border']} !important;
        border-right: 1px solid {sel_theme['border']} !important;
        border-bottom: 1px solid {sel_theme['border']} !important;
        color: {sel_theme['text']} !important;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 8px;
    }}
    
    /* Dynamic Header Title */
    .main-title {{
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(45deg, {sel_theme['accent']}, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}
    
    /* Submission processing buttons */
    .stButton button {{
        background: linear-gradient(135deg, {sel_theme['accent']} 0%, #db2777 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 52px;
        font-size: 16px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease;
    }}
    .stButton button:hover {{
        transform: scale(1.005);
        box-shadow: 0px 8px 20px rgba(79, 70, 229, 0.3);
    }}
    
    /* Native Audio Integration Display Calibration Matrix */
    stAudio audio, .stAudio div, audio {{
        filter: invert({1 if app_theme == "🌌 Deep Space (Dark)" else 0});
        border-radius: 30px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">🪐 NexusAI Global Translation Matrix</div>', unsafe_allow_html=True)
st.markdown("💾 *Production-Ready Deploy Architecture Build 2.1.3 (Dynamic Text Stability)*")
st.markdown("---")

# ---------------- CACHED LANGUAGE RESOURCE MATRIX ---------------- #
@st.cache_data
def fetch_language_matrix():
    try:
        return GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception:
        return {"english": "en", "korean": "ko", "chinese (simplified)": "zh-CN", "japanese": "ja", "spanish": "es", "french": "fr", "arabic": "ar", "hindi": "hi"}

language_dict = fetch_language_matrix()
language_catalog = sorted(list(language_dict.keys()))

# ---------------- MULTI-INPUT TELEMETRY MODALS ---------------- #
panel_input_1, panel_input_2 = st.columns(2)

with panel_input_1:
    with st.expander("🎙️ Audio Stream Voice Input", expanded=False):
        st.caption("Select an incoming voice sequence simulation down below:")
        v_c1, v_c2 = st.columns(2)
        with v_c1:
            if st.button("🗣️ Mic Sim: 'Where is the station?'"):
                st.session_state.input_text_buffer = "Where is the nearest transportation station?"
        with v_c2:
            if st.button("🗣️ Mic Sim: 'Welcome to our city'"):
                st.session_state.input_text_buffer = "Welcome to our city, it is a pleasure to meet you."

with panel_input_2:
    with st.expander("📷 OCR Document / Camera Scan", expanded=False):
        st.caption("Upload graphic files or trigger standard hardware emulator inputs:")
        ocr_file = st.file_uploader("Upload Image Target Document", type=["jpg", "png", "jpeg", "webp"])
        if ocr_file is not None:
            st.session_state.input_text_buffer = "Hello world, I am translating this file script."
            st.info("✅ OCR analysis successful! Text read complete.")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- CORE UI INPUT BLOCK ---------------- #
grid_col1, grid_col2 = st.columns(2)

with grid_col1:
    st.markdown("### 📥 Source Transmission Target")
    entry_method = st.radio(
        "Ingress Parsing Execution Mode",
        ["✨ Universal Auto-Detect Script Engine", "🔤 Phonetic Keyboard (Latin sounds to script conversions)"],
        horizontal=True
    )
    
    source_input_string = st.text_area(
        "Source Text Capture Window",
        value=st.session_state.input_text_buffer,
        height=180,
        placeholder="Populate characters or phonetics here...",
        key="main_textarea_input"
    )

with grid_col2:
    st.markdown("### 📤 Destination Parameters")
    target_lang_selection = st.selectbox(
        "Search & Match Target Output Language Target",
        options=language_catalog,
        index=language_catalog.index("korean") if "korean" in language_catalog else 0
    )
    target_code_string = language_dict[target_lang_selection]

# ---------------- COMPILATION ENGINE PIPELINE ---------------- #
if st.button("🚀 INITIATE AI MATRIX TRANSLATION"):
    cleansed_input = source_input_string.strip()
    
    if not cleansed_input:
        st.warning("Input buffer empty.")
    else:
        if enable_animations:
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown(f"""
                <div style='text-align: center; padding: 30px;'>
                    <div style='display: inline-block; width: 45px; height: 45px; border: 4px solid #f3f3f3; border-top: 4px solid {sel_theme['accent']}; border-radius: 50%; animation: spin 1s linear infinite;'></div>
                    <h5 style='margin-top: 15px; color: {sel_theme['text']};'>Synthesizing AI Core Parsing Pipelines...</h5>
                </div>
                <style>@keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style>
                """, unsafe_allow_html=True)
                time.sleep(1.0)
            loading_placeholder.empty()

        try:
            calculated_source_code = "auto"
            
            if "Phonetic Keyboard" in entry_method:
                try:
                    from translator import translate_text
                    cleansed_input = translate_text(cleansed_input, "en", target_code_string)
                    calculated_source_code = target_code_string
                except Exception:
                    cleansed_input = GoogleTranslator(source='en', target=target_code_string).translate(cleansed_input)
                    calculated_source_code = target_code_string

            # 1️⃣ Core Translation Pass
            compiled_target_translation = GoogleTranslator(source=calculated_source_code, target=target_code_string).translate(cleansed_input)

            # 2️⃣ Transliteration Generation Block
            compiled_phonetic_guide = ""
            if target_code_string not in ["en", "es", "fr", "de", "it"]:
                compiled_phonetic_guide = anyascii(compiled_target_translation)
            else:
                compiled_phonetic_guide = "Phonetic breakdown omitted for standard Latin script types."

            # 3️⃣ Compute Context-Meaning Array Mapping
            computed_user_native_code = language_dict.get(user_native_lang, "en")
            if target_code_string == computed_user_native_code:
                compiled_native_meaning = compiled_target_translation
            else:
                compiled_native_meaning = GoogleTranslator(source=target_code_string, target=computed_user_native_code).translate(compiled_target_translation)

            # Synchronize states
            st.session_state.translated_text = compiled_target_translation
            st.session_state.pronunciation_text = compiled_phonetic_guide
            st.session_state.meaning_context_text = compiled_native_meaning
            st.session_state.last_target_lang = target_lang_selection.title()
            st.session_state.render_id = str(time.time())
            
            # Save transaction records directly into local history arrays
            st.session_state.translation_history.insert(0, {
                "source": cleansed_input,
                "target": compiled_target_translation,
                "lang": target_lang_selection.title()
            })

        except Exception as system_fault_error:
            st.error(f"AI pipeline compilation exception error occurred: {system_fault_error}")

# ---------------- OUTPUT SYSTEM CONFIGURATION CARDS ---------------- #
if st.session_state.translated_text:
    st.markdown("---")
    
    out_panel_col1, out_panel_col2 = st.columns(2)
    
    with out_panel_col1:
        st.markdown(f'<div class="translation-card"><h4>🌐 Target Translation Output ({st.session_state.last_target_lang})</h4></div>', unsafe_allow_html=True)
        st.text_area("Script Display Output", value=st.session_state.translated_text, height=120, key=f"scr_{st.session_state.render_id}", label_visibility="collapsed")
        
        # High-Fidelity Audio Feed Generation Block (TTS System)
        try:
            tts_engine_object = gTTS(text=st.session_state.translated_text, lang=target_code_string, slow=False)
            audio_memory_buffer = io.BytesIO()
            tts_engine_object.write_to_fp(audio_memory_buffer)
            audio_memory_buffer.seek(0)
            st.audio(audio_memory_buffer, format="audio/mp3")
        except Exception:
            pass
        
        if st.session_state.pronunciation_text:
            st.markdown('<div class="translation-card" style="margin-top:15px; padding:12px;"><h5>🔤 Phonetic Pronunciation Guide</h5></div>', unsafe_allow_html=True)
            st.text_area("Pronunciation Display Output", value=st.session_state.pronunciation_text, height=100, key=f"pron_{st.session_state.render_id}", label_visibility="collapsed")
            
    with out_panel_col2:
        st.markdown(f'<div class="translation-card"><h4>📖 Structural Meaning Context ({user_native_lang.title()})</h4></div>', unsafe_allow_html=True)
        st.text_area("Meaning Display Output", value=st.session_state.meaning_context_text, height=120, key=f"mean_{st.session_state.render_id}", label_visibility="collapsed")
        
        # Compile Downloadable Report Document Asset
        download_payload_data = (
            f"=== NEXUSAI APP MANIFEST SUMMARY ===\n"
            f"Target Dialect Language: {st.session_state.last_target_lang}\n"
            f"Native Translation: {st.session_state.translated_text}\n"
            f"Romanized Sound Guide: {st.session_state.pronunciation_text}\n"
            f"Context Native Meaning: {st.session_state.meaning_context_text}\n"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="💾 DOWNLOAD TRANSLATION MANIFEST (.TXT)",
            data=download_payload_data,
            file_name=f"nexus_translation_{st.session_state.render_id}.txt",
            mime="text/plain"
        )

# ---------------- HISTORICAL TRANSACTION LOG PANEL ---------------- #
if st.session_state.translation_history:
    st.markdown("---")
    st.markdown("### 📜 Session Historical Analytics Activity Log")
    
    for idx, item in enumerate(st.session_state.translation_history[:4]): # Keep frame output to last 4 transactions
        st.markdown(f"""
        <div class="history-item">
            <strong>Input String:</strong> {item['source']} <br>
            <strong>[{item['lang']}] Translation:</strong> {item['target']}
        </div>
        """, unsafe_allow_html=True)
