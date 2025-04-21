# Feature‑Based Motion Analysis App

This repository contains a simple demo app for feature‑based motion analysis of user‑uploaded MP4 videos.  
It comprises:

- A **FastAPI** backend (`backend.py`) that accepts an MP4, samples frames, applies KCF tracking for motion analysis, and returns a modified MP4.  
- A **Streamlit** frontend (`frontend.py`) that lets users upload a video, draw a bounding box on the first frame, pick a time range & frame‑skip interval, and view the processed result.

---

## Features

- Upload any `.mp4` file via the Streamlit UI.  
- Select **start** & **end** times (in seconds).  
- Choose to process **every Nth frame** (e.g., skip 4 out of 5 frames).  
- Draw a bounding box on the first frame to track a specific object.  
- Backend uses OpenCV's KCF tracker to follow the selected object and draws a green rectangle around it in the output video.  
- Easily extend `process_video_with_tracking()` in `backend.py` to add your own computer‑vision logic.  

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
   - Draw a bounding box around the object to track on the first frame.  
   - Adjust **Start time** & **End time** sliders.  
   - Set **Process every Nth frame**.  
   - Click **Track & Analyze Motion**.  

2. Streamlit sends a `POST /process_video/` request with the file, bounding box, and parameters to the FastAPI server.  

3. The backend:
   - Saves the uploaded video to a temporary file.  
   - Initializes a KCF tracker with the bounding box.  
   - Tracks the object across frames and draws a green rectangle around it.  
   - Streams back the processed MP4.  

4. Streamlit displays the returned video in-browser.

---

## File Structure

- `backend.py`  — FastAPI app with `/process_video/` and `/thumbnail/` endpoints.  
- `frontend.py` — Streamlit UI for uploading videos, drawing bounding boxes, and viewing results.  
- `requirements.txt` — Python dependencies.  
