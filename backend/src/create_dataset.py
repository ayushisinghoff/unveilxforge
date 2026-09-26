from PIL import Image, ImageFilter, ImageEnhance
import os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASES = {
    "passport": "passport_base.png",
    "visa": "visa_base.png",
    "national_id": "national_id_base.png",
    "driving_license": "driving_license_base.png"
}

N = 100

for doc, base in BASES.items():
    img = Image.open(os.path.join(ROOT, base)).convert("RGB")

    for kind in ["genuine", "tampered"]:
        os.makedirs(os.path.join(ROOT, "dataset", doc, kind), exist_ok=True)

    for i in range(N):
        g = img.rotate(random.uniform(-2, 2), expand=True)
        g = ImageEnhance.Brightness(g).enhance(random.uniform(.95, 1.05))
        g.save(os.path.join(ROOT, "dataset", doc, "genuine",
                            f"{doc}_genuine_{i:03}.png"))

        t = img.rotate(random.uniform(-2, 2), expand=True)
        t = t.filter(ImageFilter.GaussianBlur(random.uniform(.4, 1.2)))
        t = ImageEnhance.Contrast(t).enhance(random.uniform(.7, .9))
        t.save(os.path.join(ROOT, "dataset", doc, "tampered",
                            f"{doc}_tampered_{i:03}.png"))

print("New dataset created!")