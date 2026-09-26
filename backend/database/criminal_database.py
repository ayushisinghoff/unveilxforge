import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent.parent / "screening.db"


# ---------------- DATABASE SETUP ----------------

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            record_id TEXT PRIMARY KEY,
            document_number TEXT UNIQUE,
            name TEXT,
            dob TEXT,
            nationality TEXT,
            case_type TEXT,
            status TEXT,
            risk_level TEXT
        )
    """)

    # Completely fictional demonstration records
    demo_data = [
        (
            "CR-1001",
            "DEMO000002",
            "RAHUL VERMA",
            "10 OCT 1997",
            "AURORIAN",
            "DOCUMENT FRAUD",
            "FLAGGED",
            "HIGH"
        ),
        (
            "CR-1002",
            "DEMO000004",
            "AMAN KHAN",
            "05 MAY 1995",
            "AURORIAN",
            "IDENTITY FRAUD",
            "FLAGGED",
            "HIGH"
        ),
        (
            "CR-1003",
            "DEMO000005",
            "NEHA SHARMA",
            "18 FEB 1999",
            "AURORIAN",
            "TRAVEL FRAUD",
            "WATCHLIST",
            "MEDIUM"
        ),
        (
            "CR-1004",
            "DEMO000003",
            "ARJUN KUMAR",
            "15 MAR 1998",
            "AURORIAN",
            "NONE",
            "CLEAR",
            "LOW"
        ),
        (
            "CR-1005",
            "DEMO000001",
            "PRIYA SHARMA",
            "22 JUL 2000",
            "AURORIAN",
            "NONE",
            "CLEAR",
            "LOW"
        )
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO persons
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_data)

    conn.commit()
    conn.close()


# ---------------- SEARCH DATABASE ----------------

def verify_person(document_number, name="", dob="", nationality=""):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            record_id,
            document_number,
            name,
            dob,
            nationality,
            case_type,
            status,
            risk_level
        FROM persons
        WHERE document_number = ?
    """, (document_number,))

    record = cursor.fetchone()
    conn.close()

    if not record:
        return {
            "found": False,
            "status": "NOT_FOUND",
            "flagged": False,
            "risk_level": "UNKNOWN"
        }

    (
        record_id,
        doc_number,
        db_name,
        db_dob,
        db_nationality,
        case_type,
        status,
        risk_level
    ) = record

    mismatches = []

    if name and name.upper() != db_name.upper():
        mismatches.append("name")

    if dob and dob.upper() != db_dob.upper():
        mismatches.append("dob")

    if nationality and nationality.upper() != db_nationality.upper():
        mismatches.append("nationality")

    return {
        "found": True,
        "record_id": record_id,
        "document_number": doc_number,
        "name": db_name,
        "dob": db_dob,
        "nationality": db_nationality,
        "case_type": case_type,
        "status": status,
        "flagged": status == "FLAGGED",
        "risk_level": risk_level,
        "mismatches": mismatches
    }


create_database()