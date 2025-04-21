from fastapi import FastAPI, File, UploadFile, Form, Response, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import tempfile
import os
import json

app = FastAPI()

def process_video_with_tracking(input_path: str,
                                output_path: str,
                                start_time: float,
                                end_time: float,
                                skip_frames: int,
                                bbox: list):
    """
    Video processing with KCF tracking:
    - Reads frames with cv2.VideoCapture
    - Initializes a KCF tracker with the provided bounding box
    - Tracks the object and draws a rectangle around it
    - Writes the processed frames to output_path
    """
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(output_path, fourcc, fps / skip_frames, (width, height))

    # Compute frame range
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps) if end_time else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Validate bounding box
    if bbox[0] < 0 or bbox[1] < 0 or bbox[0] + bbox[2] > width or bbox[1] + bbox[3] > height:
        raise HTTPException(status_code=400, detail="Bounding box is out of frame bounds")

    # Initialize KCF tracker
    tracker = cv2.TrackerKCF_create()  # Use the correct function
    ret, frame = cap.read()
    print(f"Frame read success: {ret}")
    if not ret:
        raise Exception("Failed to read the first frame for tracker initialization")
    tracker.init(frame, tuple(bbox))  # Initialize tracker with the bounding box

    frame_idx = start_frame
    while cap.isOpened() and frame_idx < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % skip_frames == 0:
            # Update tracker and draw bounding box
            success, tracked_bbox = tracker.update(frame)
            if success:
                x, y, w, h = map(int, tracked_bbox)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw green rectangle
            out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()



@app.post("/process_video/")
async def process_video_endpoint(
    file: UploadFile = File(...),
    start_time: float = Form(0.0),
    end_time: float = Form(0.0),
    skip_frames: int = Form(5),
    bbox: str = Form(...),  # Bounding box as a JSON string
):
    # Parse the bounding box
    try:
        bbox = json.loads(bbox)
        if len(bbox) != 4:
            raise ValueError("Bounding box must have 4 values: [x, y, w, h]")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid bounding box: {e}")

    # Save upload to temp MP4
    in_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    in_tmp.write(await file.read())
    in_tmp.flush()
    in_tmp.close()  # Ensure the file is closed so OpenCV can read it properly

    print(f"Temporary file path: {in_tmp.name}")

    out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out_path = out_tmp.name
    out_tmp.close()  # Close before VideoWriter opens it

    # Process video with tracking
    process_video_with_tracking(in_tmp.name, out_path, start_time, end_time, skip_frames, bbox)

    

    def iterfile():
        with open(out_path, mode="rb") as f:
            yield from f
        # Cleanup
        os.unlink(in_tmp.name)
        os.unlink(out_path)

    return StreamingResponse(iterfile(), media_type="video/mp4")

@app.post("/thumbnail/")
async def thumbnail_endpoint(file: UploadFile = File(...)):
    # Save upload to temp MP4
    in_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    in_tmp.write(await file.read())
    in_tmp.flush()
    in_tmp.close()  # Ensure the file is closed so OpenCV can read it properly

    # extract first frame
    cap = cv2.VideoCapture(in_tmp.name)
    ret, frame = cap.read()
    cap.release()
    # os.unlink(in_tmp.name)

    if not ret:
        raise HTTPException(status_code=400, detail="Failed to read first frame")

    # encode frame as PNG
    success, png_buf = cv2.imencode(".png", frame)
    if not success:
        raise HTTPException(status_code=500, detail="PNG encoding failed")

    return Response(content=png_buf.tobytes(), media_type="image/png")