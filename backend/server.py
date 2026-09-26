import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.predict import screen_document as run_tampering, cross_document_check
from ocr.main import process_document
from database.criminal_database import verify_person
from chatbot.assistant import get_response
from face_verification.face_module import verify_faces
from document_validation.image_validator import validate_image
from document_validation.mrz_validator import validate_passport_mrz
from document_validation.qr_validator import validate_qr_barcode

BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = BASE_DIR / "runtime_uploads"
TMP_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="UNVEILX FORGE - AI Document Screening",
    description="Local AI-powered document screening API for the SIH prototype.",
    version="2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Document(BaseModel):
    document_number: str
    name: str = ""
    dob: str = ""
    nationality: str = ""


class ChatRequest(BaseModel):
    question: str
    result: dict = {}


def _save_upload(upload: UploadFile, prefix: str) -> Path:
    suffix = Path(upload.filename or "upload.bin").suffix.lower() or ".bin"
    fd, raw_path = tempfile.mkstemp(prefix=f"{prefix}_", suffix=suffix, dir=TMP_DIR)
    path = Path(raw_path)
    try:
        with os.fdopen(fd, "wb") as out:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    except Exception:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
        raise
    return path


def _risk_score(ocr, validation, tampering, face, database, cross_document):
    scores = []
    if validation.get("status") == "FAIL": scores.append(65)
    elif validation.get("status") == "REVIEW": scores.append(25)

    if tampering.get("tampering_risk") == "HIGH": scores.append(90)
    elif tampering.get("tampering_risk") == "MEDIUM": scores.append(55)

    face_data = face.get("data", {}) or {}
    if face_data.get("liveness_checked") and not face_data.get("is_real", False):
        # A failed liveness/anti-spoof gate blocks biometric verification.
        scores.append(95)
    elif face.get("status") == "success" and not face_data.get("verified", False):
        scores.append(55)
    elif face.get("status") == "error":
        scores.append(70)

    if database.get("flagged"):
        scores.append(95)
    elif database.get("found"):
        scores.append(30)

    scores.append(int(cross_document.get("risk_score", 0) or 0))

    verification = ocr.get("verification", {}) or {}
    mismatches = sum(1 for v in verification.values() if v.get("status") == "MISMATCH")
    scores.append(min(mismatches * 20, 60))

    if (ocr.get("expiry") or {}).get("status") == "EXPIRED":
        scores.append(70)

    return max(scores or [0])


def _decision(score: int) -> str:
    if score > 60:
        return "REJECT / INVESTIGATE"
    if score > 25:
        return "MANUAL REVIEW"
    return "APPROVE"


@app.get("/")
def home():
    return {
        "system": "UNVEILX FORGE",
        "status": "ONLINE",
        "version": app.version,
        "modules": [
            "OCR", "Document Validation", "Tampering AI",
            "Face Verification", "Reference Database", "AI Assistant"
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
def verify_document(document: Document):
    return verify_person(
        document.document_number,
        document.name,
        document.dob,
        document.nationality,
    )


@app.post("/screen")
async def screen_document_api(
    file: UploadFile = File(...),
    selfie: UploadFile = File(...),
    second_document: Optional[UploadFile] = File(None),
):
    doc_path = selfie_path = second_path = None
    try:
        doc_path = _save_upload(file, "document")
        selfie_path = _save_upload(selfie, "selfie")
        if second_document is not None:
            second_path = _save_upload(second_document, "second_document")

        # 1. OCR + MRZ consistency
        ocr_raw = process_document(str(doc_path))
        ocr = {
            "name": ocr_raw.get("name"),
            "dob": ocr_raw.get("dob"),
            "nationality": ocr_raw.get("nationality"),
            "document_number": ocr_raw.get("document_number"),
            "fields": ocr_raw.get("ocr_fields", {}),
            "mrz": ocr_raw.get("mrz_fields", {}),
            "verification": ocr_raw.get("verification", {}),
            "expiry": ocr_raw.get("expiry", {}),
            "raw_text": ocr_raw.get("raw_text", []),
        }

        # 2. Image/QR/MRZ validation
        image_validation = validate_image(str(doc_path))
        raw_mrz = ocr.get("mrz", {}).get("raw_mrz") or []
        mrz_text = "\n".join(raw_mrz) if isinstance(raw_mrz, list) else str(raw_mrz)
        mrz_validation = validate_passport_mrz(mrz_text) if mrz_text else {
            "status": "REVIEW", "detected": False, "reason": "MRZ not available from OCR."
        }
        qr_validation = validate_qr_barcode(str(doc_path))
        validation_status = "FAIL" if image_validation.get("status") == "FAIL" else (
            "REVIEW" if any(x.get("status") == "REVIEW" for x in [image_validation, mrz_validation, qr_validation])
            else "PASS"
        )
        document_validation = {
            "status": validation_status,
            "valid": validation_status == "PASS",
            "image_validation": image_validation,
            "mrz_validation": mrz_validation,
            "qr_validation": qr_validation,
        }

        # 3. Optional cross-document check
        cross_document = {"field_results": {}, "risk_score": 0, "risk_level": "LOW"}
        if second_path:
            second_raw = process_document(str(second_path))
            cross_document = cross_document_check([ocr_raw, second_raw])

        # 4. Tampering AI
        tampering = run_tampering(str(doc_path))

        # 5. Face verification
        face = verify_faces(str(doc_path), str(selfie_path))

        # 6. Reference/demo database
        database = verify_person(
            ocr.get("document_number") or "",
            ocr.get("name") or "",
            ocr.get("dob") or "",
            ocr.get("nationality") or "",
        )

        score = _risk_score(ocr, document_validation, tampering, face, database, cross_document)
        decision = _decision(score)

        return {
            "document": {"type": "passport", "file_name": file.filename},
            "ocr": ocr,
            "document_validation": document_validation,
            "tampering": tampering,
            "face_verification": face,
            "cross_document": cross_document,
            "database": database,
            "overall_risk": {"level": "HIGH" if score > 60 else "MEDIUM" if score > 25 else "LOW", "score": score},
            "decision": decision,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Screening pipeline failed: {exc}") from exc
    finally:
        for path in [doc_path, selfie_path, second_path]:
            if path:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass


@app.post("/chat")
def chatbot(request: ChatRequest):
    return {"assistant": "UNVEILX AI Assistant", "answer": get_response(request.question, request.result)}
