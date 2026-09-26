# Deploying UnveilX Forge on Streamlit

## What changed so this can deploy at all

Before this fix, the app needed **two processes running at once** — the
FastAPI backend (`backend/server.py`, on port 8000) and the Streamlit
frontend (`app.py`, on port 8501) — started manually by `start_unveilx.bat`.
Any host that only runs a single start command (Streamlit Community Cloud
included) had no way to bring the backend up, so every screening failed.

`app.py` now starts the backend itself, in a background thread, the first
time the app runs. **A single command is enough:**

```bash
streamlit run app.py
```

If you'd rather run the backend as its own process (recommended for real
load — see the resource warning below), set the `UNVEILX_API_URL`
environment variable / Streamlit secret to that backend's URL and app.py
will not start a local copy.

## Deploying to Streamlit Community Cloud

1. Push this folder to a GitHub repo (root of the repo = this `v4work/` folder,
   containing `app.py`, `requirements.txt`, `packages.txt`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** →
   pick the repo/branch and set the main file path to `app.py`.
3. Open **Advanced settings** before deploying and pick the **Python
   version** explicitly (3.11 or 3.12). Community Cloud ignores
   `runtime.txt`; the version picker in Advanced settings is the only way
   to set it, and its current default (3.13) does not yet have prebuilt
   wheels for every package this app needs (torch/tensorflow/paddlepaddle).
4. `packages.txt` (already added) installs the system libraries OpenCV and
   `streamlit-webrtc` need (`libgl1`, `ffmpeg`, etc.) — Community Cloud
   installs these automatically, no action needed.
5. Deploy. First boot will be slow: DeepFace downloads its face-matching
   model (~90–100 MB) on first use, and PaddleOCR/TensorFlow/Torch are
   large imports.

## Read this before you rely on the free tier

Streamlit Community Cloud's free tier gives each app **~1 GB of RAM**, shared
CPU, and it can be uninstalled by the platform automatically if the app
crashes repeatedly. This app's pipeline loads **torch + tensorflow +
paddlepaddle + deepface** at once — each of those alone commonly uses several
hundred MB to over 1 GB once a model is loaded. Realistically this stack is
likely to hit the memory ceiling and get killed, especially if more than one
officer uses it at the same time.

Two honest ways forward, depending on what you need for SIH judging vs. a
real deployment:

- **For a live demo in front of judges**: the free tier may hold up for a
  single user doing occasional screenings, since the models load once and
  stay warm. Test it with your actual demo images beforehand — don't find
  out live.
- **For anything more than a demo**: run the backend (`backend/server.py`)
  on a host with more memory — a small VM (e.g. a $5–10/mo box), Render,
  Railway, or a Streamlit **Teams/Enterprise** workspace with higher
  resource limits — and deploy only the lightweight Streamlit frontend to
  Community Cloud, pointing it at that backend via the `UNVEILX_API_URL`
  secret. This also means the frontend stays fast even while the ML models
  are working.

## Local development

Nothing changes for local use — `streamlit run app.py` still works exactly
as before, and will still start its own backend automatically if one isn't
already running on port 8000. `start_unveilx.bat` still works too, since the
backend auto-start step above simply detects the already-running backend on
port 8000 and skips starting a second copy.
