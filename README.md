# Feature‑Based Motion Analysis App

This repository contains a simple demo app for feature‑based motion analysis of user‑uploaded MP4 videos.  
It comprises:

- A **FastAPI** backend (`backend.py`) that accepts an MP4, samples frames, applies placeholder image processing, and returns a modified MP4.  
- A **Streamlit** frontend (`frontend.py`) that lets users upload a video, pick a time range & frame‑skip interval, and view the processed result.

---

## Features

- Upload any `.mp4` file via the Streamlit UI  
- Select **start** & **end** times (in seconds)  
- Choose to process **every Nth frame** (e.g. skip 4 out of 5 frames)  
- Backend samples frames using OpenCV, runs placeholder feature‑based processing, and streams back the result  
- Easily extend `process_video()` in `backend.py` to add your own computer‑vision logic  

---

## Getting Started

### 1. Clone the repo
```bash
git clone <your‑repo‑url> motions‑analysis
cd motions‑analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the backend
```bash
uvicorn backend:app --reload
```

### 4. Run the frontend
```bash
streamlit run frontend.py
```

---

## Usage

1. In the Streamlit UI:
   - Click **Browse files** to upload an MP4.  
   - Adjust **Start time** & **End time** sliders.  
   - Set **Process every Nth frame**.  
   - Click **Process Video**.  
2. Streamlit sends a `POST /process_video/` with file + params to the FastAPI server.  
3. The backend:
   - Saves the upload to a temp file  
   - Samples frames via OpenCV  
   - Applies placeholder image processing  
   - Streams back the processed MP4  
4. Streamlit displays the returned video in-browser.

---

## File Structure

- `backend.py`  — FastAPI app & `process_video()` placeholder  
- `frontend.py` — Streamlit UI  
- `requirements.txt` — Python dependencies  
- `README.md` — Project overview  

---

## Extending the App

- In `backend.py`, replace the `# TODO: actual image processing here` with your own CV logic.  
- Tweak sampling logic or output FPS by adjusting `skip_frames` or writer settings.  
- Add UI controls in `frontend.py` to expose more parameters.
