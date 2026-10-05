# Amazon-Bilder Rähmchen & Mittelwände

Generator für die Produktbilder der 36 Rähmchen- und Mittelwand-Angebote aus dem
Kategorie-Angebotsbericht vom 21.08.2026, in der API-Bavaria-CI (Work Sans,
`#3f4a1f`, `#6b7d32`, Linien `#d8dfbd`, Flächen `#f5f7ec` / `#e7ecd4`, eckige Formen).

```
pip install pillow
python3 amazon/generate.py                  # alle Angebote
python3 amazon/generate.py --sku ZAH-HM-30  # einzelne SKUs
```

Ergebnis in `amazon/output/` (nicht im Git), Dateinamen nach Amazon-Schema `SKU.MAIN.jpg`,
`SKU.PT01.jpg` usw., 2000 × 2000 px:

| Bild | Inhalt |
| --- | --- |
| `MAIN` | Hauptbild: alles, was im Paket ist, auf Reinweiß (255/255/255), Produkt füllt ca. 90 %. Ohne Text. Die Menge ist sichtbar, weil alle 10 / 12 / 20 Teile abgebildet sind, beim Set Rähmchen **und** Mittelwände. |
| `PT01` | Menge & Set: Überschrift („10 Rähmchen + 10 Mittelwände“), Mengen-Siegel, Lieferumfang. Bei Halbmaß-Rähmchen die Varianten 10–60 Stück, bei Einzel-Rähmchen und Mittelwänden der Hinweis auf das Set bzw. die eingebaute Variante. |
| `PT02` | USP-Kacheln (2–4) mit Linien-Icons. Nur Angaben aus Titel und Bullets des Angebots. |
| `PT03` | Maße mit Maßlinien. |

## Warum keine USPs und kein „10 Stück“ im Hauptbild?

Amazon erlaubt im Hauptbild keinen Text, keine Grafiken, Siegel oder Einblendungen
(siehe Blatt „Bilder“ im Angebotsbericht und Seller-Central-Hilfe G1881). Verstöße führen
dazu, dass das Angebot aus der Suche fällt. Deshalb:

- **Hauptbild:** zeigt die Menge und das Bundle durch das Produkt selbst (10 Rähmchen
  nebeneinander, Rähmchen + Mittelwand-Stapel).
- **Bild 2 (PT01):** steht direkt neben dem Hauptbild und trägt „10 Stück“, das Set und die
  Varianten.
- **Bild 3 (PT02):** USPs.

## Fotos

Für das Hauptbild verlangt Amazon ein echtes Foto, keine Zeichnung. Solange in
`amazon/fotos/` kein Foto liegt, zeichnet der Generator das Produkt und legt das
Hauptbild nur als Vorschau in `output/vorschau/` ab. PT01–PT03 dürfen Grafiken enthalten
und landen direkt in `output/upload/`. Welche Fotos gebraucht werden:
[`fotos/README.md`](fotos/README.md).

## Vor dem Hochladen prüfen

Diese Angebote haben widersprüchliche Daten im Bericht. Die Bilder folgen dem Titel:

| SKU | Widerspruch |
| --- | --- |
| D8-UUW3-4YLS | Titel 12× Dadant US, Anzahl der Artikel 10, Bullet beschreibt 10 Zander-Rähmchen |
| Y1-0TY6-5BR0 | Titel 10 Stück, Anzahl 20; Bullet „Für Zander Rähmchen“ bei DNM-Wachs |
| 34-FM7T-LAY1 | Titel 20 Stück, Anzahl 10 |
| EA-63WS-YJZU | Bullet „Für Zander Rähmchen“, Titel DN |
| 4W-1L8N-3R4E, 7X-ZH88-P34V | Titel 395 × 195 mm, Bullet 390 × 194 mm |
| I8-DDCR-XBCY | gleiche ASIN wie OE-7N1P-S2ZA |
| ON-3CK2-HUZG | Bullet „Deutsches Normalmaß“, Titel Dadant US Brutraum |
| WH-L8XJ-8WH9 | Titel 2 kg, Bullet „Preis gilt für etwa 1,00 kg“ |

Die Angebotsdaten (Maße, USPs, Mengen, Set-Hinweise) stehen in `listings.py`.
