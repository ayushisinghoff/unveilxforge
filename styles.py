import streamlit as st


def load_global_styles():
    st.markdown(
        """
        <style>

        /* =========================================================
           DESIGN TOKENS & CSS VARIABLES (LIGHT/WHITE MODE IDENTITY)
           ========================================================= */

        :root {
            /* Core Color Palette */
            --primary-navy: #071A72;
            --primary-blue: #0B3FBF;
            --bright-blue: #0878D1;
            --accent-cyan: #38bdf8;
            --light-cyan: #E8FAFC;
            --pure-white: #FFFFFF;
            --background: #081728;
            --surface: #FFFFFF;
            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;
            --border: #E2E8F0;
            --border-hover: #CBD5E1;
            --border-focus: #38bdf8;

            /* Selective Identity Gradients */
            --gradient-brand: linear-gradient(120deg, #071A72 0%, #0B3FBF 45%, #22BFC9 100%);
            --gradient-oceanic: radial-gradient(circle at 50% 25%, #18426d 0%, #0e2746 45%, #071628 100%);
            --gradient-btn: linear-gradient(180deg, #0284c7 0%, #0369a1 100%);
            --gradient-btn-hover: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
            --gradient-cyan-subtle: linear-gradient(135deg, #E8FAFC 0%, #FFFFFF 100%);
            --gradient-hero: linear-gradient(135deg, rgba(232, 250, 252, 0.6) 0%, rgba(255, 255, 255, 0.95) 65%);
            --gradient-border-accent: linear-gradient(120deg, #071A72, #0B3FBF, #22BFC9);

            /* Shadows */
            --shadow-xs: 0 1px 2px rgba(7, 26, 114, 0.04);
            --shadow-sm: 0 2px 6px rgba(7, 26, 114, 0.05);
            --shadow-md: 0 6px 18px rgba(7, 26, 114, 0.07);
            --shadow-lg: 0 12px 32px rgba(7, 26, 114, 0.10);
            --shadow-glow: 0 4px 18px rgba(56, 189, 248, 0.35);
            --shadow-card: 0 1px 4px rgba(7, 26, 114, 0.03), 0 4px 14px rgba(7, 26, 114, 0.04);

            /* Glassmorphism Tokens */
            --glass-bg: rgba(255, 255, 255, 0.88);
            --glass-border: rgba(226, 232, 240, 0.85);
            --glass-blur: blur(16px);
        }


        /* =========================================================
           GLOBAL APP & RESET (MATCHES REFERENCE OCEANIC GRADIENT)
           ========================================================= */

        .stApp {
            background: radial-gradient(circle at 50% 25%, #18426d 0%, #0e2746 45%, #071628 100%) fixed !important;
            color: #F8FAFC !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        #MainMenu, footer, div[data-testid="stAppDeployButton"], [data-testid="stToolbarActions"] {
            visibility: hidden !important;
            display: none !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0 !important;
            z-index: 99999 !important;
        }

        header[data-testid="stHeader"] > div:not(:has([data-testid="collapsedControl"])):not(:has([data-testid="stExpandSidebarButton"])) {
            visibility: hidden !important;
        }

        /* Streamlit main block container */
        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1260px !important;
        }

        /* Typography Defaults */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        p, span, label, div {
            color: inherit;
        }


        /* =========================================================
           CARD CONTAINERS (NATIVE BORDER WRAPPER OVERRIDE)
           ========================================================= */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
            border: 1px solid var(--border, #E2E8F0) !important;
            border-radius: 14px !important;
            padding: 18px 22px 22px 22px !important;
            box-shadow: var(--shadow-card) !important;
            transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: var(--shadow-md) !important;
            border-color: #cbd5e1 !important;
        }

        /* Inner container typography for white cards */
        div[data-testid="stVerticalBlockBorderWrapper"] h1,
        div[data-testid="stVerticalBlockBorderWrapper"] h2,
        div[data-testid="stVerticalBlockBorderWrapper"] h3,
        div[data-testid="stVerticalBlockBorderWrapper"] h4,
        div[data-testid="stVerticalBlockBorderWrapper"] h5,
        div[data-testid="stVerticalBlockBorderWrapper"] h6 {
            color: var(--primary-navy, #071A72) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] p,
        div[data-testid="stVerticalBlockBorderWrapper"] span,
        div[data-testid="stVerticalBlockBorderWrapper"] label {
            color: var(--text-primary, #0F172A);
        }


        /* =========================================================
           AUTHENTICATION & LOGIN SCREEN STYLING (MATCHES REFERENCE)
           ========================================================= */

        /* Scoped to login screen when sidebar is hidden */
        .stApp:has([data-testid="collapsedControl"][style*="display: none"]) .block-container {
            padding-top: 4.8rem !important;
            padding-bottom: 3.5rem !important;
        }

        .stApp:has([data-testid="collapsedControl"][style*="display: none"]) div[data-testid="stVerticalBlockBorderWrapper"] {
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

        .stApp:has([data-testid="collapsedControl"][style*="display: none"]) div[data-testid="stVerticalBlockBorderWrapper"]:hover {
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
            left: -3px;
            top: 15%;
            width: 5px;
            height: 48px;
            background: #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 14px 4px #38bdf8, 0 0 32px 8px rgba(56, 189, 248, 0.9);
            pointer-events: none;
            z-index: 10;
        }

        .login-flare-right {
            position: absolute;
            right: -3px;
            top: 15%;
            width: 5px;
            height: 48px;
            background: #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 14px 4px #38bdf8, 0 0 32px 8px rgba(56, 189, 248, 0.9);
            pointer-events: none;
            z-index: 10;
        }

        .demo-badge {
            display: table;
            margin: 0 auto 30px auto;
            background: rgba(14, 165, 233, 0.15) !important;
            color: #38bdf8 !important;
            border-radius: 20px !important;
            padding: 5px 14px !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            letter-spacing: 0.6px !important;
            border: 1px solid rgba(56, 189, 248, 0.5) !important;
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.25) !important;
        }

        .login-logo-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0px auto 5px auto;
            text-align: center;
            width: 100%;
        }

        .login-logo-img {
            width:165px;
            height: 165px;
            object-fit: cover;
            border-radius: 50% !important;
            border: 2.5px solid rgba(56, 189, 248, 0.85) !important;
            box-shadow: 0 0 24px rgba(56, 189, 248, 0.5), inset 0 0 12px rgba(56, 189, 248, 0.2) !important;
            display: block;
            margin: 0 auto;
            background: rgba(10, 26, 48, 0.8) !important;
            padding: 2px;
        }

        .logo-box {
            width: 84px;
            height: 84px;
            margin: 0 auto;
            background: rgba(10, 26, 48, 0.8) !important;
            border-radius: 50% !important;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #38bdf8 !important;
            font-size: 38px;
            border: 2.5px solid rgba(56, 189, 248, 0.85) !important;
            box-shadow: 0 0 24px rgba(56, 189, 248, 0.5) !important;
        }

        .login-title {
            text-align: center;
            color: #ffffff !important;
            font-size: 23px !important;
            font-weight: 800 !important;
            margin-top: 1px;
            margin-bottom: 5px;
            letter-spacing: -0.4px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }

        .login-subtitle {
            text-align: center;
            color: #94a3b8 !important;
            font-size: 12.5px !important
            font-weight: 500 !important;
            margin-bottom: 18px !important;
        }

        .portal-row {
            background: rgba(10, 30, 56, 0.7) !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px !important;
        }

        .portal-title {
            color: #e2e8f0 !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }

        .portal-code {
            background: rgba(14, 165, 233, 0.2) !important;
            color: #38bdf8 !important;
            border: 1px solid rgba(56, 189, 248, 0.45) !important;
            padding: 3px 8px !important;
            border-radius: 5px !important;
            font-size: 10px !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px !important;
        }

        .field-label {
            color: #cbd5e1 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            margin-top: 10px !important;
            margin-bottom: 5px !important;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .field-code {
            color: #38bdf8 !important;
            font-size: 10px !important;
            font-weight: 700 !important;
        }


        /* =========================================================
           FORM INPUTS & SELECTBOXES (CLEAN WHITE + ACCENT FOCUS)
           ========================================================= */

        div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: #ffffff !important;
            border: 1.5px solid var(--border, #E2E8F0) !important;
            border-radius: 8px !important;
            height: 42px !important;
            min-height: 42px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px rgba(7, 26, 114, 0.02) !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
            border-color: var(--bright-blue, #0878D1) !important;
            box-shadow: 0 0 0 3px rgba(8, 120, 209, 0.15) !important;
        }

        div[data-testid="stTextInput"] input {
            background-color: #ffffff !important;
            border: none !important;
            color: var(--text-primary, #0F172A) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 8px 12px !important;
            height: 100% !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: var(--text-muted, #94A3B8) !important;
        }

        /* Target Verification Checkpoint & Disabled Text Inputs (Dark Box with Crisp Text) */
        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:has(input:disabled),
        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:has(input[disabled]),
        .st-key-target_checkpoint_input div[data-baseweb="base-input"] {
            background-color: #0c2340 !important;
            border: 1.5px solid rgba(56, 189, 248, 0.4) !important;
            border-radius: 8px !important;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.12) !important;
        }

        div[data-testid="stTextInput"] input:disabled,
        div[data-testid="stTextInput"] input[disabled],
        .st-key-target_checkpoint_input input {
            background-color: #0c2340 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            cursor: default !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border: none !important;
            height: 100% !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
            color: var(--text-primary, #0F172A) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }

        div[data-testid="stSelectbox"] svg {
            fill: var(--primary-navy, #071A72) !important;
            stroke: var(--primary-navy, #071A72) !important;
        }

        /* Dropdown Popover List */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            background-color: #ffffff !important;
            color: var(--text-primary, #0F172A) !important;
        }

        div[data-baseweb="popover"] {
            border: 1px solid var(--border, #E2E8F0) !important;
            border-radius: 10px !important;
            box-shadow: var(--shadow-lg) !important;
            overflow: hidden !important;
        }

        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [aria-selected="true"] {
            background-color: var(--light-cyan, #E8FAFC) !important;
            color: var(--primary-navy, #071A72) !important;
            font-weight: 600 !important;
        }


        /* =========================================================
           BUTTONS (SIGNATURE BLUE-TO-CYAN GRADIENTS & HOVERS)
           ========================================================= */

        .stButton > button {
            height: 42px !important;
            min-height: 42px !important;
            border-radius: 9px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        /* Primary Button: Signature Blue/Cyan Gradient */
        .stButton > button[kind="primary"],
        button[kind="primary"] {
            background: linear-gradient(120deg, #071A72 0%, #0B3FBF 50%, #0878D1 100%) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(11, 63, 191, 0.28) !important;
        }

        .stButton > button[kind="primary"]:hover,
        button[kind="primary"]:hover {
            background: linear-gradient(120deg, #0B3FBF 0%, #0878D1 50%, #22BFC9 100%) !important;
            box-shadow: 0 6px 20px rgba(34, 191, 201, 0.38) !important;
            transform: translateY(-1.5px) !important;
            color: #ffffff !important;
        }

        /* Secondary Button: Crisp White Card Button */
        .stButton > button[kind="secondary"],
        button[kind="secondary"] {
            background: #ffffff !important;
            color: var(--primary-navy, #071A72) !important;
            border: 1px solid var(--border, #E2E8F0) !important;
            box-shadow: 0 1px 3px rgba(7, 26, 114, 0.04) !important;
        }

        .stButton > button[kind="secondary"]:hover,
        button[kind="secondary"]:hover {
            background: var(--light-cyan, #E8FAFC) !important;
            color: var(--primary-blue, #0B3FBF) !important;
            border-color: var(--accent-cyan, #22BFC9) !important;
            box-shadow: 0 4px 12px rgba(34, 191, 201, 0.15) !important;
            transform: translateY(-1px) !important;
        }

        .status-row {
            text-align: center;
            color: var(--text-secondary, #64748B);
            font-size: 11px;
            margin-top: 16px;
            font-weight: 600;
            letter-spacing: 0.2px;
        }

        .status-dot {
            color: var(--accent-cyan, #22BFC9);
            font-size: 11px;
        }


        /* =========================================================
           SIDEBAR NAVIGATION (DARK OCEANIC THEME MATCHING REFERENCE)
           ========================================================= */

        section[data-testid="stSidebar"] {
            background-color: #021639 !important;
            background: #021639 !important;
            border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
            color: #F8FAFC !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.45) !important;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        section[data-testid="stSidebar"].custom-sidebar-closed,
        section[data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: -19rem !important;
            transform: translateX(-100%) !important;
        }

        /* Streamlit Native Sidebar Collapse Button (<< matching reference) */
        div[data-testid="stSidebarCollapseButton"] {
            position: absolute !important;
            top: 22px !important;
            right: 16px !important;
            z-index: 1000 !important;
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            width: 32px !important;
            height: 32px !important;
        }

        div[data-testid="stSidebarCollapseButton"] button {
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
            max-width: 32px !important;
            border-radius: 8px !important;
            background: rgba(14, 39, 75, 0.85) !important;
            border: 1px solid rgba(56, 189, 248, 0.25) !important;
            color: #7dd3fc !important;
            cursor: pointer !important;
            padding: 0 !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stSidebarCollapseButton"] button:hover {
            background: rgba(56, 189, 248, 0.22) !important;
            border-color: rgba(56, 189, 248, 0.6) !important;
            color: #ffffff !important;
            transform: scale(1.05) !important;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
        }

        div[data-testid="stSidebarCollapseButton"] button span {
            color: #7dd3fc !important;
            font-size: 20px !important;
            transition: color 0.2s ease !important;
        }

        div[data-testid="stSidebarCollapseButton"] button:hover span {
            color: #ffffff !important;
        }

        /* Streamlit Collapsed Control & Expand Button (>> when sidebar is closed) */
        div[data-testid="collapsedControl"],
        button[data-testid="stExpandSidebarButton"] {
            visibility: visible !important;
            position: fixed !important;
            top: 14px !important;
            left: 14px !important;
            z-index: 999999 !important;
        }

        div[data-testid="collapsedControl"] button,
        button[data-testid="stExpandSidebarButton"] {
            width: 34px !important;
            height: 34px !important;
            border-radius: 8px !important;
            background: #021639 !important;
            border: 1px solid rgba(56, 189, 248, 0.35) !important;
            color: #38bdf8 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="collapsedControl"] button:hover,
        button[data-testid="stExpandSidebarButton"]:hover {
            background: #0b3fbf !important;
            border-color: #38bdf8 !important;
            color: #ffffff !important;
            transform: scale(1.06) !important;
        }

        div[data-testid="collapsedControl"] svg,
        button[data-testid="stExpandSidebarButton"] svg,
        button[data-testid="stExpandSidebarButton"] span {
            stroke: #38bdf8 !important;
            fill: #38bdf8 !important;
            color: #38bdf8 !important;
            font-size: 20px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.2rem !important;
        }

        section[data-testid="stSidebar"] .stMarkdown {
            color: #F8FAFC !important;
        }

        /* Sidebar Brand Header */
        .sidebar-brand-wrapper {
            display: flex;
            align-items: center;
            padding: 10px 42px 14px 4px;
            border-bottom: 1px solid rgba(56, 189, 248, 0.14);
            margin-bottom: 6px;
        }

        .sidebar-brand-logo {
            width: 88px;
            height: 88px;
            border-radius: 8px;
            object-fit: cover;
            border: 1.5px solid rgba(56, 189, 248, 0.45);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
            background: #061e47;
            display: block;
        }

        .sidebar-brand-title {
            color: #ffffff;
            font-size: 26px;
            font-weight: 800;
            line-height: 1.33;
            letter-spacing: +1.19px;
        }

        .sidebar-brand-sub {
            color: #38bdf8;
            font-size: 10.5px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1.0px;
        }

        /* Pipeline Readiness Checklist (High contrast dark text on white card) */
        .pipeline-readiness-checklist,
        .pipeline-readiness-checklist * {
            color: #0f172a !important;
        }

        .pipeline-readiness-checklist strong {
            color: #0f172a !important;
            font-weight: 700 !important;
        }

        .pipeline-readiness-checklist span {
            color: #1e293b !important;
        }

        /* Checkpoint Station Card (matching reference store card) */
        .sidebar-station-card {
            background: rgba(14, 39, 75, 0.6);
            border: 3px solid rgba(56, 189, 248, 0.22);
            border-radius: 45px;
            padding: 8.9px 29px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 15px 0 9px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease;
        }

        .sidebar-station-card:hover {
            border-color: rgba(56, 189, 248, 0.4);
            background: rgba(14, 39, 75, 0.8);
        }

        .sidebar-station-left {
            display: flex;
            align-items: center;
            gap: 13px;
        }

        .sidebar-station-icon {
            width: 28px;
            height: 27px;
            border-radius: 3px;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 26px;
            font-weight: 700;
            flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.35);
        }

        .sidebar-station-text {
            color: #f1f5f9;
            font-size:15px;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Category section labels (matching reference 'Stores', 'Genaral', 'Tools') */
        .sidebar-section-label {
            color: #7b8eac;
            font-size: 15.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 14px 0 11px 35px;
        }

        /* Sidebar Navigation Buttons */
        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 8px 12px !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            border: 1px solid transparent !important;
            margin: 1px 0 !important;
            height: 38px !important;
            min-height: 38px !important;
            transition: all 0.15s ease !important;
        }

        /* Inactive Sidebar Buttons */
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background-color: transparent !important;
            color: #cbd5e1 !important;
            box-shadow: none !important;
            border: 1px solid transparent !important;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background-color: rgba(56, 189, 248, 0.08) !important;
            color: #ffffff !important;
            border-color: rgba(56, 189, 248, 0.25) !important;
            transform: translateX(2px) !important;
        }

        /* Active Sidebar Button */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(120deg, #071A72 0%, #0B3FBF 60%, #0878D1 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            box-shadow: 0 4px 14px rgba(11, 63, 191, 0.35) !important;
            font-weight: 700 !important;
        }

        /* Toggle styling in sidebar */
        section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
            color: #cbd5e1 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        /* Sidebar Disclaimer Box */
        .sidebar-disclaimer-box {
            background: rgba(12, 35, 64, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.16);
            border-radius: 9px;
            padding: 9px 11px;
            margin-top: 10px;
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.4;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }

        .sidebar-disclaimer-dot {
            width: 6px;
            height: 6px;
            background: #22c55e;
            border-radius: 50%;
            margin-top: 4px;
            flex-shrink: 0;
            box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
        }


        /* =========================================================
           TOP GLOBAL HEADER BAR (LIGHT THEME WITH CYAN ACCENTS)
           ========================================================= */

        .top-global-header {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 10px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom:16px;
            box-shadow: var(--shadow-card);
        }

        .top-header-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .top-header-main-title {
            color: var(--primary-navy, #071A72);
            font-size: 18px;
            font-weight: 800;
            letter-spacing: -0.3px;
        }

        .top-header-badge {
            background: var(--light-cyan, #E8FAFC);
            color: var(--primary-blue, #0B3FBF);
            border: 1px solid var(--accent-cyan, #22BFC9);
            font-size: 10.5px;
            font-weight: 800;
            padding: 3px 9px;
            border-radius: 6px;
            letter-spacing: 0.3px;
        }

        .top-header-subtitle {
            color: var(--text-secondary, #64748B);
            font-size: 12px;
            margin-top: 2px;
            font-weight: 500;
        }

        .top-header-right-group {
            display: flex;
            align-items: center;
            gap: 22px;
        }

        .system-online-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: 700;
            color: var(--primary-navy, #071A72);
            box-shadow: 0 1px 3px rgba(7, 26, 114, 0.03);
        }

        .green-pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #16a34a;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.2);
        }

        .header-icon-btn {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 1px solid var(--border, #E2E8F0);
            background: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            color: var(--text-secondary, #64748B);
            box-shadow: 0 1px 2px rgba(7, 26, 114, 0.02);
            transition: all 0.15s ease;
            cursor: pointer;
        }

        .header-icon-btn:hover {
            border-color: var(--accent-cyan, #22BFC9);
            background: var(--light-cyan, #E8FAFC);
            color: var(--primary-navy, #071A72);
        }

        .officer-header-card {
            display: flex;
            align-items: center;
            gap: 15px;
            padding-left: 6px;
        }

        .officer-header-text {
            text-align: right;
        }

        .officer-header-name {
            color: var(--primary-navy, #071A72);
            font-size: 12.5px;
            font-weight: 800;
            line-height: 1.2;
        }

        .officer-header-id {
            color: var(--text-secondary, #64748B);
            font-size: 10.5px;
            font-weight: 500;
            line-height: 1.2;
        }

        .officer-header-avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            border: 1.5px solid var(--bright-blue, #0878D1);
            object-fit: cover;
            box-shadow: 0 2px 6px rgba(8, 120, 209, 0.2);
        }


        /* =========================================================
           ACTIVE CHECKPOINT BANNER
           ========================================================= */

        .checkpoint-banner-card {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            box-shadow: var(--shadow-card);
        }

        .checkpoint-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .checkpoint-icon-box {
            width: 40px;
            height: 40px;
            border-radius: 7px;
            background: var(--light-cyan, #E8FAFC);
            border: 1px solid var(--accent-cyan, #22BFC9);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: var(--primary-blue, #0B3FBF);
        }

        .checkpoint-label {
            color: var(--text-secondary, #64748B);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .checkpoint-title {
            color: var(--primary-navy, #071A72);
            font-size: 19px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .checkpoint-right-pills {
            display: flex;
            align-items: center;
            gap: 25px;
        }

        .model-active-pill {
            background: var(--light-cyan, #E8FAFC);
            border: 1px solid var(--accent-cyan, #22BFC9);
            color: var(--primary-navy, #071A72);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .offline-cache-pill {
            background: var(--light-cyan, #E8FAFC);
            border: 1px solid var(--accent-cyan, #E2E8F0);
            color: #334155;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }


        /* =========================================================
           HERO CARD & ACTION BUTTONS
           ========================================================= */

        .hero-card {
            background: linear-gradient(135deg, rgba(232, 250, 252, 0.65) 0%, #FFFFFF 65%);
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 20px 22px;
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
            height: 100%;
        }

        .hero-tag {
            display: inline-block;
            background: var(--light-cyan, #E8FAFC);
            color: var(--primary-navy, #071A72);
            border: 1px solid var(--accent-cyan, #22BFC9);
            font-size: 10px;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 12px;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .hero-title {
            color: var(--primary-navy, #071A72);
            font-size: 24px;
            font-weight: 800;
            margin: 4px 0 6px 0;
            letter-spacing: -0.3px;
        }

        .hero-subtitle {
            color: var(--text-secondary, #64748B);
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        .hero-buttons-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            position: relative;
            z-index: 2;
        }

        .hero-btn-secondary {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            color: var(--primary-blue, #0B3FBF);
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 12.5px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.15s ease;
            box-shadow: 0 1px 3px rgba(7, 26, 114, 0.03);
        }

        .hero-btn-secondary:hover {
            background: var(--light-cyan, #E8FAFC);
            border-color: var(--accent-cyan, #22BFC9);
            color: var(--primary-navy, #071A72);
        }

        .hero-btn-badge {
            background: var(--light-cyan, #E8FAFC);
            color: var(--primary-blue, #0B3FBF);
            border: 1px solid #cceef3;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 6px;
        }


        /* =========================================================
           T3-L04 SCANNER CARD
           ========================================================= */

        .scanner-card {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: var(--shadow-card);
            height: 100%;
        }

        .scanner-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .scanner-title-group {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .scanner-title-text {
            color: var(--primary-navy, #071A72);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .scanner-live-pill {
            background: var(--primary-navy, #071A72);
            color: var(--accent-cyan, #22BFC9);
            font-size: 9px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            letter-spacing: 0.4px;
        }

        .scanner-fps-text {
            color: var(--text-secondary, #64748B);
            font-size: 11px;
            font-weight: 600;
        }

        .scanner-img-wrapper {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            width: 100%;
            height: 136px;
            box-shadow: 0 2px 6px rgba(7, 26, 114, 0.08);
            border: 1px solid var(--border, #E2E8F0);
        }

        .scanner-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .scanner-footer-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            font-size: 11px;
        }

        .scanner-calib-label {
            color: var(--text-secondary, #64748B);
            font-weight: 500;
        }

        .scanner-calib-time {
            color: var(--primary-navy, #071A72);
            font-weight: 700;
        }


        /* =========================================================
           4 KPI METRIC CARDS
           ========================================================= */

        .kpi-card {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: #cbd5e1;
        }

        .kpi-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .kpi-title {
            color: var(--text-secondary, #64748B);
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .kpi-icon-badge {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
        }

        .kpi-icon-blue {
            background: var(--light-cyan, #E8FAFC);
            color: var(--primary-blue, #0B3FBF);
            border: 1px solid var(--accent-cyan, #22BFC9);
        }

        .kpi-icon-red {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }

        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--primary-navy, #071A72);
            line-height: 1.1;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
        }

        .kpi-subtext {
            font-size: 11.5px;
            color: var(--text-secondary, #64748B);
            font-weight: 500;
            margin-bottom: 12px;
        }

        .kpi-accent-bar {
            height: 3.5px;
            border-radius: 2px;
            width: 100%;
        }


        /* =========================================================
           ANALYTICS CARDS (BOTTOM ROW)
           ========================================================= */

        .analytics-card {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 12px;
            padding: 20px 22px;
            box-shadow: var(--shadow-card);
            height: 100%;
        }

        .analytics-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .analytics-title {
            color: var(--primary-navy, #071A72);
            font-size: 15px;
            font-weight: 800;
            letter-spacing: -0.2px;
        }

        .analytics-tag {
            color: var(--text-secondary, #64748B);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .analytics-subtitle {
            color: var(--text-secondary, #64748B);
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 18px;
            line-height: 1.4;
        }

        /* Donut Chart Inner Layout */
        .donut-section-grid {
            display: grid;
            grid-template-columns: 1fr 1.3fr;
            gap: 16px;
            align-items: center;
        }

        .donut-col-label {
            color: var(--text-muted, #94A3B8);
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .donut-breakdown-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 7px 0;
            border-bottom: 1px solid #f8fafc;
        }

        .donut-breakdown-left {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .donut-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .donut-breakdown-name {
            color: var(--text-primary, #0F172A);
            font-size: 12px;
            font-weight: 700;
            line-height: 1.2;
        }

        .donut-breakdown-sub {
            color: var(--text-secondary, #64748B);
            font-size: 10px;
            font-weight: 500;
            line-height: 1.2;
        }

        .donut-breakdown-right {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .donut-count {
            color: var(--primary-navy, #071A72);
            font-size: 12px;
            font-weight: 800;
        }

        .donut-badge {
            font-size: 10.5px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
        }

        /* Diagnostics Progress Bars */
        .diag-item {
            margin-bottom: 14px;
        }

        .diag-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .diag-label-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .diag-icon-box {
            width: 22px;
            height: 22px;
            background: var(--light-cyan, #E8FAFC);
            border: 1px solid var(--accent-cyan, #22BFC9);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            color: var(--primary-blue, #0B3FBF);
            font-weight: 700;
        }

        .diag-title-text {
            color: var(--primary-navy, #071A72);
            font-size: 12px;
            font-weight: 700;
        }

        .diag-metric-text {
            font-size: 11.5px;
            font-weight: 800;
            color: var(--primary-navy, #071A72);
        }

        .diag-bar-track {
            width: 100%;
            height: 6px;
            background: #f1f5f9;
            border-radius: 3px;
            overflow: hidden;
        }

        .diag-bar-fill {
            height: 100%;
            border-radius: 3px;
        }

        /* Metric Card Container (Compatibility) */
        .metric-card-container {
            background: #ffffff;
            border: 1px solid var(--border, #E2E8F0);
            border-radius: 10px;
            padding: 16px;
            box-shadow: var(--shadow-card);
            transition: transform 0.15s ease;
        }

        .metric-card-container:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .metric-card-title {
            font-size: 12px;
            color: var(--text-secondary, #64748B);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .metric-card-value {
            font-size: 26px;
            color: var(--primary-navy, #071A72);
            font-weight: 800;
            margin-bottom: 2px;
        }

        .metric-card-sub {
            font-size: 11px;
            color: var(--text-muted, #94A3B8);
            font-weight: 500;
        }

        /* Responsible AI Advisory Banner */
        .responsible-ai-banner {
            background: var(--light-cyan, #E8FAFC);
            border-left: 4px solid var(--bright-blue, #0878D1);
            border-radius: 6px;
            padding: 10px 14px;
            margin: 14px 0;
            font-size: 12px;
            color: var(--primary-navy, #071A72);
            line-height: 1.4;
        }

        .responsible-ai-title {
            font-weight: 700;
            margin-bottom: 2px;
            color: var(--primary-blue, #0B3FBF);
        }


        /* =========================================================
           GLASSMORPHISM UTILITIES
           ========================================================= */

        .glass-card {
            background: var(--glass-bg) !important;
            backdrop-filter: var(--glass-blur) !important;
            -webkit-backdrop-filter: var(--glass-blur) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 16px !important;
            box-shadow: var(--shadow-lg) !important;
        }


        /* =========================================================
           STREAMLIT NATIVE ELEMENT OVERRIDES (TABS, METRICS, TABLES)
           ========================================================= */

        /* Tabs */
        div[data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 2px solid var(--border, #E2E8F0) !important;
            gap: 10px !important;
        }

        div[data-baseweb="tab"] {
            color: var(--text-secondary, #64748B) !important;
            font-weight: 600 !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 8px 18px !important;
            transition: all 0.15s ease !important;
        }

        div[data-baseweb="tab"]:hover {
            color: var(--primary-blue, #0B3FBF) !important;
            background-color: var(--light-cyan, #E8FAFC) !important;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary-navy, #071A72) !important;
            font-weight: 800 !important;
            border-bottom: 3px solid var(--accent-cyan, #22BFC9) !important;
        }

        /* Streamlit Metrics (Light text for dark theme visibility) */
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

        /* Dataframe & Tables */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border, #E2E8F0) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            box-shadow: var(--shadow-card) !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
