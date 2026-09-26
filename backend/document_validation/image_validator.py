from PIL import Image
import cv2
import numpy as np


def validate_image(image_path: str) -> dict:
    """
    Basic document image quality validation.
    Returns measurable checks for resolution, blur and brightness.
    """

    try:
        image = Image.open(image_path)
        width, height = image.size

        # OpenCV image
        cv_image = cv2.imread(image_path)

        if cv_image is None:
            return {
                "status": "FAIL",
                "reason": "Image could not be read"
            }

        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Blur detection using Laplacian variance
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Brightness
        brightness = float(np.mean(gray))

        # Resolution check
        resolution_ok = width >= 600 and height >= 400

        # Blur check
        blur_ok = blur_score >= 80

        # Brightness check
        brightness_ok = 40 <= brightness <= 220

        checks = {
            "resolution": {
                "status": "PASS" if resolution_ok else "FAIL",
                "width": width,
                "height": height
            },
            "blur": {
                "status": "PASS" if blur_ok else "FAIL",
                "score": round(blur_score, 2)
            },
            "brightness": {
                "status": "PASS" if brightness_ok else "FAIL",
                "score": round(brightness, 2)
            }
        }

        failed_checks = sum(
            1 for check in checks.values()
            if check["status"] == "FAIL"
        )

        overall_status = "PASS" if failed_checks == 0 else "REVIEW"

        return {
            "status": overall_status,
            "image_size": {
                "width": width,
                "height": height
            },
            "checks": checks
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "reason": str(e)
        }
