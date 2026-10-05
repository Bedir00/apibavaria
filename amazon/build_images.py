"""Erzeugt Amazon-Bilder (Hauptbild + USP-Bild) aus den Shopify-Produktfotos.

    pip install Pillow numpy rembg onnxruntime
    python3 amazon/build_images.py            # alle Listings
    python3 amazon/build_images.py --only bundle-dnm-10-raehmchen-10-mittelwaende

Quelle der Fotos: amazon/shop_export.json (Export der aktiven Produkte aus Shopify).
Eigene, bessere Fotos: als amazon/src_override/<handle>__<bildindex>.jpg|png ablegen,
sie haben Vorrang vor dem Shopify-Foto.

Hauptbild (MAIN): 2000 × 2000 px, reines Weiß (255/255/255), Produkt füllt 88 %
der Bildkante, kein Text, keine Grafiken. Menge und Bundle werden nur über die
abgebildeten Artikel gezeigt.
USP-Bild (PT01): CI-Farben und Poppins, Mengen-/Set-Kachel, Vorteile, Passt-zu.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from listings import LISTINGS  # noqa: E402

ROOT = Path(__file__).parent
CACHE = ROOT / ".cache"
OVERRIDE = Path(os.environ.get("AMAZON_SRC_OVERRIDE", ROOT / "src_override"))
OUT = ROOT / "output"
FONTS = ROOT / "fonts"

SIZE = 2000
FILL = 0.88  # längste Produktkante im Hauptbild, Amazon verlangt mindestens 85 %
PX_PER_MM = 4.0

# CI aus dem Live-Theme (color_palette + PDP-Flächen)
GREEN_DARK = (63, 74, 31)  # #3f4a1f
GREEN = (107, 125, 50)  # #6b7d32
LINE = (216, 223, 189)  # #d8dfbd
SURFACE = (245, 247, 236)  # #f5f7ec
SAGE = (231, 236, 212)  # #e7ecd4
WHITE = (255, 255, 255)


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"Poppins-{weight}.ttf"), size)


# ------------------------------------------------------------------ Quellen

def load_products():
    data = json.loads((ROOT / "shop_export.json").read_text())
    return {p["handle"]: p for p in data}


def source_path(product, index):
    for ext in ("png", "jpg", "jpeg", "webp"):
        own = OVERRIDE / f"{product['handle']}__{index}.{ext}"
        if own.exists():
            return own
    images = product["images"]
    if not images:
        raise LookupError(f"{product['handle']}: kein Produktfoto in Shopify")
    url = images[min(index, len(images) - 1)]["url"]
    ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
    target = CACHE / "src" / f"{product['handle']}__{index}.{ext}"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, target)
    return target


_session = None


def cutout(path):
    """Freigestelltes Produkt als RGBA, auf den Inhalt beschnitten (gecacht)."""
    global _session
    target = CACHE / "cut" / (path.stem + ".png")
    if not target.exists():
        from rembg import new_session, remove

        if _session is None:
            _session = new_session("isnet-general-use")
        target.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(path).convert("RGB")
        remove(img, session=_session, post_process_mask=True).save(target)
    img = Image.open(target).convert("RGBA")
    alpha = np.array(img.getchannel("A"))
    alpha[alpha < 12] = 0  # Restschleier der Maske entfernen
    img.putalpha(Image.fromarray(alpha))
    return img.crop(img.getbbox())


# --------------------------------------------------------------- Anordnung

def scaled(cut, width_mm):
    w = int(width_mm * PX_PER_MM)
    h = round(cut.height * w / cut.width)
    return cut.resize((w, h), Image.LANCZOS)


def layer_shadow(item):
    """Weicher Schatten, damit die Kanten gestapelter Artikel zählbar bleiben."""
    a = item.getchannel("A").point(lambda v: int(v * 0.22))
    shadow = Image.new("RGBA", item.size, (40, 45, 20, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(10)))
    return shadow


def place(items):
    """items: Liste (bild, x, y) von hinten nach vorne -> RGBA, beschnitten."""
    xs = [x for _, x, _ in items] + [x + im.width for im, x, _ in items]
    ys = [y for _, _, y in items] + [y + im.height for im, _, y in items]
    pad = 40
    ox, oy = -min(xs) + pad, -min(ys) + pad
    canvas = Image.new("RGBA", (int(max(xs) - min(xs)) + 2 * pad, int(max(ys) - min(ys)) + 2 * pad))
    for im, x, y in items:
        sh = layer_shadow(im)
        canvas.alpha_composite(sh, (int(x + ox + 6), int(y + oy + 10)))
        canvas.alpha_composite(im, (int(x + ox), int(y + oy)))
    return canvas.crop(canvas.getbbox())


def fan(item, n):
    """n gleiche Artikel als Stapel nach hinten oben versetzt, jede Kante sichtbar."""
    if n > 20:  # große Mengen: Stapel à 10 nebeneinander
        stacks = [fan(item, 10) for _ in range(n // 10)]
        cols = 3 if len(stacks) > 4 else 2
        st = stacks[0]
        items = []
        for i, s in enumerate(stacks):
            r, c = divmod(i, cols)
            items.append((s, c * st.width * 0.78 + r * st.width * 0.12, -r * st.height * 0.55 + c * st.height * 0.04))
        items.sort(key=lambda t: t[2])  # hintere Reihe zuerst
        return place(items)
    spread_x = item.width * (0.16 if n <= 10 else 0.22)
    spread_y = item.height * (0.42 if n <= 10 else 0.55)
    step_x, step_y = spread_x / max(n - 1, 1), spread_y / max(n - 1, 1)
    return place([(item, i * step_x, -i * step_y) for i in range(n - 1, -1, -1)])


def grid(item, n):
    cols = {12: 4, 6: 3, 10: 5}.get(n, 4)
    rows = -(-n // cols)
    items = []
    for r in range(rows):  # r = 0 ist die hinterste Reihe
        for c in range(cols):
            if r * cols + c >= n:
                break
            back = rows - 1 - r
            x = c * item.width * 0.94 + (back % 2) * item.width * 0.47
            y = -back * item.height * 0.34
            items.append((item, x, y))
    return place(items)


def row(item, n):
    return place([(item, i * item.width * 0.74, (i % 2) * item.height * 0.04) for i in range(n)])


def build_part(products, p):
    cut = scaled(cutout(source_path(products[p["handle"]], p["image"])), p["width_mm"])
    n = p.get("copies", 1)
    layout = p.get("layout", "single")
    if n == 1 or layout == "single":
        return cut
    return {"fan": fan, "grid": grid, "row": row}[layout](cut, n)


def compose(products, listing):
    groups = [build_part(products, p) for p in listing["parts"]]
    if len(groups) == 1:
        return groups[0]
    g0 = groups[0]
    items = [(g0, 0, 0)]
    rest = list(zip(listing["parts"][1:], groups[1:]))
    stacks = [g for p, g in rest if p.get("layout") != "single"]
    accessories = [g for p, g in rest if p.get("layout") == "single"]
    for i, g in enumerate(stacks, 1):  # weitere Stapel rechts vorne
        items.append((g, g0.width * 0.42 * i, g0.height * 0.40 * i))
    for g in accessories:  # Zubehör (z. B. Trafolöter) vorne links unten
        bottom = max(y + im.height for im, _, y in items)
        items.append((g, g0.width * 0.02, bottom - g.height * 0.85))
    return place(items)


# ------------------------------------------------------------- Hauptbild

def main_image(product):
    canvas = Image.new("RGB", (SIZE, SIZE), WHITE)
    scale = FILL * SIZE / max(product.size)
    prod = product.resize((round(product.width * scale), round(product.height * scale)), Image.LANCZOS)
    layer = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    layer.alpha_composite(prod, ((SIZE - prod.width) // 2, (SIZE - prod.height) // 2))
    canvas.paste(layer, mask=layer.getchannel("A"))
    # alles außerhalb des Produkts exakt RGB 255/255/255
    arr = np.array(canvas)
    arr[np.array(layer.getchannel("A")) < 3] = 255
    return Image.fromarray(arr)


def check_main(img):
    arr = np.array(img.convert("RGB")).astype(int)
    nonwhite = (arr < 250).any(axis=2)
    ys, xs = np.where(nonwhite)
    border = np.concatenate([arr[:8].reshape(-1, 3), arr[-8:].reshape(-1, 3),
                             arr[:, :8].reshape(-1, 3), arr[:, -8:].reshape(-1, 3)])
    fill = max(xs.max() - xs.min(), ys.max() - ys.min()) / SIZE
    return {
        "size": img.size,
        "border_pure_white": bool((border == 255).all()),
        "fill": round(float(fill), 3),
        "ok": bool((border == 255).all() and fill >= 0.85 and img.size == (SIZE, SIZE)),
    }


# --------------------------------------------------------------- USP-Bild

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=fnt) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def check_icon(draw, x, y, s):
    draw.rectangle([x, y, x + s, y + s], fill=GREEN)
    draw.line([(x + s * 0.24, y + s * 0.52), (x + s * 0.43, y + s * 0.70), (x + s * 0.78, y + s * 0.30)],
              fill=WHITE, width=max(4, s // 9), joint="curve")


def plus_icon(draw, x, y, s):
    draw.rectangle([x, y, x + s, y + s], outline=GREEN, width=5)
    m, k = s / 2, s * 0.26
    draw.line([(x + m, y + k), (x + m, y + s - k)], fill=GREEN, width=6)
    draw.line([(x + k, y + m), (x + s - k, y + m)], fill=GREEN, width=6)


def usp_image(product_img, listing, product):
    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    d = ImageDraw.Draw(img)
    pad = 90
    bar_h = 300

    # Kopfleiste: Marke + Titel, rechts Mengen-/Set-Kachel
    d.rectangle([0, 0, SIZE, bar_h], fill=GREEN_DARK)
    badge = listing.get("badge")
    title_w = SIZE - 2 * pad - (bar_h if badge else 0)
    d.text((pad, 62), "API BAVARIA · IMKEREIBEDARF", font=font("Medium", 34), fill=LINE)
    size = 76
    while d.textlength(listing["title"], font=font("SemiBold", size)) > title_w and size > 48:
        size -= 2
    tfont = font("SemiBold", size)
    lines = wrap(d, listing["title"], tfont, title_w)[:2]
    ty = 128 if len(lines) == 1 else 112
    for ln in lines:
        d.text((pad, ty), ln, font=tfont, fill=WHITE)
        ty += size + 6
    if badge:
        x0 = SIZE - bar_h
        d.rectangle([x0, 0, SIZE, bar_h], fill=GREEN)
        num, unit = badge
        nsize = 150 if len(num) <= 2 else (118 if len(num) <= 3 else 96)
        nf = font("Bold", nsize)
        nw = d.textlength(num, font=nf)
        d.text((x0 + (bar_h - nw) / 2, 150 - nsize * 0.62), num, font=nf, fill=WHITE)
        uf = font("SemiBold", 44)
        uw = d.textlength(unit, font=uf)
        d.text((x0 + (bar_h - uw) / 2, 212), unit, font=uf, fill=WHITE)

    # Produktfläche
    top, bottom = bar_h, 1400
    d.rectangle([0, top, SIZE, bottom], fill=SURFACE)
    d.line([(0, bottom), (SIZE, bottom)], fill=LINE, width=4)
    box_w, box_h = SIZE - 2 * pad, bottom - top - 150
    s = min(box_w / product_img.width, box_h / product_img.height)
    prod = product_img.resize((round(product_img.width * s), round(product_img.height * s)), Image.LANCZOS)
    img.paste(prod, ((SIZE - prod.width) // 2, top + 110 + (box_h - prod.height) // 2), prod)

    systems = product.get("beutensysteme") or []
    if systems:
        chip = "PASST ZU: " + " · ".join(systems).upper()
        cf = font("SemiBold", 36)
        cw = d.textlength(chip, font=cf)
        d.rectangle([pad, top + 40, pad + cw + 56, top + 112], fill=WHITE, outline=GREEN, width=3)
        d.text((pad + 28, top + 52), chip, font=cf, fill=GREEN_DARK)

    # Vorteile / Lieferumfang
    rows = []
    for c in listing.get("contents", []):
        rows.append(("plus", c))
    usps = listing.get("usps") or product.get("vorteile") or []
    for u in usps:
        if len(rows) >= 4:
            break
        rows.append(("check", u))
    rf = font("Medium", 46)
    if listing["kind"] == "bundle":
        y = bottom + 60
        d.text((pad, y), "IM SET ENTHALTEN", font=font("SemiBold", 34), fill=GREEN)
        y += 70
        for kind, text in rows:
            (plus_icon if kind == "plus" else check_icon)(d, pad, y + 4, 60)
            d.text((pad + 96, y), text, font=rf, fill=GREEN_DARK)
            y += 112
    else:
        col_w = (SIZE - 2 * pad - 60) / 2
        for i, (_, text) in enumerate(rows[:4]):
            cx = pad + (i % 2) * (col_w + 60)
            cy = bottom + 90 + (i // 2) * 250
            check_icon(d, cx, cy + 6, 66)
            for j, ln in enumerate(wrap(d, text, rf, col_w - 100)[:2]):
                d.text((cx + 100, cy + j * 64), ln, font=rf, fill=GREEN_DARK)
    return img


# ------------------------------------------------------------------- Ablauf

def save_jpg(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=95, subsampling=0, optimize=True)


def overview(results):
    mains = [Image.open(r["main"]) for r in results if r.get("main")]
    if not mains:
        return
    cols, t = 6, 400
    rows_n = -(-len(mains) // cols)
    sheet = Image.new("RGB", (cols * (t + 20) + 20, rows_n * (t + 20) + 20), SAGE)
    for i, im in enumerate(mains):
        r, c = divmod(i, cols)
        sheet.paste(im.resize((t, t), Image.LANCZOS), (20 + c * (t + 20), 20 + r * (t + 20)))
    save_jpg(sheet, OUT / "uebersicht-hauptbilder.jpg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    products = load_products()
    results = []
    for listing in LISTINGS:
        if args.only and listing["key"] not in args.only:
            continue
        key = listing["key"]
        try:
            comp = compose(products, listing)
        except Exception as e:  # fehlendes Foto o. ä.: weitermachen, im Bericht vermerken
            print(f"FEHLER {key}: {e}")
            results.append({"key": key, "error": str(e)})
            continue
        main_img = main_image(comp)
        report = check_main(main_img)
        first = products[listing["parts"][0]["handle"]]
        report["source_px"] = min(max(Image.open(source_path(products[p["handle"]], p["image"])).size)
                                  for p in listing["parts"])
        save_jpg(main_img, OUT / key / f"{key}.MAIN.jpg")
        save_jpg(usp_image(comp, listing, first), OUT / key / f"{key}.PT01.jpg")
        results.append({"key": key, "main": str(OUT / key / f"{key}.MAIN.jpg"), **report})
        flag = "ok" if report["ok"] and report["source_px"] >= 1000 else "PRÜFEN"
        print(f"{flag:6} {key}  fill={report['fill']}  quelle={report['source_px']}px")
    if not args.only:
        overview(results)
        (OUT / "pruefbericht.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
