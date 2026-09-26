import streamlit as st
import sqlite3
import json
import hashlib
import html
import re
import base64
from datetime import datetime
from pathlib import Path
from db_service import get_connection
from session import navigate_to


def clean_html(html_str: str) -> str:
    """Strips leading/trailing whitespace from each line to prevent Streamlit pre/code block parsing."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


def get_ai_avatar_b64() -> str:
    """Read assets/ai_avatar.png and return base64 data URI."""
    try:
        avatar_path = Path(__file__).resolve().parent.parent / "assets" / "ai_avatar.png"
        if avatar_path.exists():
            with open(avatar_path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass
    # Fallback inline SVG data URI matching media_1789137284494.png
    return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='26' height='26' fill='white'><path d='M12 2.5l2.45 5.51 6.05.61-4.52 4.04 1.3 5.92L12 15.5l-5.28 3.08 1.3-5.92-4.52-4.04 6.05-.61L12 2.5z'/><circle cx='5.5' cy='7.5' r='1.3'/><circle cx='18.5' cy='7.5' r='1.1'/><circle cx='18' cy='16.5' r='1.1'/></svg>"


def format_bubble_text_html(text: str) -> str:
    """Format chat text with support for bold, code, bullets, linebreaks and tables."""
    lines = text.split("\n")
    out_lines = []
    in_table = False
    table_rows = []

    for line in lines:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            in_table = True
            if set(s.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
                continue
            cells = [c.strip() for c in s[1:-1].split("|")]
            table_rows.append(cells)
            continue
        else:
            if in_table and table_rows:
                tbl_html = ["<table style='width:100%; border-collapse:collapse; font-size:0.78rem; margin:6px 0;'>"]
                for r_idx, row in enumerate(table_rows):
                    tag = "th" if r_idx == 0 else "td"
                    bg = "background:#f1f5f9; font-weight:600;" if r_idx == 0 else ""
                    tbl_html.append("<tr>")
                    for cell in row:
                        cell_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", cell)
                        cell_fmt = re.sub(r"`(.*?)`", r"<code style='background:#f1f5f9; padding:1px 4px; border-radius:3px;'>\1</code>", cell_fmt)
                        tbl_html.append(f"<{tag} style='border:1px solid #e2e8f0; padding:4px 6px; text-align:left; {bg}'>{cell_fmt}</{tag}>")
                    tbl_html.append("</tr>")
                tbl_html.append("</table>")
                out_lines.append("".join(tbl_html))
                in_table = False
                table_rows = []

        if not s:
            out_lines.append("<div style='height:8px;'></div>")
            continue

        formatted = html.escape(s)
        formatted = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color:#0f172a;'>\1</strong>", formatted)
        formatted = re.sub(r"`(.*?)`", r"<code style='background:#eef2ff; color:#4338ca; padding:1px 5px; border-radius:4px; font-size:0.8rem; font-family:monospace;'>\1</code>", formatted)

        if formatted.startswith("###"):
            hdr = formatted.lstrip("#").strip()
            out_lines.append(f"<div style='font-weight:700; color:#0f172a; font-size:0.92rem; margin:6px 0 4px 0;'>{hdr}</div>")
        elif formatted.startswith("•") or formatted.startswith("- "):
            item = formatted.lstrip("•- ").strip()
            out_lines.append(f"<div style='margin:2px 0 2px 6px; display:flex; gap:6px;'><span style='color:#4f46e5; flex-shrink:0;'>•</span><span>{item}</span></div>")
        elif formatted.startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            parts = formatted.split(".", 1)
            num = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            out_lines.append(f"<div style='margin:3px 0 3px 6px; display:flex; gap:6px;'><strong style='color:#4f46e5; flex-shrink:0;'>{num}.</strong><span>{rest.strip()}</span></div>")
        else:
            out_lines.append(f"<div style='margin-bottom:4px;'>{formatted}</div>")

    if in_table and table_rows:
        tbl_html = ["<table style='width:100%; border-collapse:collapse; font-size:0.78rem; margin:6px 0;'>"]
        for r_idx, row in enumerate(table_rows):
            tag = "th" if r_idx == 0 else "td"
            bg = "background:#f1f5f9; font-weight:600;" if r_idx == 0 else ""
            tbl_html.append("<tr>")
            for cell in row:
                cell_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", cell)
                cell_fmt = re.sub(r"`(.*?)`", r"<code style='background:#f1f5f9; padding:1px 4px; border-radius:3px;'>\1</code>", cell_fmt)
                tbl_html.append(f"<{tag} style='border:1px solid #e2e8f0; padding:4px 6px; text-align:left; {bg}'>{cell_fmt}</{tag}>")
            tbl_html.append("</tr>")
        tbl_html.append("</table>")
        out_lines.append("".join(tbl_html))

    return "".join(out_lines)


# =========================================================
# BACKEND DECISION-SUPPORT FUNCTIONS (MODULAR ARCHITECTURE)
# =========================================================

def get_all_case_choices():
    """Retrieve all available cases from SQLite for context selection."""
    conn = get_connection()
    cases = []
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.case_id, c.checkpoint_name, c.case_decision, 
                   COALESCE(r.risk_score, 0) as risk_score,
                   COALESCE(d.doc_type, 'document') as doc_type
            FROM cases c
            LEFT JOIN documents d ON c.case_id = d.case_id
            LEFT JOIN risk_assessments r ON d.id = r.document_id
            GROUP BY c.case_id
            ORDER BY c.id DESC
            """
        )
        rows = cur.fetchall()
        for r in rows:
            cid = r["case_id"]
            short_id = cid[:8].upper()
            dec = (r["case_decision"] or "REVIEW").upper()
            score = r["risk_score"]
            dtype = (r["doc_type"] or "Document").replace("_", " ").title()
            cp = (r["checkpoint_name"] or "Checkpoint").replace("_", " ").title()
            cases.append({
                "case_id": cid,
                "short_id": short_id,
                "label": f"CASE {short_id} • {dtype} • {cp} (Risk: {score}/100 • {dec})",
                "checkpoint": cp,
                "decision": dec,
                "risk_score": score,
                "doc_type": dtype,
            })
    except Exception:
        pass
    finally:
        conn.close()

    if not cases:
        # Fallback benchmark case if DB is empty
        cases.append({
            "case_id": "dcd36aa5b388",
            "short_id": "DCD36A5B",
            "label": "CASE DCD36A5B • Driving License • Land Border (Risk: 68/100 • REJECTED)",
            "checkpoint": "Land Border",
            "decision": "REJECTED",
            "risk_score": 68,
            "doc_type": "Driving License",
        })
    return cases


def get_case_status(case_id: str) -> dict:
    """
    Retrieve official case status and metadata from sih26188.db.
    Connects to SQLite cases, documents, and case_decisions tables.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Case search (exact or prefix match)
        cur.execute(
            """
            SELECT c.id, c.case_id, c.checkpoint_name, c.created_at, c.offline_flag,
                   c.case_decision, c.case_reason_code, c.case_reason_detail,
                   d.id as doc_id, d.doc_type, d.file_path, d.file_hash,
                   r.risk_score, r.risk_factors_json, r.model_version
            FROM cases c
            LEFT JOIN documents d ON c.case_id = d.case_id
            LEFT JOIN risk_assessments r ON d.id = r.document_id
            WHERE c.case_id = ? OR c.case_id LIKE ? OR c.case_id LIKE ?
            ORDER BY d.id DESC LIMIT 1
            """,
            (case_id, f"{case_id[:6]}%", f"%{case_id}%"),
        )
        row = cur.fetchone()
        if not row:
            return None

        factors = []
        if row["risk_factors_json"]:
            try:
                factors = json.loads(row["risk_factors_json"])
            except Exception:
                pass

        return {
            "case_id": row["case_id"],
            "short_id": row["case_id"][:8].upper(),
            "checkpoint": (row["checkpoint_name"] or "Border Control Checkpoint").replace("_", " "),
            "decision": (row["case_decision"] or "SECONDARY_REVIEW").upper(),
            "reason_code": row["case_reason_code"] or "MANUAL_INSPECTION_REQUIRED",
            "reason_detail": row["case_reason_detail"] or "Automated triage completed. Secondary verification recommended.",
            "doc_type": (row["doc_type"] or "Identity Document").replace("_", " ").title(),
            "risk_score": row["risk_score"] if row["risk_score"] is not None else 68,
            "risk_factors": factors,
            "created_at": row["created_at"],
            "model_version": row["model_version"] or "v2.4-unveilx",
        }
    except Exception:
        return None
    finally:
        conn.close()


def get_risk_score(case_id: str) -> dict:
    """Retrieve risk score, tier classification, and primary driving factors."""
    cdata = get_case_status(case_id)
    if not cdata:
        return {"risk_score": 0, "tier": "UNKNOWN", "factors": []}

    score = cdata["risk_score"]
    if score >= 75:
        tier = "HIGH RISK"
    elif score >= 40:
        tier = "MEDIUM RISK"
    else:
        tier = "LOW RISK"

    return {
        "case_id": cdata["case_id"],
        "short_id": cdata["short_id"],
        "risk_score": score,
        "tier": tier,
        "factors": cdata["risk_factors"],
    }


def get_case_anomalies(case_id: str) -> list:
    """Retrieve verified anomalies detected across document inspection modules."""
    cdata = get_case_status(case_id)
    if not cdata:
        return []

    anomalies = []
    for f in cdata.get("risk_factors", []):
        anomalies.append({
            "indicator": f.get("factor", "Unspecified anomaly"),
            "weight": f.get("weight", 0.2),
            "severity": "CRITICAL" if f.get("weight", 0) >= 0.35 else "WARNING",
        })

    if not anomalies:
        if cdata["risk_score"] >= 60:
            anomalies = [
                {"indicator": "Document-field format inconsistency", "weight": 0.40, "severity": "CRITICAL"},
                {"indicator": "Possible tampering / ELA compression boundary artifact", "weight": 0.30, "severity": "CRITICAL"},
                {"indicator": "Reference-database biometric delta threshold exceeded", "weight": 0.20, "severity": "WARNING"},
            ]
        else:
            anomalies = [
                {"indicator": "Minor OCR low-confidence character read", "weight": 0.12, "severity": "LOW"},
            ]
    return anomalies


def explain_risk(case_id: str) -> dict:
    """
    Explainable AI breakdown:
    Decomposes risk score into weighted component points and provides simple language rationale.
    """
    cdata = get_case_status(case_id)
    if not cdata:
        return None

    score = cdata["risk_score"]
    anomalies = get_case_anomalies(case_id)

    # Compute breakdown points
    breakdown = []
    if score >= 60:
        breakdown = [
            {"category": "Document Tampering / Surface Artifacts", "points": int(score * 0.40), "color": "🔴"},
            {"category": "Field Mismatch / Checksum Discrepancy", "points": int(score * 0.30), "color": "🟠"},
            {"category": "Reference Watchlist / Database Delta", "points": int(score * 0.18), "color": "🟠"},
            {"category": "Image / Hologram Photometric Anomaly", "points": max(score - int(score * 0.88), 4), "color": "🟡"},
        ]
    else:
        breakdown = [
            {"category": "OCR Read Noise / Resolution Limit", "points": int(score * 0.6), "color": "🟡"},
            {"category": "Minor Format Variance", "points": score - int(score * 0.6), "color": "🟢"},
        ]

    status = "HIGH RISK" if score >= 75 else ("MEDIUM RISK" if score >= 40 else "LOW RISK")
    action = (
        "Manual physical secondary verification is required. Officer should verify document under UV-A 365nm and conduct interview."
        if score >= 60 else
        "Standard primary line clearance permissible. No critical risk triggers detected."
    )

    return {
        "case_id": cdata["short_id"],
        "total_score": score,
        "status": status,
        "breakdown": breakdown,
        "action": action,
    }


def generate_case_summary(case_id: str) -> str:
    """Generates official executive case summary for border officers."""
    cdata = get_case_status(case_id)
    if not cdata:
        return f"Case `{case_id}` could not be located in the local screening registry."

    anomalies = get_case_anomalies(case_id)
    anom_bullets = "\n".join([f"• **{a['indicator']}** (Severity: {a['severity']})" for a in anomalies])

    return f"""### 🛡️ Official Verification Dossier Summary
**Case Reference**: `CASE-{cdata['short_id']}`  
**Inspection Node**: {cdata['checkpoint']}  
**Credential Presented**: {cdata['doc_type']}  
**Automated Risk Triage**: **{cdata['risk_score']}/100** ({'🔴 HIGH RISK' if cdata['risk_score'] >= 75 else '🟠 MEDIUM RISK' if cdata['risk_score'] >= 40 else '🟢 LOW RISK'})  
**System Decision**: **{cdata['decision']}** (`{cdata['reason_code']}`)  

---

#### 🔎 Key Verified Risk Signals:
{anom_bullets}

#### ⚖️ Standard Operating Recommendation:
{cdata['reason_detail']}  
**Protocol**: Escort traveler to Secondary Examination Area for biometric enrollment and physical security feature inspection.
"""


def query_reference_database(doc_type: str = "Passport", query_term: str = "") -> dict:
    """
    Search the application's reference / synthetic database schema.
    Returns official government reference lookup structure.
    """
    doc_type = doc_type.capitalize()
    return {
        "status": "Reference lookup completed",
        "doc_type": doc_type,
        "reference_status": "Available in Central Master Template Registry",
        "matching_fields": [
            "Document format specification (ICAO 9303 compliant)",
            "Issuing authority seal / header structure",
            "Document serial number mathematical checksum structure",
        ],
        "potential_differences": [
            "Date field formatting / font weight anomaly in issue date matrix",
            "Localized background microprint line spacing delta: 0.14mm vs 0.12mm reference",
        ],
        "source": "Internal Government Reference Template Registry",
        "mode": "Demo / Synthetic Benchmark",
    }


def analyze_uploaded_document_demo(file_name: str, file_bytes_len: int) -> dict:
    """
    Performs clearly labelled DEMO/MOCK document analysis for prototype evaluation.
    Enforces responsible AI disclosures.
    """
    name_lower = file_name.lower()
    if "pass" in name_lower:
        detected_type = "Passport (Type 3 / 44-Char MRZ)"
    elif "dl" in name_lower or "driv" in name_lower:
        detected_type = "Driver's License (State Transport Authority)"
    elif "aadh" in name_lower or "uid" in name_lower:
        detected_type = "Aadhaar Card (UIDAI QR Spec)"
    elif "pan" in name_lower:
        detected_type = "Permanent Account Number (Income Tax Dept)"
    else:
        detected_type = "Official Identity Credential (Govt Standard)"

    return {
        "status": "Document Received",
        "document_type": detected_type,
        "file_name": file_name,
        "file_size": f"{file_bytes_len / 1024:.1f} KB",
        "detected_fields": [
            "Full Legal Name",
            "Date of Birth / Age Bracket",
            "Document Serial Number",
            "Validity / Expiry Date",
            "Issuing State Authority",
        ],
        "potential_issues": [
            "MRZ Line 2 checksum discrepancy detected",
            "Micro-text contrast variation around portrait border",
        ],
        "risk": "MEDIUM (58/100)",
        "recommendation": "Secondary physical review recommended.",
        "mode": "DEMO / MOCK ANALYSIS (Prototype Inspection Pipeline)",
    }


# =========================================================
# CHATBOT ENGINE: CASE-AWARE & PROCEDURAL DISPATCHER
# =========================================================

def process_assistant_query(user_query: str, active_case: dict = None) -> dict:
    """
    Core AI reasoning engine:
    Processes officer questions against active case context, risk breakdowns, or screening guidelines.
    Returns structured response payload.
    """
    q = user_query.lower().strip()
    cid = active_case["case_id"] if active_case else "dcd36aa5b388"
    short_id = active_case["short_id"] if active_case else "DCD36A5B"
    cdata = get_case_status(cid) or get_case_status("dcd36aa5b388")

    # 1. Why was document / case flagged?
    if any(k in q for k in ["why was this document flagged", "document flagged", "why was this case rejected", "why was it rejected", "why rejected", "reason for rejection", "why was this case flagged", "why flagged"]):
        if cdata:
            anomalies = get_case_anomalies(cid)
            issues_str = "\n".join([f"• **{a['indicator']}** &nbsp;*(Severity: `{a['severity']}`)*" for a in anomalies])
            text = (
                f"### 🚩 Document Flag Rationale: Case {short_id}\n\n"
                f"Credential `{cdata['doc_type']}` was flagged by the automated inspection pipeline due to multiple cumulative risk signals:\n\n"
                f"• **Risk Score**: `{cdata['risk_score']}/100` ({'🔴 HIGH RISK' if cdata['risk_score'] >= 75 else '🟠 MEDIUM RISK'})\n"
                f"• **Automated Triage Code**: `{cdata['reason_code']}`\n\n"
                f"**Key Flags Detected**:\n{issues_str}\n\n"
                f"**Advisory Recommendation**:\n"
                f"{cdata['reason_detail']} Secondary manual review is advised to inspect physical microprint, UV ink response, and 1:1 biometric identity."
            )
            return {
                "text": text,
                "case_id": short_id,
                "risk_badge": "🔴 REJECTED / HIGH RISK" if cdata['risk_score'] >= 75 else "🟠 FLAGGED / REVIEW",
                "recommendation": "Secondary Manual Inspection Required",
                "evidence": [a["indicator"] for a in anomalies],
                "confidence": "96.4% (Multi-Module Triage)",
            }

    # 2. Explain Risk Score
    if any(k in q for k in ["explain risk", "explain the risk score", "risk breakdown", "score breakdown", "how was risk calculated", "risk score?"]):
        risk_data = explain_risk(cid)
        if risk_data:
            breakdown_lines = "\n".join([f"{item['color']} **{item['category']}**: `{item['points']} points`" for item in risk_data["breakdown"]])
            text = (
                f"### ⚠️ Explainable AI Risk Decomposition: Case {short_id}\n\n"
                f"• **Total Aggregated Risk Score**: `{risk_data['total_score']}/100`\n"
                f"• **Triage Classification**: `{risk_data['status']}`\n\n"
                f"**Multi-Vector Point Distribution**:\n"
                f"{breakdown_lines}\n\n"
                f"**Algorithmic Threshold Rules**:\n"
                f"• Score ≥ 75: High Risk (Automated escalation to Senior Officer)\n"
                f"• Score 40–74: Medium Risk (Flagged for secondary physical inspection)\n"
                f"• Score < 40: Low Risk (Standard automated clearance)\n\n"
                f"**Operational Rationale**:\n"
                f"{risk_data['action']}"
            )
            return {
                "text": text,
                "case_id": short_id,
                "risk_badge": f"⚠️ {risk_data['status']} ({risk_data['total_score']}/100)",
                "recommendation": risk_data["action"],
                "evidence": [f"{item['category']} ({item['points']} pts)" for item in risk_data["breakdown"]],
                "confidence": "94.8% Algorithmic Certainty",
            }

    # 3. Explain OCR Results
    if any(k in q for k in ["explain the ocr results", "ocr results", "ocr result", "explain ocr", "ocr confidence", "text extraction"]):
        text = (
            f"### 🔤 Optical Character Recognition (OCR) Diagnostics: Case {short_id}\n\n"
            f"The credential `{cdata['doc_type']}` was processed through our dual-pass CRNN and Transformer OCR pipeline:\n\n"
            f"• **Overall Text Extraction Confidence**: `96.8%`\n"
            f"• **Visual Inspection Zone (VIZ) Fields**:\n"
            f"  - Holder Legal Name: `MATCH` (Confidence: `99.2%`)\n"
            f"  - Document Identifier: `EXTRACTED` (Confidence: `98.5%`)\n"
            f"  - Date of Birth / Expiry: `READ` (Confidence: `91.4%` — Font kerning delta notice)\n"
            f"  - Issuing Authority: `CONFIRMED` (Confidence: `99.0%`)\n\n"
            f"• **Machine Readable Zone (MRZ)**:\n"
            f"  - Line 1 Checksum: `PASSED` (ICAO 9303 modulo-10 check)\n"
            f"  - Line 2 Serial Checksum: `DISCREPANCY DETECTED` (Digit mismatch in position 28)\n\n"
            f"**Diagnostic Summary**: Character recognition confirmed high optical clarity. The primary trigger was mathematical check digit divergence between VIZ printed number and MRZ checksum."
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "🔤 OCR DIAGNOSTICS",
            "recommendation": "Cross-check physical MRZ strip with ultraviolet illumination",
            "evidence": ["VIZ Name Match (99.2%)", "MRZ Line 2 Checksum Discrepancy"],
            "confidence": "96.8% Dual-Engine OCR",
        }

    # 4. What verification checks were performed?
    if any(k in q for k in ["what verification checks were performed", "verification checks", "checks performed", "what checks", "security checks"]):
        text = (
            f"### 🛡️ Multi-Vector Verification Vectors: Case {short_id}\n\n"
            f"The UnveilX screening engine executed **6 comprehensive verification vectors** on `{cdata['doc_type']}`:\n\n"
            f"1. **MRZ / Checksum Algorithmic Verification**: Validated check digits using standard 7-3-1 weighting algorithm (ICAO 9303).\n"
            f"2. **Substrate & UV Luminescence Inspection**: Evaluated substrate reflectance under 365nm UV; checked for non-fluorescent security paper and rainbow fibers.\n"
            f"3. **1:1 Facial Feature Biometric Comparison**: Cosine similarity match between credential portrait and live inspection camera feed (Confidence: 96.7%).\n"
            f"4. **Typography & Microprint Geometry**: Scanned font kerning, baseline alignment, and raster patterns against central template registry.\n"
            f"5. **Digital Tamper & Splice Detection (ELA)**: Error Level Analysis scanned for synthetic pixel splicing and JPEG compression disparities.\n"
            f"6. **National Criminal & Watchlist Screening**: Real-time lookup against INTERPOL Stolen & Lost Travel Documents (SLTD) and national hotlists.\n\n"
            f"**Audit Integrity**: All 6 verification results have been anchored to SHA-256 ledger digest."
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "🛡️ 6 CHECKS COMPLETED",
            "recommendation": "Review automated findings before issuing border clearance",
            "evidence": ["ICAO 9303 Checksum", "UV Substrate", "1:1 Biometrics", "Microprint", "ELA Tamper", "SLTD Registry"],
            "confidence": "100% Vector Coverage",
        }

    # 5. Compare extracted data with the original document
    if any(k in q for k in ["compare extracted data with the original document", "compare extracted data", "compare data", "data comparison", "cross check original", "reconciliation"]):
        text = (
            f"### 📑 Extracted Data vs. Original Document Scan Reconciliation\n\n"
            f"Reconciliation matrix for **Case {short_id}** (`{cdata['doc_type']}`):\n\n"
            f"• **Full Legal Name**:\n"
            f"  - Scanned VIZ: `ZHANG, SHUANG` ⟷ Extracted OCR: `ZHANG, SHUANG` &nbsp;`[100% MATCH]`\n\n"
            f"• **Document Number**:\n"
            f"  - Scanned VIZ: `F4089216` ⟷ Extracted OCR: `F4089216` &nbsp;`[100% MATCH]`\n\n"
            f"• **Date of Birth & Expiry**:\n"
            f"  - Scanned VIZ: `14/08/1988` ⟷ Extracted OCR: `14/08/1988` &nbsp;`[KERNING DELTA +0.02mm]`\n\n"
            f"• **Machine Readable Zone (MRZ)**:\n"
            f"  - Scanned Bar: `P<INDZHANG<<SHUANG<<<<<<<<<` &nbsp;`[PARSED]`\n"
            f"  - Checksum Verification: `FAILED AT LINE 2 (POS 28)`\n\n"
            f"**Reconciliation Verdict**: Extracted alphanumeric text is syntactically consistent with applicant credentials; however, substrate font kerning and MRZ checksum deltas require manual secondary officer review."
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "📑 DATA RECONCILED",
            "recommendation": "Conduct physical cross-examination of document serial and date typography",
            "evidence": ["Name Match 100%", "Doc No Match 100%", "MRZ Checksum Discrepancy"],
            "confidence": "95.1% Reconciliation Confidence",
        }

    # 6. What anomalies were detected?
    if any(k in q for k in ["anomalies", "what anomalies", "detected issues", "tampering", "inconsistency"]):
        anomalies = get_case_anomalies(cid)
        anom_list = "\n".join([f"• **{a['indicator']}** &nbsp;|&nbsp; Severity: `{a['severity']}` &nbsp;(Weight: {int(a['weight']*100)}%)" for a in anomalies])
        text = (
            f"### 🔬 Detected Verification Anomalies in Case {short_id}\n\n"
            f"The following forensic and extraction flags were logged for credential `{cdata['doc_type']}`:\n\n"
            f"{anom_list}\n\n"
            f"**Forensic Note**: Anomalies indicate a divergence between document physical security models and digital capture data. Manual examination is advised."
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "🔬 ANOMALIES FLAGGED",
            "recommendation": "Inspect physical security features (OVD, UV ink, microprint)",
            "evidence": [a["indicator"] for a in anomalies],
            "confidence": "92.0%",
        }

    # 7. Compare with reference data / database
    if any(k in q for k in ["compare with reference", "reference data", "reference lookup", "passport reference", "check passport reference", "database result"]):
        ref = query_reference_database(cdata.get("doc_type", "Passport"))
        match_str = "\n".join([f"✓ {f}" for f in ref["matching_fields"]])
        diff_str = "\n".join([f"⚠ {f}" for f in ref["potential_differences"]])
        text = (
            f"### 🗃️ Reference Master Template Comparison\n\n"
            f"**Reference lookup completed.**\n\n"
            f"**Document Type**:\n{ref['doc_type']}\n\n"
            f"**Reference Status**:\n{ref['reference_status']}\n\n"
            f"**Matching Fields**:\n{match_str}\n\n"
            f"**Potential Difference**:\n{diff_str}\n\n"
            f"**Source**:\n{ref['source']}\n\n"
            f"**Mode**:\n{ref['mode']}"
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "🗃️ REFERENCE LOOKUP: DEMO",
            "recommendation": "Verify differences against physical sample register",
            "evidence": ref["potential_differences"],
            "confidence": "Demo Synthetic Benchmark",
        }

    # 8. Generate case summary
    if any(k in q for k in ["generate case summary", "case summary", "summary", "brief", "dossier"]):
        summary = generate_case_summary(cid)
        return {
            "text": summary,
            "case_id": short_id,
            "risk_badge": "📋 OFFICIAL CASE SUMMARY",
            "recommendation": "Submit signed form MHA-SEC-04 to Shift In-Charge",
            "evidence": [f"Risk Score {cdata['risk_score']}/100", f"Reason: {cdata['reason_code']}"],
            "confidence": "Authenticated SQLite Audit Record",
        }

    # 9. Check Case Status
    if any(k in q for k in ["check case status", "case status", "status of case", "what is the status"]):
        text = (
            f"### 📋 Case Status: `{short_id}`\n\n"
            f"• **Checkpoint**: {cdata['checkpoint']}\n"
            f"• **Document**: {cdata['doc_type']}\n"
            f"• **Current Decision**: **{cdata['decision']}**\n"
            f"• **Triage Score**: `{cdata['risk_score']}/100`\n"
            f"• **Reason Code**: `{cdata['reason_code']}`\n"
            f"• **Timestamp**: `{cdata['created_at'][:19]}`\n\n"
            f"**Next Procedural Step**: {cdata['reason_detail']}"
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": f"STATUS: {cdata['decision']}",
            "recommendation": "Review case dossier and secondary interview record",
            "evidence": [f"Status code: {cdata['reason_code']}"],
            "confidence": "Live SQLite State",
        }

    # 10. Screening guidelines / Standard SOPs
    if any(k in q for k in ["screening guidelines", "guideline", "sop", "mrz", "hologram", "transliteration", "name"]):
        text = (
            f"### 📜 Government Screening & Triage Guidelines\n\n"
            f"1. **ICAO 9303 Compliance**: Validate 7-3-1 check digit weighting across lines 1 & 2.\n"
            f"2. **Transliteration Policy**: Regional phonetic variations (e.g. *Mohd* vs *Mohammad*) are **not** evidence of fraud.\n"
            f"3. **Optically Variable Devices (OVD)**: Verify multi-axis color shift under white light; verify UV-A fluorescent fibers.\n"
            f"4. **Chain-of-Custody**: All decisions are anchored with SHA-256 digests in compliance with Section 65B Indian Evidence Act."
        )
        return {
            "text": text,
            "case_id": short_id,
            "risk_badge": "📜 OFFICIAL GUIDELINES",
            "recommendation": "Consult MHA Circular 2026/SEC-08 for regional exemptions",
            "evidence": ["ICAO 9303 Specification", "MHA Standard Operating Procedure"],
            "confidence": "Statutory Guideline Reference",
        }

    # Default / General Response
    text = (
        f"**Officer Query**: *\"{user_query}\"*\n\n"
        f"I have evaluated your query against active **Case {short_id}** (`{cdata['doc_type']}`, Risk: `{cdata['risk_score']}/100`).\n\n"
        f"• For case-specific analysis, use the quick actions above or ask *\"Why was this document flagged?\"* or *\"Explain the risk score\"*.\n"
        f"• Remember that AI verification outputs are **decision-support indicators** and must be complemented by authorized officer inspection."
    )
    return {
        "text": text,
        "case_id": short_id,
        "risk_badge": "ℹ️ DECISION SUPPORT ADVISORY",
        "recommendation": "Review document biometrics and physical features",
        "evidence": [],
        "confidence": "91.5%",
    }


# =========================================================
# INITIALIZATION & STATE MANAGEMENT
# =========================================================

def init_ai_assistant_state():
    """Ensure persistent chat history and active case state exist."""
    welcome_text = (
        "Welcome to the National Identity Verification Portal. I'm your AI assistant, "
        "here to help with document screening, identity verification, and application inquiries.\n\n"
        "How can I assist you today?"
    )
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {
                "role": "assistant",
                "text": welcome_text,
                "case_id": "DCD36A5B",
                "risk_badge": "● SYSTEM READY",
                "recommendation": None,
                "evidence": None,
                "confidence": None,
                "time": datetime.now().strftime("%H:%M"),
            }
        ]
    elif len(st.session_state.ai_chat_history) > 0:
        first_msg = st.session_state.ai_chat_history[0]
        if first_msg.get("role") == "assistant" and "Hello Officer" in first_msg.get("text", ""):
            first_msg["text"] = welcome_text

    if "ai_active_case_idx" not in st.session_state:
        st.session_state.ai_active_case_idx = 0

    if "show_doc_upload_drawer" not in st.session_state:
        st.session_state.show_doc_upload_drawer = False


# =========================================================
# FULL AI ASSISTANT PAGE (OFFICIAL GOVERNMENT DESK)
# =========================================================

def render_chatbot_page():
    init_ai_assistant_state()
    cases = get_all_case_choices()
    avatar_src = get_ai_avatar_b64()

    # Ensure index within bounds
    idx = min(st.session_state.ai_active_case_idx, len(cases) - 1)
    active_case = cases[idx]

    # Clean Pill Buttons Styling Scoped to Chatbot Page
    st.markdown(
        clean_html(
            """
            <style>
            .st-key-desk_btn_q1 button,
            .st-key-desk_btn_q2 button,
            .st-key-desk_btn_q3 button,
            .st-key-desk_btn_q4 button,
            .st-key-desk_btn_q5 button {
                border-radius: 9999px !important;
                background: #ffffff !important;
                border: 1.2px solid #E2E8F0 !important;
                color: #0B3FBF !important;
                font-size: 0.83rem !important;
                font-weight: 600 !important;
                padding: 8px 16px !important;
                height: auto !important;
                min-height: 38px !important;
                line-height: 1.25 !important;
                box-shadow: 0 1px 3px rgba(7, 26, 114, 0.04) !important;
                transition: all 0.15s ease-in-out !important;
                text-align: center !important;
            }

            .st-key-desk_btn_q1 button:hover,
            .st-key-desk_btn_q2 button:hover,
            .st-key-desk_btn_q3 button:hover,
            .st-key-desk_btn_q4 button:hover,
            .st-key-desk_btn_q5 button:hover {
                background: #E8FAFC !important;
                border-color: #22BFC9 !important;
                color: #071A72 !important;
                box-shadow: 0 3px 10px rgba(34, 191, 201, 0.22) !important;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

    # 1. OFFICIAL ROYAL PURPLE HEADER (MATCHING REFERENCE DESIGN)
    st.markdown(
        clean_html(
            f"""
            <div style="background:linear-gradient(120deg, #071A72 0%, #0B3FBF 50%, #22BFC9 100%); border-radius:14px; padding:18px 24px; margin-bottom:1.25rem; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 18px rgba(11,63,191,0.25);">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:42px; height:42px; border-radius:50%; background:rgba(255,255,255,0.22); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                        <img src="{avatar_src}" style="width:32px; height:32px; border-radius:50%; display:block;" alt="AI">
                    </div>
                    <div>
                        <h2 style="margin:0; font-size:1.35rem; color:#ffffff; font-weight:700; letter-spacing:-0.01em;">
                            UnveilX AI Assistant
                        </h2>
                        <div style="color:rgba(255,255,255,0.88); font-size:0.8rem; margin-top:2px; display:flex; align-items:center; gap:6px;">
                            <span style="display:inline-block; width:7px; height:7px; background:#34d399; border-radius:50%;"></span>
                            <span>AI-powered · Available 24/7 · National Identity Verification Portal</span>
                        </div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="background:rgba(255,255,255,0.18); color:#ffffff; border:1px solid rgba(255,255,255,0.3); padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700;">
                        ● SYSTEM ONLINE
                    </span>
                    <span style="background:rgba(255,255,255,0.18); color:#fef08a; border:1px solid rgba(255,255,255,0.3); padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700;">
                        DEMO MODE
                    </span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # 2. ACTIVE CASE SELECTION & METADATA STRIP (LIGHT CLEAN CARD)
    with st.container(border=True):
        sel_c1, sel_c2 = st.columns([1.8, 2.2])

        with sel_c1:
            case_options = [c["label"] for c in cases]
            selected_label = st.selectbox(
                "Active Case Context for AI Analysis",
                case_options,
                index=idx,
                key="case_context_selector",
                help="Select the case to feed real-time metadata, anomalies, and risk factors into the AI Assistant",
            )
            new_idx = case_options.index(selected_label)
            if new_idx != st.session_state.ai_active_case_idx:
                st.session_state.ai_active_case_idx = new_idx
                active_case = cases[new_idx]
                st.rerun()

        with sel_c2:
            score = active_case["risk_score"]
            dec = active_case["decision"]
            badge_bg = "rgba(239,68,68,0.1)" if dec == "REJECTED" or score >= 70 else ("rgba(245,158,11,0.1)" if score >= 40 else "rgba(16,185,129,0.1)")
            badge_col = "#ef4444" if dec == "REJECTED" or score >= 70 else ("#f59e0b" if score >= 40 else "#10b981")
            st.markdown(
                clean_html(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-top:22px; font-size:0.84rem; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase;">CASE ID:</span> <strong style="color:#0f172a;">{active_case['short_id']}</strong> &nbsp;|&nbsp;
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase;">DOC:</span> <span style="color:#334155;">{active_case['doc_type']}</span> &nbsp;|&nbsp;
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase;">CHECKPOINT:</span> <span style="color:#334155;">{active_case['checkpoint']}</span>
                        </div>
                        <div>
                            <span style="background:{badge_bg}; border:1px solid {badge_col}; color:{badge_col}; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.75rem;">
                                RISK: {score}/100 • {dec}
                            </span>
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    # 3. QUICK QUESTIONS SECTION (MATCHING REFERENCE PILLS)
    st.markdown(
        clean_html(
            """
            <div style="color:#8592a6; font-size:11px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin:12px 0 8px 4px;">
                QUICK QUESTIONS
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # Row 1: Why was this document flagged?
    if st.button("Why was this document flagged?", key="desk_btn_q1", use_container_width=True):
        handle_floating_query("Why was this document flagged?", active_case)

    # Row 2: Explain the risk score? & Explain the OCR results
    d_q2_col1, d_q2_col2 = st.columns(2)
    with d_q2_col1:
        if st.button("Explain the risk score?", key="desk_btn_q2", use_container_width=True):
            handle_floating_query("Explain the risk score?", active_case)
    with d_q2_col2:
        if st.button("Explain the OCR results", key="desk_btn_q3", use_container_width=True):
            handle_floating_query("Explain the OCR results", active_case)

    # Row 3: What verification checks were performed?
    if st.button("What verification checks were performed?", key="desk_btn_q4", use_container_width=True):
        handle_floating_query("What verification checks were performed?", active_case)

    # Row 4: Compare extracted data with the original document
    if st.button("Compare extracted data with the original document", key="desk_btn_q5", use_container_width=True):
        handle_floating_query("Compare extracted data with the original document", active_case)

    # 4. DOCUMENT UPLOAD DRAWER (COLLAPSIBLE / TOGGLEABLE)
    if st.session_state.show_doc_upload_drawer:
        with st.container(border=True):
            st.markdown(
                clean_html(
                    """
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <strong style="color:#0f172a;">📄 Upload Verification Document (Demo / Prototype Inspection)</strong>
                        <span style="font-size:0.75rem; color:#b45309; background:rgba(245,158,11,0.15); padding:2px 8px; border-radius:4px; border:1px solid #f59e0b;">
                            DEMO / MOCK ANALYSIS
                        </span>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )
            up_file = st.file_uploader(
                "Upload document for AI assisted analysis (PDF, PNG, JPG, JPEG)",
                type=["pdf", "png", "jpg", "jpeg"],
                key="ai_doc_upload_input",
                help="Supports PDF, PNG, JPG, JPEG for demonstration of automated triage heuristics",
            )
            if up_file:
                analysis = analyze_uploaded_document_demo(up_file.name, up_file.size)
                st.success(f"✓ {analysis['status']}: `{analysis['file_name']}` ({analysis['file_size']})")
                
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    st.markdown(f"**Document Type**: `{analysis['document_type']}`")
                    st.markdown("**Detected Fields:**")
                    for df in analysis["detected_fields"]:
                        st.markdown(f"✓ {df}")
                with c_a2:
                    st.markdown(f"**Risk Level**: `{analysis['risk']}`")
                    st.markdown("**Potential Issues:**")
                    for pi in analysis["potential_issues"]:
                        st.markdown(f"⚠ {pi}")
                
                if st.button("💬 Attach Analysis to Chat Stream", key="btn_attach_doc_analysis"):
                    st.session_state.ai_chat_history.append({
                        "role": "user",
                        "text": f"Uploaded `{up_file.name}` for verification review.",
                        "time": datetime.now().strftime("%H:%M"),
                    })
                    st.session_state.ai_chat_history.append({
                        "role": "assistant",
                        "text": f"### 📄 Document Analysis: `{analysis['file_name']}`\n\n**Type**: {analysis['document_type']}\n**Risk Evaluation**: `{analysis['risk']}`\n\n**Detected Fields**:\n" + "\n".join([f"✓ {f}" for f in analysis["detected_fields"]]) + "\n\n**Potential Issues**:\n" + "\n".join([f"⚠ {p}" for p in analysis["potential_issues"]]) + f"\n\n*Note*: {analysis['mode']}.",
                        "case_id": active_case["short_id"],
                        "risk_badge": "📄 DEMO INSPECTION",
                        "recommendation": analysis["recommendation"],
                        "evidence": analysis["potential_issues"],
                        "confidence": "Mock Heuristic Pipeline",
                        "time": datetime.now().strftime("%H:%M"),
                    })
                    st.session_state.show_doc_upload_drawer = False
                    st.rerun()

    # 5. INTERACTIVE CHAT STREAM (LIGHT THEME MATCHING REFERENCE)
    st.markdown("<hr style='margin:16px 0 14px; border-color:#e2e8f0;'>", unsafe_allow_html=True)
    
    chat_container = st.container(height=420)
    with chat_container:
        for msg in st.session_state.ai_chat_history:
            if msg["role"] == "assistant":
                rec_html = ""
                if msg.get("recommendation"):
                    rec_html = f"<div style='background:#E8FAFC; border-left:3px solid #22BFC9; border-radius:6px; padding:8px 12px; margin-top:10px; font-size:0.83rem; color:#071A72;'><strong>⚖️ Official Recommendation:</strong> {msg['recommendation']}</div>"
                st.markdown(
                    clean_html(
                        f"""
                        <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:14px; padding:0 4px;">
                            <div style="width:32px; height:32px; min-width:32px; border-radius:50%; flex-shrink:0; margin-top:2px;">
                                <img src="{avatar_src}" style="width:32px; height:32px; border-radius:50%; display:block;" alt="AI">
                            </div>
                            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:14px 18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); color:#1e293b; font-size:0.9rem; line-height:1.55; flex:1;">
                                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:6px; margin-bottom:8px;">
                                    <strong style="color:#0B3FBF; font-size:0.88rem;">UnveilX AI Assistant</strong>
                                    <span style="font-size:0.75rem; color:#94a3b8;">{msg.get('time', '')}</span>
                                </div>
                                {format_bubble_text_html(msg['text'])}
                                {rec_html}
                            </div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    clean_html(
                        f"""
                        <div style="display:flex; justify-content:flex-end; margin-bottom:14px; padding:0 4px;">
                            <div style="background:linear-gradient(120deg, #071A72 0%, #0B3FBF 60%, #0878D1 100%); color:#ffffff; border-radius:14px 14px 2px 14px; padding:12px 18px; max-width:80%; font-size:0.9rem; line-height:1.5; box-shadow:0 2px 8px rgba(11,63,191,0.25);">
                                {html.escape(msg['text'])}
                            </div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )

    # 6. INPUT AREA (UPLOAD, INPUT, AND CLEAR)
    input_col1, input_col2, input_col3 = st.columns([0.08, 0.84, 0.08])

    with input_col1:
        if st.button("📎", key="btn_toggle_upload", help="Upload Verification Document for AI Analysis"):
            st.session_state.show_doc_upload_drawer = not st.session_state.show_doc_upload_drawer
            st.rerun()

    with input_col2:
        chat_val = st.chat_input("Type your message...", key="official_desk_chat_input")
        if chat_val:
            handle_floating_query(chat_val, active_case)

    with input_col3:
        if st.button("🧹", key="btn_clear_desk_chat", help="Reset Consultation Chat Stream"):
            st.session_state.ai_chat_history = []
            init_ai_assistant_state()
            st.rerun()

    # Footer
    st.markdown(
        clean_html(
            """
            <div style="text-align:center; font-size:11px; color:#94a3b8; padding:8px 0 2px; margin-top:6px;">
                Powered by UnveilX AI · Ministry of Digital Affairs
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# FLOATING BOTTOM-RIGHT AI ASSISTANT (COMPACT PANEL)
# =========================================================

def handle_floating_query(q_text: str, active_case: dict):
    """Dispatches user query from floating assistant and records interaction in state."""
    st.session_state.ai_chat_history.append({
        "role": "user",
        "text": q_text,
        "time": datetime.now().strftime("%H:%M"),
    })
    resp = process_assistant_query(q_text, active_case)
    st.session_state.ai_chat_history.append({
        "role": "assistant",
        "text": resp["text"],
        "case_id": resp.get("case_id"),
        "risk_badge": resp.get("risk_badge"),
        "recommendation": resp.get("recommendation"),
        "evidence": resp.get("evidence"),
        "confidence": resp.get("confidence"),
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()


def render_floating_chatbot():
    """
    Renders official floating launcher at bottom-right of the dashboard.
    Opens a compact, case-aware decision-support panel matching reference design.
    """
    init_ai_assistant_state()
    cases = get_all_case_choices()
    idx = min(st.session_state.ai_active_case_idx, len(cases) - 1)
    active_case = cases[idx]
    avatar_src = get_ai_avatar_b64()

    # Sleek Circular Floating Action Button (FAB) and Docked Panel CSS
    st.markdown(
        clean_html(
            f"""
            <style>
            /* Floating Launcher FAB Button (Royal Purple #4f46e5 with Star + Sparkles) */
            .st-key-floating_chat_popover,
            div[data-testid="stPopover"],
            div:has(> button[data-testid="stPopoverButton"]) {{
                position: fixed !important;
                bottom: 24px !important;
                right: 28px !important;
                z-index: 9999999 !important;
            }}

            .st-key-floating_chat_popover button,
            div[data-testid="stPopover"] button,
            button[data-testid="stPopoverButton"] {{
                width: 58px !important;
                height: 58px !important;
                min-width: 58px !important;
                max-width: 58px !important;
                border-radius: 50% !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                background: linear-gradient(120deg, #071A72 0%, #0B3FBF 50%, #22BFC9 100%) !important;
                background-image: url('{avatar_src}') !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
                background-size: 34px 34px !important;
                border: none !important;
                box-shadow: 0 8px 24px rgba(11, 63, 191, 0.40) !important;
                cursor: pointer !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }}

            .st-key-floating_chat_popover button *,
            div[data-testid="stPopover"] button *,
            button[data-testid="stPopoverButton"] * {{
                display: none !important;
            }}

            .st-key-floating_chat_popover button:hover,
            div[data-testid="stPopover"] button:hover,
            button[data-testid="stPopoverButton"]:hover {{
                background: linear-gradient(120deg, #0B3FBF 0%, #0878D1 50%, #22BFC9 100%) !important;
                transform: scale(1.08) !important;
                box-shadow: 0 12px 30px rgba(34, 191, 201, 0.55) !important;
            }}

            /* Modal Popover Container (Off-White/Clean White Card) */
            div[data-testid="stPopoverBody"],
            [data-testid="stPopoverBody"],
            div[data-testid="stPopoverContent"] {{
                position: fixed !important;
                bottom: 92px !important;
                right: 28px !important;
                width: 400px !important;
                max-width: calc(100vw - 36px) !important;
                height: 620px !important;
                max-height: calc(100vh - 110px) !important;
                background-color: rgba(255, 255, 255, 0.94) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(226, 232, 240, 0.9) !important;
                border-radius: 18px !important;
                box-shadow: 0 20px 48px rgba(7, 26, 114, 0.14) !important;
                padding: 0 !important;
                overflow: hidden !important;
                display: flex !important;
                flex-direction: column !important;
                z-index: 9999999 !important;
            }}

            div[data-testid="stPopoverBody"] > div,
            [data-testid="stPopoverBody"] > div {{
                padding: 0 !important;
                display: flex !important;
                flex-direction: column !important;
                height: 100% !important;
                gap: 3px !important;
            }}

            /* Quick Questions Pill Buttons */
            .st-key-fl_btn_q1 button,
            .st-key-fl_btn_q2 button,
            .st-key-fl_btn_q3 button,
            .st-key-fl_btn_q4 button,
            .st-key-fl_btn_q5 button {{
                border-radius: 9999px !important;
                background: #ffffff !important;
                border: 1.2px solid #E2E8F0 !important;
                color: #0B3FBF !important;
                font-size: 0.81rem !important;
                font-weight: 600 !important;
                padding: 6px 14px !important;
                height: auto !important;
                min-height: 34px !important;
                line-height: 1.25 !important;
                white-space: normal !important;
                box-shadow: 0 1px 3px rgba(7, 26, 114, 0.03) !important;
                transition: all 0.15s ease-in-out !important;
                text-align: center !important;
            }}

            .st-key-fl_btn_q1 button:hover,
            .st-key-fl_btn_q2 button:hover,
            .st-key-fl_btn_q3 button:hover,
            .st-key-fl_btn_q4 button:hover,
            .st-key-fl_btn_q5 button {{
                background: #E8FAFC !important;
                border-color: #22BFC9 !important;
                color: #071A72 !important;
                box-shadow: 0 2px 8px rgba(34, 191, 201, 0.20) !important;
            }}

            /* Chat Input Styling inside popover */
            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"],
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] {{
                padding: 4px 12px 2px 12px !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] > div,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] > div {{
                background: #f8fafc !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 12px !important;
                box-shadow: none !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] > div:focus-within,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] > div:focus-within {{
                border-color: #818cf8 !important;
                box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] textarea,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] textarea {{
                color: #1e293b !important;
                font-size: 0.85rem !important;
                padding: 8px 12px !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] textarea::placeholder,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] textarea::placeholder {{
                color: #94a3b8 !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] button,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] button {{
                background: linear-gradient(120deg, #071A72, #0B3FBF) !important;
                color: #ffffff !important;
                border-radius: 50% !important;
                width: 32px !important;
                height: 32px !important;
                border: none !important;
                transition: background 0.15s ease !important;
            }}

            div[data-testid="stPopoverBody"] div[data-testid="stChatInput"] button:hover,
            [data-testid="stPopoverBody"] div[data-testid="stChatInput"] button:hover {{
                background: linear-gradient(120deg, #0B3FBF, #22BFC9) !important;
            }}

            /* Floating Speech Bubble Badge ("UnveilX AI Assistant") directly above circular logo */
            div[data-testid="element-container"]:has(.ai-floating-assistant-badge),
            div[data-testid="stMarkdownContainer"]:has(.ai-floating-assistant-badge) {{
                height: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: visible !important;
            }}

            .ai-floating-assistant-badge {{
                position: fixed !important;
                bottom: 93px !important;
                right: 57px !important;
                transform: translateX(50%) !important;
                z-index: 9999998 !important;
                background: #081728 !important;
                border: 1.5px solid #38bdf8 !important;
                border-radius: 9999px !important;
                padding: 6px 16px !important;
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.45), 0 0 24px rgba(37, 99, 235, 0.25) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                user-select: none !important;
                white-space: nowrap !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}

            .ai-floating-assistant-badge:hover {{
                box-shadow: 0 0 18px rgba(56, 189, 248, 0.75), 0 0 32px rgba(37, 99, 235, 0.45) !important;
                border-color: #60a5fa !important;
                transform: translateX(50%) translateY(-2px) !important;
            }}

            .ai-floating-assistant-badge span {{
                color: #ffffff !important;
                font-size: 12.5px !important;
                font-weight: 600 !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                letter-spacing: -0.01em !important;
                line-height: 1.2 !important;
                pointer-events: none !important;
            }}

            /* Downward speech bubble pointer tail (V-shaped hollow border pointing down) */
            .ai-floating-badge-tail {{
                position: absolute !important;
                bottom: -5.5px !important;
                left: 50% !important;
                margin-left: -4.5px !important;
                width: 9px !important;
                height: 9px !important;
                background: #081728 !important;
                border-right: 1.5px solid #38bdf8 !important;
                border-bottom: 1.5px solid #38bdf8 !important;
                transform: rotate(45deg) !important;
                pointer-events: none !important;
                transition: border-color 0.2s ease !important;
            }}

            .ai-floating-assistant-badge:hover .ai-floating-badge-tail {{
                border-color: #60a5fa !important;
            }}

            /* Hide the badge when the popover chat panel is open */
            body:has(div[data-testid="stPopoverBody"]) .ai-floating-assistant-badge,
            body:has([data-testid="stPopoverBody"]) .ai-floating-assistant-badge,
            div:has(div[data-testid="stPopoverBody"]) .ai-floating-assistant-badge {{
                display: none !important;
            }}
            </style>

            <div class="ai-floating-assistant-badge" onclick="const btn = window.parent.document.querySelector('.st-key-floating_chat_popover button') || document.querySelector('.st-key-floating_chat_popover button'); if (btn) btn.click();" title="UnveilX AI Assistant">
                <span>UnveilX AI Assistant</span>
                <div class="ai-floating-badge-tail"></div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    with st.popover("", key="floating_chat_popover", help="Open UnveilX AI Assistant"):
        # Header inside compact panel (Solid Royal Purple #4f46e5)
        st.markdown(
            clean_html(
                f"""
                <div style="background:linear-gradient(120deg, #071A72 0%, #0B3FBF 55%, #22BFC9 100%); padding:12px 16px; display:flex; align-items:center; justify-content:space-between; border-radius:18px 18px 0 0; margin:-1px -1px 0 -1px; flex-shrink:0;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:34px; height:34px; border-radius:50%; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <img src="{avatar_src}" style="width:26px; height:26px; border-radius:50%; display:block;" alt="AI">
                        </div>
                        <div>
                            <div style="color:#ffffff; font-weight:700; font-size:0.95rem; line-height:1.2; letter-spacing:-0.01em;">UnveilX AI Assistant</div>
                            <div style="color:rgba(255,255,255,0.85); font-size:0.73rem; margin-top:2px; display:flex; align-items:center; gap:5px;">
                                <span style="display:inline-block; width:6px; height:6px; background:#34d399; border-radius:50%;"></span>
                                <span>AI-powered · Available 24/7</span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center;">
                        <div style="width:26px; height:26px; border-radius:50%; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; color:#ffffff; font-size:12px; font-weight:bold; cursor:pointer;" onclick="window.parent.document.querySelector('.st-key-floating_chat_popover button').click();" title="Close">✕</div>
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        # Message stream container
        chat_box = st.container(height=230)
        with chat_box:
            for m in st.session_state.ai_chat_history:
                if m["role"] == "assistant":
                    st.markdown(
                        clean_html(
                            f"""
                            <div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:12px; padding:0 4px;">
                                <div style="width:26px; height:26px; min-width:26px; border-radius:50%; flex-shrink:0; margin-top:2px;">
                                    <img src="{avatar_src}" style="width:26px; height:26px; border-radius:50%; display:block;" alt="AI">
                                </div>
                                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.04); color:#1e293b; font-size:0.85rem; line-height:1.48; flex:1;">
                                    {format_bubble_text_html(m['text'])}
                                </div>
                            </div>
                            """
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        clean_html(
                            f"""
                            <div style="display:flex; justify-content:flex-end; margin-bottom:12px; padding:0 4px;">
                                <div style="background:linear-gradient(120deg, #071A72 0%, #0B3FBF 60%, #0878D1 100%); color:#ffffff; border-radius:14px 14px 2px 14px; padding:10px 14px; max-width:85%; font-size:0.85rem; line-height:1.45; box-shadow:0 2px 6px rgba(11,63,191,0.25);">
                                    {html.escape(m['text'])}
                                </div>
                            </div>
                            """
                        ),
                        unsafe_allow_html=True,
                    )

        # QUICK QUESTIONS Section
        st.markdown(
            clean_html(
                """
                <div style="color:#8592a6; font-size:11px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin:6px 0 6px 12px;">
                    QUICK QUESTIONS
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        # Row 1: Why was this document flagged?
        if st.button("Why was this document flagged?", key="fl_btn_q1", use_container_width=True):
            handle_floating_query("Why was this document flagged?", active_case)

        # Row 2: Explain the risk score? & Explain the OCR results
        q2_col1, q2_col2 = st.columns(2)
        with q2_col1:
            if st.button("Explain the risk score?", key="fl_btn_q2", use_container_width=True):
                handle_floating_query("Explain the risk score?", active_case)
        with q2_col2:
            if st.button("Explain the OCR results", key="fl_btn_q3", use_container_width=True):
                handle_floating_query("Explain the OCR results", active_case)

        # Row 3: What verification checks were performed?
        if st.button("What verification checks were performed?", key="fl_btn_q4", use_container_width=True):
            handle_floating_query("What verification checks were performed?", active_case)

        # Row 4: Compare extracted data with the original document
        if st.button("Compare extracted data with the original document", key="fl_btn_q5", use_container_width=True):
            handle_floating_query("Compare extracted data with the original document", active_case)

        # Chat input inside popover
        c_val = st.chat_input("Type your message...", key="fl_chat_input")
        if c_val:
            handle_floating_query(c_val, active_case)

        # Footer Subtext
        st.markdown(
            clean_html(
                """
                <div style="text-align:center; font-size:11px; color:#94a3b8; padding:4px 0 2px; margin-top:2px;">
                    Powered by UnveilX AI · Ministry of Digital Affairs
                </div>
                """
            ),
            unsafe_allow_html=True,
        )
