import streamlit as st
import requests
from io import BytesIO

st.title("Streamlit → FastAPI Video Processor")

uploaded = st.file_uploader("Upload MP4", type="mp4")
if uploaded:
    # get duration estimate (optional)
    start = st.slider("Start time (s)", 0.0, 60.0, 0.0, 0.5)
    end   = st.slider("End time (s)",   0.0, 60.0, 10.0, 0.5)
    skip  = st.number_input("Process every Nth frame", min_value=1, max_value=30, value=5)
    if st.button("Process Video"):
        files = {"file": ("input.mp4", uploaded, "video/mp4")}
        data  = {"start_time": start, "end_time": end, "skip_frames": skip}
        resp = requests.post("http://localhost:8000/process_video/", files=files, data=data)
        if resp.status_code == 200:
            st.success("Processed!")
            st.video(BytesIO(resp.content))
        else:
            st.error(f"Error {resp.status_code}")