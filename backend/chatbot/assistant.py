# ---------------- UNVEILX AI ASSISTANT ----------------

def get_response(question, result):

    question = question.lower().strip()

    tampering = result.get("tampering", "")
    confidence = result.get("tampering_confidence", 0)
    overall_risk = result.get("overall_risk", "")

    database = result.get("database", {})
    cross_document = result.get("cross_document", {})

    mismatches = cross_document.get("field_results", {})

    # TAMPERING
    if "tamper" in question or "fake" in question:

        if tampering == "TAMPERED":
            return (
                f"The document was detected as TAMPERED "
                f"with {confidence}% confidence. "
                f"Further verification is recommended."
            )

        if tampering == "GENUINE":
            return (
                f"The document was classified as GENUINE "
                f"with {confidence}% confidence."
            )

        return "Tampering information is not available."

    # RISK
    if "risk" in question or "safe" in question:

        if overall_risk:
            return (
                f"The current overall risk level is {overall_risk}. "
                f"This assessment is based on the available "
                f"verification checks."
            )

        return "Overall risk information is not available."

    # DATABASE
    if (
        "criminal" in question
        or "database" in question
        or "flagged" in question
        or "watchlist" in question
    ):

        if not database:
            return "No database verification result is available."

        if database.get("found"):

            status = database.get("status", "UNKNOWN")
            risk = database.get("risk_level", "UNKNOWN")

            if database.get("flagged"):
                return (
                    f"A database record was found. "
                    f"The person is marked as {status} "
                    f"with a {risk} risk level. "
                    f"Case type: {database.get('case_type', 'UNKNOWN')}."
                )

            return (
                f"A database record was found, but the person "
                f"is currently marked as {status}. "
                f"Database risk level: {risk}."
            )

        return "No matching record was found in the demonstration database."

    # MISMATCH
    if "mismatch" in question or "cross" in question:

        found_mismatches = [
            field
            for field, status in mismatches.items()
            if status == "MISMATCH"
        ]

        if found_mismatches:
            return (
                "Mismatches were detected in: "
                + ", ".join(found_mismatches)
                + "."
            )

        return "No mismatches were found in the available fields."

    # NEXT STEP
    if (
        "what should i do" in question
        or "next step" in question
        or "what do i do" in question
    ):

        if overall_risk == "HIGH":
            return (
                "The document is HIGH RISK. "
                "Manual verification and additional identity "
                "checks are recommended before clearance."
            )

        if overall_risk == "MEDIUM":
            return (
                "The document has MEDIUM RISK. "
                "Review the flagged verification fields "
                "before making a final decision."
            )

        return (
            "The current screening result is LOW RISK. "
            "Continue with the standard verification procedure."
        )

    # HELP
    if "help" in question or "what can you do" in question:

        return (
            "I am UNVEILX AI Assistant. I can explain "
            "tampering results, risk levels, database matches, "
            "cross-document mismatches, and recommended next steps."
        )

    # DEFAULT
    return (
        "I can help explain the document's tampering result, "
        "database status, risk level, mismatches, and "
        "recommended verification steps."
    )