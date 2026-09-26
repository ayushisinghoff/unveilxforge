import streamlit as st
from datetime import datetime


def render_appreciation():
    user = st.session_state.get("user") or {
        "name": "Insp. Vikramaditya Sharma",
        "officer_id": "UID-MHA-8842",
        "checkpoint": "ICP Attari - Border Checkpoint Alpha",
        "department": "Bureau of Immigration (BOI) - MHA",
        "role": "Senior Document Verification Officer",
    }

    # 1. Header
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.6rem; color:#0f172a; font-weight:700;">
                    👏 Officer Service Recognition & Commendation
                </h2>
                <p style="margin:0.25rem 0 0; color:#334155; font-size:0.9rem; font-weight:500;">
                    Bureau of Immigration • Ministry of Home Affairs • Official Duty Honors & Citations
                </p>
            </div>
            <div style="background:#fef3c7; border:1px solid #f59e0b; border-radius:6px; padding:6px 12px; font-size:0.75rem; color:#92400e; font-weight:700;">
                ★ MERIT CITATION • GRADE A1
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Officer Honor Banner
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, rgba(232, 250, 252, 0.7) 0%, #FFFFFF 65%); border:1px solid #E2E8F0; border-left:5px solid #22BFC9; border-radius:12px; padding:20px 24px; margin-bottom:1.5rem; box-shadow:0 2px 10px rgba(7,26,114,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:64px; height:64px; border-radius:50%; background:linear-gradient(120deg, #071A72, #0B3FBF); border:2px solid #22BFC9; display:flex; align-items:center; justify-content:center; font-size:1.8rem; box-shadow:0 4px 14px rgba(2,132,199,0.4);">
                        🛡️
                    </div>
                    <div>
                        <div style="font-size:1.25rem; font-weight:800; color:#071A72;">
                            {user['name']}
                        </div>
                        <div style="font-size:0.85rem; color:#0878D1; font-weight:700; margin-top:2px;">
                            {user['role']} &nbsp;•&nbsp; <code>{user['officer_id']}</code>
                        </div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">
                            📍 Assigned Post: <strong style="color:#071A72; font-weight:700;">{user.get('checkpoint', 'T3 Arrival Gate 4B')}</strong> &nbsp;|&nbsp; {user.get('department', 'Bureau of Immigration')}
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid #22c55e; padding:4px 10px; border-radius:4px; font-size:0.75rem; font-weight:700;">
                        ACTIVE DUTY • COMMENDED
                    </span>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">
                        Citation Ref: <code>MHA-CIT-2026-8812</code>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Operational Milestones
    st.markdown("#### 🏆 Duty Milestones & Screening Performance")
    m1, m2, m3, m4 = st.columns(4)

    metrics = [
        ("1,428+", "Total Credentials Screened", "100% Audit Logged", "#38bdf8", "🛡️"),
        ("84", "Adverse Risks Intercepted", "Counterfeit & Impoundments", "#ef4444", "🚨"),
        ("99.4%", "Verification Precision", "Zero False Discharges", "#22c55e", "🎯"),
        ("34 sec", "Avg Clearance Time", "High-Throughput Gate Pace", "#facc15", "⚡"),
    ]

    for col, (val, title, sub, colr, icon) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #E2E8F0; box-shadow:0 1px 4px rgba(7,26,114,0.04); border-top:3px solid {colr}; border-radius:8px; padding:14px; text-align:center;">
                    <div style="font-size:1.5rem; margin-bottom:4px;">{icon}</div>
                    <div style="font-size:1.6rem; font-weight:800; color:{colr};">{val}</div>
                    <div style="font-weight:700; color:#071A72; font-size:0.82rem; margin:2px 0;">{title}</div>
                    <div style="font-size:0.72rem; color:#64748b;">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Service Medals & Badges
    st.markdown("#### 🏅 Service Medals & Operational Honors")
    b1, b2, b3, b4 = st.columns(4)

    badges = [
        ("Eagle Eye Citation", "Detected microscopic font and ELA compression forgery with precision.", "🦅", "#38bdf8"),
        ("Guardian of the Gate", "Completed over 1,000 flawless primary line verifications with zero lapses.", "🛡️", "#22c55e"),
        ("Rapid Clearance Star", "Maintained under 40-second queue clearance during high-density flight arrivals.", "⚡", "#facc15"),
        ("Responsible AI Leader", "Exemplary fair triage, avoiding bias while ensuring rigorous secondary review.", "⚖️", "#a855f7"),
    ]

    for col, (b_title, b_desc, b_icon, b_colr) in zip([b1, b2, b3, b4], badges):
        with col:
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #E2E8F0; box-shadow:0 1px 4px rgba(7,26,114,0.04); border-radius:8px; padding:16px; height:100%; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                    <div style="width:48px; height:48px; margin:0 auto 10px; border-radius:50%; background:#E8FAFC; border:1.5px solid {b_colr}; display:flex; align-items:center; justify-content:center; font-size:1.4rem;">
                        {b_icon}
                    </div>
                    <div style="font-size:0.88rem; font-weight:700; color:#071A72; margin-bottom:6px;">{b_title}</div>
                    <div style="font-size:0.76rem; color:#94a3b8; line-height:1.5;">{b_desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Official Commendation Letters
    st.markdown("#### 📜 Official Commendation & Citations on Record")

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="border-left:4px solid #d97706; padding-left:16px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:#0f172a; font-size:0.95rem;">
                        DIRECTORATE GENERAL OF BORDER SECURITY & IMMIGRATION
                    </strong>
                    <span style="font-size:0.75rem; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; padding:2px 8px; border-radius:4px; font-weight:700;">
                        OFFICIAL COMMENDATION
                    </span>
                </div>
                <div style="font-size:0.8rem; color:#475569; margin-top:2px;">
                    Order No: <code>BOI/HQ/SEC-COMM-2026/041</code> &nbsp;•&nbsp; Date: {datetime.now().strftime('%d %B %Y')}
                </div>
            </div>
            <div style="font-size:0.85rem; color:#1e293b; line-height:1.8; font-style:italic;">
                "This commendation is formally awarded to <strong>{user['name']}</strong> (Badge ID: <code>{user['officer_id']}</code>) 
                for displaying exemplary vigilance, steadfast integrity, and superior operational competence while operating the 
                <strong>UnveilX Forge Identity Screening Console</strong> at checkpoint <strong>{user.get('checkpoint', 'T3 Arrival')}</strong>. 
                Your prompt intervention in intercepting advanced digital forgeries and maintaining uncompromised chain-of-custody records 
                has substantially strengthened national border security."
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; border-top:1px solid #e2e8f0; padding-top:10px;">
                <div style="font-size:0.75rem; color:#475569;">
                    Signed by: <strong>Joint Secretary (Internal Security & Border Management)</strong>
                </div>
                <div style="font-size:0.72rem; color:#2563eb; font-family:monospace; font-weight:600;">
                    Cryptographic Seal: SHA256-COMM-8841-VERIFIED
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 6. Action Row: Download Certificate & Log Duty Note
    st.markdown("<br>", unsafe_allow_html=True)
    c_act1, c_act2 = st.columns([1.2, 1])

    with c_act1:
        cert_text = f"""=================================================================
MINISTRY OF HOME AFFAIRS • BUREAU OF IMMIGRATION
OFFICIAL CERTIFICATE OF SERVICE RECOGNITION & COMMENDATION
=================================================================

AWARDED TO: {user['name']}
OFFICER ID: {user['officer_id']}
DESIGNATION: {user['role']}
STATION: {user.get('checkpoint', 'T3 Arrival Gate 4B')}
DATE OF ISSUE: {datetime.now().strftime('%d-%m-%Y')}

SUMMARY OF CITATION:
In formal recognition of extraordinary vigilance, high-precision
document screening, and unwavering dedication to safeguarding national
borders utilizing the UnveilX Forge AI-assisted verification system.

SCREENING METRICS:
- Total Screenings Handled: 1,428+
- Adverse Indicators Intercepted: 84
- Precision Index: 99.4%
- Chain of Custody: Section 65B Compliant (SHA-256 Verified)

AUTHORIZED BY:
Directorate General of Immigration & Border Security
Govt. of India
================================================================="""

        st.download_button(
            "📥 Download Official Commendation Certificate (Text / Dossier)",
            data=cert_text,
            file_name=f"Commendation_{user['officer_id']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary",
        )

    with c_act2:
        if st.button("🎖️ Acknowledge Citation & Record to Personal File", use_container_width=True):
            st.success(f"Commendation citation registered into officer profile `{user['officer_id']}`!")
