"""Amazon-Listings für API Bavaria: welche Bilder pro Angebot entstehen.

Jeder Eintrag ist ein eigenes Amazon-Angebot (eigene ASIN). Mengenvarianten sind
eigene Einträge, weil das Hauptbild genau die verkaufte Stückzahl zeigen muss.

Felder:
  key        Dateiname der Bilder (amazon/output/<key>/...)
  kind       "single" | "multi" | "bundle"
  title      Überschrift auf dem USP-Bild (Bild 2)
  badge      (Zahl, Einheit) für die Mengen-/Set-Kachel auf Bild 2
  parts      Bestandteile des Hauptbilds:
               handle   Shopify-Handle des Produkts
               image    Index des Shopify-Produktbilds (0 = Hauptbild)
               copies   wie oft das freigestellte Foto im Bild erscheint
                        (1, wenn das Foto die Packung schon komplett zeigt)
               layout   "single" | "fan" (Stapel, Kanten sichtbar) | "grid" | "row"
               width_mm reale Breite, damit Teile im Bundle maßstäblich sind
  usps       vier Vorteile für Bild 2 (Standard: apb.vorteile des ersten Teils)
  contents   bei Bundles: Lieferumfang-Zeilen für Bild 2
"""

H_DNM_FRAME = "dnm-raehmchen-hoffmann-223-mm-10-stueck"
H_DNM_MW = "dnm-mittelwaende-350-200-mm-1-kg"
H_ZANDER_HALF_FRAME = "zander-halbmass-raehmchen-110-mm-hoffmann"
H_ZANDER_MW = "zander-mittelwande-395-195-mm"
H_ZANDER_FLAT_MW = "zander-halb-und-flachzargen-mittelwande-410-145-mm-20-stuck"
H_DADANT_MW = "dadant-brutraum-mittelwaende-420-260-mm-1-kg"
H_TRAFO = "trafoloeter-9v-lange-messspitzen"

FRAME_DNM = dict(handle=H_DNM_FRAME, image=0, layout="fan", width_mm=394)
SHEET_DNM = dict(handle=H_DNM_MW, image=0, layout="fan", width_mm=350)
SHEET_ZANDER = dict(handle=H_ZANDER_MW, image=0, layout="fan", width_mm=395)
TRAFO = dict(handle=H_TRAFO, image=0, layout="single", copies=1, width_mm=230)


def part(base, **kw):
    return {**base, **kw}


LISTINGS = [
    # ---------------------------------------------------------------- Bundles
    {
        "key": "bundle-dnm-10-raehmchen-10-mittelwaende",
        "kind": "bundle",
        "title": "Rähmchen + Mittelwände Set · Deutsch Normal",
        "badge": ("10+10", "SET"),
        "parts": [part(FRAME_DNM, copies=10), part(SHEET_DNM, image=1, copies=10)],
        "contents": ["10 × DNM-Rähmchen Hoffmann 394 × 223 mm, gedrahtet",
                     "10 × DNM-Mittelwände 350 × 200 mm, 100 % Bienenwachs"],
        "usps": ["Passend aufeinander abgestimmt", "Rähmchen 8-fach geöst und gedrahtet"],
    },
    {
        "key": "bundle-dnm-20-raehmchen-20-mittelwaende",
        "kind": "bundle",
        "title": "Rähmchen + Mittelwände Set · Deutsch Normal",
        "badge": ("20+20", "SET"),
        "parts": [part(FRAME_DNM, copies=20), part(SHEET_DNM, image=1, copies=20)],
        "contents": ["20 × DNM-Rähmchen Hoffmann 394 × 223 mm, gedrahtet",
                     "20 × DNM-Mittelwände 350 × 200 mm, 100 % Bienenwachs"],
        "usps": ["Für zwei komplette Zargen", "Rähmchen 8-fach geöst und gedrahtet"],
    },
    {
        "key": "bundle-dnm-komplett-raehmchen-mittelwaende-trafoloeter",
        "kind": "bundle",
        "title": "Komplett-Set Einlöten · Deutsch Normal",
        "badge": ("3in1", "SET"),
        "parts": [part(FRAME_DNM, copies=10), part(SHEET_DNM, image=1, copies=10), TRAFO],
        "contents": ["10 × DNM-Rähmchen Hoffmann 394 × 223 mm, gedrahtet",
                     "10 × DNM-Mittelwände 350 × 200 mm, 100 % Bienenwachs",
                     "1 × Trafolöter 9 V mit langen Messspitzen"],
        "usps": ["Alles zum Einlöten in einem Paket"],
    },
    {
        "key": "bundle-zander-20-mittelwaende-trafoloeter",
        "kind": "bundle",
        "title": "Mittelwände + Trafolöter Set · Zander",
        "badge": ("2in1", "SET"),
        "parts": [part(SHEET_ZANDER, copies=20), TRAFO],
        "contents": ["20 × Zander-Mittelwände 395 × 195 mm, 100 % Bienenwachs",
                     "1 × Trafolöter 9 V mit langen Messspitzen"],
        "usps": ["Wachs aus dem Bayerischen Wald", "Mittelwände sauber einlöten"],
    },
    # ------------------------------------------------------- Mengen (Rähmchen)
    {"key": "dnm-raehmchen-hoffmann-10-stueck", "kind": "multi",
     "title": "DNM-Rähmchen Hoffmann 223 mm", "badge": ("10", "STÜCK"),
     "parts": [part(FRAME_DNM, copies=10)]},
    *[
        {"key": f"zander-halbmass-raehmchen-110-mm-{n}-stueck", "kind": "multi",
         "title": "Zander Halbmaß-Rähmchen 110 mm", "badge": (str(n), "STÜCK"),
         "parts": [dict(handle=H_ZANDER_HALF_FRAME, image=0, layout="fan", copies=n, width_mm=448)]}
        for n in (10, 20, 30, 40, 50, 60)
    ],
    # ---------------------------------------------------- Mengen (Mittelwände)
    *[
        {"key": f"dnm-mittelwaende-350-200-{n}-stueck", "kind": "multi",
         "title": "DNM-Mittelwände 350 × 200 mm", "badge": (str(n), "STÜCK"),
         "parts": [part(SHEET_DNM, image=1, copies=n)]}
        for n in (10, 20)
    ],
    *[
        {"key": f"zander-mittelwaende-395-195-{n}-stueck", "kind": "multi",
         "title": "Zander-Mittelwände 395 × 195 mm", "badge": (str(n), "STÜCK"),
         "parts": [part(SHEET_ZANDER, copies=n)]}
        for n in (10, 20)
    ],
    {"key": "zander-halb-flachzargen-mittelwaende-410-145-20-stueck", "kind": "multi",
     "title": "Zander Halb- & Flachzargen-Mittelwände", "badge": ("20", "STÜCK"),
     "parts": [dict(handle=H_ZANDER_FLAT_MW, image=0, layout="fan", copies=20, width_mm=410)]},
    # Gewichtsvarianten: das Foto zeigt die Packung, 2 kg = zwei Packungen
    {"key": "dnm-mittelwaende-350-200-1-kg", "kind": "multi",
     "title": "DNM-Mittelwände 350 × 200 mm", "badge": ("1", "KG"),
     "parts": [part(SHEET_DNM, copies=1, layout="single")]},
    {"key": "dnm-mittelwaende-350-200-2-kg", "kind": "multi",
     "title": "DNM-Mittelwände 350 × 200 mm", "badge": ("2", "KG"),
     "parts": [part(SHEET_DNM, copies=2, layout="row")]},
    {"key": "zander-mittelwaende-395-195-1-kg", "kind": "multi",
     "title": "Zander-Mittelwände 395 × 195 mm", "badge": ("1", "KG"),
     "parts": [part(SHEET_ZANDER, copies=1, layout="single")]},
    {"key": "zander-mittelwaende-395-195-2-kg", "kind": "multi",
     "title": "Zander-Mittelwände 395 × 195 mm", "badge": ("2", "KG"),
     "parts": [part(SHEET_ZANDER, copies=2, layout="row")]},
    {"key": "dadant-brutraum-mittelwaende-420-260-1-kg", "kind": "multi",
     "title": "Dadant Brutraum-Mittelwände", "badge": ("1", "KG"),
     "parts": [dict(handle=H_DADANT_MW, image=0, layout="single", copies=1, width_mm=420)]},
    # ------------------------------------------------------- Mengen (Gläser)
    {"key": "dib-einheitsglaeser-500-g-12-stueck", "kind": "multi",
     "title": "DIB-Einheitsgläser 500 g inkl. Deckel", "badge": ("12", "STÜCK"),
     "parts": [dict(handle="dib-einheitsglaser-500-g-12-stuck-inkl-deckel", image=0,
                    layout="grid", copies=12, width_mm=80)]},
    {"key": "twist-off-honiglaeser-500-g-12-stueck", "kind": "multi",
     "title": "Twist-off-Honiggläser 500 g inkl. Deckel", "badge": ("12", "STÜCK"),
     "parts": [dict(handle="twist-off-honigglaser-500-g-12-stuck-inkl-deckel", image=0,
                    layout="grid", copies=12, width_mm=80)]},
    {"key": "neutrale-honiglaeser-500-g-12-stueck", "kind": "multi",
     "title": "Neutrale Honiggläser 500 g inkl. Deckel", "badge": ("12", "STÜCK"),
     "parts": [dict(handle="neutrale-honigglaser-500-g-12-stuck-inkl-deckel", image=0,
                    layout="grid", copies=12, width_mm=80)]},
    # ------------------------------------------------------- Mengen (Futter)
    {"key": "apiinvert-5-x-2-5-kg", "kind": "multi",
     "title": "Apiinvert Bienenfutter 5 × 2,5 kg", "badge": ("5×", "2,5 KG"),
     "parts": [dict(handle="apiinvert-bienenfutter-5-2-5-kg", image=0, layout="row", copies=5, width_mm=200)]},
    {"key": "apifonda-5-x-2-5-kg", "kind": "multi",
     "title": "Apifonda Futterteig 5 × 2,5 kg", "badge": ("5×", "2,5 KG"),
     "parts": [dict(handle="apifonda-bienenfutterteig-5-2-5-kg", image=0, layout="row", copies=5, width_mm=200)]},
    {"key": "apifonda-12-x-1-kg", "kind": "multi",
     "title": "Apifonda Futterteig 12 × 1 kg", "badge": ("12×", "1 KG"),
     "parts": [dict(handle="apifonda-bienenfutterteig-12-1-kg", image=0, layout="grid", copies=12, width_mm=150)]},
    # ------------------------------------------------------- Einzelartikel
    *[
        {"key": key, "kind": "single", "title": title, "badge": badge,
         "parts": [dict(handle=handle, image=0, layout="single", copies=1, width_mm=300)]}
        for key, handle, title, badge in [
            ("trafoloeter-9v", H_TRAFO, "Trafolöter 9 V mit langen Messspitzen", ("9", "VOLT")),
            ("futtertrog-8-l-zander", "futtertrog-8-l-fur-zander", "Futtertrog 8 l für Zander", ("8", "LITER")),
            ("nicot-futterzarge-10-kg", "nicot-futterzarge-10-kg-zander-langstroth", "Nicot Futterzarge 10 kg", ("10", "KG")),
            ("futtertasche-zander", "futtertasche-zander-477-220-mm", "Futtertasche Zander 477 × 220 mm", None),
            ("futtertasche-dadant", "futtertasche-dadant-446-285-mm", "Futtertasche Dadant 446 × 285 mm", None),
            ("futtertasche-deutsch-normal", "futtertasche-deutsch-normal-393-220-mm", "Futtertasche Deutsch Normal", None),
            ("apiinvert-14-kg-eimer", "apiinvert-bienenfutter-14-kg-eimer", "Apiinvert Bienenfutter 14 kg Eimer", ("14", "KG")),
            ("apiinvert-16-kg-karton", "apiinvert-bienenfutter-16-kg-karton", "Apiinvert Bienenfutter 16 kg Karton", ("16", "KG")),
            ("apifonda-15-kg-karton", "apifonda-bienenfutterteig-15-kg-karton", "Apifonda Futterteig 15 kg Karton", ("15", "KG")),
        ]
    ],
]

# Ohne Shopify-Foto, daher kein Hauptbild möglich:
#   nicot-kunststoff-futterer-dadant-blatt-430-500-mm, apiinvert-bienenfutter-28-kg-karton
