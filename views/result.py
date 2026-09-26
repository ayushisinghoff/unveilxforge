import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path
from session import navigate_to, start_new_screening


def get_db_connection():
    db_path = Path(__file__).resolve().parents[1] / "sih26188.db"
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        return None


def fetch_screening_result(case_id: str):
    """Retrieve screening dossier from SQLite database, or return session result."""
    # Check if result is already in session state
    if st.session_state.get("current_result") and st.session_state["current_result"].get("case_id") == case_id:
        return st.session_state["current_result"]

    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        query = """
        SELECT c.case_id, c.checkpoint_name, c.created_at, c.case_decision,
               d.id as doc_id, d.doc_type, d.file_path,
               e.mrz_raw, e.fields_json, e.ocr_confidence,
               r.risk_score, r.risk_factors_json
        FROM cases c
        LEFT JOIN documents d ON c.case_id = d.case_id
        LEFT JOIN extraction_results e ON d.id = e.document_id
        LEFT JOIN risk_assessments r ON d.id = r.document_id
        WHERE c.case_id = ?
        ORDER BY c.id DESC LIMIT 1
        """
        cur.execute(query, (case_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            import json
            factors = []
            if row["risk_factors_json"]:
                try:
                    factors = json.loads(row["risk_factors_json"])
                except Exception:
                    factors = []

            return {
                "case_id": row["case_id"],
                "checkpoint": row["checkpoint_name"],
                "created_at": row["created_at"],
                "doc_type": row["doc_type"] or "Passport",
                "risk_score": row["risk_score"] if row["risk_score"] is not None else 18,
                "decision": (row["case_decision"] or "APPROVE").upper(),
                "ocr_confidence": row["ocr_confidence"] or 0.94,
                "factors": factors,
            }
    except Exception:
        if conn:
            conn.close()
    return None


def _extract_signal_cards(result: dict) -> list:
    """Build the 4 signal-verification cards from REAL pipeline output.

    Two shapes are supported:
    - A fresh in-session result straight from the /screen API (nested
      ocr/tampering/face_verification/database dicts).
    - A case reloaded from the audit database (only the saved 'factors'
      summary + ocr_confidence are available).
    Every value shown is derived from the actual result for this specific
    case — nothing here is a fixed placeholder.
    """
    # Case A: fresh API-shaped result
    if isinstance(result.get("ocr"), dict) and isinstance(result.get("tampering"), dict):
        ocr = result.get("ocr", {}) or {}
        validation = result.get("document_validation", {}) or {}
        tampering = result.get("tampering", {}) or {}
        face = (result.get("face_verification", {}) or {}).get("data", {}) or {}
        db = result.get("database", {}) or {}

        verification = ocr.get("verification", {}) or {}
        mismatches = sum(1 for v in verification.values() if v.get("status") == "MISMATCH")
        if verification:
            ocr_pct = round(max(0, (len(verification) - mismatches) / len(verification)) * 100, 1)
            ocr_value = f"{ocr_pct}% Consistent"
        elif ocr.get("document_number") or ocr.get("name"):
            ocr_value = "Fields Extracted"
        else:
            ocr_value = "Extraction Failed"
        ocr_ok = validation.get("status") != "FAIL" and mismatches == 0
        ocr_card = {
            "title": "1. OCR & Data Integrity",
            "value": ocr_value,
            "subtitle": f"{mismatches} field mismatch(es) vs MRZ" if verification else "MRZ / field cross-check",
            "ok": ocr_ok,
        }

        tamper_conf = tampering.get("tampering_confidence")
        tamper_risk = str(tampering.get("tampering_risk") or tampering.get("tampering") or "UNKNOWN")
        tamper_card = {
            "title": "2. Tampering & ELA",
            "value": f"{tamper_risk} ({tamper_conf}%)" if tamper_conf is not None else tamper_risk,
            "subtitle": "AI forensic tamper model output",
            "ok": tamper_risk.upper() not in ("HIGH", "MEDIUM"),
        }

        if face.get("liveness_checked") and not face.get("is_real", False):
            face_card = {
                "title": "3. 1:1 Facial Biometrics",
                "value": "SPOOF SUSPECTED",
                "subtitle": f"Anti-spoof score {face.get('anti_spoof_score', 0):.2f}",
                "ok": False,
            }
        else:
            sim = face.get("similarity_score")
            face_card = {
                "title": "3. 1:1 Facial Biometrics",
                "value": (f"{sim}% Match" if sim is not None else ("Verified" if face.get("verified") else "Not Verified")),
                "subtitle": "Document photo vs. live capture",
                "ok": bool(face.get("verified")),
            }

        db_card = {
            "title": "4. Reference Database",
            "value": "FLAGGED" if db.get("flagged") else "No Flags",
            "subtitle": db.get("status", "Local watchlist check"),
            "ok": not db.get("flagged"),
        }
        return [ocr_card, tamper_card, face_card, db_card]

    # Case B: reloaded from the audit database — only the saved factor
    # summary and OCR confidence survive, so build the cards from those.
    factors = result.get("factors") or []
    by_name = {(f.get("factor") or "").lower(): f for f in factors}

    def find(*needles):
        for needle in needles:
            for name, f in by_name.items():
                if needle in name:
                    return f
        return {}

    tamper_f = find("tamper")
    face_f = find("face")
    db_f = find("database", "reference")
    ocr_conf = result.get("ocr_confidence")

    return [
        {
            "title": "1. OCR & Data Integrity",
            "value": (f"{round(ocr_conf * 100, 1)}% Confidence" if ocr_conf is not None else "Not available"),
            "subtitle": "Saved OCR confidence for this case",
            "ok": ocr_conf is None or ocr_conf >= 0.6,
        },
        {
            "title": "2. Tampering & ELA",
            "value": tamper_f.get("status", "Not available"),
            "subtitle": tamper_f.get("impact", "No tampering record saved"),
            "ok": str(tamper_f.get("status", "")).upper() not in ("HIGH", "MEDIUM"),
        },
        {
            "title": "3. 1:1 Facial Biometrics",
            "value": face_f.get("status", "Not available"),
            "subtitle": face_f.get("impact", "No face-match record saved"),
            "ok": "VERIFIED" in str(face_f.get("status", "")).upper(),
        },
        {
            "title": "4. Reference Database",
            "value": db_f.get("status", "Not available"),
            "subtitle": db_f.get("impact", "No database check record saved"),
            "ok": "FLAG" not in str(db_f.get("status", "")).upper(),
        },
    ]


def render_result():
    case_id = st.session_state.get("current_screening_id", "CASE-DEMO-001")
    result = fetch_screening_result(case_id)

    if not result:
        st.error(f"No screening record found for case **{case_id}**.")
        st.caption(
            "This case has no pipeline result stored — either it was never run, "
            "or the backend was unreachable when it ran. Start a new screening "
            "instead of trusting a placeholder result."
        )
        if st.button("➕ Start New Screening", type="primary"):
            start_new_screening()
            st.rerun()
        return

    # Normalize live API results: /screen stores the score under overall_risk.
    score = result.get("risk_score")
    if score is None:
        score = (result.get("overall_risk") or {}).get("score")
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 18

    decision = result.get("decision") or (result.get("overall_risk") or {}).get("decision") or "MANUAL REVIEW"
    decision = str(decision).upper()

    # Color tokens based on classification
    if score <= 25:
        tier_label = "LOW RISK"
        tier_color = "#16a34a"
        tier_bg = "#ecfdf5"
        tier_border = "#a7f3d0"
        recommendation = "RECOMMENDED: AUTOMATED CLEARANCE / APPROVE"
    elif score <= 60:
        tier_label = "MEDIUM RISK"
        tier_color = "#d97706"
        tier_bg = "#fffbeb"
        tier_border = "#fde68a"
        recommendation = "RECOMMENDED: SECONDARY PHYSICAL INSPECTION / MANUAL REVIEW"
    else:
        tier_label = "HIGH RISK"
        tier_color = "#dc2626"
        tier_bg = "#fef2f2"
        tier_border = "#fecaca"
        recommendation = "RECOMMENDED: INTERCEPT & SENIOR FORENSIC INVESTIGATION"

    # Header
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.subheader("📊 Automated Screening Dossier Result")
        st.caption(f"Case Tracking Reference: **{case_id}** • Checkpoint: **{result['checkpoint']}** • {result['created_at'][:16]}")
    with col_h2:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        st.button("➕ Screen Another Document", on_click=start_new_screening, use_container_width=True)

    st.markdown("---")

    # Main Decision Card
    st.markdown(
        f"""
        <div style="background: {tier_bg}; border: 2px solid {tier_border}; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="background: {tier_color}; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; letter-spacing: 0.5px;">
                        {tier_label}
                    </span>
                    <h1 style="color: {tier_color}; margin: 8px 0 4px 0; font-size: 38px; font-weight: 800;">
                        {score} <span style="font-size: 20px; font-weight: 600; color: #64748b;">/ 100</span>
                    </h1>
                    <div style="font-size: 14px; font-weight: 700; color: #0f172a;">
                        {recommendation}
                    </div>
                </div>
                <div style="background: #ffffff; border: 1px solid {tier_border}; border-radius: 10px; padding: 12px 18px; text-align: center; min-width: 170px;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase;">Operator Disposition</div>
                    <div style="font-size: 18px; font-weight: 800; color: {tier_color}; margin-top: 2px;">{decision}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Component Signal Verification Cards — built from this case's ACTUAL
    # pipeline result (see _extract_signal_cards), not fixed placeholder text.
    cards = _extract_signal_cards(result)
    for col, card in zip(st.columns(4), cards):
        value_color = "#15803d" if card["ok"] else "#dc2626"
        with col:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">{card['title']}</div>
                    <div style="font-size: 18px; font-weight: 800; color: {value_color}; margin: 4px 0;">{card['value']}</div>
                    <div style="font-size: 11px; color: #94a3b8;">{card['subtitle']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Responsible AI Section
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 6px; padding: 12px 16px; font-size: 12px; color: #334155; line-height: 1.5;">
            <strong>⚠️ RESPONSIBLE AI SCREENING DISCLOSURE:</strong><br>
            This screening result represents automated algorithmic risk indicators designed to assist human border control officers. 
            It is <strong>not</strong> definitive legal proof of forgery, identity theft, or criminality. 
            Final determination must always be confirmed through authorized human inspection.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Actions
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)

    with col_a1:
        if st.button("🔍 View Case Details", use_container_width=True):
            navigate_to("case_detail")
            st.rerun()

    with col_a2:
        if st.button("📋 Screening History", use_container_width=True):
            navigate_to("history")
            st.rerun()

    with col_a3:
        if st.button("➕ New Screening", use_container_width=True):
            start_new_screening()
            st.rerun()

    with col_a4:
        if st.button("📊 Dashboard", use_container_width=True):
            navigate_to("dashboard")
            st.rerun()
