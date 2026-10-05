"""Erzeugt Amazon-Produktbilder für Rähmchen und Mittelwände in der API-Bavaria-CI.

    python3 amazon/generate.py                 # alle Angebote
    python3 amazon/generate.py --sku 2K-IJ79-Y9PS ZAH-HM-30

Ausgabe in amazon/output/:
    upload/   fertige Bilder (Hauptbild nur, wenn echte Fotos vorliegen)
    vorschau/ Hauptbilder mit gezeichnetem Produkt – NICHT hochladen,
              Amazon verlangt für das Hauptbild ein echtes Foto
    uebersicht.jpg  Kontaktbogen aller Bilder

Fotos: freigestellte PNGs (transparenter Hintergrund) in amazon/fotos/, Namen
siehe amazon/fotos/README.md. Fehlt ein Foto, wird das Produkt gezeichnet.
"""

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from listings import LISTINGS, SYSTEME

ROOT = Path(__file__).resolve().parent
FOTOS = ROOT / "fotos"
FONTS = ROOT / "fonts"

SIZE = 2000
SS = 3  # Supersampling für Zeichnungen und Icons

# CI (siehe README im Repo-Root)
WHITE = (255, 255, 255)
OLIVE = (63, 74, 31)      # #3f4a1f
GREEN = (107, 125, 50)    # #6b7d32
LINE = (216, 223, 189)    # #d8dfbd
MIST = (245, 247, 236)    # #f5f7ec
SAGE = (231, 236, 212)    # #e7ecd4
SAGE_DARK = (198, 210, 157)  # #c6d29d

# Material
WOOD = (228, 203, 152)
WOOD_EDGE = (172, 138, 82)
WOOD_GRAIN = (206, 176, 120)
BRASS = (196, 156, 62)
WIRE = (150, 156, 160)
WAX = (240, 200, 98)
WAX_DARK = (214, 165, 60)
WAX_LIGHT = (250, 222, 140)


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"work-sans-latin-{weight}-normal.woff"), size)


# ---------------------------------------------------------------- Fotos

def foto(key):
    path = FOTOS / f"{key}.png"
    if not path.exists():
        return None
    im = Image.open(path).convert("RGBA")
    bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(bbox) if bbox else im


def fit(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


# ---------------------------------------------------------------- Zeichnungen

def _hex_cells(d, x0, y0, x1, y1, cell, fill_dark, fill_light):
    """Wabenprägung: versetzte Sechsecke im Rechteck."""
    r = cell / 2
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    row = 0
    y = y0 - r
    while y < y1 + r:
        x = x0 - dx + (dx / 2 if row % 2 else 0)
        while x < x1 + dx:
            pts = [(x + r * 0.92 * math.cos(math.radians(60 * k + 30)), y + r * 0.92 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            d.polygon(pts, fill=fill_light, outline=fill_dark, width=max(1, round(cell * 0.09)))
            x += dx
        y += dy
        row += 1


def zeichne_mittelwand(w_mm, h_mm, width):
    """Mittelwand frontal, width in Pixeln."""
    W = width * SS
    H = round(W * h_mm / w_mm)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], fill=WAX)
    _hex_cells(d, 0, 0, W, H, cell=W / 34, fill_dark=WAX_DARK, fill_light=WAX_LIGHT)
    # Kante und Licht
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle([0, 0, W - 1, H - 1], fill=255)
    im.putalpha(mask)
    d.rectangle([0, 0, W - 1, H - 1], outline=WAX_DARK, width=max(2, W // 300))
    return im.resize((width, max(1, round(H / SS))), Image.LANCZOS)


def zeichne_rahmen(sys_key, width, mit_mittelwand=False):
    """Rähmchen frontal mit Ohren, Drähten und Ösen. width = Länge Oberträger in Pixeln."""
    w_mm, h_mm = SYSTEME[sys_key]["rahmen"]
    draehte = SYSTEME[sys_key]["draehte"]
    W = width * SS
    k = W / w_mm  # px pro mm
    H = round(h_mm * k)
    body_w = round(w_mm * 0.92 * k)
    bx0 = (W - body_w) // 2
    bx1 = bx0 + body_w
    top = round(19 * k)
    side = round(12 * k)
    bottom = round(10 * k)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(2, round(0.8 * k))

    if mit_mittelwand:
        mw = zeichne_mittelwand(body_w - 2 * side, H - top - bottom - round(4 * k), (body_w - 2 * side) // SS)
        mw = mw.resize((body_w - 2 * side, H - top - bottom - round(4 * k)), Image.LANCZOS)
        im.alpha_composite(mw, (bx0 + side, top))

    def holz(box):
        d.rectangle(box, fill=WOOD, outline=WOOD_EDGE, width=lw)
        x0, y0, x1, y1 = box
        horizontal = (x1 - x0) > (y1 - y0)
        n = 3
        for i in range(1, n + 1):
            if horizontal:
                y = y0 + (y1 - y0) * i / (n + 1)
                d.line([(x0 + lw * 3, y), (x1 - lw * 3, y + (i - 2) * k * 0.6)], fill=WOOD_GRAIN, width=max(1, lw // 2))
            else:
                x = x0 + (x1 - x0) * i / (n + 1)
                d.line([(x, y0 + lw * 3), (x, y1 - lw * 3)], fill=WOOD_GRAIN, width=max(1, lw // 2))

    # Drähte (bei eingebauter Mittelwand nur angedeutet)
    inner_top = top
    inner_bottom = H - bottom
    wire_ys = [inner_top + (inner_bottom - inner_top) * (i + 1) / (draehte + 1) for i in range(draehte)]
    wire_col = (205, 170, 85) if mit_mittelwand else WIRE
    for y in wire_ys:
        d.line([(bx0 + side, y), (bx1 - side, y)], fill=wire_col, width=max(2, round(0.7 * k)))

    holz((bx0, 0, bx0 + side, H - 1))
    holz((bx1 - side, 0, bx1, H - 1))
    holz((bx0, H - bottom, bx1, H - 1))
    # Oberträger mit Ohren
    ear_h = round(top * 0.6)
    holz((0, 0, W - 1, ear_h))
    holz((bx0, 0, bx1, top))
    # Ösen
    r = max(3, round(2.4 * k))
    for y in wire_ys:
        for cx in (bx0 + side / 2, bx1 - side / 2):
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=BRASS, outline=(150, 115, 40), width=max(1, lw // 2))
    return im.resize((width, max(1, round(H / SS))), Image.LANCZOS)


def ist_gezeichnet(listing):
    return any(foto(k) is None for k in foto_keys(listing))


def foto_keys(listing):
    s = listing["system"]
    art = listing["art"]
    if art == "raehmchen":
        return [f"raehmchen-{s}"]
    if art == "eingebaut":
        return [f"raehmchen-{s}-mittelwand"]
    if art == "set":
        return [f"raehmchen-{s}", f"mittelwand-{s}"]
    return [f"mittelwand-{s}"]


def einzelteil(listing, teil, width):
    """Ein einzelnes Rähmchen / eine Mittelwand als RGBA, Foto vor Zeichnung."""
    s = listing["system"]
    if teil == "mittelwand":
        im = foto(f"mittelwand-{s}")
        if im is not None:
            return fit(im, width, width * 4)
        w, h = SYSTEME[s]["mw"]
        return zeichne_mittelwand(w, h, width)
    eingebaut = teil == "eingebaut"
    im = foto(f"raehmchen-{s}-mittelwand" if eingebaut else f"raehmchen-{s}")
    if im is not None:
        return fit(im, width, width * 4)
    return zeichne_rahmen(s, width, mit_mittelwand=eingebaut)


# ---------------------------------------------------------------- Anordnungen

def raster(item, n, gap_ratio=0.07, target=1.0):
    """n gleiche Teile im Raster, Seitenverhältnis möglichst nah an target."""
    gap = round(item.width * gap_ratio)
    best = None
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        if cols * rows - n >= cols:
            continue
        w = cols * item.width + (cols - 1) * gap
        h = rows * item.height + (rows - 1) * gap
        score = abs(math.log((w / h) / target)) + (cols * rows - n) * 0.6
        if best is None or score < best[0]:
            best = (score, cols, rows, w, h)
    _, cols, rows, w, h = best
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n):
        r, c = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        off = (cols - in_row) * (item.width + gap) // 2  # letzte Reihe zentrieren
        out.alpha_composite(item, (off + c * (item.width + gap), r * (item.height + gap)))
    return out


def faecher(item, n, dx_ratio=0.05, dy_ratio=0.07):
    """n undurchsichtige Teile versetzt gestapelt, vorderstes vollständig sichtbar."""
    dx = max(2, round(item.width * dx_ratio))
    dy = max(2, round(item.height * dy_ratio))
    w = item.width + (n - 1) * dx
    h = item.height + (n - 1) * dy
    out = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    shadow = Image.new("RGBA", item.size, (40, 30, 10, 0))
    shadow.putalpha(item.getchannel("A").point(lambda a: a * 0.22))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(2, item.width // 160)))
    for i in range(n):  # i = 0 ist ganz hinten
        x = (n - 1 - i) * dx
        y = i * dy
        depth = (n - 1 - i) / max(1, n - 1)
        layer = item
        if depth > 0:
            rgb = ImageEnhance.Brightness(item.convert("RGB")).enhance(1 - 0.10 * depth)
            layer = rgb.convert("RGBA")
            layer.putalpha(item.getchannel("A"))
        out.alpha_composite(shadow, (x + 4, y + 4))
        out.alpha_composite(layer, (x, y))
    return out.crop(out.getchannel("A").getbbox())


def neben(a, b, gap, align="center"):
    w = a.width + gap + b.width
    h = max(a.height, b.height)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ya = (h - a.height) // 2
    yb = (h - b.height) // 2 if align == "center" else h - b.height
    out.alpha_composite(a, (0, ya))
    out.alpha_composite(b, (a.width + gap, yb))
    return out


def komposition(listing, target=1.0):
    """Alles, was im Paket ist – für Hauptbild und Mengenbild."""
    art = listing["art"]
    if art == "raehmchen":
        teil = einzelteil(listing, "rahmen", 700)
        return raster(teil, listing["anzahl"], target=target)
    if art == "eingebaut":
        teil = einzelteil(listing, "eingebaut", 1100)
        return faecher(teil, listing["anzahl"])
    if art == "mittelwand":
        teil = einzelteil(listing, "mittelwand", 1100)
        n = listing["anzahl"]
        return faecher(teil, n, dx_ratio=0.5 / n, dy_ratio=0.6 / n)
    if art == "mittelwand_kg":
        teil = einzelteil(listing, "mittelwand", 1100)
        n = 14 * listing["kg"]
        return faecher(teil, n, dx_ratio=0.12 / n * listing["kg"], dy_ratio=0.16 / n * listing["kg"])
    if art == "set":
        rahmen = raster(einzelteil(listing, "rahmen", 600), listing["anzahl"], target=max(0.6, target * 0.55))
        n = listing["anzahl"]
        mw = faecher(einzelteil(listing, "mittelwand", 1100), n, dx_ratio=0.5 / n, dy_ratio=0.6 / n)
        mw = fit(mw, rahmen.width * 1.05, rahmen.height)
        return neben(rahmen, mw, round(rahmen.width * 0.1))
    raise ValueError(art)


# ---------------------------------------------------------------- Icons (Linienstil der CI)

def icon(name, size, color=OLIVE):
    S = size * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = round(S * 0.055)
    m = S * 0.16

    def hexagon(cx, cy, r):
        return [(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(7)]

    if name == "wabe":
        r = S * 0.17
        for cx, cy in [(S / 2, S * 0.33), (S / 2 - r * 0.88, S * 0.33 + r * 1.5), (S / 2 + r * 0.88, S * 0.33 + r * 1.5)]:
            d.line(hexagon(cx, cy, r), fill=color, width=w, joint="curve")
    elif name == "blatt":
        leaf = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ld = ImageDraw.Draw(leaf)
        ld.ellipse([S * 0.3, S * 0.1, S * 0.7, S * 0.9], outline=color, width=w)
        ld.line([(S * 0.5, S * 0.18), (S * 0.5, S * 0.98)], fill=color, width=w)
        for yy in (0.4, 0.58):
            ld.line([(S * 0.5, S * (yy + 0.1)), (S * 0.62, S * yy)], fill=color, width=w // 2 + 1)
            ld.line([(S * 0.5, S * (yy + 0.1)), (S * 0.38, S * yy)], fill=color, width=w // 2 + 1)
        im.alpha_composite(leaf.rotate(-40, resample=Image.BICUBIC))
    elif name == "berge":
        d.line([(m, S - m), (S * 0.4, S * 0.3), (S * 0.56, S * 0.52), (S * 0.68, S * 0.4), (S - m, S - m), (m, S - m)], fill=color, width=w, joint="curve")
        d.ellipse([S * 0.66, m * 0.8, S * 0.82, m * 0.8 + S * 0.16], outline=color, width=w)
    elif name == "mass":
        d.rectangle([m, S * 0.38, S - m, S * 0.62], outline=color, width=w)
        for i in range(1, 8):
            x = m + (S - 2 * m) * i / 8
            d.line([(x, S * 0.38), (x, S * 0.38 + (S * 0.12 if i % 2 else S * 0.07))], fill=color, width=w // 2 + 1)
    elif name == "holz":
        d.rectangle([m, S * 0.3, S - m, S * 0.7], outline=color, width=w)
        d.ellipse([S - m - S * 0.16, S * 0.3, S - m + S * 0.0, S * 0.7], outline=color, width=w)
        for y in (0.42, 0.55):
            d.line([(m + S * 0.06, S * y), (S * 0.62, S * y)], fill=color, width=w // 2 + 1)
    elif name == "draht":
        d.rectangle([m, m, S - m, S - m], outline=color, width=w)
        for i in range(1, 4):
            y = m + (S - 2 * m) * i / 4
            d.line([(m, y), (S - m, y)], fill=color, width=w // 2 + 1)
            for x in (m, S - m):
                d.ellipse([x - w * 0.9, y - w * 0.9, x + w * 0.9, y + w * 0.9], fill=color)
    elif name == "hoffmann":
        # Seitenteil im Profil: oben breit (Abstandshalter), unten schmal
        pts = [(S * 0.35, m), (S * 0.65, m), (S * 0.65, S * 0.48), (S * 0.57, S * 0.52), (S * 0.57, S - m), (S * 0.43, S - m), (S * 0.43, S * 0.52), (S * 0.35, S * 0.48), (S * 0.35, m)]
        d.line(pts, fill=color, width=w, joint="curve")
        d.line([(m * 0.6, S * 0.3), (S * 0.27, S * 0.3)], fill=color, width=w // 2 + 1)
        d.line([(S * 0.73, S * 0.3), (S - m * 0.6, S * 0.3)], fill=color, width=w // 2 + 1)
    elif name == "paket":
        d.line([(m, S * 0.35), (S / 2, m), (S - m, S * 0.35), (S - m, S * 0.72), (S / 2, S - m), (m, S * 0.72), (m, S * 0.35)], fill=color, width=w, joint="curve")
        d.line([(m, S * 0.35), (S / 2, S * 0.55), (S - m, S * 0.35)], fill=color, width=w, joint="curve")
        d.line([(S / 2, S * 0.55), (S / 2, S - m)], fill=color, width=w)
    elif name == "set":
        d.rectangle([m, m, S * 0.62, S * 0.62], outline=color, width=w)
        d.rectangle([S * 0.38, S * 0.38, S - m, S - m], outline=color, width=w)
        d.line([(S * 0.69, S * 0.5), (S * 0.69, S * 0.74)], fill=color, width=w)
        d.line([(S * 0.57, S * 0.62), (S * 0.81, S * 0.62)], fill=color, width=w)
    elif name == "einhaengen":
        d.line([(m, S * 0.3), (S - m, S * 0.3)], fill=color, width=w)
        d.rectangle([S * 0.24, S * 0.3, S * 0.76, S - m], outline=color, width=w)
        r = S * 0.08
        for cx, cy in [(S * 0.42, S * 0.52), (S * 0.58, S * 0.52), (S * 0.5, S * 0.66), (S * 0.42, S * 0.8), (S * 0.58, S * 0.8)]:
            d.line(hexagon(cx, cy, r), fill=color, width=w // 2 + 1)
    elif name == "temperatur":
        d.rounded_rectangle([S * 0.42, m, S * 0.58, S * 0.66], radius=S * 0.08, outline=color, width=w)
        d.ellipse([S * 0.33, S * 0.6, S * 0.67, S - m * 0.7], outline=color, width=w)
        d.line([(S * 0.5, S * 0.35), (S * 0.5, S * 0.7)], fill=color, width=w)
        for y in (0.25, 0.38, 0.51):
            d.line([(S * 0.62, S * y), (S * 0.74, S * y)], fill=color, width=w // 2 + 1)
    elif name == "check":
        d.rectangle([m, m, S - m, S - m], outline=color, width=w)
        d.line([(S * 0.3, S * 0.52), (S * 0.45, S * 0.66), (S * 0.72, S * 0.36)], fill=color, width=w, joint="curve")
    elif name == "plus":
        d.line([(S / 2, m), (S / 2, S - m)], fill=color, width=w)
        d.line([(m, S / 2), (S - m, S / 2)], fill=color, width=w)
    else:
        raise ValueError(name)
    return im.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- Text

def wrap(d, text, f, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        t = f"{line} {w}".strip()
        if d.textlength(t, font=f) <= max_w or not line:
            line = t
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def text_block(d, xy, text, f, fill, max_w, spacing=1.18, max_lines=3):
    x, y = xy
    lines = wrap(d, text, f, max_w)[:max_lines]
    lh = round(f.size * spacing)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def fit_font(d, text, weight, size, max_w, max_lines, min_size=40):
    while size > min_size:
        f = font(weight, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines and all(d.textlength(ln, font=f) <= max_w for ln in lines):
            return f
        size -= 4
    return font(weight, min_size)


def kopf(img, overline, headline, x=110, y=110, max_w=1780):
    d = ImageDraw.Draw(img)
    f_over = font(600, 40)
    t = overline.upper()
    tx = x
    for ch in t:  # Sperrsatz wie im Theme
        d.text((tx, y), ch, font=f_over, fill=GREEN)
        tx += d.textlength(ch, font=f_over) + 4
    f_head = fit_font(d, headline, 600, 100, max_w, 2)
    return text_block(d, (x, y + 70), headline, f_head, OLIVE, max_w, spacing=1.12, max_lines=2)


def paste_center(img, item, box):
    x0, y0, x1, y1 = box
    item = fit(item, x1 - x0, y1 - y0)
    img.alpha_composite(item, (x0 + (x1 - x0 - item.width) // 2, y0 + (y1 - y0 - item.height) // 2))
    return (x0 + (x1 - x0 - item.width) // 2, y0 + (y1 - y0 - item.height) // 2, item.width, item.height)


# ---------------------------------------------------------------- Bilder

def system_name(listing):
    return SYSTEME[listing["system"]]["name"]


def menge_text(listing):
    if listing["art"] == "mittelwand_kg":
        return f"{listing['kg']} kg"
    return f"{listing['anzahl']}"


def hauptbild(listing):
    img = Image.new("RGBA", (SIZE, SIZE), WHITE + (255,))
    comp = komposition(listing)
    paste_center(img, comp, (100, 100, SIZE - 100, SIZE - 100))  # Produkt füllt ≥ 85 %
    return img


def lieferumfang(listing):
    art = listing["art"]
    sysn = system_name(listing)
    n = listing.get("anzahl")
    if art == "raehmchen":
        return [f"{n} × Rähmchen {sysn}"]
    if art == "eingebaut":
        return [f"{n} × Rähmchen {sysn}", "Mittelwand jeweils fertig eingebaut"]
    if art == "set":
        mw = SYSTEME[listing["system"]]["mw"]
        return [f"{n} × Rähmchen {sysn}", f"{n} × Mittelwand {mw[0]} × {mw[1]} mm"]
    if art == "mittelwand":
        mw = SYSTEME[listing["system"]]["mw"]
        return [f"{n} × Mittelwand {sysn}", f"{mw[0]} × {mw[1]} mm, 100 % Bienenwachs"]
    blatt = listing.get("blatt")
    zusatz = f" (ca. {blatt} Blatt)" if blatt else ""
    return [f"{listing['kg']} kg Mittelwände {sysn}{zusatz}"]


def mengenbild(listing):
    img = Image.new("RGBA", (SIZE, SIZE), MIST + (255,))
    d = ImageDraw.Draw(img)
    art = listing["art"]
    if art == "set":
        over, head = "Set", f"{listing['anzahl']} Rähmchen + {listing['anzahl']} Mittelwände"
    elif art == "eingebaut":
        over, head = "Fertig zum Einhängen", f"{listing['anzahl']} Rähmchen mit eingebauter Mittelwand"
    elif art == "mittelwand_kg":
        over, head = "Lieferumfang", f"{listing['kg']} kg Mittelwände {system_name(listing)}"
    elif art == "mittelwand":
        over, head = "Lieferumfang", f"{listing['anzahl']} Mittelwände {system_name(listing)}"
    else:
        over, head = "Lieferumfang", f"{listing['anzahl']} Rähmchen {system_name(listing)}"
    kopf(img, over, head)

    # Produktfläche
    has_strip = bool(listing.get("varianten") or listing.get("auch_als"))
    panel = (110, 400, SIZE - 110, 1440 if has_strip else 1560)
    d.rectangle(panel, fill=WHITE, outline=LINE, width=4)
    # Mengen-Siegel (eckig, CI) rechts oben, Produkt links daneben
    bw = 330
    bx1, by0 = panel[2] - 40, panel[1] - 60
    bx0 = bx1 - bw
    box = (panel[0] + 70, panel[1] + 70, bx0 - 50, panel[3] - 70)
    comp = komposition(listing, target=(box[2] - box[0]) / (box[3] - box[1]))
    paste_center(img, comp, box)
    d.rectangle([bx0, by0, bx1, by0 + bw], fill=OLIVE)
    if art == "set":
        big, small = f"{listing['anzahl']}+{listing['anzahl']}", "Stück"
    elif art == "mittelwand_kg":
        big, small = f"{listing['kg']} kg", "Bienenwachs"
    else:
        big, small = f"{listing['anzahl']}×", "Stück"
    fb = fit_font(d, big, 700, 150, bw - 50, 1)
    tw = d.textlength(big, font=fb)
    d.text((bx0 + (bw - tw) / 2, by0 + 70), big, font=fb, fill=WHITE)
    fs = font(500, 48)
    tw = d.textlength(small, font=fs)
    d.text((bx0 + (bw - tw) / 2, by0 + 230), small, font=fs, fill=SAGE)

    # Lieferumfang
    y = panel[3] + 50
    f_li = font(500, 50)
    for line in lieferumfang(listing)[:2]:
        img.alpha_composite(icon("check", 56, GREEN), (110, y + 2))
        d.text((190, y), line, font=f_li, fill=OLIVE)
        y += 74

    if listing.get("varianten"):
        variantenleiste(img, listing, y + 20)
    elif listing.get("auch_als"):
        hinweis(img, listing["auch_als"], y + 20)
    return img


def variantenleiste(img, listing, y):
    d = ImageDraw.Draw(img)
    f_lab = font(600, 40)
    d.text((110, y), "ERHÄLTLICH IN", font=f_lab, fill=GREEN)
    vs = listing["varianten"]
    x0, x1 = 110, SIZE - 110
    gap = 20
    bw = (x1 - x0 - gap * (len(vs) - 1)) / len(vs)
    by = y + 64
    f = font(600, 56)
    for i, v in enumerate(vs):
        bx = x0 + i * (bw + gap)
        aktiv = v == listing["anzahl"]
        d.rectangle([bx, by, bx + bw, by + 120], fill=OLIVE if aktiv else WHITE, outline=OLIVE if aktiv else LINE, width=4)
        t = f"{v} Stk."
        tw = d.textlength(t, font=f)
        d.text((bx + (bw - tw) / 2, by + 28), t, font=f, fill=WHITE if aktiv else OLIVE)


def hinweis(img, text, y):
    d = ImageDraw.Draw(img)
    x0, x1 = 110, SIZE - 110
    h = min(SIZE - 90, y + 190) - y
    d.rectangle([x0, y, x1, y + h], fill=SAGE, outline=SAGE_DARK, width=4)
    img.alpha_composite(icon("set", 96, OLIVE), (x0 + 40, y + (h - 96) // 2))
    f = fit_font(d, text, 600, 54, x1 - x0 - 220, 2, min_size=40)
    lines = wrap(d, text, f, x1 - x0 - 220)[:2]
    lh = round(f.size * 1.18)
    ty = y + (h - lh * len(lines)) / 2
    for ln in lines:
        d.text((x0 + 170, ty), ln, font=f, fill=OLIVE)
        ty += lh


def uspbild(listing):
    img = Image.new("RGBA", (SIZE, SIZE), WHITE + (255,))
    d = ImageDraw.Draw(img)
    s = SYSTEME[listing["system"]]
    over = f"{s['name']} · {listing['titel'].split(',')[0]}" if s["name"] not in listing["titel"] else listing["titel"]
    kopf(img, over, listing["claim"])

    usps = listing["usps"][:4]
    rows = 2 if len(usps) == 4 else 1
    tiles_top = 1180 if rows == 2 else 1440
    panel = (110, 400, SIZE - 110, tiles_top - 50)
    d.rectangle(panel, fill=MIST)
    art = listing["art"]
    teil = {"raehmchen": "rahmen", "set": "rahmen", "eingebaut": "eingebaut"}.get(art, "mittelwand")
    item = einzelteil(listing, teil, 1400)
    if art == "set":
        mw = einzelteil(listing, "mittelwand", 1400)
        item = neben(item, fit(mw, item.width * 0.8, item.height * 0.9), 80)
    paste_center(img, item, (panel[0] + 90, panel[1] + 60, panel[2] - 90, panel[3] - 60))

    cols = 2 if len(usps) == 4 else len(usps)
    gap = 40
    x0, x1 = 110, SIZE - 110
    tw = (x1 - x0 - gap * (cols - 1)) / cols
    th = (SIZE - 100 - tiles_top - gap * (rows - 1)) / rows
    for i, (ic, title, sub) in enumerate(usps):
        r, c = divmod(i, cols)
        tx = x0 + c * (tw + gap)
        ty = tiles_top + r * (th + gap)
        d.rectangle([tx, ty, tx + tw, ty + th], fill=WHITE, outline=LINE, width=4)
        isz = 150
        iy = ty + 36 if cols == 3 else ty + (th - isz) / 2
        d.rectangle([tx + 36, iy, tx + 36 + isz, iy + isz], fill=SAGE)
        img.alpha_composite(icon(ic, isz - 30, OLIVE), (round(tx + 51), round(iy + 15)))
        txt_x = tx + 36 + isz + 34
        max_w = tx + tw - 30 - txt_x
        ft = font(600, 50) if cols == 3 else fit_font(d, title, 600, 58, max_w, 2, min_size=44)
        fsub = font(400, 42)
        if cols == 3:  # schmale Kacheln: Icon oben, Text darunter
            txt_x, max_w = tx + 36, tw - 72
            yy = ty + 36 + isz + 30
        else:  # Text und Icon vertikal mittig
            h_txt = len(wrap(d, title, ft, max_w)[:2]) * round(ft.size * 1.18) + 10 + len(wrap(d, sub, fsub, max_w)[:3]) * round(fsub.size * 1.18)
            yy = ty + max(36, (th - h_txt) / 2)
        yy = text_block(d, (txt_x, yy), title, ft, OLIVE, max_w, max_lines=2)
        text_block(d, (txt_x, yy + 10), sub, fsub, OLIVE, max_w, max_lines=3)
    return img


def mass_labels(listing):
    """(Breite, Höhe) als Beschriftung; None, wenn unbekannt."""
    t = listing.get("masse_text")
    s = SYSTEME[listing["system"]]
    if listing["art"] in ("mittelwand", "mittelwand_kg"):
        w, h = s["mw"]
        return f"{w} mm", f"{h} mm"
    if t:
        m = re.match(r"(.+?) × (\d+) mm", t)
        if m:
            return f"{m.group(1)} mm", f"{m.group(2)} mm"
        m = re.match(r"Höhe (\d+) mm", t)
        if m:
            return None, f"{m.group(1)} mm"
    w, h = s["rahmen"]
    return f"{w} mm", f"{h} mm"


def massbild(listing):
    img = Image.new("RGBA", (SIZE, SIZE), WHITE + (255,))
    d = ImageDraw.Draw(img)
    s = SYSTEME[listing["system"]]
    art = listing["art"]
    kopf(img, "Maße", f"Maßgenau für {s['name']}")
    teil = {"raehmchen": "rahmen", "set": "eingebaut", "eingebaut": "eingebaut"}.get(art, "mittelwand")
    item = einzelteil(listing, teil if art != "set" else "rahmen", 1400)
    x, y, w, h = paste_center(img, item, (190, 520, SIZE - 330, 1500))
    wl, hl = mass_labels(listing)
    lw = 5
    f = font(600, 60)

    def label(cx, cy, t):
        tw = d.textlength(t, font=f)
        d.rectangle([cx - tw / 2 - 26, cy - 50, cx + tw / 2 + 26, cy + 50], fill=WHITE, outline=GREEN, width=4)
        d.text((cx - tw / 2, cy - 38), t, font=f, fill=OLIVE)

    if wl:
        ly = y + h + 90
        d.line([(x, ly), (x + w, ly)], fill=GREEN, width=lw)
        for xx in (x, x + w):
            d.line([(xx, ly - 30), (xx, ly + 30)], fill=GREEN, width=lw)
            d.line([(xx, y + h + 15), (xx, ly - 30)], fill=LINE, width=3)
        label(x + w / 2, ly, wl)
    if hl:
        lx = x + w + 90
        d.line([(lx, y), (lx, y + h)], fill=GREEN, width=lw)
        for yy in (y, y + h):
            d.line([(lx - 30, yy), (lx + 30, yy)], fill=GREEN, width=lw)
            d.line([(x + w + 15, yy), (lx - 30, yy)], fill=LINE, width=3)
        tw = d.textlength(hl, font=f)
        cy = y + h / 2
        d.rectangle([lx - tw / 2 - 26, cy - 50, lx + tw / 2 + 26, cy + 50], fill=WHITE, outline=GREEN, width=4)
        d.text((lx - tw / 2, cy - 38), hl, font=f, fill=OLIVE)

    # Infozeile unten
    chips = []
    if art == "set":
        mw = s["mw"]
        chips.append(f"Mittelwand {mw[0]} × {mw[1]} mm")
    chips += listing.get("details", [])
    if art in ("mittelwand", "mittelwand_kg"):
        chips.append("100 % Bienenwachs")
    chips.append(f"Für {s['name']}-Beuten" if art not in ("mittelwand", "mittelwand_kg") else f"Für {s['name']}-Rähmchen")
    cx = 110
    cy = 1760
    fc = font(500, 44)
    for c in chips[:3]:
        tw = d.textlength(c, font=fc)
        if cx + tw + 60 > SIZE - 110:
            break
        d.rectangle([cx, cy, cx + tw + 60, cy + 100], fill=MIST, outline=LINE, width=3)
        d.text((cx + 30, cy + 24), c, font=fc, fill=OLIVE)
        cx += tw + 60 + 24
    return img


BILDER = [("MAIN", hauptbild), ("PT01", mengenbild), ("PT02", uspbild), ("PT03", massbild)]


def speichern(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=90, optimize=True, progressive=True)


def kontaktbogen(paths, out):
    thumbs = 4
    t = 360
    pad = 16
    rows = []
    for sku, files in paths:
        rows.append((sku, files))
    W = pad + thumbs * (t + pad) + 340
    H = pad + len(rows) * (t + pad)
    sheet = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(sheet)
    f = font(600, 30)
    for r, (sku, files) in enumerate(rows):
        y = pad + r * (t + pad)
        d.text((pad, y + t / 2 - 40), sku, font=f, fill=OLIVE)
        for c, p in enumerate(files):
            im = Image.open(p)
            im.thumbnail((t, t))
            x = 340 + pad + c * (t + pad)
            sheet.paste(im, (x, y))
            d.rectangle([x, y, x + t - 1, y + t - 1], outline=LINE, width=2)
    sheet.save(out, "JPEG", quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sku", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "output"))
    args = ap.parse_args()
    out = Path(args.out)
    todo = [l for l in LISTINGS if not args.sku or l["sku"] in args.sku]
    alle = []
    for l in todo:
        gezeichnet = ist_gezeichnet(l)
        files = []
        for code, fn in BILDER:
            ziel = "vorschau" if (code == "MAIN" and gezeichnet) else "upload"
            p = out / ziel / f"{l['sku']}.{code}.jpg"
            speichern(fn(l), p)
            files.append(p)
        alle.append((l["sku"], files))
        flag = "  (Hauptbild nur Vorschau: Foto fehlt)" if gezeichnet else ""
        print(f"{l['sku']:<14} {l['art']:<14}{flag}")
    if alle:
        kontaktbogen(alle, out / "uebersicht.jpg")
    pruefen = [l for l in todo if l.get("pruefen")]
    if pruefen:
        print("\nVor dem Hochladen prüfen:")
        for l in pruefen:
            print(f"  {l['sku']}: {l['pruefen']}")


if __name__ == "__main__":
    main()
