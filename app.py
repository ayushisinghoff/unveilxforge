import streamlit as st
import base64
import os
import socket
import sys
import threading
from pathlib import Path
import importlib

from session import (
    initialize_session,
    login_user,
    logout_user,
    navigate_to,
    start_new_screening,
)
import styles
import views.dashboard
import views.officer_profile
import views.new_screening
import views.processing
import views.result
import views.history
import views.case_detail
import views.cross_document
import views.criminal_database
import views.chatbot
import views.appreciation

importlib.reload(styles)
from styles import load_global_styles

importlib.reload(views.dashboard)
importlib.reload(views.officer_profile)
importlib.reload(views.new_screening)
importlib.reload(views.processing)
importlib.reload(views.result)
importlib.reload(views.history)
importlib.reload(views.case_detail)
importlib.reload(views.cross_document)
importlib.reload(views.criminal_database)
importlib.reload(views.chatbot)
importlib.reload(views.appreciation)

from views.dashboard import render_dashboard
from views.officer_profile import render_officer_profile
from views.new_screening import render_new_screening
from views.processing import render_processing
from views.result import render_result
from views.history import render_history
from views.case_detail import render_case_detail
from views.cross_document import render_cross_document
from views.criminal_database import render_criminal_database
from views.chatbot import render_floating_chatbot, render_chatbot_page
from views.appreciation import render_appreciation


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="UnveilX Forge - Identity Screening System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# AUTO-START THE LOCAL SCREENING BACKEND
# =========================================================
# Previously this whole app only worked if you separately started
# `uvicorn server:app` from backend/ (start_unveilx.bat did that on
# Windows). Any single-command deploy (streamlit run app.py — including
# on Streamlit Community Cloud, which only ever runs one start command)
# had no way to bring the backend up, so /screen calls failed. This
# starts the same FastAPI app in a background thread inside the
# Streamlit process itself, so `streamlit run app.py` alone is enough.
#
# Set the UNVEILX_API_URL env var to point at an already-running backend
# (e.g. a separate, bigger machine for the heavy CV/DeepFace/OCR models)
# instead of spawning one locally.

def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0


def _start_local_backend():
    if os.getenv("UNVEILX_API_URL"):
        return  # Using an external backend — don't start a local one.

    host, port = "127.0.0.1", 8000
    if _port_open(host, port):
        return  # Already running (this thread, or a separately started process).

    backend_dir = Path(__file__).resolve().parent / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    try:
        import uvicorn
        from server import app as backend_app  # backend/server.py
    except Exception as exc:
        st.session_state["_backend_start_error"] = (
            f"Local screening backend failed to start: {exc}"
        )
        return

    config = uvicorn.Config(backend_app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()


_start_local_backend()


# =========================================================
# INITIALIZATION
# =========================================================

initialize_session()
load_global_styles()

if st.session_state.get("_backend_start_error"):
    st.error(st.session_state["_backend_start_error"])
    st.caption(
        "The screening pipeline (OCR, tampering, face match, database check) "
        "needs this backend. Fix the error above, or set UNVEILX_API_URL to "
        "point at a backend running elsewhere."
    )


# =========================================================
# LOGO HELPER
# =========================================================

def get_logo_base64():
    """Return base64 encoded string of the UnveilX Forge logo for reliable centered rendering."""
    paths = [
        Path("assets/unveilx_logo.jpg"),
        Path("assets/sih_logo_icon.jpg"),
        Path("assets/logo sih.jpeg"),
    ]
    for p in paths:
        if p.exists():
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None


# =========================================================
# LOGIN PAGE (MATCHES REFERENCE DESIGN - NO SIDEBAR)
# =========================================================

def show_login():
    # Hide sidebar ONLY on the login screen and add dark oceanic radial gradient backdrop + glowing cyan glass card
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        div[data-testid="collapsedControl"],
        button[data-testid="stExpandSidebarButton"],
        .sidebar-custom-expand-btn {
            display: none !important;
        }
        .stApp {
            background: radial-gradient(circle at 50% 25%, #18426d 0%, #0e2746 45%, #071628 100%) fixed !important;
        }

        /* Center and shift the login card vertically for perfect screen balance */
        .block-container {
            padding-top: 4.8rem !important;
            padding-bottom: 3.5rem !important;
        }

        /* Glassmorphic cyan glowing card container */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            position: relative !important;
            background: rgba(14, 38, 68, 0.58) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border: 1.5px solid rgba(56, 189, 248, 0.75) !important;
            border-radius: 28px !important;
            padding: 28px 28px 32px 28px !important;
            box-shadow: 
                0 0 35px rgba(56, 189, 248, 0.35),
                0 0 70px rgba(14, 165, 233, 0.20),
                inset 0 0 20px rgba(56, 189, 248, 0.10),
                0 25px 60px rgba(0, 0, 0, 0.6) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(56, 189, 248, 0.95) !important;
            box-shadow: 
                0 0 45px rgba(56, 189, 248, 0.45),
                0 0 85px rgba(14, 165, 233, 0.25),
                inset 0 0 25px rgba(56, 189, 248, 0.15),
                0 30px 70px rgba(0, 0, 0, 0.7) !important;
        }

        /* Sparkling white/cyan neon accent lines on both sides of the logo */
        .login-flare-left {
            position: absolute;
            left: 30px;
            top: 100%;
            width: 4px;
            height: 180px;
            background: #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 14px 4px #38bdf8, 0 0 32px 8px rgba(56, 189, 248, 0.9);
            pointer-events: none;
            z-index: 10;
        }

        .login-flare-right {
            position: absolute;
            right: 30px;
            top: 100%;
            width: 4px;
            height: 180px;
            background: #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 14px 4px #38bdf8, 0 0 32px 8px rgba(56, 189, 248, 0.9);
            pointer-events: none;
            z-index: 10;
        }

        /* Form Inputs & Selectbox */
        div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: rgba(9, 27, 50, 0.75) !important;
            border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
            border-radius: 12px !important;
            height: 44px !important;
            min-height: 44px !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25) !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.45), inset 0 2px 4px rgba(0, 0, 0, 0.25) !important;
        }

        div[data-testid="stTextInput"] input {
            background-color: transparent !important;
            border: none !important;
            color: #ffffff !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #64748b !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: none !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
            color: #ffffff !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
        }

        div[data-testid="stSelectbox"] svg {
            fill: #38bdf8 !important;
            stroke: #38bdf8 !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            background-color: #0c2340 !important;
            color: #ffffff !important;
        }

        div[data-baseweb="popover"] {
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.25) !important;
        }

        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [aria-selected="true"] {
            background-color: rgba(14, 165, 233, 0.25) !important;
            color: #38bdf8 !important;
        }

        /* Sign In Button */
        .stButton > button[kind="primary"],
        button[kind="primary"] {
            background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(56, 189, 248, 0.6) !important;
            border-radius: 12px !important;
            height: 44px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 18px rgba(14, 165, 233, 0.45), 0 0 20px rgba(56, 189, 248, 0.3) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stButton > button[kind="primary"]:hover,
        button[kind="primary"]:hover {
            background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
            border-color: #38bdf8 !important;
            box-shadow: 0 6px 26px rgba(56, 189, 248, 0.65), 0 0 25px rgba(56, 189, 248, 0.4) !important;
            transform: translateY(-1.5px) !important;
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 1.25, 1])

    with col_center:
        with st.container(border=True):
            # Sparkling side accent lines
            st.markdown(
                """
                <div class="login-flare-left"></div>
                <div class="login-flare-right"></div>
                """,
                unsafe_allow_html=True,
            )

            # Enlarged & Centered Logo
            logo_b64 = get_logo_base64()
            if logo_b64:
                st.markdown(
                    f"""
                    <div class="login-logo-wrapper">
                        <img src="data:image/jpeg;base64,{logo_b64}" class="login-logo-img" alt="UnveilX Forge" />
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div class="login-logo-wrapper"><div class="logo-box">◈</div></div>', unsafe_allow_html=True)

            # Title & Subtitle
            st.markdown(
                """
                <div class="login-title">
                    Identity Screening System
                </div>
                <div class="login-subtitle">
                    AI-Based Fake Identity & Document Screening Platform
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Portal Header Row
            st.markdown(
                """
                <div class="portal-row">
                    <div class="portal-title">
                        🛡 Officer Credential Portal
                    </div>
                    <div class="portal-code">
                        PORT-SEC-IN
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Officer ID
            st.markdown(
                """
                <div class="field-label">
                    <span>Officer ID</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            email = st.text_input(
                "Officer ID",
                value="",
                placeholder="Please enter Officer ID",
                label_visibility="collapsed",
                key="login_officer_id_input",
            )

            # Password
            st.markdown(
                """
                <div class="field-label">
                    <span>Password</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            password = st.text_input(
                "Password",
                type="password",
                value="",
                placeholder="Please enter Password",
                label_visibility="collapsed",
                key="login_user_password_input",
            )

            # Assigned Checkpoint
            st.markdown(
                """
                <div class="field-label">
                    <span>Assigned Checkpoint</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            checkpoint = st.selectbox(
                "Assigned Checkpoint",
                [
                    "ICP Attari - Border Checkpoint Alpha",
                    "T3 - Int'l Arrival Gate 4B",
                    "Nhava Sheva - Sea Port Terminal 2",
                    "RGIA Hyderabad - E-Gate Immigration 01",
                ],
                label_visibility="collapsed",
                key="login_checkpoint_selection",
            )

            # Sign In Button
            if st.button("🔒 Sign In to Console", use_container_width=True, type="primary"):
                if not email.strip() or not password.strip():
                    st.error("Please enter Officer ID and Password.")
                else:
                    login_user(email.strip(), checkpoint)
                    st.rerun()


def get_image_base64(filepath):
    """Return base64 encoded string of an image file."""
    p = Path(filepath)
    if p.exists():
        try:
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return None


def clean_html(html_str: str) -> str:
    """Strip leading/trailing whitespace from each line and eliminate empty lines so Markdown never treats it as a code block."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


# =========================================================
# TOP GLOBAL HEADER BAR (MATCHES REFERENCE DESIGN)
# =========================================================

def render_top_header():
    import datetime
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
    avatar_b64 = get_image_base64("assets/officer_avatar.png")
    avatar_html = (
        f'<img src="data:image/png;base64,{avatar_b64}" class="officer-header-avatar" alt="Officer">'
        if avatar_b64
        else '<div class="officer-header-avatar" style="background:#2563eb; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px;">SZ</div>'
    )
    user = st.session_state.get("user") or {}
    officer_name = user.get("name", "Officer S. Zhang")
    officer_id = user.get("officer_id", "VOF-40892")
    checkpoint = user.get("checkpoint", "ICP Attari - Border Checkpoint Alpha")
    cp_display = "ICP Attari" if "Attari" in checkpoint else ("T3 Checkpoint" if "T3" in checkpoint else checkpoint)

    st.markdown(
        clean_html(
            f"""
            <div class="top-global-header">
                <div>
                    <div class="top-header-title-row">
                        <span class="top-header-main-title">Identity Screening System</span>
                        <span class="top-header-badge">Demo Mode | SIH Prototype</span>
                    </div>
                    <div class="top-header-subtitle">
                        AI-Based Fake Identity & Document Screening
                    </div>
                </div>
                <div class="top-header-right-group">
                    <div class="system-online-pill">
                        <span class="green-pulse-dot"></span>
                        <span>System Online &nbsp;{now_utc}</span>
                    </div>
                    <div class="header-icon-btn" title="Alerts & Notifications">🔔</div>
                    <div class="header-icon-btn" title="Documentation & System Help">❔</div>
                    <div class="officer-header-card">
                        <div class="officer-header-text">
                            <div class="officer-header-name">{officer_name}</div>
                            <div class="officer-header-id">ID: {officer_id} | {cp_display}</div>
                        </div>
                        {avatar_html}
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR NAVIGATION (DISPLAYED ONLY AFTER SIGN IN)
# =========================================================

def render_sidebar():
    # Ensure sidebar is visible after login
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            width: 19rem !important;
            min-width: 19rem !important;
            z-index: 100 !important;
        }
        button[data-testid="stExpandSidebarButton"] {
            display: flex !important;
            visibility: visible !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        logo_b64 = (
            get_image_base64("assets/unveilx_sidebar_logo.png")
            or get_image_base64("assets/veriscan_logo.png")
            or get_image_base64("assets/unveilx_logo.jpg")
        )
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" class="sidebar-brand-logo" alt="UnveilX">'
            if logo_b64
            else '<div class="sidebar-brand-logo" style="background:#090f1d; color:#38bdf8; display:flex; align-items:center; justify-content:center; font-weight:800;">UX</div>'
        )

        st.markdown(
            clean_html(
                f"""
                <div class="sidebar-brand-wrapper">
                    <div style="display:flex; align-items:center; gap:12px; flex:1; min-width:0;">
                        {logo_html}
                        <div style="min-width:0;">
                            <div class="sidebar-brand-title">UnveilX Forge</div>
                            <div class="sidebar-brand-sub">BORDER INSPECTION</div>
                        </div>
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        # 1. Station Context Section (matching reference "Stores" / "Capstore" card)
        user = st.session_state.get("user") or {}
        checkpoint_name = user.get("checkpoint", "ICP Attari - Border Checkpoint Alpha")
        cp_short = "ICP Attari" if "Attari" in checkpoint_name else ("T3 Checkpoint" if "T3" in checkpoint_name else checkpoint_name[:22])

        st.markdown('<div class="sidebar-section-label">CHECKPOINT STATION</div>', unsafe_allow_html=True)
        st.markdown(
            clean_html(
                f"""
                <div class="sidebar-station-card">
                    <div class="sidebar-station-left">
                        <div class="sidebar-station-icon">🛂</div>
                        <div class="sidebar-station-text" title="{checkpoint_name}">{cp_short}</div>
                    </div>
                    <span style="color:#38bdf8; font-size:11px; opacity:0.8;">▾</span>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        # 2. General Operations Section (matching reference "General")
        st.markdown('<div class="sidebar-section-label">OPERATIONS</div>', unsafe_allow_html=True)

        core_pages = {
            "dashboard": "⊞  Dashboard",
            "new_screening": "⚲  New Screening",
            "history": "🕒  Screening History",
            "cross_document": "⇄  Cross-Document Check",
        }

        for page_key, page_label in core_pages.items():
            is_active = st.session_state.current_page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_label, use_container_width=True, type=btn_type, key=f"nav_{page_key}"):
                if page_key == "new_screening":
                    start_new_screening()
                else:
                    navigate_to(page_key)
                st.rerun()

        # 3. System Tools Section (matching reference "Tools")
        st.markdown('<div class="sidebar-section-label">INTELLIGENCE & TOOLS</div>', unsafe_allow_html=True)

        tool_pages = {
            "criminal_database": "🗄️  Reference Database",
            "chatbot": "🤖  AI Assistant",
            "officer_profile": "👤  Officer Profile",
            "appreciation": "👥  Appreciation & Team",
        }

        for page_key, page_label in tool_pages.items():
            is_active = st.session_state.current_page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_label, use_container_width=True, type=btn_type, key=f"nav_{page_key}"):
                navigate_to(page_key)
                st.rerun()

        st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)

        # 4. System Controls & Utilities
        is_offline = st.session_state.get("offline_mode", True)
        offline_toggle = st.toggle(
            "Offline Mode Sync",
            value=is_offline,
            key="toggle_offline_mode",
            help="Sync documents to local encrypted vault or live FastAPI backend",
        )
        if offline_toggle != is_offline:
            st.session_state.offline_mode = offline_toggle
            st.rerun()

        # Sign Out Button
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

        # Decision-Support Disclaimer at bottom of sidebar
        st.markdown(
            clean_html(
                """
                <div class="sidebar-disclaimer-box">
                    <span style="font-size: 13px; color: #38bdf8; flex-shrink: 0;">🛡️</span>
                    <span>Screening decision-support only. Does not determine fraud or criminality.</span>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )


# =========================================================
# MAIN APP ROUTER
# =========================================================

if not st.session_state.authenticated:
    show_login()
else:
    render_sidebar()
    render_top_header()
    # Render floating AI Assistant widget only when logged in
    render_floating_chatbot()

    curr = st.session_state.current_page

    if curr == "dashboard":
        render_dashboard()

    elif curr == "officer_profile":
        render_officer_profile()

    elif curr == "new_screening":
        render_new_screening()

    elif curr == "processing":
        render_processing()

    elif curr == "result":
        render_result()

    elif curr == "history":
        render_history()

    elif curr == "case_detail":
        render_case_detail()

    elif curr == "cross_document":
        render_cross_document()

    elif curr == "criminal_database":
        render_criminal_database()

    elif curr == "chatbot":
        render_chatbot_page()

    elif curr == "appreciation":
        render_appreciation()
