import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

def get_connection():
    db_path = BASE_DIR / "sih26188.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def save_screening_case(
    case_id: str,
    checkpoint_name: str,
    doc_type: str,
    risk_score: int,
    decision: str,
    factors: list,
    fields: dict,
    officer_id: int = 1,
    mrz_raw: str = "",
    ocr_confidence: float = None,
    file_name: str = None,
) -> bool:
    """Member 6 Database Service: Persists complete screening case and blockchain anchor."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        now_iso = datetime.now().isoformat()

        # 1. Insert into cases
        cur.execute(
            """
            INSERT INTO cases (case_id, checkpoint_name, created_at, created_by, offline_flag, case_decision, case_reason_code, case_reason_detail)
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (
                case_id,
                checkpoint_name,
                now_iso,
                officer_id,
                decision.lower(),
                "AUTO_SCREEN" if decision == "APPROVE" else "SECONDARY_REVIEW",
                f"Automated risk triage score: {risk_score}/100",
            ),
        )

        # 2. Insert into documents
        file_path = f"uploads/{case_id}_{doc_type}_{file_name or 'document'}"
        payload_bytes = f"{case_id}:{doc_type}:{now_iso}".encode("utf-8")
        file_hash = hashlib.sha256(payload_bytes).hexdigest()

        cur.execute(
            """
            INSERT INTO documents (case_id, file_path, file_hash, doc_type, uploaded_by, uploaded_at, status, offline_flag)
            VALUES (?, ?, ?, ?, ?, ?, 'analyzed', 1)
            """,
            (case_id, file_path, file_hash, doc_type, officer_id, now_iso),
        )
        doc_db_id = cur.lastrowid

        # 3. Insert into extraction_results
        mrz_sim = mrz_raw or ""
        cur.execute(
            """
            INSERT INTO extraction_results (document_id, mrz_raw, fields_json, ocr_confidence)
            VALUES (?, ?, ?, ?)
            """,
            (doc_db_id, mrz_sim, json.dumps(fields), ocr_confidence),
        )

        # 4. Insert into risk_assessments
        cur.execute(
            """
            INSERT INTO risk_assessments (document_id, risk_score, risk_factors_json, model_version, assessed_at)
            VALUES (?, ?, ?, 'v2.4-unveilx', ?)
            """,
            (doc_db_id, risk_score, json.dumps(factors), now_iso),
        )

        # 5. Insert into case_decisions
        cur.execute(
            """
            INSERT INTO case_decisions (document_id, decision, reason_code, reason_detail, decided_at, decided_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                doc_db_id,
                decision.lower(),
                "AUTO_SCREEN" if decision == "APPROVE" else "FLAGGED_CHECK",
                f"Automated risk assessment score {risk_score}",
                now_iso,
                officer_id,
            ),
        )

        # 6. Insert into audit_logs
        cur.execute(
            """
            INSERT INTO audit_logs (case_id, officer_id, action, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (case_id, officer_id, f"Completed screening - decision: {decision}", now_iso),
        )

        # 7. Insert into blockchain_anchors (Member 6 Blockchain verification hook)
        block_payload = f"{case_id}:{file_hash}:{risk_score}:{now_iso}"
        payload_hash = hashlib.sha256(block_payload.encode("utf-8")).hexdigest()
        tx_hash = "0x" + hashlib.sha256((payload_hash + "BLOCKCHAIN_SIM").encode("utf-8")).hexdigest()

        cur.execute(
            """
            INSERT INTO blockchain_anchors (case_id, payload_hash, tx_hash, chain, anchored_at, verified)
            VALUES (?, ?, ?, 'Ethereum-Sepolia-L2', ?, 1)
            """,
            (case_id, payload_hash, tx_hash, now_iso),
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False
