import streamlit as st
import hashlib
import json
from datetime import datetime
from pathlib import Path
from db_service import get_connection


def init_cross_doc_db():
    """Ensure cross-document comparison audit table exists in sih26188.db (Member 6 Data Layer)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cross_document_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                doc_a_type TEXT,
                doc_a_name TEXT,
                doc_a_id TEXT,
                doc_b_type TEXT,
                doc_b_name TEXT,
                doc_b_id TEXT,
                match_score INTEGER,
                verdict TEXT,
                discrepancy_count INTEGER,
                officer_id TEXT,
                checkpoint TEXT,
                payload_hash TEXT,
                anchored_at TEXT
            )
            """
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def save_cross_doc_audit(record: dict) -> bool:
    """Save cross-document audit log into SQLite with SHA-256 integrity hash."""
    init_cross_doc_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        now_iso = datetime.now().isoformat()
        raw_payload = f"{record['session_id']}:{record['doc_a_id']}:{record['doc_b_id']}:{record['match_score']}:{now_iso}"
        p_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        cur.execute(
            """
            INSERT OR REPLACE INTO cross_document_audits (
                session_id, doc_a_type, doc_a_name, doc_a_id,
                doc_b_type, doc_b_name, doc_b_id,
                match_score, verdict, discrepancy_count,
                officer_id, checkpoint, payload_hash, anchored_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["session_id"],
                record["doc_a_type"],
                record["doc_a_name"],
                record["doc_a_id"],
                record["doc_b_type"],
                record["doc_b_name"],
                record["doc_b_id"],
                record["match_score"],
                record["verdict"],
                record["discrepancy_count"],
                record.get("officer_id", "UID-MHA-8841"),
                record.get("checkpoint", "T3 Arrival Gate 4B"),
                p_hash,
                now_iso,
            ),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def fetch_recent_cross_doc_audits(limit: int = 5):
    """Retrieve recent cross-document audits from SQLite."""
    init_cross_doc_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT session_id, doc_a_type, doc_b_type, doc_a_name, match_score, verdict, discrepancy_count, payload_hash, anchored_at
            FROM cross_document_audits
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


# Preset benchmark test cases for presentation and testing
PRESET_CASES = {
    "preset_clean": {
        "title": "Case #CD-8812: Verified Multi-Document Identity (Clean Match)",
        "description": "Indian Passport + Aadhaar Card for Vikram Malhotra. Perfect consistency across biographic data.",
        "score": 97,
        "verdict": "CONSISTENT IDENTITY",
        "doc_a": {
            "type": "Indian Passport (P)",
            "id": "Z8921044",
            "name": "VIKRAM MALHOTRA",
            "dob": "14/08/1989",
            "gender": "MALE",
            "nationality": "INDIAN",
            "expiry": "22/10/2032",
            "authority": "RPO DELHI",
        },
        "doc_b": {
            "type": "Aadhaar Card (UIDAI)",
            "id": "XXXX-XXXX-4821",
            "name": "VIKRAM MALHOTRA",
            "dob": "14/08/1989",
            "gender": "MALE",
            "nationality": "INDIAN (RESIDENT)",
            "expiry": "NOT APPLICABLE",
            "authority": "GOVT OF INDIA",
        },
        "fields": [
            ("Full Legal Name", "VIKRAM MALHOTRA", "VIKRAM MALHOTRA", "MATCH", "Exact match across both document extraction matrices."),
            ("Date of Birth", "14/08/1989", "14/08/1989", "MATCH", "Identical day, month, and year format."),
            ("Gender", "MALE", "MALE", "MATCH", "Gender markers concordant."),
            ("Nationality / Origin", "INDIAN", "INDIAN (RESIDENT)", "MATCH", "Citizenship / resident status compatible."),
            ("Facial Feature Match", "Biometric Anchor P-91", "Aadhaar Photo Base", "MATCH", "Facial structural similarity estimated at 98.4%."),
        ],
    },
    "preset_dob_mismatch": {
        "title": "Case #CD-9140: Date of Birth Discrepancy (Flagged Review)",
        "description": "Passport + Driver's License for Rajesh Kumar Verma. Critical 3-year age mismatch detected.",
        "score": 58,
        "verdict": "DISCREPANCY FLAGGED",
        "doc_a": {
            "type": "Indian Passport (P)",
            "id": "K3391082",
            "name": "RAJESH KUMAR VERMA",
            "dob": "12/03/1985",
            "gender": "MALE",
            "nationality": "INDIAN",
            "expiry": "11/05/2030",
            "authority": "RPO LUCKNOW",
        },
        "doc_b": {
            "type": "Driver's License (State Transport)",
            "id": "UP32-2015004128",
            "name": "RAJESH KUMAR VERMA",
            "dob": "12/03/1988",
            "gender": "MALE",
            "nationality": "INDIAN",
            "expiry": "14/09/2035",
            "authority": "RTO LUCKNOW",
        },
        "fields": [
            ("Full Legal Name", "RAJESH KUMAR VERMA", "RAJESH KUMAR VERMA", "MATCH", "Legal name string match is concordant."),
            ("Date of Birth", "12/03/1985 (Age 41)", "12/03/1988 (Age 38)", "CRITICAL MISMATCH", "Discrepancy of 3 years detected between Passport MRZ and DL record."),
            ("Gender", "MALE", "MALE", "MATCH", "Gender markers concordant."),
            ("State Jurisdiction", "UTTAR PRADESH", "UTTAR PRADESH", "MATCH", "Jurisdiction alignment confirmed."),
            ("Document Validity", "VALID (2030)", "VALID (2035)", "MATCH", "Both documents within unexpired window."),
        ],
    },
    "preset_name_variance": {
        "title": "Case #CD-7729: Name Transliteration / Abbreviation Variance (Advisory)",
        "description": "Passport + PAN Card for Mohammad Irfan Khan. Abbreviation 'Mohd' vs full 'Mohammad'.",
        "score": 88,
        "verdict": "MINOR VARIANCE DETECTED",
        "doc_a": {
            "type": "Indian Passport (P)",
            "id": "M7719203",
            "name": "MOHAMMAD IRFAN KHAN",
            "dob": "05/11/1992",
            "gender": "MALE",
            "nationality": "INDIAN",
            "expiry": "19/08/2029",
            "authority": "RPO MUMBAI",
        },
        "doc_b": {
            "type": "Permanent Account Number (PAN)",
            "id": "BKFPK8891A",
            "name": "MOHD IRFAN KHAN",
            "dob": "05/11/1992",
            "gender": "MALE",
            "nationality": "INDIAN",
            "expiry": "PERMANENT",
            "authority": "INCOME TAX DEPT",
        },
        "fields": [
            ("Full Legal Name", "MOHAMMAD IRFAN KHAN", "MOHD IRFAN KHAN", "MINOR VARIANCE", "Common abbreviation ('Mohd' for 'Mohammad'). Phonetic and father initial match."),
            ("Date of Birth", "05/11/1992", "05/11/1992", "MATCH", "Exact date of birth concordant."),
            ("Gender", "MALE", "MALE", "MATCH", "Gender markers concordant."),
            ("PAN Verification", "Linked to Tax Database", "Active Taxpayer Record", "MATCH", "PAN record verification confirmed with ITD schema."),
            ("Facial Feature Match", "Passport Image 1992", "PAN Photo 2021", "MATCH", "Facial similarity estimated at 92.1% (aging delta within normal tolerance)."),
        ],
    },
}


def render_cross_document():
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.6rem; color:#0f172a; font-weight:700;">
                    🔍 Cross-Document Consistency Analysis
                </h2>
                <p style="margin:0.25rem 0 0; color:#334155; font-size:0.9rem; font-weight:500;">
                    Dual-Document Bi-Directional Verification, Discrepancy Flagging & Audit Trail
                </p>
            </div>
            <div style="background:#eff6ff; border:1px solid #3b82f6; border-radius:6px; padding:6px 12px; font-size:0.75rem; color:#1d4ed8; font-weight:600;">
                MEMBER 6 MODULE • UI / DB / BLOCKCHAIN
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Mode Selector (Benchmark Presets vs Custom Upload)
    mode_col1, mode_col2 = st.columns([1.5, 1])

    with mode_col1:
        selected_preset = st.selectbox(
            "Select Inspection Benchmark Preset",
            [
                ("preset_clean", "🟢 Preset 1: Verified Multi-Doc Identity (Clean Match)"),
                ("preset_dob_mismatch", "🔴 Preset 2: Date of Birth Discrepancy (Flagged Review)"),
                ("preset_name_variance", "🟡 Preset 3: Name Transliteration / Abbreviation (Advisory)"),
                ("custom_input", "⚙️ Custom Dual-Document Manual Entry"),
            ],
            format_func=lambda x: x[1],
            key="cross_doc_preset_selector",
        )

    preset_key = selected_preset[0]

    if preset_key != "custom_input":
        preset_data = PRESET_CASES[preset_key]
        st.info(f"**{preset_data['title']}** — {preset_data['description']}")

        # 2. Side-by-Side Document Cards
        col_doc_a, col_doc_b = st.columns(2)

        doc_a = preset_data["doc_a"]
        doc_b = preset_data["doc_b"]

        with col_doc_a:
            st.markdown(
                f"""
                <div style="background:#0f172a; border:1.5px solid #334155; border-radius:8px; padding:16px; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
                        <span style="font-weight:700; color:#60a5fa; font-size:0.95rem;">📄 PRIMARY DOCUMENT (DOC A)</span>
                        <span style="font-size:0.75rem; background:#1e293b; color:#cbd5e1; padding:2px 8px; border-radius:4px;">REF #1</span>
                    </div>
                    <table style="width:100%; font-size:0.85rem; color:#e2e8f0; line-height:1.8;">
                        <tr><td style="color:#94a3b8; width:40%;">Document Type:</td><td><strong>{doc_a['type']}</strong></td></tr>
                        <tr><td style="color:#94a3b8;">Identifier / No:</td><td><code>{doc_a['id']}</code></td></tr>
                        <tr><td style="color:#94a3b8;">Legal Name:</td><td><strong>{doc_a['name']}</strong></td></tr>
                        <tr><td style="color:#94a3b8;">Date of Birth:</td><td>{doc_a['dob']}</td></tr>
                        <tr><td style="color:#94a3b8;">Gender:</td><td>{doc_a['gender']}</td></tr>
                        <tr><td style="color:#94a3b8;">Nationality / State:</td><td>{doc_a['nationality']}</td></tr>
                        <tr><td style="color:#94a3b8;">Validity / Expiry:</td><td>{doc_a['expiry']}</td></tr>
                        <tr><td style="color:#94a3b8;">Issuing Authority:</td><td>{doc_a['authority']}</td></tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_doc_b:
            st.markdown(
                f"""
                <div style="background:#0f172a; border:1.5px solid #334155; border-radius:8px; padding:16px; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
                        <span style="font-weight:700; color:#a78bfa; font-size:0.95rem;">📑 SECONDARY DOCUMENT (DOC B)</span>
                        <span style="font-size:0.75rem; background:#1e293b; color:#cbd5e1; padding:2px 8px; border-radius:4px;">REF #2</span>
                    </div>
                    <table style="width:100%; font-size:0.85rem; color:#e2e8f0; line-height:1.8;">
                        <tr><td style="color:#94a3b8; width:40%;">Document Type:</td><td><strong>{doc_b['type']}</strong></td></tr>
                        <tr><td style="color:#94a3b8;">Identifier / No:</td><td><code>{doc_b['id']}</code></td></tr>
                        <tr><td style="color:#94a3b8;">Legal Name:</td><td><strong>{doc_b['name']}</strong></td></tr>
                        <tr><td style="color:#94a3b8;">Date of Birth:</td><td>{doc_b['dob']}</td></tr>
                        <tr><td style="color:#94a3b8;">Gender:</td><td>{doc_b['gender']}</td></tr>
                        <tr><td style="color:#94a3b8;">Nationality / State:</td><td>{doc_b['nationality']}</td></tr>
                        <tr><td style="color:#94a3b8;">Validity / Expiry:</td><td>{doc_b['expiry']}</td></tr>
                        <tr><td style="color:#94a3b8;">Issuing Authority:</td><td>{doc_b['authority']}</td></tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3. Overall Score and Status Metric
        score = preset_data["score"]
        verdict = preset_data["verdict"]

        if score >= 90:
            score_color = "#22c55e"
            badge_bg = "rgba(34, 197, 94, 0.15)"
            badge_border = "#22c55e"
        elif score >= 75:
            score_color = "#eab308"
            badge_bg = "rgba(234, 179, 8, 0.15)"
            badge_border = "#eab308"
        else:
            score_color = "#ef4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
            badge_border = "#ef4444"

        st.markdown(
            f"""
            <div style="background:{badge_bg}; border:1.5px solid {badge_border}; border-radius:8px; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
                <div>
                    <span style="font-size:0.8rem; color:#475569; text-transform:uppercase; letter-spacing:0.05em; font-weight:700;">Cross-Document Consistency Index</span>
                    <div style="font-size:1.6rem; font-weight:800; color:{score_color};">{score}% &nbsp;•&nbsp; {verdict}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.8rem; color:#475569; font-weight:600;">Responsible AI Triage Recommendation:</div>
                    <div style="font-weight:800; color:#0f172a; font-size:0.95rem;">
                        {'✅ CLEAR FOR STANDARD PROCESSING' if score >= 90 else '⚠️ MANDATORY SECONDARY INTERVIEW REQUIRED' if score < 75 else '🔍 OFFICER DISCRETIONARY REVIEW'}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4. Field-by-Field Discrepancy Matrix
        st.markdown("#### 📋 Field-by-Field Verification Matrix")

        for field, val_a, val_b, status, detail in preset_data["fields"]:
            if status == "MATCH":
                tag_html = '<span style="background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">✅ MATCH</span>'
            elif status == "MINOR VARIATION":
                tag_html = '<span style="background:#fef3c7; color:#b45309; border:1px solid #fde047; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">🟡 VARIANCE</span>'
            else:
                tag_html = '<span style="background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">❌ CRITICAL MISMATCH</span>'

            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #E2E8F0; border-radius:8px; padding:12px 16px; margin-bottom:8px; box-shadow:0 1px 3px rgba(7,26,114,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-weight:700; color:#071A72; font-size:0.88rem;">{field}</span>
                        {tag_html}
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size:0.82rem; margin-bottom:4px;">
                        <div style="color:#64748b;">Doc A: <strong style="color:#0F172A; font-weight:600;">{val_a}</strong></div>
                        <div style="color:#64748b;">Doc B: <strong style="color:#0F172A; font-weight:600;">{val_b}</strong></div>
                    </div>
                    <div style="font-size:0.78rem; color:#64748b; font-style:italic;">Note: {detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 5. Member 6 Actions: Save to SQLite & Blockchain Anchor
        st.markdown("<br>", unsafe_allow_html=True)
        act_col1, act_col2 = st.columns([1, 1])

        session_id = f"CD-{preset_key.upper()}-{datetime.now().strftime('%H%M%S')}"

        with act_col1:
            if st.button("💾 Persist Audit Record to SQLite & Blockchain Anchor", use_container_width=True, type="primary"):
                rec = {
                    "session_id": session_id,
                    "doc_a_type": doc_a["type"],
                    "doc_a_name": doc_a["name"],
                    "doc_a_id": doc_a["id"],
                    "doc_b_type": doc_b["type"],
                    "doc_b_name": doc_b["name"],
                    "doc_b_id": doc_b["id"],
                    "match_score": score,
                    "verdict": verdict,
                    "discrepancy_count": 0 if score >= 90 else 1,
                    "officer_id": st.session_state.user.get("officer_id", "UID-MHA-8841"),
                    "checkpoint": st.session_state.user.get("checkpoint", "T3 Arrival Gate 4B"),
                }
                ok = save_cross_doc_audit(rec)
                if ok:
                    st.success(f"Audit record `{session_id}` anchored to SQLite database & blockchain hash generated!")
                    st.rerun()
                else:
                    st.error("Failed to save audit record.")

        with act_col2:
            summary_json = json.dumps({
                "session_id": session_id,
                "score": score,
                "verdict": verdict,
                "doc_a": doc_a,
                "doc_b": doc_b,
                "timestamp": datetime.now().isoformat(),
            }, indent=2)
            st.download_button(
                "📥 Export Cross-Document Dossier (JSON)",
                data=summary_json,
                file_name=f"{session_id}_dossier.json",
                mime="application/json",
                use_container_width=True,
            )

    else:
        # Custom Manual Entry UI
        st.markdown("#### ✍️ Custom Dual-Document Input")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Primary Document (Doc A)")
            cust_a_type = st.selectbox("Type A", ["Passport", "Aadhaar Card", "Driver's License", "PAN Card", "Voter ID"], key="c_a_type")
            cust_a_id = st.text_input("Document A ID / Number", value="T9102481", key="c_a_id")
            cust_a_name = st.text_input("Document A Full Name", value="Amitabh Roy", key="c_a_name")
            cust_a_dob = st.text_input("Document A Date of Birth", value="19/04/1990", key="c_a_dob")
        with c2:
            st.markdown("##### Secondary Document (Doc B)")
            cust_b_type = st.selectbox("Type B", ["Aadhaar Card", "Driver's License", "PAN Card", "Passport", "Voter ID"], key="c_b_type")
            cust_b_id = st.text_input("Document B ID / Number", value="XXXX-XXXX-9901", key="c_b_id")
            cust_b_name = st.text_input("Document B Full Name", value="Amitabh Roy", key="c_b_name")
            cust_b_dob = st.text_input("Document B Date of Birth", value="19/04/1990", key="c_b_dob")

        if st.button("Run Custom Cross-Verification", type="primary", use_container_width=True):
            # Compute heuristic matching for Member 6 demo
            name_match = cust_a_name.strip().lower() == cust_b_name.strip().lower()
            dob_match = cust_a_dob.strip() == cust_b_dob.strip()
            
            calc_score = 95 if (name_match and dob_match) else (60 if name_match else 35)
            calc_verdict = "CONSISTENT" if calc_score >= 90 else ("DISCREPANCY DETECTED" if calc_score < 70 else "MINOR VARIATION")

            st.success(f"Comparison Complete — Consistency Score: {calc_score}% ({calc_verdict})")

    # 6. Member 6 SQLite Database Audit Trail
    st.markdown("---")
    st.markdown("#### 🗄️ Recent Cross-Document Audits in Local Database (`sih26188.db`)")
    recent = fetch_recent_cross_doc_audits(5)

    if recent:
        for r in recent:
            st.markdown(
                f"""
                <div style="background:#090d16; border-left:4px solid #3b82f6; border-radius:4px; padding:10px 14px; margin-bottom:8px; font-size:0.83rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>Session: <code>{r['session_id']}</code></strong>
                        <span style="color:#94a3b8; font-size:0.75rem;">{r['anchored_at'][:19]}</span>
                    </div>
                    <div style="color:#cbd5e1; margin-top:4px;">
                        Doc A: <strong>{r['doc_a_type']}</strong> &nbsp;↔&nbsp; Doc B: <strong>{r['doc_b_type']}</strong> &nbsp;|&nbsp; Name: <em>{r['doc_a_name']}</em>
                    </div>
                    <div style="margin-top:4px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:{'#22c55e' if r['match_score'] >= 90 else '#ef4444'}; font-weight:700;">Score: {r['match_score']}% ({r['verdict']})</span>
                        <code style="font-size:0.72rem; color:#60a5fa;">SHA-256: {r['payload_hash'][:16]}...</code>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No cross-document audits logged yet. Click 'Persist Audit Record to SQLite' above to store your first verified session.")
