"""
face_module.py  (DeepFace version)
====================================
MEMBER 5 — Face Verification Module
AI-Based Fake Identity and Document Screening System

WHY THIS VERSION:
------------------
Pehla version "face_recognition" library use karta tha, jiske andar
"dlib" install hota hai — jo kabhi kabhi Windows par compile errors deta
hai (C++ build tools maangta hai).

Yeh version "deepface" library use karta hai — isko sirf "pip install"
se hi install kiya ja sakta hai, koi C++ compiling nahi chahiye.
Function names aur output SAME hain, isliye Member 1 (backend) ke liye
kuch bhi change nahi karna padega — bas import line badlegi.

INSTALL (ek baar terminal mein chalao):
----------------------------------------
    pip install -r requirements.txt

NOTE: Pehli baar chalane par DeepFace khud-ba-khud ek pre-trained AI
model (~90-100 MB) internet se download karega. Isliye pehli run mein
thoda time lagega aur internet connection chahiye hoga. Uske baad woh
model computer mein save ho jata hai, dobara download nahi hoga.
"""

import os
from deepface import DeepFace


# ---------------------------------------------------------------------
# CONFIG — yeh values tune ki ja sakti hain (prototype values)
# ---------------------------------------------------------------------
# DeepFace ke andar kai models available hain (VGG-Face, Facenet, ArcFace, etc.)
# "VGG-Face" default aur beginner-friendly hai — accha balance deta hai
# speed aur accuracy ke beech.
MODEL_NAME = "Facenet512"

# DeepFace face detect karne ke liye alag "detector backend" use karta hai.
# "opencv" sabse fast aur lightweight hai, beginners ke liye best.
DETECTOR_BACKEND = "opencv"


def _build_response(status="success", data=None, errors=None):
    """
    Har function ka output SAME SHAPE mein hona chahiye
    (Part 9 ke contract ke according), taaki Member 1 ka
    backend consistently handle kar sake.
    """
    return {
        "status": status,
        "data": data if data is not None else {},
        "errors": errors if errors is not None else []
    }


def _count_faces(image_path):
    """
    INTERNAL HELPER FUNCTION.
    Image mein kitne faces hain, yeh count karta hai.

    Returns: (face_count, error_message_or_None)
    """
    if not os.path.exists(image_path):
        return 0, f"File not found: {image_path}"

    try:
        # enforce_detection=False -> agar face na mile to crash nahi karega,
        # bajaye iske empty list dega jise hum khud handle karenge.
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False
        )
    except Exception as e:
        return 0, f"Could not process image: {str(e)}"

    # DeepFace kabhi kabhi ek "fake" low-confidence face de deta hai jab
    # asal mein koi face nahi hota — isliye confidence check bhi karte hain.
    real_faces = [f for f in faces if f.get("confidence", 0) > 0.5]
    return len(real_faces), None


def verify_faces(document_path, selfie_path):
    """
    MAIN FUNCTION — ise Member 1 backend se call karega.
    (SAME INPUT/OUTPUT CONTRACT as the face_recognition version)

    INPUT:
        document_path : ID document image ka file path (string)
        selfie_path    : selfie image ka file path (string)

    OUTPUT (JSON / Python dict):
    {
        "status": "success" | "error",
        "data": {
            "verified": true/false,
            "similarity_score": 0.0 - 1.0,
            "document_face_count": int,
            "selfie_face_count": int
        },
        "errors": ["list of human-readable problems, if any"]
    }
    """
    errors = []

    # ---- Step 1: Basic file existence check ----
    if not os.path.exists(document_path):
        errors.append(f"Document image issue: File not found: {document_path}")
    if not os.path.exists(selfie_path):
        errors.append(f"Selfie image issue: File not found: {selfie_path}")

    if errors:
        return _build_response(
            status="error",
            data={"verified": False, "similarity_score": 0.0,
                  "document_face_count": 0, "selfie_face_count": 0},
            errors=errors
        )

    # ---- Step 2: Dono images mein face count karo ----
    doc_face_count, doc_error = _count_faces(document_path)
    selfie_face_count, selfie_error = _count_faces(selfie_path)

    if doc_error:
        errors.append(f"Document image issue: {doc_error}")
    if selfie_error:
        errors.append(f"Selfie image issue: {selfie_error}")

    if doc_face_count == 0:
        errors.append("No face detected in document image")
    if selfie_face_count == 0:
        errors.append("No face detected in selfie image")

    if doc_face_count > 1:
        errors.append("Multiple faces detected in document image")
    if selfie_face_count > 1:
        errors.append("Multiple faces detected in selfie image")

    # Agar koi face hi nahi mila kisi image mein, compare karna bekaar hai
    if doc_face_count == 0 or selfie_face_count == 0:
        return _build_response(
            status="error",
            data={
                "verified": False,
                "similarity_score": 0.0,
                "document_face_count": doc_face_count,
                "selfie_face_count": selfie_face_count
            },
            errors=errors
        )
    # ---- Step 3: Liveness check ----
    liveness_result = check_liveness(selfie_path)

    if liveness_result.get("status") != "success":
        return _build_response(
            status="error",
            data={
                "verified": False,
                "similarity_score": 0.0,
                "document_face_count": doc_face_count,
                "selfie_face_count": selfie_face_count,
                "liveness_checked": False
            },
            errors=liveness_result.get("errors", ["Liveness check failed"])
        )

    liveness_data = liveness_result.get("data", {})

    if not liveness_data.get("is_real", False):
        return _build_response(
            status="error",
            data={
                "verified": False,
                "similarity_score": 0.0,
                "document_face_count": doc_face_count,
                "selfie_face_count": selfie_face_count,
                "liveness_checked": True,
                "is_real": False,
                "anti_spoof_score": liveness_data.get("anti_spoof_score", 0.0)
            },
            errors=["Liveness check failed: possible spoof detected"]
        )

    # ---- Step 3: DeepFace se dono faces compare karo ----
    try:
        result = DeepFace.verify(
            img1_path=document_path,
            img2_path=selfie_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False
        )
    except Exception as e:
        errors.append(f"Face comparison failed: {str(e)}")
        return _build_response(
            status="error",
            data={
                "verified": False,
                "similarity_score": 0.0,
                "document_face_count": doc_face_count,
                "selfie_face_count": selfie_face_count
            },
            errors=errors
        )

    # DeepFace "distance" deta hai (0 = identical faces, bada number = alag).
    # Hum ise ek 0-1 ke "similarity_score" mein convert karte hain.
    distance = result.get("distance", 1.0)
    threshold = result.get("threshold", 0.4)

    # Simple normalization: agar distance threshold ke bilkul barabar hai,
    # similarity_score ~0.5 aayega. Isse kam distance -> zyada similarity.
    similarity_score = round(max(0.0, min(1.0, 1 - (distance / (threshold * 2)))), 4)

    verified = bool(result.get("verified", False))

    return _build_response(
        status="success",
        data={
            "verified": verified,
            "similarity_score": similarity_score,
            "document_face_count": doc_face_count,
            "selfie_face_count": selfie_face_count,
            "liveness_checked": True,
            "is_real": liveness_data.get("is_real", False),
            "anti_spoof_score": liveness_data.get("anti_spoof_score", 0.0)
        },
        errors=errors   # note: multiple-face warnings yahan bhi aa sakti hain, error nahi hai zaroori
    )


# -----------------------------------------------------------------------
# LIVENESS PLACEHOLDER (Part 8 ke according — abhi optional/future work)
# -----------------------------------------------------------------------
def check_liveness(selfie_path):
    """
    Check whether the selfie appears to come from a real face
    using DeepFace anti-spoofing.
    """

    if not os.path.exists(selfie_path):
        return _build_response(
            status="error",
            data={
                "liveness_checked": False,
                "is_real": False,
                "anti_spoof_score": 0.0
            },
            errors=[f"Selfie image not found: {selfie_path}"]
        )

    try:
        faces = DeepFace.extract_faces(
            img_path=selfie_path,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            anti_spoofing=True
        )

        if len(faces) != 1:
            return _build_response(
                status="error",
                data={
                    "liveness_checked": False,
                    "is_real": False,
                    "anti_spoof_score": 0.0,
                    "face_count": len(faces)
                },
                errors=[f"Expected exactly 1 face, found {len(faces)}."]
            )

        face = faces[0]

        is_real = bool(face.get("is_real", False))
        anti_spoof_score = float(face.get("antispoof_score", 0.0))

        return _build_response(
            status="success",
            data={
                "liveness_checked": True,
                "is_real": is_real,
                "anti_spoof_score": round(anti_spoof_score, 4),
                "face_count": 1
            },
            errors=[]
        )

    except Exception as e:
        return _build_response(
            status="error",
            data={
                "liveness_checked": False,
                "is_real": False,
                "anti_spoof_score": 0.0
            },
            errors=[f"Liveness check failed: {str(e)}"]
        )


# -----------------------------------------------------------------------
# QUICK TEST BLOCK — isko seedha "python face_module.py" se chala sakte ho
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # YAHAN APNI TEST IMAGES KA PATH DAALO:
    test_document_image = "sample_document.jpg"
    test_selfie_image = "sample_selfie.jpg"

    print("Testing verify_faces() [DeepFace version]...")
    print("-" * 50)

    result = verify_faces(test_document_image, test_selfie_image)
    print(json.dumps(result, indent=2))

    print("-" * 50)
    print("Agar 'File not found' error dikh raha hai, to upar wale")
    print("test_document_image aur test_selfie_image paths ko apni")
    print("actual image files ke path se replace karo.") 