"""Lädt die Shopify-Produktfotos der Rähmchen und Mittelwände aus einem Produktexport.

    python3 amazon/fotos_laden.py products_export.csv

Speichert jedes Bild als amazon/fotos/shopify/<handle>-<position>.jpg und eine
freigestellte Fassung (weißer Hintergrund -> transparent) als .png daneben.
Danach das passende Bild nach amazon/fotos/<schlüssel>.png kopieren
(Schlüssel siehe amazon/fotos/README.md) und generate.py neu starten.
"""

import csv
import re
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ZIEL = Path(__file__).resolve().parent / "fotos" / "shopify"
MUSTER = re.compile(r"r[aä]hm|mittelw", re.I)


def freistellen(im, toleranz=18):
    """Weißen Hintergrund vom Rand her transparent machen (Flood-Fill)."""
    rgb = im.convert("RGB")
    marke = (255, 0, 255)
    w, h = rgb.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if min(rgb.getpixel(seed)) >= 255 - toleranz * 2:
            ImageDraw.floodfill(rgb, seed, marke, thresh=toleranz)
    maske = Image.eval(rgb.convert("RGB").split()[0], lambda _: 255)
    px_rgb = rgb.load()
    px_m = maske.load()
    for y in range(h):
        for x in range(w):
            if px_rgb[x, y] == marke:
                px_m[x, y] = 0
    maske = maske.filter(ImageFilter.GaussianBlur(1))
    out = im.convert("RGBA")
    out.putalpha(maske)
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ZIEL.mkdir(parents=True, exist_ok=True)
    titel = {}
    for row in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")):
        if row["Title"]:
            titel[row["Handle"]] = row["Title"]
        if not row["Image Src"] or not MUSTER.search(row["Handle"] + " " + titel.get(row["Handle"], "")):
            continue
        name = f"{row['Handle']}-{row['Image Position']}"
        jpg = ZIEL / f"{name}.jpg"
        if not jpg.exists():
            try:
                with urllib.request.urlopen(row["Image Src"], timeout=30) as r:
                    data = r.read()
            except OSError as e:
                print(f"FEHLER {name}: {e}")
                continue
            Image.open(BytesIO(data)).convert("RGB").save(jpg, quality=95)
        freistellen(Image.open(jpg)).save(ZIEL / f"{name}.png")
        print(f"ok     {name}")


if __name__ == "__main__":
    main()
