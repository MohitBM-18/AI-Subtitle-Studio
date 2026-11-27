# 🎬 AI Subtitle Studio

**AI-powered video subtitling — transcribe, translate, and permanently embed subtitles into any video.**

Upload a video → AI detects the language → Whisper transcribes every word with timestamps → translate into 100+ languages → export a ready-to-post MP4 with subtitles burned directly into the frames.

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🎙️ Auto language detection | Whisper identifies the spoken language automatically |
| ⏱️ Word-level timestamps | Every word is timed precisely — no drift |
| 🌍 AI Translation | Translate into 100+ languages via GPT-3.5 |
| 🎤 Karaoke mode | Word-by-word highlight effect |
| 📝 Sentence mode | Full-phrase subtitles |
| 🔥 Hardcoded subtitles | FFmpeg burns subtitles permanently into the video |
| 📱 Social presets | Portrait 9:16, Square 1:1, Landscape 16:9 |
| 🎨 Style customisation | Font, colour, highlight, background, position |

---

## 🗂️ Project Structure

```
AI-Subtitle-Studio/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings from .env
│   ├── routes/
│   │   ├── upload.py            # POST /api/upload
│   │   ├── transcription.py     # POST /api/transcribe/{video_id}
│   │   ├── translation.py       # POST /api/translate
│   │   ├── rendering.py         # POST /api/render + GET /api/videos/{name}
│   │   └── jobs.py              # POST /api/jobs/process + GET /api/jobs/{id}
│   ├── services/
│   │   ├── audio_extractor.py   # FFmpeg: extract 16kHz mono WAV
│   │   ├── language_detection.py# OpenAI Whisper: detect language
│   │   ├── speech_recognition.py# OpenAI Whisper: transcribe + word timestamps
│   │   ├── translation.py       # OpenAI GPT: translate subtitle text
│   │   ├── subtitle_generator.py# Write SRT files (karaoke / sentence / bilingual)
│   │   └── video_renderer.py    # FFmpeg: burn subtitles into video
│   ├── models/
│   │   └── schemas.py           # Pydantic data models
│   └── utils/
│       ├── file_validation.py   # Size & type checks
│       └── cleanup.py           # Purge expired files
├── frontend/
│   ├── index.html               # Landing page
│   ├── upload.html              # Drag-and-drop upload
│   ├── editor.html              # Subtitle configuration & preview
│   ├── processing.html          # Live processing dashboard
│   ├── results.html             # Final video player & download
│   ├── css/style.css            # Dark professional theme
│   └── js/
│       ├── upload.js
│       ├── editor.js
│       ├── processing.js
│       └── results.js
├── storage/
│   ├── uploads/                 # Uploaded videos (auto-cleaned)
│   ├── temporary/               # Audio + SRT temp files
│   └── outputs/                 # Rendered final videos
├── .env.example                 # Configuration template
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Python 3.11+**
- **FFmpeg** — [Download](https://ffmpeg.org/download.html) and add to PATH
- **OpenAI API key** — [Get one](https://platform.openai.com/api-keys)

### 1. Clone the repo
```powershell
git clone https://github.com/YOUR_USERNAME/AI-Subtitle-Studio.git
cd AI-Subtitle-Studio
```

### 2. Create a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables
```powershell
Copy-Item .env.example .env
# Open .env and add your OPENAI_API_KEY
```

### 5. Start the server
```powershell
uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

---

## 🐳 Docker

```bash
cp .env.example .env
# Edit .env to add OPENAI_API_KEY
docker-compose up --build
```

The app will be available at **http://localhost:8000**.

---

## 🔑 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a video file |
| `POST` | `/api/transcribe/{video_id}` | Transcribe (auto-detect language) |
| `POST` | `/api/translate` | Translate an SRT file |
| `POST` | `/api/render` | Burn subtitles into video |
| `POST` | `/api/jobs/process` | Run the full pipeline in background |
| `GET`  | `/api/jobs/{job_id}` | Poll job status |
| `GET`  | `/api/videos/{name}` | Download rendered video |
| `GET`  | `/health` | Health check |

Interactive docs: **http://127.0.0.1:8000/api/docs**

---

## 🌍 Supported Languages

English, Hindi, Kannada, Tamil, Telugu, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese (Simplified), Arabic, Russian, and 80+ more (all languages supported by OpenAI Whisper).

---

## ⚙️ Configuration

Edit `.env` to customise:

```env
OPENAI_API_KEY=sk-...
MAX_VIDEO_SIZE_MB=500
ALLOWED_EXTENSIONS=.mp4,.mov,.mkv,.avi,.webm
CLEANUP_AFTER_HOURS=24
PORT=8000
```

---

## 🔒 Security

- API keys are stored in `.env` and never exposed to the frontend
- File type and size validation on every upload
- Path traversal protection on all file download endpoints
- Automatic cleanup of expired temporary files

---

## 🛣️ Roadmap

- [ ] Speaker diarisation (colour per speaker)
- [ ] WebSocket real-time progress updates
- [ ] Batch video processing
- [ ] User accounts & processing history
- [ ] Social media export presets
- [ ] Custom subtitle templates

---

## 📄 License

MIT — free to use, modify and distribute.
