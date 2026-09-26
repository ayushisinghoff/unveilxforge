from datetime import datetime


def normalize(value):
    """
    Makes values easier to compare.
    """

    if value is None:
        return ""

    return (
        str(value)
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("/", "")
        .strip()
    )


def normalize_date(value):
    """
    Converts different date formats into YYYY-MM-DD.
    """

    if not value:
        return None

    value = str(value).strip().upper()

    try:
        date = datetime.strptime(value, "%Y-%m-%d")
        return date.strftime("%Y-%m-%d")
    except ValueError:
        pass

    try:
        date = datetime.strptime(value, "%d %b %Y")
        return date.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return value


def compare_values(ocr_value, mrz_value):
    """
    Compares one OCR value with one MRZ value.
    """

    if not ocr_value or not mrz_value:
        return {
            "match": None,
            "status": "NOT_AVAILABLE"
        }

    if normalize_date(ocr_value) == normalize_date(mrz_value):
        return {
            "match": True,
            "status": "MATCH"
        }

    return {
        "match": False,
        "status": "MISMATCH"
    }


def verify_document(ocr_fields, mrz_fields):

    verification = {}

    verification["passport_number"] = compare_values(
        ocr_fields.get("passport_number"),
        mrz_fields.get("passport_number")
    )

    verification["date_of_birth"] = compare_values(
        ocr_fields.get("date_of_birth"),
        mrz_fields.get("date_of_birth")
    )

    verification["sex"] = compare_values(
        ocr_fields.get("sex"),
        mrz_fields.get("sex")
    )

    verification["nationality"] = compare_values(
        ocr_fields.get("nationality"),
        mrz_fields.get("nationality")
    )

    if mrz_fields.get("passport_number_checksum") is False:
        verification["passport_number_checksum"] = {
            "match": False,
            "status": "MISMATCH"
        }

    return verification


def get_document_status(verification):
    """
    Determines the final document status.
    """

    mismatches = []

    for field, result in verification.items():
        if result["status"] == "MISMATCH":
            mismatches.append(field)

    if mismatches:
        return {
            "status": "SUSPICIOUS",
            "reason": mismatches
        }

    return {
        "status": "VERIFIED",
        "reason": []
    }


def check_expiry(expiry_date):
    """
    Checks whether the document has expired.
    """

    if not expiry_date:
        return {
            "status": "NOT_AVAILABLE"
        }

    try:
        expiry = datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        ).date()

        today = datetime.today().date()

        if expiry < today:
            return {
                "status": "EXPIRED"
            }

        return {
            "status": "VALID"
        }

    except ValueError:
        return {
            "status": "INVALID_DATE"
        }
    