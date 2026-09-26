"""Live webcam capture and pre-verification quality gate for UnveilX Forge."""
from dataclasses import dataclass
from threading import Lock
from typing import Optional

import cv2
import numpy as np
from streamlit_webrtc import VideoProcessorBase


@dataclass
class FrameQuality:
    ok: bool
    reason: str
    blur_score: float
    brightness: float
    face_count: int
    screen_score: float


def _screen_replay_score(gray: np.ndarray) -> float:
    """Heuristic for display/photo replay. This is not a certified liveness test."""
    # Periodic vertical/horizontal line energy can increase when a camera points at a display.
    resized = cv2.resize(gray, (256, 256))
    gx = cv2.Sobel(resized, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(resized, cv2.CV_32F, 0, 1, ksize=3)
    line_energy = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))
    # Normalize into a small 0..1 heuristic range.
    return float(max(0.0, min(1.0, line_energy / 180.0)))


def assess_frame(frame_bgr: np.ndarray) -> FrameQuality:
    if frame_bgr is None or frame_bgr.size == 0:
        return FrameQuality(False, "No camera frame received.", 0, 0, 0, 0)

    h, w = frame_bgr.shape[:2]
    if w < 320 or h < 240:
        return FrameQuality(False, "Camera resolution is too low. Move closer or use a higher-resolution camera.", 0, 0, 0, 0)

    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))

    if blur < 70:
        return FrameQuality(False, f"Image is too blurry (focus score {blur:.0f}). Hold still and refocus.", blur, brightness, 0, 0)
    if brightness < 35:
        return FrameQuality(False, "Image is too dark. Improve lighting.", blur, brightness, 0, 0)
    if brightness > 225:
        return FrameQuality(False, "Image is overexposed. Reduce glare or move away from direct light.", blur, brightness, 0, 0)

    cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(70, 70))
    face_count = len(faces)
    if face_count != 1:
        return FrameQuality(False, f"Exactly one face is required. Detected {face_count}.", blur, brightness, face_count, 0)

    screen_score = _screen_replay_score(gray)
    # This threshold is intentionally conservative only as a UI warning; the final
    # decision is DeepFace anti-spoofing in the backend.
    if screen_score > 0.88:
        return FrameQuality(False, "Possible display/photo replay pattern detected. Verification paused.", blur, brightness, face_count, screen_score)

    return FrameQuality(True, "Frame passed the pre-verification quality gate.", blur, brightness, face_count, screen_score)


class LiveFaceProcessor(VideoProcessorBase):
    """Stores the latest webcam frame for a user-triggered capture."""
    def __init__(self):
        self._lock = Lock()
        self.latest_frame: Optional[np.ndarray] = None
        self.quality: Optional[FrameQuality] = None

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        with self._lock:
            self.latest_frame = image.copy()
            self.quality = assess_frame(image)
        return frame

    def snapshot(self):
        with self._lock:
            if self.latest_frame is None:
                return None, None
            return self.latest_frame.copy(), self.quality
