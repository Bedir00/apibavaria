"""Amazon-Angebote Rähmchen & Mittelwände (Stand: Kategorie-Angebotsbericht 21.08.2026).

Jeder Eintrag erzeugt vier Bilder:
  <SKU>.MAIN.jpg  Hauptbild: nur Produkt auf Reinweiß, ohne Text (Amazon-Regel)
  <SKU>.PT01.jpg  Menge / Set / Varianten
  <SKU>.PT02.jpg  USP-Kacheln
  <SKU>.PT03.jpg  Maße

Felder:
  art        raehmchen | set | eingebaut | mittelwand | mittelwand_kg
  system     Schlüssel aus SYSTEME (Maße, Fotodateien)
  anzahl     Stückzahl im Paket (bei set: Rähmchen und Mittelwände je anzahl)
  kg         nur mittelwand_kg
  usps       2–4 Kacheln: (Icon, Titel, Unterzeile). Nur Angaben aus Titel/Bullets.
  varianten  Mengen-Familie, die aktuelle Menge wird hervorgehoben
  auch_als   Hinweis auf das Set / die eingebaute Variante (Cross-Selling)
  pruefen    Widerspruch in den Amazon-Daten, vor dem Hochladen klären
"""

SYSTEME = {
    "dnm": {"name": "Deutsch Normalmaß", "kurz": "DNM", "rahmen": (394, 223), "mw": (350, 200), "draehte": 4},
    "zander": {"name": "Zander", "kurz": "Zander", "rahmen": (420, 220), "mw": (395, 195), "draehte": 4},
    "zander-halbmass": {"name": "Zander Halbmaß", "kurz": "Zander Halbmaß", "rahmen": (394, 110), "mw": None, "draehte": 2},
    "zander-flachzarge": {"name": "Zander Flachzarge", "kurz": "Zander Flachzarge", "rahmen": None, "mw": (410, 145), "draehte": 2},
    "dadant-us-brutraum": {"name": "Dadant US Brutraum", "kurz": "Dadant US", "rahmen": (448, 285), "mw": (420, 260), "draehte": 4},
    "dadant-us-honigraum": {"name": "Dadant US Honigraum", "kurz": "Dadant US", "rahmen": (448, 159), "mw": None, "draehte": 3},
}

# Wiederkehrende Kacheln
WACHS_100 = ("wabe", "100 % Bienenwachs", "Reines Wachs für sauberen Wabenbau")
PESTIZIDFREI = ("blatt", "Frei von Pestiziden", "Geprüfte Wachsqualität")
BAYERWALD = ("berge", "Bayerischer Wald", "Wachs von Imkern aus der Region")
HOFFMANN = ("hoffmann", "Hoffmann-Seiten", "Gleichmäßige Wabengassen ohne Abstandshalter")
GEDRAHTET = ("draht", "Geöst & gedrahtet", "Edelstahldraht – Mittelwand direkt einlöten")
ZELLE_54 = ("wabe", "Zellgröße 5,4 mm", "Bewährte Prägung für gleichmäßigen Bau")


def masse(sys_key, teil="rahmen", text=None):
    if text:
        return text
    w, h = SYSTEME[sys_key][teil]
    return f"{w} × {h} mm"


LISTINGS = [
    # ------------------------------------------------------------ Rähmchen (leer)
    {
        "sku": "0E-FAQY-1RUA", "asin": "B0DLV9STRN", "art": "raehmchen", "system": "dnm", "anzahl": 10,
        "titel": "Rähmchen DNM, Hoffmann",
        "claim": "Gedrahtet und geöst – bereit für die Mittelwand",
        "usps": [("mass", "Deutsch Normalmaß", "394 × 223 mm, für alle gängigen DNM-Beuten"), ("holz", "Qualitätsholz", "Trocken, glatt geschliffen, passgenau"), HOFFMANN, ("draht", "Fertig gedrahtet", "Edelstahldraht erleichtert das Einlöten")],
        "auch_als": "Auch als Set mit 10 Mittelwänden oder mit fertig eingebauter Mittelwand",
    },
    {
        "sku": "0P-K3I8-XA0K", "asin": "B0DDJ7SG6J", "art": "raehmchen", "system": "dnm", "anzahl": 10,
        "titel": "Rähmchen DNM, Hoffmann 223 mm",
        "claim": "Lindenholz, 8-fach geöst, waagerecht gedrahtet",
        "usps": [("holz", "Lindenholz", "Holzstärke ca. 8–10 mm"), ("draht", "8-fach geöst", "Waagerecht gedrahtet"), HOFFMANN, ("mass", "394 × 223 mm", "Deutsch Normalmaß")],
        "auch_als": "Auch als Set mit 10 Mittelwänden oder mit fertig eingebauter Mittelwand",
        "details": ["Holzstärke ca. 8–10 mm", "Lindenholz"],
    },
    {
        "sku": "AE-AXBU-OZW1", "asin": "B09Q11569C", "art": "raehmchen", "system": "dnm", "anzahl": 10,
        "titel": "Rähmchen DNM, Hoffmann 223 mm",
        "claim": "Hoffmann-Rähmchen im Deutsch Normalmaß",
        "usps": [("mass", "Höhe 223 mm", "Deutsch Normalmaß"), HOFFMANN, ("paket", "10 Stück", "Für Erweiterung und Austausch")],
        "masse_text": "Höhe 223 mm",
        "auch_als": "Auch als Set mit 10 Mittelwänden oder mit fertig eingebauter Mittelwand",
    },
    {
        "sku": "180739979", "asin": "B09NYQ1ZLX", "art": "raehmchen", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen, Hoffmann modifiziert",
        "claim": "Zander modifiziert mit Hoffmann-Seiten",
        "usps": [("mass", "Zander modifiziert", "220 mm Höhe"), HOFFMANN, ("paket", "10 Stück", "Für Erweiterung und Austausch")],
        "auch_als": "Auch als Set mit 10 Mittelwänden oder mit fertig eingebauter Mittelwand",
        "masse_text": "Höhe 220 mm",
    },
    {
        "sku": "EV-A8VQ-H1J3", "asin": "4270003217736", "art": "raehmchen", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen aus Lindenholz",
        "claim": "Lindenholz, geöst und 4-fach gedrahtet",
        "usps": [("holz", "Premium Lindenholz", "Leicht, robust und verzugsarm"), ("draht", "Geöst & 4-fach gedrahtet", "Ösen schützen das Holz, Draht gleichmäßig gespannt"), HOFFMANN, ("mass", "Passgenau für Zander", "Für gängige Zander-Beuten und Magazine")],
        "auch_als": "Auch als Set mit 10 Mittelwänden oder mit fertig eingebauter Mittelwand",
    },
    {
        "sku": "7Q-0QXN-BSC7", "asin": "B09QB8V2PQ", "art": "raehmchen", "system": "dadant-us-brutraum", "anzahl": 10,
        "titel": "Dadant US Brutraum-Rähmchen, modifiziert",
        "claim": "Brutraum-Rähmchen für Dadant US",
        "usps": [("mass", "Dadant US Brutraum", "285 mm Höhe, modifiziert"), ("paket", "10 Stück", "Für Erweiterung und Austausch")],
        "auch_als": "Auch mit fertig eingebauter Mittelwand erhältlich",
        "masse_text": "Höhe 285 mm",
    },
    {
        "sku": "J4-VUHX-E5AA", "asin": "B0CTGMQ3XH", "art": "raehmchen", "system": "dadant-us-brutraum", "anzahl": 10,
        "titel": "Dadant US Brutraum-Rähmchen, Hoffmann",
        "claim": "Hoffmann-Rähmchen für den Dadant-US-Brutraum",
        "usps": [("mass", "Dadant US Brutraum", "285 mm Höhe"), HOFFMANN, ("paket", "10 Stück", "Für Erweiterung und Austausch")],
        "auch_als": "Auch mit fertig eingebauter Mittelwand erhältlich",
        "masse_text": "Höhe 285 mm",
    },
    {
        "sku": "7E-BBT2-7BOK", "asin": "B01GCQDL38", "art": "raehmchen", "system": "dadant-us-brutraum", "anzahl": 12,
        "titel": "Dadant US Brutraum-Rähmchen, Hoffmann",
        "claim": "Verzapft, verleimt und 4-fach gedrahtet",
        "usps": [("mass", "ca. 285 × 435 mm", "Dadant US Brutraum"), ("draht", "4-fach Edelstahldraht", "Rostfrei und langlebig"), ("holz", "Verzapft & verleimt", "Fichten- oder Lindenholz, sehr stabil"), HOFFMANN],
        "auch_als": "Auch mit fertig eingebauter Mittelwand erhältlich",
        "masse_text": "ca. 435 × 285 mm",
    },
    {
        "sku": "D8-UUW3-4YLS", "asin": "4260635281151", "art": "raehmchen", "system": "dadant-us-brutraum", "anzahl": 12,
        "titel": "Dadant US Brutraum-Rähmchen, Hoffmann",
        "claim": "Gedrahtet und geöst aus Lindenholz",
        "usps": [("mass", "Dadant US Brutraum", "285 mm Höhe"), HOFFMANN, ("draht", "Geöst & gedrahtet", "Edelstahldraht"), ("holz", "Lindenholz", "Stabil und langlebig")],
        "auch_als": "Auch mit fertig eingebauter Mittelwand erhältlich",
        "masse_text": "Höhe 285 mm",
        "pruefen": "Titel sagt 12× Dadant US, Anzahl der Artikel = 10, Bullet 1 beschreibt 10 Zander-Rähmchen. Bilder folgen dem Titel (12 Dadant).",
    },
    # Zander Halbmaß: Variantenfamilie HN-4KKT-O2MX (Eltern-SKU braucht keine eigenen Bilder)
    *[
        {
            "sku": f"ZAH-HM-{n}", "asin": "", "art": "raehmchen", "system": "zander-halbmass", "anzahl": n,
            "titel": "Zander-Rähmchen Halbmaß 110 mm",
            "claim": "Halbmaß-Rähmchen für den Honigraum",
            "usps": [("mass", "394 × 110 mm", "Zander Halbmaß für den Honigraum"), ("holz", "Lindenholz", "Holzstärke ca. 8–10 mm"), ("draht", "4-fach geöst", "Waagerecht gedrahtet"), HOFFMANN],
            "varianten": [10, 20, 30, 40, 50, 60],
            "details": ["Holzstärke ca. 8–10 mm", "Lindenholz"],
        }
        for n in (10, 20, 30, 40, 50, 60)
    ],
    # ------------------------------------------------------------ Sets: Rähmchen + Mittelwände lose
    {
        "sku": "2K-IJ79-Y9PS", "asin": "B0D4MFDKWP", "art": "set", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen modifiziert + Mittelwände",
        "claim": "Rähmchen und Mittelwände im Set",
        "usps": [("set", "Alles in einem Paket", "10 Rähmchen + 10 Mittelwände"), PESTIZIDFREI, GEDRAHTET, HOFFMANN],
    },
    {
        "sku": "67-KSET-NNKV", "asin": "B0CZTZ5YT6", "art": "set", "system": "dnm", "anzahl": 10,
        "titel": "DNM-Rähmchen + Mittelwände",
        "claim": "Rähmchen und Mittelwände im Set",
        "usps": [("set", "Alles in einem Paket", "10 Rähmchen + 10 Mittelwände"), PESTIZIDFREI, GEDRAHTET, HOFFMANN],
    },
    {
        "sku": "NB-VKNZ-YTWS", "asin": "B0CZLNCZ2T", "art": "set", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen Linde + Mittelwände",
        "claim": "Rähmchen aus Lindenholz mit passenden Mittelwänden",
        "usps": [("set", "Alles in einem Paket", "10 Rähmchen + 10 Mittelwände"), ("holz", "Lindenholz", "Geleimt und getackert"), ("draht", "Edelstahldraht", "Waagerecht gedrahtet, Messingösen"), HOFFMANN],
        "masse_text": "477 × 220 mm",
    },
    # ------------------------------------------------------------ Rähmchen mit eingebauter Mittelwand
    {
        "sku": "75-GOGP-XM8P", "asin": "B0D4MH3ZSR", "art": "eingebaut", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen modifiziert, Mittelwand eingebaut",
        "claim": "Mittelwand fertig eingebaut – einfach einhängen",
        "usps": [("einhaengen", "Fertig eingebaut", "Kein Drahten, kein Einlöten"), HOFFMANN, PESTIZIDFREI, ("mass", "Zander modifiziert", "Höhe 220 mm")],
        "masse_text": "Höhe 220 mm",
    },
    {
        "sku": "II-EQID-70O9", "asin": "B0F8FDXV5M", "art": "eingebaut", "system": "zander", "anzahl": 10,
        "titel": "Zander-Rähmchen, Mittelwand eingebaut",
        "claim": "Sofort einsetzbar im Brut- oder Honigraum",
        "usps": [("einhaengen", "Sofort einsetzbar", "Mittelwand fertig eingebaut"), ("wabe", "100 % Bienenwachs", "Rein und seuchenfrei"), HOFFMANN, ("mass", "420 × 220 mm", "Zander")],
    },
    {
        "sku": "V8-9IC7-DXAH", "asin": "", "art": "eingebaut", "system": "dnm", "anzahl": 10,
        "titel": "DNM-Rähmchen, Mittelwand eingebaut",
        "claim": "Mittelwand fertig eingebaut – einfach einhängen",
        "usps": [("einhaengen", "Fertig eingebaut", "Kein Drahten, kein Einlöten"), ("wabe", "Bienenwachs", "Mittelwand im Rähmchen"), ("mass", "Deutsch Normalmaß", "Für DNM-Beuten"), ("paket", "10 Stück", "Für Erweiterung und Austausch")],
    },
    {
        "sku": "OE-7N1P-S2ZA", "asin": "B0D4MHHQ3N", "art": "eingebaut", "system": "dadant-us-honigraum", "anzahl": 10,
        "titel": "Dadant US Honigraum-Rähmchen, Mittelwand eingebaut",
        "claim": "Honigraum-Rähmchen, fertig mit Mittelwand",
        "usps": [("einhaengen", "Fertig eingebaut", "Kein Drahten, kein Einlöten"), ("mass", "482/448 × 159 mm", "Dadant US Honigraum"), ("wabe", "Bienenwachs", "Mittelwand im Rähmchen"), ("paket", "10 Stück", "Für einen Honigraum")],
        "masse_text": "482/448 × 159 mm",
    },
    {
        "sku": "I8-DDCR-XBCY", "asin": "B0D4MHHQ3N", "art": "eingebaut", "system": "dadant-us-honigraum", "anzahl": 10,
        "titel": "Dadant US Honigraum-Rähmchen, Mittelwand eingebaut",
        "claim": "Honigraum-Rähmchen, fertig mit Mittelwand",
        "usps": [("einhaengen", "Fertig eingebaut", "Kein Drahten, kein Einlöten"), ("mass", "482/448 × 159 mm", "Dadant US Honigraum"), ("wabe", "Bienenwachs", "Mittelwand im Rähmchen"), ("paket", "10 Stück", "Für einen Honigraum")],
        "masse_text": "482/448 × 159 mm",
        "pruefen": "Gleiche ASIN wie OE-7N1P-S2ZA – doppeltes Angebot?",
    },
    {
        "sku": "ON-3CK2-HUZG", "asin": "B0D4ML33DH", "art": "eingebaut", "system": "dadant-us-brutraum", "anzahl": 12,
        "titel": "Dadant US Brutraum-Rähmchen, Mittelwand eingebaut",
        "claim": "Brutraum-Rähmchen, fertig mit Mittelwand",
        "usps": [("einhaengen", "Fertig eingebaut", "Kein Drahten, kein Einlöten"), ("mass", "482 × 285 mm", "Dadant US Brutraum"), ("wabe", "Bienenwachs", "Mittelwand im Rähmchen"), ("paket", "12 Stück", "Für einen Brutraum")],
        "masse_text": "482 × 285 mm",
        "pruefen": "Bullet 1 spricht von Deutsch Normalmaß, Titel von Dadant US Brutraum.",
    },
    # ------------------------------------------------------------ Mittelwände nach Stück
    {
        "sku": "Y1-0TY6-5BR0", "asin": "", "art": "mittelwand", "system": "dnm", "anzahl": 10,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Bienenwachs aus dem Bayerischen Wald",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "350 × 200 mm", "Für DNM-Rähmchen")],
        "auch_als": "Auch als Set: 10 DNM-Rähmchen + 10 Mittelwände",
        "pruefen": "Titel sagt 10 Stück, Anzahl der Artikel = 20. Bullet 1 sagt „Für Zander Rähmchen“ (DNM-Wachs).",
    },
    {
        "sku": "34-FM7T-LAY1", "asin": "B0F35FRJWR", "art": "mittelwand", "system": "dnm", "anzahl": 20,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Bienenwachs aus dem Bayerischen Wald",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "350 × 200 mm", "Für DNM-Rähmchen")],
        "auch_als": "Auch als Set: 10 DNM-Rähmchen + 10 Mittelwände",
        "pruefen": "Titel sagt 20 Stück, Anzahl der Artikel = 10.",
    },
    {
        "sku": "EA-63WS-YJZU", "asin": "", "art": "mittelwand", "system": "dnm", "anzahl": 20,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Bienenwachs aus dem Bayerischen Wald",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "350 × 200 mm", "Für DNM-Rähmchen")],
        "auch_als": "Auch als Set: 10 DNM-Rähmchen + 10 Mittelwände",
        "pruefen": "Bullet 1 sagt „Für Zander Rähmchen“, Titel DN.",
    },
    {
        "sku": "4W-1L8N-3R4E", "asin": "B0F1ZJMZRC", "art": "mittelwand", "system": "zander", "anzahl": 10,
        "titel": "Mittelwände Zander",
        "claim": "Bienenwachs aus dem Bayerischen Wald",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "395 × 195 mm", "Für Zander-Rähmchen")],
        "auch_als": "Auch als Set: 10 Zander-Rähmchen + 10 Mittelwände",
        "pruefen": "Titel 395 × 195 mm, Bullet 390 × 194 mm.",
    },
    {
        "sku": "7X-ZH88-P34V", "asin": "B0F1ZHLWPX", "art": "mittelwand", "system": "zander", "anzahl": 20,
        "titel": "Mittelwände Zander",
        "claim": "Bienenwachs aus dem Bayerischen Wald",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "395 × 195 mm", "Für Zander-Rähmchen")],
        "auch_als": "Auch als Set: 10 Zander-Rähmchen + 10 Mittelwände",
        "pruefen": "Titel 395 × 195 mm, Bullet 390 × 194 mm.",
    },
    {
        "sku": "VB-PVZQ-T9P1", "asin": "", "art": "mittelwand", "system": "zander-flachzarge", "anzahl": 20,
        "titel": "Mittelwände Zander Flachzarge",
        "claim": "Für Halb- und Flachzargen im Zandermaß",
        "usps": [WACHS_100, PESTIZIDFREI, BAYERWALD, ("mass", "410 × 145 mm", "Halbzarge / Flachzarge")],
    },
    # ------------------------------------------------------------ Mittelwände nach Gewicht
    {
        "sku": "9B-JT0Q-2RQ5", "asin": "B0F31GP3GY", "art": "mittelwand_kg", "system": "dnm", "kg": 1,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Imkerqualität aus kontrollierter Produktion",
        "usps": [WACHS_100, ZELLE_54, ("mass", "350 × 200 mm", "Deutsch Normalmaß"), ("check", "Kontrollierte Produktion", "Imkerqualität")],
        "auch_als": "Auch als Set: 10 DNM-Rähmchen + 10 Mittelwände",
    },
    {
        "sku": "FU-MM41-QXE7", "asin": "", "art": "mittelwand_kg", "system": "dnm", "kg": 2,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Imkerqualität aus kontrollierter Produktion",
        "usps": [WACHS_100, ZELLE_54, ("mass", "350 × 200 mm", "Deutsch Normalmaß"), ("check", "Kontrollierte Produktion", "Imkerqualität")],
        "auch_als": "Auch als Set: 10 DNM-Rähmchen + 10 Mittelwände",
    },
    {
        "sku": "WH-L8XJ-8WH9", "asin": "", "art": "mittelwand_kg", "system": "dnm", "kg": 2,
        "titel": "Mittelwände Deutsch Normalmaß",
        "claim": "Täglich frisch gegossen in Deutschland",
        "usps": [ZELLE_54, ("check", "Laborgeprüftes Wachs", "Vor der Verarbeitung analysiert"), ("temperatur", "Über 100 °C erhitzt", "Rückstandsarm und seuchenfrei"), ("mass", "350 × 200 mm", "Deutsch Normalmaß")],
        "pruefen": "Titel 2 kg, Bullet: „Preis gilt für etwa 1,00 kg“.",
    },
    {
        "sku": "ML-MXG4-1639", "asin": "B0F31NN4JZ", "art": "mittelwand_kg", "system": "zander", "kg": 1, "blatt": 13,
        "titel": "Mittelwände Zander",
        "claim": "Sterilisiert bei 130 °C – keimfrei ins Volk",
        "usps": [WACHS_100, ZELLE_54, ("temperatur", "2 h bei 130 °C", "Sterilisiert, beugt Krankheiten vor"), ("mass", "395 × 195 mm", "Zander-Standardmaß")],
        "auch_als": "Auch als Set: 10 Zander-Rähmchen + 10 Mittelwände",
    },
    {
        "sku": "ZR-5030-C1MN", "asin": "", "art": "mittelwand_kg", "system": "zander", "kg": 2, "blatt": 28,
        "titel": "Mittelwände Zander",
        "claim": "Sterilisiert bei 130 °C – keimfrei ins Volk",
        "usps": [WACHS_100, ZELLE_54, ("temperatur", "2 h bei 130 °C", "Sterilisiert, beugt Krankheiten vor"), ("mass", "395 × 195 mm", "Zander-Standardmaß")],
        "auch_als": "Auch als Set: 10 Zander-Rähmchen + 10 Mittelwände",
    },
    {
        "sku": "DB01", "asin": "", "art": "mittelwand_kg", "system": "dadant-us-brutraum", "kg": 1,
        "titel": "Mittelwände Dadant Brutraum",
        "claim": "Das Fundament für einen starken Dadant-Brutraum",
        "usps": [WACHS_100, ZELLE_54, ("mass", "420 × 260 mm", "Dadant Brutraum"), ("check", "Kontrollierte Produktion", "Imkerqualität")],
        "auch_als": "Auch als Rähmchen mit fertig eingebauter Mittelwand",
    },
]
