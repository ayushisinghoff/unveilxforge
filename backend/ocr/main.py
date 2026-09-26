import json
from pathlib import Path

from paddleocr import PaddleOCR

from ocr.field_parser import extract_fields

from ocr.mrz_parser import (
    find_mrz_lines,
    parse_mrz
)

from ocr.verifier import (
    verify_document,
    get_document_status,
    check_expiry
)


IMAGE_PATH = "ocr/test_images/passport.jpg"

_OCR_ENGINE = None


# -----------------------------------------
# OCR PROCESSING FUNCTION
# -----------------------------------------

def process_document(image_path):
    """Run OCR/MRZ extraction for one uploaded document and return structured data."""
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        _OCR_ENGINE = PaddleOCR(lang="en", enable_mkldnn=False)

    result = _OCR_ENGINE.predict(image_path)
    ocr_text = []
    for res in result:
        data = res.json
        if callable(data):
            data = data()
        if isinstance(data, dict):
            res_data = data.get("res", data)
            for text in res_data.get("rec_texts", []):
                if text and text.strip():
                    ocr_text.append(text.strip())

    ocr_fields = extract_fields(ocr_text)
    mrz_lines = find_mrz_lines(ocr_text)
    mrz_fields = parse_mrz(mrz_lines)
    if mrz_fields.get("surname") and mrz_fields.get("given_names"):
        ocr_fields["name"] = f"{mrz_fields['given_names']} {mrz_fields['surname']}".strip()

    verification = verify_document(ocr_fields, mrz_fields)
    document_status = get_document_status(verification)
    expiry_status = check_expiry(mrz_fields.get("date_of_expiry"))

    with open(Path(__file__).resolve().parents[1] / "ocr_result.json", "w", encoding="utf-8") as file:
        json.dump({"ocr_fields": ocr_fields, "mrz_fields": mrz_fields,
                   "verification": verification, "expiry": expiry_status},
                  file, indent=4, ensure_ascii=False)

    return {
        "name": ocr_fields.get("name"),
        "dob": ocr_fields.get("date_of_birth"),
        "nationality": ocr_fields.get("nationality"),
        "document_number": ocr_fields.get("passport_number"),
        "ocr_fields": ocr_fields,
        "mrz_fields": mrz_fields,
        "verification": verification,
        "expiry": expiry_status,
        "document_status": document_status,
        "raw_text": ocr_text,
    }


# -----------------------------------------
# STANDALONE TEST
# -----------------------------------------

if __name__ == "__main__":

    process_document(
        IMAGE_PATH
    )