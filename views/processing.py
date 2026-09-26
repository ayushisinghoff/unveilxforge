import os
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

from session import navigate_to
from db_service import save_screening_case

API_URL = os.getenv("UNVEILX_API_URL", "http://127.0.0.1:8000")


def _call_pipeline():
    doc = st.session_state.get("document_file")
    selfie = st.session_state.get("selfie_file")
    if not doc or not selfie:
        raise RuntimeError("Both document and selfie are required.")

    doc_name = st.session_state.get("document_name") or "document.jpg"
    selfie_name = st.session_state.get("selfie_name") or "selfie.jpg"
    files = {
        "file": (doc_name, doc, "image/jpeg"),
        "selfie": (selfie_name, selfie, "image/jpeg"),
    }
    response = requests.post(f"{API_URL}/screen", files=files, timeout=600)
    response.raise_for_status()
    return response.json()


def _build_factors(result):
    factors = []
    ocr = result.get("ocr", {})
    validation = result.get("document_validation", {})
    tampering = result.get("tampering", {})
    face = result.get("face_verification", {})
    db = result.get("database", {})

    factors.append({"factor": "OCR / MRZ consistency", "status": ocr.get("document_status", {}).get("status", "REVIEW"), "impact": "Structured document fields extracted."})
    factors.append({"factor": "Document image validation", "status": validation.get("status", "REVIEW"), "impact": "Resolution, blur and brightness checks."})
    factors.append({"factor": "Tampering AI", "status": tampering.get("tampering", "UNKNOWN"), "impact": f"Confidence {tampering.get('tampering_confidence', 0)}%"})
    face_data = face.get("data", {}) or {}
    if face_data.get("liveness_checked") and not face_data.get("is_real", False):
        face_status = "PAUSED — POSSIBLE SPOOF"
        face_impact = f"Anti-spoof score {face_data.get('anti_spoof_score', 0):.2f}"
    elif face_data.get("verified"):
        face_status = "VERIFIED"
        face_impact = f"Similarity {face_data.get('similarity_score', 0)}"
    else:
        face_status = "REVIEW"
        face_impact = f"Similarity {face_data.get('similarity_score', 0)}"
    factors.append({"factor": "Face verification", "status": face_status, "impact": face_impact})
    factors.append({"factor": "Reference database", "status": "FLAGGED" if db.get("flagged") else "CLEAR", "impact": db.get("status", "No matching record")})
    return factors


def render_processing():
    case_id = st.session_state.get("current_screening_id", "CASE-DEMO-001")
    doc_type = st.session_state.get("selected_doc_type", "Passport")
    user = st.session_state.get("user", {}) or {}
    checkpoint = user.get("checkpoint", "ICP Attari - Border Checkpoint Alpha")

    st.subheader("⚙️ Multi-Layer Forensic Screening")
    st.caption(f"Case: {case_id}  •  Document: {doc_type}  •  Checkpoint: {checkpoint}")

    if st.session_state.get("current_result") is None:
        with st.status("Running integrated screening pipeline...", expanded=True) as status:
            st.write("📁 Ingesting uploaded document and selfie...")
            st.write("🔍 Running OCR + MRZ extraction...")
            st.write("📑 Running document quality / MRZ / QR validation...")
            st.write("🔬 Running tampering detection model...")
            st.write("👤 Running 1:1 face verification...")
            st.write("🗂️ Checking the local reference database...")
            try:
                result = _call_pipeline()
                result["case_id"] = case_id
                result["checkpoint"] = checkpoint
                result["doc_type"] = doc_type
                result["created_at"] = datetime.now().isoformat(timespec="seconds")
                st.session_state.current_result = result

                # Keep a local copy of the uploaded document for the audit record.
                upload_dir = Path(__file__).resolve().parents[1] / "uploads"
                upload_dir.mkdir(exist_ok=True)
                doc_name = st.session_state.get("document_name") or "document.jpg"
                safe_name = Path(doc_name).name
                with open(upload_dir / f"{case_id}_{safe_name}", "wb") as f:
                    f.write(st.session_state["document_file"])

                score = int(result.get("overall_risk", {}).get("score", 0))
                level = result.get("overall_risk", {}).get("level", "LOW")
                decision = result.get("decision", "MANUAL REVIEW")
                fields = result.get("ocr", {})
                save_screening_case(
                    case_id=case_id,
                    checkpoint_name=checkpoint,
                    doc_type=doc_type,
                    risk_score=score,
                    decision=decision,
                    factors=_build_factors(result),
                    fields={
                        "name": fields.get("name"),
                        "dob": fields.get("dob"),
                        "passport_no": fields.get("document_number"),
                        "nationality": fields.get("nationality"),
                        "expiry_date": fields.get("mrz", {}).get("date_of_expiry"),
                    },
                    officer_id=1,
                    mrz_raw="\n".join(fields.get("mrz", {}).get("raw_mrz", []) or []),
                    ocr_confidence=None,
                    file_name=st.session_state.get("document_name"),
                )
                status.update(label=f"Screening complete — {level} / {decision}", state="complete", expanded=False)
            except Exception as exc:
                status.update(label="Pipeline failed", state="error", expanded=True)
                st.error(f"Could not complete screening: {exc}")
                st.info("Make sure the local API is running. The Start UnveilX Forge shortcut does this automatically.")
                if st.button("↩ Back to New Screening"):
                    navigate_to("new_screening")
                    st.rerun()
                return

    result = st.session_state.get("current_result")
    if result:
        face_data = result.get("face_verification", {}).get("data", {}) or {}
        if face_data.get("liveness_checked") and not face_data.get("is_real", False):
            st.error("🛑 FACE VERIFICATION PAUSED — POSSIBLE SPOOF DETECTED")
            st.warning("The biometric step was stopped because the live capture did not pass the anti-spoof/liveness gate. Do not approve this case automatically; retake a live capture or send it for manual review.")
        else:
            st.success("✅ Real module results have been received and stored in the local audit database.")
        if st.button("📊 View Comprehensive Screening Result", type="primary", use_container_width=True):
            navigate_to("result")
            st.rerun()
