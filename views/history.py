import streamlit as st
import sqlite3
import pandas as pd
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


def fetch_all_history():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        query = """
        SELECT c.case_id, c.checkpoint_name, c.created_at, c.case_decision,
               COALESCE(r.risk_score, 0) as risk_score,
               COALESCE(d.doc_type, 'Passport') as doc_type,
               COALESCE(b.tx_hash, '0xPendingAnchor...') as tx_hash,
               COALESCE(b.verified, 1) as verified
        FROM cases c
        LEFT JOIN documents d ON c.case_id = d.case_id
        LEFT JOIN risk_assessments r ON d.id = r.document_id
        LEFT JOIN blockchain_anchors b ON c.case_id = b.case_id
        GROUP BY c.case_id
        ORDER BY c.id DESC
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        records = []
        for r in rows:
            decision = r["case_decision"]
            score = r["risk_score"]
            if not decision:
                if score > 60:
                    decision = "REJECT / INVESTIGATE"
                elif score > 25:
                    decision = "MANUAL REVIEW"
                else:
                    decision = "APPROVE"
            else:
                decision = decision.upper()

            records.append({
                "Case ID": r["case_id"],
                "Document": str(r["doc_type"]).capitalize(),
                "Checkpoint": r["checkpoint_name"].replace("_", " "),
                "Timestamp": str(r["created_at"])[:16].replace("T", " "),
                "Risk Score": f"{score}/100",
                "Decision": decision,
                "Blockchain Anchor": r["tx_hash"][:16] + "...",
                "_full_tx": r["tx_hash"],
                "_score_raw": score,
            })
        return records
    except Exception:
        if conn:
            conn.close()
        return []


def render_history():
    st.subheader("📋 Case Screening History & Audit Ledger")
    st.markdown(
        """
        <div style="color: #64748b; font-size: 13px; margin-top: -8px; margin-bottom: 18px;">
            Immutable case records retrieved from local SQLite database and anchored to blockchain verification ledger.
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = fetch_all_history()

    if not records:
        st.info("No past screening cases found in database.")
        if st.button("➕ Start First Screening", type="primary"):
            start_new_screening()
            st.rerun()
        return

    # Filter Bar
    col_s, col_f, col_sort = st.columns([2, 1.2, 1])

    with col_s:
        search_query = st.text_input("🔍 Search by Case ID or Checkpoint", placeholder="e.g. fac7 or T3...")

    with col_f:
        decision_filter = st.selectbox(
            "Filter by Disposition",
            ["All Dispositions", "APPROVE", "MANUAL REVIEW", "REJECT"],
        )

    with col_sort:
        sort_order = st.selectbox("Sort By", ["Newest First", "Highest Risk", "Lowest Risk"])

    # Apply filters
    filtered = records
    if search_query.strip():
        q = search_query.lower().strip()
        filtered = [r for r in filtered if q in r["Case ID"].lower() or q in r["Checkpoint"].lower()]

    if decision_filter != "All Dispositions":
        filtered = [r for r in filtered if decision_filter in r["Decision"]]

    if sort_order == "Highest Risk":
        filtered = sorted(filtered, key=lambda x: x["_score_raw"], reverse=True)
    elif sort_order == "Lowest Risk":
        filtered = sorted(filtered, key=lambda x: x["_score_raw"])

    # Metric summary pill row
    st.markdown(
        """
        <style>
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #ffffff !important;
            font-weight: 800 !important;
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] * {
            color: #cbd5e1 !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            font-size: 11px !important;
            letter-spacing: 0.5px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    c1.metric("Total Ingested Cases", len(records))
    c2.metric("Filtered View", len(filtered))

    st.markdown("<br>", unsafe_allow_html=True)

    # Clean display table
    display_df = pd.DataFrame([
        {
            "Case Tracking ID": r["Case ID"],
            "Document Type": r["Document"],
            "Checkpoint": r["Checkpoint"],
            "Date / Time": r["Timestamp"],
            "Risk Score": r["Risk Score"],
            "Decision": r["Decision"],
            "Blockchain Anchor": r["Blockchain Anchor"],
        }
        for r in filtered
    ])

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Case Inspector tool
    st.markdown("#### 🔎 Open Specific Case Dossier")
    col_pick, col_go = st.columns([2.5, 1])

    with col_pick:
        case_options = [r["Case ID"] for r in records]
        selected_cid = st.selectbox(
            "Select Case Tracking ID to inspect",
            case_options,
            index=None,
            placeholder="Select Case Tracking ID...",
            key="inspect_case_selection",
        )

    with col_go:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📂 Open Detailed Dossier", type="primary", use_container_width=True):
            if selected_cid:
                st.session_state.current_screening_id = selected_cid
                navigate_to("case_detail")
                st.rerun()
            else:
                st.warning("Please select a Case Tracking ID to inspect.")

    # CSV Export button
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Audit History (CSV)",
        data=csv_data,
        file_name="unveilx_screening_history.csv",
        mime="text/csv",
    )
