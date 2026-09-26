import io
import uuid
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_webrtc import webrtc_streamer, WebRtcMode

from session import navigate_to, start_new_screening
from services.live_camera import LiveFaceProcessor, assess_frame


def _clear_inputs():
    """Kept for the in-page 'Clear All Inputs' button. Delegates to the same
    reset used everywhere else so behaviour (and the widget-key bump) stays
    consistent."""
    start_new_screening()


def render_new_screening():
    st.subheader("➕ New Identity & Document Screening")
    st.caption("Live-camera biometric verification is required. Uploaded selfie images are intentionally disabled for anti-spoof protection.")

    # Every widget below is keyed off this nonce. It only changes when a
    # screening is reset (see session.start_new_screening), so mid-screening
    # reruns keep the same widgets/state, but a fresh "New Screening" always
    # gets brand-new, unstuck widget instances.
    nonce = st.session_state.get("screening_nonce", 0)

    user = st.session_state.get("user", {}) or {}

    col_type, col_station = st.columns([1.5, 1])
    with col_type:
        doc_type = st.selectbox(
            "Document Category",
            ["Passport", "Aadhaar Card", "Driving License (Smart Card)", "PAN Tax Identity Card", "Visa"],
            index=0,
            key="new_screening_doc_type_select",
        )
    with col_station:
        st.text_input(
            "Target Verification Checkpoint",
            value=user.get("checkpoint", "ICP Attari - Border Checkpoint Alpha"),
            disabled=True,
            key="target_checkpoint_input",
        )

    st.divider()
    col_doc, col_face = st.columns(2)

    # ---------------- Document ----------------
    with col_doc:
        st.markdown("### 1. Identity Document")
        st.caption("Upload the document bio-data/front page. JPEG/PNG only.")
        uploaded_doc = st.file_uploader(
            "Upload identity document",
            type=["jpg", "jpeg", "png"],
            key=f"doc_uploader_{nonce}",
            help="Use a clear, glare-free image.",
        )
        doc_image = None
        if uploaded_doc is not None:
            try:
                st.session_state.document_file = uploaded_doc.getvalue()
                st.session_state.document_name = uploaded_doc.name
                doc_image = Image.open(io.BytesIO(st.session_state.document_file))
            except Exception as exc:
                st.error(f"Unable to read document: {exc}")
        elif st.session_state.get("document_file"):
            doc_image = Image.open(io.BytesIO(st.session_state.document_file))

        if doc_image is not None:
            st.image(doc_image, caption=st.session_state.get("document_name", "Document"), use_container_width=True)
            st.success("Document loaded.")
        else:
            st.info("Awaiting document upload…")

    # ---------------- Live Face ----------------
    with col_face:
        st.markdown("### 2. Live Facial Verification")
        st.caption("Use the live webcam. A phone photo, screenshot, or uploaded portrait cannot be used for verification.")

        ctx = webrtc_streamer(
            key=f"unveilx-live-face-{nonce}",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LiveFaceProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        processor = ctx.video_processor
        quality = processor.quality if processor is not None else None

        if quality:
            if quality.ok:
                st.success(
                    f"Live frame ready • focus {quality.blur_score:.0f} • brightness {quality.brightness:.0f} • 1 face"
                )
            else:
                st.warning(f"🛑 Capture blocked: {quality.reason}")

        if ctx.state.playing:
            st.info("Camera is live. Keep one face centered, remove glare, and hold still.")
            if st.button("📸 Capture & Run Anti-Spoof Gate", type="primary", use_container_width=True):
                if processor is None:
                    st.error("Camera processor is not ready yet. Start the camera and wait one second.")
                else:
                    frame, frame_quality = processor.snapshot()
                    if frame is None:
                        st.error("No webcam frame received. Please restart the camera.")
                    elif frame_quality is None or not frame_quality.ok:
                        st.error(f"🛑 Verification PAUSED: {frame_quality.reason if frame_quality else 'No valid frame.'}")
                        st.session_state.pop("selfie_file", None)
                    else:
                        import cv2
                        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                        if not ok:
                            st.error("Could not encode the live frame.")
                        else:
                            st.session_state.selfie_file = encoded.tobytes()
                            st.session_state.selfie_name = "Live_Webcam_Capture.jpg"
                            st.session_state.live_face_quality = {
                                "blur_score": frame_quality.blur_score,
                                "brightness": frame_quality.brightness,
                                "face_count": frame_quality.face_count,
                                "screen_score": frame_quality.screen_score,
                            }
                            st.success("Live frame captured. Backend anti-spoof verification will run before face matching.")
                            st.rerun()
        else:
            st.info("Click START above to enable the webcam. Browser camera permission may be requested.")

        if st.session_state.get("selfie_file"):
            captured = Image.open(io.BytesIO(st.session_state.selfie_file))
            st.image(captured, caption="Captured live frame", use_container_width=True)
            st.success("Live capture stored for verification.")

    st.divider()

    doc_ready = bool(st.session_state.get("document_file"))
    face_ready = bool(st.session_state.get("selfie_file"))
    live_gate_ready = bool(st.session_state.get("live_face_quality"))

    st.markdown("#### Pipeline readiness")
    checks = [
        (doc_ready, "Document scan"),
        (face_ready and live_gate_ready, "Live face capture + pre-gate"),
        (True, "Backend DeepFace anti-spoof gate"),
    ]
    for ok, label in checks:
        st.write(f"{'🟢' if ok else '⚪'} {label}")

    if doc_ready and face_ready and live_gate_ready:
        if st.button("🚀 Start Automated Forensic Screening", type="primary", use_container_width=True):
            case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
            st.session_state.current_screening_id = case_id
            st.session_state.selected_doc_type = doc_type
            navigate_to("processing")
            st.rerun()
    else:
        st.button("🚀 Start Automated Forensic Screening", type="primary", use_container_width=True, disabled=True)
        st.caption("Both the document and a valid live-camera capture are required.")

    if doc_ready or face_ready:
        if st.button("🔄 Clear All Inputs", use_container_width=True):
            _clear_inputs()
            st.rerun()
