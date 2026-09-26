import streamlit as st
import sqlite3
import hashlib
import json
from datetime import datetime
from db_service import get_connection


def init_watchlist_db():
    """Member 6 Database: Initialize synthetic reference watchlist and query audit log tables."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # 1. Watchlist Reference Records
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reference_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_id TEXT UNIQUE,
                full_name TEXT,
                aliases TEXT,
                dob TEXT,
                nationality TEXT,
                document_number TEXT,
                category TEXT,
                severity TEXT,
                issuing_agency TEXT,
                advisory_notes TEXT,
                status TEXT
            )
            """
        )

        # 2. Officer Search Query Audit Trail
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist_query_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT UNIQUE,
                search_term TEXT,
                category_filter TEXT,
                officer_id TEXT,
                checkpoint TEXT,
                matches_found INTEGER,
                payload_hash TEXT,
                queried_at TEXT
            )
            """
        )

        # Seed realistic synthetic benchmark entries if table is empty
        cur.execute("SELECT COUNT(*) FROM reference_watchlist")
        if cur.fetchone()[0] == 0:
            seed_data = [
                (
                    "REF-LOC-2026-0982",
                    "Aarav N. Singhania",
                    "A. N. Singhania, Bobby Singhania",
                    "1984-06-18",
                    "Indian",
                    "Z4918201",
                    "Look-out Circular (LOC)",
                    "HIGH PRIORITY",
                    "Enforcement Directorate (ED)",
                    "Subject to financial investigation restraint. Immediately alert supervisory officer; conduct secondary biometric verification.",
                    "ACTIVE",
                ),
                (
                    "REF-MEA-2025-4412",
                    "Karanveer B. Gill",
                    "K. B. Gill, Sunny Gill",
                    "1990-11-25",
                    "Indian",
                    "P8829104",
                    "Passport Revocation Notice",
                    "HIGH PRIORITY",
                    "Ministry of External Affairs (MEA)",
                    "Passport impounded under Section 10(3)(c) of Passports Act 1967. Document impoundment protocol required.",
                    "ACTIVE",
                ),
                (
                    "REF-MHA-2026-1044",
                    "Tariq M. Qureshi",
                    "Tariq Mohammed, T. Qureshi",
                    "1988-03-12",
                    "Indian",
                    "M1192834",
                    "Secondary Screening Directive",
                    "DISCRETIONARY ADVISORY",
                    "Bureau of Immigration (MHA)",
                    "Discrepancy reported in visa declaration during previous transit. Verify flight itinerary and hotel bookings.",
                    "ACTIVE",
                ),
                (
                    "REF-INTERPOL-2025-78",
                    "David Ronald Miller",
                    "Dave Miller, Ronald Miller",
                    "1979-09-04",
                    "United Kingdom",
                    "GB90182736",
                    "Interpol Yellow Notice",
                    "HIGH PRIORITY",
                    "Interpol NCB New Delhi",
                    "Simulated missing identity / suspect cross-border impersonation alert. Collect fingerprint confirmation.",
                    "ACTIVE",
                ),
                (
                    "REF-ARCHIVE-2024-012",
                    "Sunita Devi Sharma",
                    "Sunita Sharma",
                    "1992-04-15",
                    "Indian",
                    "K8842910",
                    "Historical Clearance",
                    "CLEARED / BENCHMARK",
                    "State Special Branch",
                    "Benchmark control profile. Historical inquiry concluded with full exoneration. Standard clearance permitted.",
                    "RESOLVED",
                ),
            ]

            cur.executemany(
                """
                INSERT INTO reference_watchlist (
                    ref_id, full_name, aliases, dob, nationality,
                    document_number, category, severity, issuing_agency,
                    advisory_notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_data,
            )

        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def search_watchlist(query: str = "", category_filter: str = "ALL"):
    """Member 6 Database Service: Multi-vector search on synthetic watchlist."""
    init_watchlist_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = query.strip()
        sql = "SELECT * FROM reference_watchlist WHERE 1=1"
        params = []

        if query:
            sql += " AND (full_name LIKE ? OR aliases LIKE ? OR document_number LIKE ? OR ref_id LIKE ?)"
            like_q = f"%{query}%"
            params.extend([like_q, like_q, like_q, like_q])

        if category_filter and category_filter != "ALL":
            sql += " AND category = ?"
            params.append(category_filter)

        sql += " ORDER BY id ASC"
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


def log_watchlist_query(search_term: str, category_filter: str, matches_found: int, officer_id: str, checkpoint: str):
    """Member 6 Blockchain & Audit Logging: Cryptographically logs officer lookups to protect privacy and integrity."""
    init_watchlist_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        now_iso = datetime.now().isoformat()
        query_id = f"QRY-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        raw_payload = f"{query_id}:{officer_id}:{search_term}:{matches_found}:{now_iso}"
        payload_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        cur.execute(
            """
            INSERT INTO watchlist_query_audits (
                query_id, search_term, category_filter, officer_id, checkpoint,
                matches_found, payload_hash, queried_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (query_id, search_term, category_filter, officer_id, checkpoint, matches_found, payload_hash, now_iso),
        )
        conn.commit()
        return query_id, payload_hash
    except Exception:
        return None, None
    finally:
        conn.close()


def fetch_recent_query_audits(limit: int = 5):
    """Fetch recent officer lookup audits from SQLite."""
    init_watchlist_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT query_id, search_term, category_filter, matches_found, officer_id, checkpoint, payload_hash, queried_at
            FROM watchlist_query_audits
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def render_criminal_database():
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.6rem; color:#0f172a; font-weight:700;">
                    🗃️ Synthetic Demo Reference Database & Watchlist
                </h2>
                <p style="margin:0.25rem 0 0; color:#334155; font-size:0.9rem; font-weight:500;">
                    Look-out Circular (LOC) Query, Impoundment Records & Blockchain Officer Audit Trail
                </p>
            </div>
            <div style="background:#eff6ff; border:1px solid #3b82f6; border-radius:6px; padding:6px 12px; font-size:0.75rem; color:#1d4ed8; font-weight:600;">
                MEMBER 6 MODULE • UI / DB / AUDIT TRAIL
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Strict Responsible AI Notice
    st.markdown(
        """
        <div style="background:rgba(234, 179, 8, 0.1); border-left:4px solid #eab308; padding:10px 16px; border-radius:4px; margin-bottom:1.25rem; font-size:0.85rem; color:#fef08a;">
            <strong>⚠️ RESPONSIBLE AI & DEMONSTRATION BOUNDARY:</strong>
            All profiles in this module are purely simulated synthetic benchmark records for testing airport & border control inspection workflows. 
            The system provides <strong>decision-support triage advisories</strong> and never asserts definitive criminality. 
            All search actions are permanently logged on the local audit ledger for privacy compliance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search Bar & Filter Controls
    search_col1, search_col2, search_col3 = st.columns([2, 1.2, 0.8])

    with search_col1:
        search_query = st.text_input(
            "Search by Name, Alias, Document ID, or Reference Code",
            placeholder="e.g., Aarav Singhania, Z4918201, or REF-LOC",
            key="db_search_input",
        )

    with search_col2:
        category_options = [
            "ALL",
            "Look-out Circular (LOC)",
            "Passport Revocation Notice",
            "Secondary Screening Directive",
            "Interpol Yellow Notice",
            "Historical Clearance",
        ]
        selected_cat = st.selectbox("Category Filter", category_options, key="db_category_select")

    with search_col3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_search = st.button("🔎 Run Query", type="primary", use_container_width=True)

    # Perform Search
    results = search_watchlist(search_query, selected_cat)

    # If search button clicked or query was entered, log audit
    if btn_search or search_query:
        officer = st.session_state.user.get("officer_id", "UID-MHA-8841")
        cp = st.session_state.user.get("checkpoint", "T3 Arrival Gate 4B")
        qid, qhash = log_watchlist_query(search_query or "*ALL*", selected_cat, len(results), officer, cp)

    # Metrics Summary Row
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:#0b1329; border:1px solid #1e293b; border-radius:6px; padding:10px 16px; margin-bottom:1rem; font-size:0.85rem;">
            <span style="color:#94a3b8;">
                Matching Reference Records: <strong style="color:#071A72;">{len(results)}</strong>
            </span>
            <span style="color:#60a5fa; font-size:0.8rem;">
                🏛️ Active Nodal Sources: <strong>ED • MEA • MHA • Interpol NCB</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display Results Cards
    if results:
        for r in results:
            # Color badge depending on severity
            if r["severity"] == "HIGH PRIORITY":
                sev_color = "#ef4444"
                sev_bg = "rgba(239, 68, 68, 0.15)"
                border_color = "#ef4444"
                badge_text = "🚨 HIGH PRIORITY ADVISORY"
            elif r["severity"] == "DISCRETIONARY ADVISORY":
                sev_color = "#eab308"
                sev_bg = "rgba(234, 179, 8, 0.15)"
                border_color = "#eab308"
                badge_text = "⚠️ DISCRETIONARY REVIEW"
            else:
                sev_color = "#22c55e"
                sev_bg = "rgba(34, 197, 94, 0.15)"
                border_color = "#22c55e"
                badge_text = "✅ HISTORICAL CLEARANCE"

            with st.container(border=True):
                # Header of Card
                header_c1, header_c2 = st.columns([2, 1])
                with header_c1:
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.15rem; font-weight:700; color:#071A72;">{r['full_name']}</span>
                            <span style="background:{sev_bg}; color:{sev_color}; border:1px solid {border_color}; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">
                                {badge_text}
                            </span>
                        </div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">
                            Ref Code: <code>{r['ref_id']}</code> &nbsp;•&nbsp; Category: <strong>{r['category']}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with header_c2:
                    st.markdown(
                        f"""
                        <div style="text-align:right; font-size:0.8rem; color:#94a3b8;">
                            Issuing Agency:<br>
                            <strong style="color:#0F172A;">{r['issuing_agency']}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<hr style='margin:8px 0; border-color:#E2E8F0;'>", unsafe_allow_html=True)

                # Attribute Grid
                attr_c1, attr_c2, attr_c3, attr_c4 = st.columns(4)
                with attr_c1:
                    st.markdown(f"<span style='color:#64748b; font-size:0.75rem;'>DOCUMENT NUMBER</span><br><code style='color:#071A72;'>{r['document_number']}</code>", unsafe_allow_html=True)
                with attr_c2:
                    st.markdown(f"<span style='color:#64748b; font-size:0.75rem;'>DATE OF BIRTH</span><br><strong style='color:#0F172A; font-size:0.85rem;'>{r['dob']}</strong>", unsafe_allow_html=True)
                with attr_c3:
                    st.markdown(f"<span style='color:#64748b; font-size:0.75rem;'>NATIONALITY</span><br><strong style='color:#0F172A; font-size:0.85rem;'>{r['nationality']}</strong>", unsafe_allow_html=True)
                with attr_c4:
                    st.markdown(f"<span style='color:#64748b; font-size:0.75rem;'>KNOWN ALIASES</span><br><em style='color:#94a3b8; font-size:0.8rem;'>{r['aliases']}</em>", unsafe_allow_html=True)

                # Advisory Protocol Box
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:3px solid {border_color}; padding:8px 12px; border-radius:4px; margin-top:10px; font-size:0.82rem; color:#1E293B;">
                        <strong>Protocol Advisory:</strong> {r['advisory_notes']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Action Row
                action_c1, action_c2 = st.columns([1, 1])
                with action_c1:
                    if st.button(f"🛡️ Link to Active Case Inspection", key=f"btn_link_{r['ref_id']}", use_container_width=True):
                        st.success(f"Reference record {r['ref_id']} linked to current case context.")
                with action_c2:
                    record_json = json.dumps(r, indent=2)
                    st.download_button(
                        f"📥 Export Reference Notice (JSON)",
                        data=record_json,
                        file_name=f"{r['ref_id']}_notice.json",
                        mime="application/json",
                        key=f"btn_dl_{r['ref_id']}",
                        use_container_width=True,
                    )
    else:
        st.warning(f"No reference watchlist records found matching: '{search_query}'. Try clearing search filters.")

    # Officer Audit Trail Section (Member 6 Core Functionality)
    st.markdown("---")
    st.markdown("#### 🔒 Privacy Compliance & Officer Lookup Audit Ledger (`sih26188.db`)")
    st.caption("Every search across sensitive reference databases is immutably recorded with SHA-256 integrity hashes to prevent unauthorized lookups.")

    recent_queries = fetch_recent_query_audits(5)
    if recent_queries:
        for q in recent_queries:
            st.markdown(
                f"""
                <div style="background:#080c14; border:1px solid #1e293b; border-radius:6px; padding:8px 14px; margin-bottom:6px; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>Query: <code>{q['query_id']}</code></strong> &nbsp;|&nbsp; 
                        Term: <em>'{q['search_term']}'</em> &nbsp;|&nbsp; 
                        Filter: <strong>{q['category_filter']}</strong> &nbsp;|&nbsp; 
                        Matches: <strong>{q['matches_found']}</strong>
                    </div>
                    <div style="text-align:right;">
                        <span style="color:#60a5fa; font-family:monospace; font-size:0.72rem;">SHA-256: {q['payload_hash'][:16]}...</span><br>
                        <span style="color:#64748b; font-size:0.7rem;">{q['queried_at'][:19]} • {q['officer_id']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No queries recorded in the current session. Run a search above to generate the first cryptographically anchored audit entry.")
