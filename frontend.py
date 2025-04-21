import streamlit as st
import requests
import json
import tempfile
from io import BytesIO
import base64
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.title("Streamlit → FastAPI Feature Tracking Video Processor")

# 1. Upload video
uploaded = st.file_uploader("Upload MP4", type="mp4")
if not uploaded:
    st.info("Please upload an MP4 to begin.")
    st.stop()

# 2. Request thumbnail (first frame) from backend
thumb_resp = requests.post(
    "http://localhost:8000/thumbnail/",
    files={"file": ("input.mp4", uploaded, "video/mp4")},
)
if thumb_resp.status_code != 200:
    st.error("Failed to load thumbnail from backend.")
    st.stop()

# load PIL image
frame = Image.open(BytesIO(thumb_resp.content))

# Convert PIL image to base64-encoded data URI
buffer = BytesIO()
frame.save(buffer, format="PNG")
buffer.seek(0)
data_uri = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"
# Assign the data URI as a frame attiribute
frame.data_uri = data_uri

st.write("Draw a rectangle around the object to track:")

# 3. Let user draw a bounding box
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=2,
    stroke_color="red",
    background_image=frame,
    height=frame.height,
    width=frame.width,
    drawing_mode="rect",
    key="canvas",
)

# 4. Once a box is drawn, show parameters & motion settings
if canvas_result.json_data and canvas_result.json_data["objects"]:
    obj = canvas_result.json_data["objects"][0]
    x, y = obj["left"], obj["top"]
    w, h = obj["width"], obj["height"]
    st.write(f"Selected bbox: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    start = st.slider("Start time (s)", 0.0, 60.0, 0.0, 0.5)
    end   = st.slider("End time (s)",   0.0, 60.0, 10.0, 0.5)
    skip  = st.number_input("Process every Nth frame", min_value=1, max_value=30, value=5)

    if st.button("Track & Analyze Motion"):
        files = {"file": ("input.mp4", uploaded, "video/mp4")}
        data = {
            "start_time": start,
            "end_time": end,
            "skip_frames": skip,
            "bbox": json.dumps([x, y, w, h])
        }
        resp = requests.post("http://localhost:8000/process_video/", files=files, data=data)
        if resp.status_code == 200:
            st.success("Motion analysis complete!")
            st.video(BytesIO(resp.content))
        else:
            st.error(f"Processing error: {resp.status_code}")
else:
    st.warning("Use the rectangle tool to select an object on the frame.")