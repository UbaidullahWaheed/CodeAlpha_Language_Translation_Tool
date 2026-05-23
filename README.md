<div align="center">

# 🌐 NexusAI Translation Matrix

### *Intelligent Multi-Language Engine — v4.0*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Translate](https://img.shields.io/badge/Google_Translate-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://pypi.org/project/deep-translator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)

<br/>

*A production-grade, multi-theme AI translation tool with phonetics, audio playback, phrasebook, and batch file support — built with Streamlit.*

<br/>

---

</div>

## ✨ Features

| Feature | Description |
|---|---|
| 🌍 **100+ Languages** | Powered by Google Translate via `deep-translator` |
| 🎨 **4 UI Themes** | Midnight Cosmos, Arctic Clarity, Warm Parchment, Forest Terminal |
| 🔤 **Phonetics** | Romanized pronunciation output via AnyAscii |
| 🔊 **Text-to-Speech** | Audio playback for both source and translated text via gTTS |
| 📖 **Meaning Context** | Translation re-rendered in your native language for deeper understanding |
| ⚖️ **Side-by-Side Compare** | Original vs translated view in one panel |
| 📌 **Phrasebook** | Save, browse, and export your favourite translations |
| 📂 **Batch File Upload** | Upload `.txt` or `.docx` files for bulk translation |
| 📊 **Confidence Score** | Heuristic quality indicator for every translation |
| 💾 **Report Download** | Export full translation report as `.txt` |
| 🔄 **Swap Languages** | Instantly swap source ↔ last translation |
| 💎 **Tier System** | Free / Pro / Enterprise character limits and history caps |

---

## 🖥️ Screenshots

> *Four themes — one engine.*

| 🌌 Midnight Cosmos | ☀️ Arctic Clarity |
|---|---|
| Dark blue-black with electric blue accents | Clean white with indigo highlights |

| 🪵 Warm Parchment | 🌿 Forest Terminal |
|---|---|
| Warm beige with amber accents | Deep near-black with neon teal grid |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8+**
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/nexusai-translation-matrix.git
cd nexusai-translation-matrix

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## 📦 Dependencies

```txt
streamlit
deep-translator
anyascii
gTTS
python-docx
```

Install all at once:

```bash
pip install streamlit deep-translator anyascii gTTS python-docx
```

Or use the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🗂️ Project Structure

```
nexusai-translation-matrix/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # You are here
└── .streamlit/
    └── config.toml         # Optional: Streamlit server config
```

---

## 🎨 Themes

The app ships with **4 hand-crafted themes**, switchable live from the sidebar:

### 🌌 Midnight Cosmos
Deep navy-black background with electric blue accents. Designed for focus and extended use in low-light environments.

### ☀️ Arctic Clarity
Clean white/light grey with crisp indigo and violet highlights. Ideal for daytime use and presentations.

### 🪵 Warm Parchment
Soft beige and cream tones with warm amber accents. Evokes a classic editorial feel — easy on the eyes.

### 🌿 Forest Terminal
Near-black with a subtle teal grid pattern and neon green accents. A professional dark terminal aesthetic with a glowing radial depth effect.

---

## 💎 Account Tiers

| Tier | Char Limit / Translation | History | Phrasebook |
|---|---|---|---|
| 🔓 Free | 500 | 5 entries | 10 entries |
| 🚀 Pro | 5,000 | 50 entries | 100 entries |
| 🏢 Enterprise | 99,999 | 999 entries | 9,999 entries |

> *Tier is selectable in the sidebar — no login required.*

---

## 🔧 How It Works

1. **Input** — Type or paste text (or upload a `.txt`/`.docx` file) into the source panel.
2. **Select** — Choose your target language from 100+ options.
3. **Translate** — Hit **🚀 Translate Now**. The engine splits text into sentences and translates in parallel using `ThreadPoolExecutor`.
4. **Review** — Explore results across five tabs:
   - **Translation** — The translated output with copy & audio playback
   - **Meaning** — Re-translated into your native language for context
   - **Phonetics** — AnyAscii romanization of the output
   - **Compare** — Side-by-side original vs translation
   - **Phrasebook** — Save entries for later

---

## ⚠️ Known Limitations

- **Language detection** uses `deep-translator`'s auto mode; the specific detected language code is not exposed by the library and shows as *"auto-detected"*.
- **gTTS** requires an active internet connection for audio generation.
- **Confidence score** is heuristic (length ratio + randomisation) and not a true model-level confidence metric.
- `.docx` support requires `python-docx` to be installed separately.

---

## 🤝 Contributing

Contributions are welcome! To get started:

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please follow existing code style and test your changes locally before submitting.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**NexusAI Translation Matrix** &nbsp;·&nbsp; v4.0 &nbsp;·&nbsp; Powered by Google Translate & gTTS

*Built with ❤️ using [Streamlit](https://streamlit.io)*

</div>
