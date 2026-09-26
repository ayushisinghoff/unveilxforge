import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "tampering_model.pth"

labels = ["GENUINE", "TAMPERED"]

# Load model
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])


def detect_tampering(file):
    image = Image.open(file).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)
        probability = torch.softmax(output, dim=1)
        confidence, prediction = torch.max(probability, 1)

    result = labels[prediction.item()]
    confidence = round(confidence.item() * 100, 2)

    if result == "TAMPERED":
        risk_level = "HIGH"
    else:
        risk_level = "LOW"

    return {
        "result": result,
        "confidence": confidence,
        "risk_level": risk_level
    }


def cross_document_check(documents):
    fields = ["name", "dob", "nationality"]

    results = {}
    mismatches = 0

    for field in fields:

        values = []

        for doc in documents:
            value = str(doc.get(field) or "").strip().lower()

            if value:
                values.append(value)

        if len(values) == 0:
            results[field] = "NOT_AVAILABLE"

        elif len(values) < len(documents):
            results[field] = "NOT_AVAILABLE"

        elif len(set(values)) == 1:
            results[field] = "MATCH"

        else:
            results[field] = "MISMATCH"
            mismatches += 1

    risk_score = min(mismatches * 20, 100)

    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "field_results": results,
        "risk_score": risk_score,
        "risk_level": risk_level
    }

def screen_document(file, documents=None):
    tampering = detect_tampering(file)

    result = {
        "tampering": tampering["result"],
        "tampering_confidence": tampering["confidence"],
        "tampering_risk": tampering["risk_level"]
    }

    if documents:
        cross_check = cross_document_check(documents)

        result["cross_document"] = cross_check
        result["overall_risk"] = (
            "HIGH"
            if tampering["result"] == "TAMPERED"
            or cross_check["risk_level"] == "HIGH"
            else cross_check["risk_level"]
        )
    else:
        result["overall_risk"] = tampering["risk_level"]

    return result


