# UnveilX Forge — SIH 26188 Integrated Build

AI-based fake identity and document screening prototype with OCR, document validation, tampering detection, live face verification, DeepFace anti-spoofing, local reference database, and Streamlit dashboard.

## What changed in this build

- Replaced the broken `st.camera_input()` selfie widget with a live WebRTC camera stream.
- Selfie upload is disabled for biometric verification.
- Added a pre-verification quality gate for:
  - blur/focus
  - brightness/overexposure
  - exactly one detected face
  - a conservative display/replay visual heuristic
- The backend runs DeepFace anti-spoofing (`anti_spoofing=True`) before face matching.
- If liveness/anti-spoofing fails, face verification is explicitly **PAUSED** and the case is sent to manual review instead of being approved.
- Updated the launcher to use Python 3.13 when available.

## One-click local launch

1. Extract this folder.
2. Double-click `start_unveilx.bat`.
3. Keep the two command windows open.
4. The dashboard opens at `http://127.0.0.1:8501`.

For the first launch, package installation can take several minutes and DeepFace may download model data on first use.

## Manual launch

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

## Camera test

```powershell
python -m streamlit run camera_test.py --server.port 8505
```

Then open `http://127.0.0.1:8505` and click START.

## Security note

The image-quality and display-replay checks are heuristics. DeepFace anti-spoofing is an additional model-based gate, but no software-only webcam system can guarantee detection of every possible presentation attack. A failed or uncertain liveness result is treated conservatively as a verification pause/manual-review event.


## Camera fix (2026-09-19)

The live-camera integration uses the supported `WebRtcStreamerContext.video_processor` property. The project pins `streamlit-webrtc==0.77.0` so the camera API is consistent across installs. `camera_test.py` is included for isolated webcam testing.
