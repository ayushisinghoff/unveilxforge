import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.live_camera import LiveFaceProcessor

st.set_page_config(page_title="UnveilX Camera Test", layout="centered")
st.title("UnveilX Live Camera Test")
st.write("Click START, allow camera access, and check that a live preview appears.")
ctx = webrtc_streamer(
    key="camera-test",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=LiveFaceProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
processor = ctx.video_processor

if ctx.state.playing:
    st.success("Camera stream is active.")
    if processor is not None:
        frame, quality = processor.snapshot()
        if quality is not None:
            st.write({
                "focus_score": round(quality.blur_score, 1),
                "brightness": round(quality.brightness, 1),
                "faces": quality.face_count,
                "pre_gate": quality.ok,
                "reason": quality.reason,
            })
        else:
            st.info("Receiving camera... wait a moment for the first frame.")
else:
    st.info("Click START above and allow camera access in Chrome.")
