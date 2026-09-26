import streamlit as st


def initialize_session():
    """Initialize all Streamlit session state variables."""

    defaults = {
        "authenticated": False,
        "user": None,
        "current_page": "dashboard",
        "offline_mode": True,  # Default to True for reliable offline/demo presentations
        "current_screening_id": None,
        "current_result": None,
        "document_file": None,
        "selfie_file": None,
        "cross_doc_1": None,
        "cross_doc_2": None,
        # Bumped every time a screening is finished/reset so the file uploader and
        # live-camera widgets on the New Screening page get brand-new Streamlit
        # widget keys instead of re-using stale, "stuck" ones.
        "screening_nonce": 0,
        "chat_history": [
            {
                "role": "assistant",
                "content": (
                    "Hello Officer. I am your Screening Decision Assistant. "
                    "You can ask me about risk score calculations, OCR discrepancies, "
                    "tampering indicators, or guidelines for manual secondary inspection."
                ),
            }
        ],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(email: str, checkpoint: str = "ICP Attari - Border Checkpoint Alpha", name: str = None):
    """Store authenticated officer information."""
    st.session_state.authenticated = True
    
    officer_name = name or "Insp. Vikramaditya Sharma"
    officer_id = "UID-MHA-8842"
    dept = "Bureau of Immigration (BOI) - MHA"
    role = "Senior Document Verification Officer"

    if "zhang" in email.lower():
        officer_name = "Officer S. Zhang"
        officer_id = "UID-MHA-4091"
        dept = "Border Control & Document Verification"
        role = "Primary Line Verification Officer"
    elif "admin" in email.lower():
        officer_name = "Admin Rajesh Kumar"
        officer_id = "ADM-SEC-001"
        dept = "National Identity Screening Directorate"
        role = "System Administrator"

    st.session_state.user = {
        "name": officer_name,
        "officer_id": officer_id,
        "department": dept,
        "role": role,
        "email": email,
        "checkpoint": checkpoint,
    }
    st.session_state.current_page = "dashboard"


def logout_user():
    """Clear authentication-related state and reset session."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_page = "dashboard"
    st.session_state.current_screening_id = None
    st.session_state.current_result = None
    st.session_state.document_file = None
    st.session_state.selfie_file = None


def navigate_to(page_name: str):
    """Navigate to a specific page view."""
    st.session_state.current_page = page_name


def start_new_screening():
    """Reset every piece of state left over from the previous screening and
    navigate to a clean 'New Screening' page.

    This is the fix for "can't start a new screening in the same login":
    previously, navigating back to New Screening kept the old uploaded
    document, the old live-camera capture, and the old pipeline result in
    session_state, so the page looked pre-filled/frozen and new uploads or a
    fresh camera capture appeared to do nothing. Bumping screening_nonce also
    forces the file_uploader and webrtc_streamer widgets to be recreated with
    new keys, instead of re-using widget instances left in a finished state.
    """
    for key in [
        "document_file", "document_name",
        "selfie_file", "selfie_name",
        "live_face_quality",
        "current_result", "current_screening_id",
        "selected_doc_type",
    ]:
        st.session_state.pop(key, None)
    st.session_state.screening_nonce = st.session_state.get("screening_nonce", 0) + 1
    st.session_state.current_page = "new_screening"
