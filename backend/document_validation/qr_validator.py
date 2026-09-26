import cv2


def validate_qr_barcode(image_path: str) -> dict:
    """
    Detect and decode QR codes.
    Also detects barcode-like regions.
    Detection does not prove document authenticity.
    """

    try:
        image = cv2.imread(image_path)

        if image is None:
            return {
                "status": "FAIL",
                "qr": {
                    "detected": False,
                    "decoded": False,
                    "data": None
                },
                "barcode": {
                    "detected": False
                }
            }

        # -------------------------
        # QR CODE
        # -------------------------

        qr_detector = cv2.QRCodeDetector()

        qr_data, points, _ = qr_detector.detectAndDecode(image)

        qr_detected = points is not None
        qr_decoded = bool(qr_data)

        # -------------------------
        # BARCODE-LIKE DETECTION
        # -------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        edges = cv2.Canny(
            gray,
            50,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        barcode_detected = False

        for contour in contours:

            x, y, w, h = cv2.boundingRect(contour)

            if h > 20 and w > 80:

                ratio = w / float(h)

                if ratio > 3:
                    barcode_detected = True
                    break

        if qr_decoded:
            status = "PASS"

        elif qr_detected or barcode_detected:
            status = "REVIEW"

        else:
            status = "REVIEW"

        return {
            "status": status,

            "qr": {
                "detected": qr_detected,
                "decoded": qr_decoded,
                "data": qr_data if qr_decoded else None
            },

            "barcode": {
                "detected": barcode_detected
            },

            "note": (
                "QR/barcode detection is an additional "
                "validation signal and does not prove authenticity."
            )
        }

    except Exception as e:

        return {
            "status": "FAIL",
            "reason": str(e)
        }