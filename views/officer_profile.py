import streamlit as st
import textwrap
from session import logout_user


def render_officer_profile():
    user = st.session_state.get("user", {})

    st.subheader("👤 Officer Profile & Station Credentials")
    st.markdown(
        textwrap.dedent(
            """
            <div style="color: #64748b; font-size: 13px; margin-top: -8px; margin-bottom: 16px;">
                Authorized border security, immigration, and document verification personnel dossier.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # Main Officer ID Dossier Card
    col_card, col_stats = st.columns([1.5, 1])

    with col_card:
        card_html = textwrap.dedent(
            f"""
            <div style="background: linear-gradient(135deg, rgba(232, 250, 252, 0.7) 0%, #FFFFFF 65%); border: 1px solid #E2E8F0; border-left: 5px solid #22BFC9; border-radius: 14px; padding: 22px; color: #0F172A; box-shadow: 0 4px 16px rgba(7,26,114,0.05);">
                <div style="display: flex; align-items: center; margin-bottom: 14px;">
                    <div style="width: 52px; height: 52px; background: linear-gradient(120deg, #071A72, #0B3FBF); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 26px; margin-right: 14px; box-shadow: 0 4px 12px rgba(37,99,235,0.4);">
                        🛡️
                    </div>
                    <div>
                        <div style="font-size: 18px; font-weight: 800; letter-spacing: 0.3px;">{user.get('name', 'Insp. Vikramaditya Sharma')}</div>
                        <div style="color: #0878D1; font-size: 12px; font-weight: 600;">{user.get('role', 'Senior Document Verification Officer')}</div>
                    </div>
                </div>
                <div style="border-top: 1px solid #E2E8F0; padding-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
                    <div>
                        <span style="color: #94a3b8;">Officer ID:</span><br>
                        <strong style="color: #071A72;">{user.get('officer_id', 'UID-MHA-8842')}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Department:</span><br>
                        <strong style="color: #071A72;">{user.get('department', 'Bureau of Immigration (BOI) - MHA')}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Official Email:</span><br>
                        <strong style="color: #071A72;">{user.get('email', 's.zhang@border-verification.gov.in')}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Assigned Gate:</span><br>
                        <strong style="color: #0B3FBF;">{user.get('checkpoint', "ICP Attari - Border Checkpoint Alpha")}</strong>
                    </div>
                </div>
                <div style="margin-top: 14px; background: #E8FAFC; border: 1px solid #22BFC9; border-radius: 6px; padding: 6px 10px; font-size: 11px; display: flex; justify-content: space-between; align-items: center;">
                    <span>Security Clearance: <strong>GovRAMP Level 3</strong></span>
                    <span style="color: #34d399; font-weight: 700;">● ACTIVE SHIFT</span>
                </div>
            </div>
            """
        )
        st.markdown(card_html, unsafe_allow_html=True)

    with col_stats:
        stats_html = textwrap.dedent(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                    📊 Shift Performance Summary
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 12px;">
                    <span style="color: #64748b;">Total Screenings:</span>
                    <strong style="color: #0f172a;">12 Cases</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 12px;">
                    <span style="color: #16a34a;">Clearance Rate:</span>
                    <strong style="color: #16a34a;">75.0%</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 12px;">
                    <span style="color: #d97706;">Secondary Review:</span>
                    <strong style="color: #d97706;">3 Cases</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0; font-size: 12px;">
                    <span style="color: #dc2626;">Flagged / High Risk:</span>
                    <strong style="color: #dc2626;">2 Cases</strong>
                </div>
            </div>
            """
        )
        st.markdown(stats_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Edit Profile Section
    with st.expander("✏️ Edit Officer Profile & Assigned Gate", expanded=False):
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            new_name = st.text_input("Officer Full Name", value=user.get("name", "Insp. Vikramaditya Sharma"))
            new_dept = st.text_input("Department / Branch", value=user.get("department", "Bureau of Immigration (BOI) - MHA"))

        with col_e2:
            new_email = st.text_input("Official Email Address", value=user.get("email", "s.zhang@border-verification.gov.in"))
            new_checkpoint = st.selectbox(
                "Assigned Checkpoint Gate",
                [
                    "ICP Attari - Border Checkpoint Alpha",
                    "T3 - Int'l Arrival Gate 4B",
                    "Nhava Sheva - Sea Port Terminal 2",
                    "RGIA Hyderabad - E-Gate Immigration 01",
                ],
                index=0,
            )

        if st.button("💾 Save Profile Changes", type="primary"):
            st.session_state.user["name"] = new_name.strip()
            st.session_state.user["department"] = new_dept.strip()
            st.session_state.user["email"] = new_email.strip()
            st.session_state.user["checkpoint"] = new_checkpoint
            st.success("Officer profile updated successfully!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Sign Out Option
    col_out, _ = st.columns([1, 3])
    with col_out:
        if st.button("🚪 Sign Out / End Shift", use_container_width=True):
            logout_user()
            st.rerun()

    st.markdown(
        textwrap.dedent(
            """
            <div style="margin-top: 20px; font-size: 11px; color: #94a3b8; text-align: center;">
                🔒 Certified GovRAMP L3 Security Profile • Demo Simulation for Smart India Hackathon
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
