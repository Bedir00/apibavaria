# API Bavaria – Shopify Theme-Erweiterungen

Dieses Repository enthält die eigenen Erweiterungen für das Shopify-Theme von
[apibavaria.de](https://apibavaria.de) (Basis: Horizon 4.1.4). Unter `theme/` liegen
nur die neuen oder geänderten Dateien, in derselben Ordnerstruktur wie im Theme.

## Motion Graphics

Ruhige Animationen, die zur kantigen, technischen CI passen. Sie verwenden ausschließlich die CI-Farben, auch für die Bienen.

| Element | Wo | Dateien |
| --- | --- | --- |
| Animierte Honigwabe: Zellen zeichnen sich, Honigzellen pulsieren, zwei Bienen fliegen Schleifen | Startseiten-Hero, Motion-Banner | `snippets/apibavaria-motion-hive.liquid` |
| Headline steigt ein, „Imkereibedarf“ bekommt einen Textmarker in CI-Salbei, das Hero-Bild zoomt sanft auf (nur Desktop) | Startseiten-Hero | `assets/apibavaria-motion.css` |
| Scroll-Reveals: Überschriften, Kategorie-/Produktkarten, Trust-Box und Produktraster blenden gestaffelt ein | Startseite, Kollektionsseiten | `assets/apibavaria-motion.js`, `assets/apibavaria-motion.css` |
| Die Linien-Icons der Trust-Box zeichnen sich beim Einblenden | Startseite | `assets/apibavaria-motion.js`, `assets/apibavaria-motion.css` |
| Pulsierender Statuspunkt bei „Weitere Kategorien folgen!“ | Startseite | `assets/apibavaria-motion.css` |
| Neue Sektion **API Bavaria Motion-Banner** (Überzeile, Überschrift, Text, Button, Farbschema, Bienen an/aus) | im Theme-Editor überall hinzufügbar | `sections/apibavaria-motion-banner.liquid` |

Geänderte Theme-Dateien:

- `layout/theme.liquid`: bindet im `<head>` das Snippet `apibavaria-motion` ein.
- `sections/apibavaria-home-focus.liquid`: zeigt die Wabe im Hero und positioniert sie.
- `config/settings_schema.json`: zwei neue Einstellungen unter *Theme-Einstellungen > Animationen*:
  - **Scroll-Animationen** (`apb_motion_enabled`)
  - **Animierte Honigwabe mit Bienen im Startseiten-Hero** (`apb_motion_hero`)
- `templates/index.json`: der Motion-Banner steht auf der Startseite unter der Fokus-Sektion.

### Barrierefreiheit und Performance

- Bei der Systemeinstellung „Bewegung reduzieren“ (`prefers-reduced-motion: reduce`)
  wird nichts animiert: Die Wabe ist statisch, die Bienen sind ausgeblendet, alle Inhalte
  sind sofort sichtbar.
- Ohne JavaScript bleiben alle Inhalte sichtbar. Ausgeblendet wird nur, was das Skript
  unterhalb des sichtbaren Bereichs selbst markiert.
- Elemente, die beim Laden schon im Bild sind, werden nicht versteckt, damit nichts flackert.
- Animiert werden nur `transform`, `opacity` und SVG-Striche. Wabe und Bienen pausieren,
  sobald sie aus dem Bild gescrollt sind oder der Tab im Hintergrund ist.
- Kein zusätzliches Framework. Die Grafik ist Inline-SVG (keine Bild- oder Videodateien),
  dazu kommen rund 5 KB JavaScript und 3 KB CSS.

## Produktseiten (PDP)

Jede Produktseite baut sich aus eigenen Produktdaten auf und sieht deshalb für jedes
Produkt anders aus. Die Inhalte liegen in Produkt-Metafeldern (Namespace `apb`). Du
pflegst sie im Shopify-Admin unter *Produkt > Metafelder*, alle Felder beginnen mit „PDP:“.

| Metafeld | Format | Wo es erscheint |
| --- | --- | --- |
| PDP: Vorteile (Buy-Box) `apb.vorteile` | Liste | Häkchen-Liste unter dem Titel |
| PDP: Passt zu Beutensystem `apb.beutensysteme` | Auswahl | „Passt zu“-Chips in der Buy-Box und Systemleiste in der Story |
| PDP: Story-Überschrift `apb.claim` | Text | Große Überschrift der Produktstory |
| PDP: Story-Einleitung `apb.einleitung` | Mehrzeilig | Einleitungstext |
| PDP: Kennzahlen `apb.kennzahlen` | `Wert \| Beschriftung` | Kennzahlen-Leiste |
| PDP: Anwendungsschritte `apb.anwendung` | `Schritt \| Erklärung` | „So setzt du es ein“ |
| PDP: Einsatzmonate `apb.einsatzmonate` | Auswahl Jan–Dez | Kalender „Wann im Bienenjahr?“ |
| PDP: Hinweis Einsatzkalender `apb.einsatz_hinweis` | Text | Satz unter dem Kalender |
| PDP: Technische Daten `apb.technische_daten` | `Merkmal \| Wert` | Akkordeon in der Buy-Box |
| PDP: Lieferumfang `apb.lieferumfang` | Liste | Akkordeon in der Buy-Box |
| PDP: Fragen und Antworten `apb.faq` | `Frage \| Antwort` | „Häufige Fragen“ |
| PDP: Passendes Zubehör `apb.zubehoer` | Produkte | „Das passt dazu“ (max. 3) |

Bereiche ohne Daten werden automatisch ausgeblendet. Alle Farben stammen aus der
API-Bavaria-CI (Weiß, `#3f4a1f`, `#6b7d32`, Linien `#d8dfbd`, Flächen `#f5f7ec` / `#e7ecd4`),
Ecken sind eckig, und Hover-Effekte kommen ohne Bewegung aus. Je nach Produkttyp
ändern sich nur das Linien-Motiv (Tropfen, Wabe, Rähmchen, Glas, Smoker) und der
Flächenton der Story-Einleitung (Salbei, Mist oder Weiß), so wie bei den
Kategoriekarten der Startseite.

Theme-Dateien:

- `sections/apibavaria-pdp-story.liquid`: neue Sektion „API Bavaria Produktstory“ unter der Buy-Box
- `blocks/api-pdp-fit.liquid`: neuer Block „Passt zu (Beutensystem)“ in der Buy-Box
- `blocks/api-product-benefits.liquid`: Vorteile kommen aus `apb.vorteile` statt aus einer festen Liste im Code
- `blocks/api-pdp-details.liquid`: Lieferumfang und Technische Daten aus den Metafeldern, FAQ abschaltbar
- `snippets/apibavaria-pdp-motif.liquid`: Linien-Motive je Kategorie
- `templates/product.json`: „Passt zu“ nach dem Titel, Produktstory nach der Buy-Box

Die Inhalte für alle 23 aktiven Produkte liegen in `content/pdp_content.py`. Sie
stützen sich auf die Angaben in den Produktbeschreibungen.

## Angebote & Pop-up

Mengenrabatte und Zubehör-Sets, auf der Produktseite und als Pop-up nach „In den
Warenkorb“. Die Rabatte rechnet ausschließlich Shopify (native Rabatte). Das Theme
zeigt sie nur an und löst die Set-Codes im Hintergrund ein.

| Angebot | Gilt für | Shopify-Rabatt |
| --- | --- | --- |
| Mengenrabatt: ab 2 Stück −5 %, ab 3 Stück −10 %, gemischt je Kategorie | Kollektionen Bienenfutter, Gläser, Mittelwände, Rähmchen | 8 automatische Rabatte „Mengenrabatt <Kategorie>: ab 2/3 Stück …“ |
| Set: passendes Zubehör −10 %, beide Zubehörartikel −15 % (Rabatt aufs Zubehör) | Fütterungszubehör und Trafolöter (Zubehör = erste zwei Einträge aus `apb.zubehoer`) | 14 Rabattcodes `APB-SET10-<Produkt-ID>` / `APB-SET15-<Produkt-ID>` (Kaufe X, erhalte Y) |

**Ablauf**

- **PDP:** Der Block „Mengen- & Set-Angebot“ steht über dem Warenkorb-Button. Bei
  Mengenprodukten wählt der Kunde 1 / 2 / 3 Stück mit Preis und Ersparnis, die Auswahl
  setzt die Menge. Bei Set-Produkten wählt er das Zubehör per Checkbox und legt das Set
  mit einem Klick in den Warenkorb, der Set-Code wird automatisch eingelöst.
- **Pop-up:** Nach „In den Warenkorb“ zeigt ein Fenster das Angebot mit
  1-Klick-Buttons. Bei Mengenprodukten sind das „+1 / +2 hinzufügen“ und zwei Produkte
  zum Kombinieren aus derselben Kategorie, bei Set-Produkten die einzelnen Zubehörartikel
  oder „Beide hinzufügen“. Danach öffnet sich der Warenkorb-Drawer. Das Pop-up erscheint
  pro Produkt höchstens einmal pro Sitzung und nur, wenn noch ein Rabatt erreichbar ist.
- Pro Warenkorbzeile greift nur ein Produktrabatt, Shopify nimmt den höheren. Darauf
  weist das Pop-up hin.

**Theme-Einstellungen > API Bavaria Angebote:** Angebote an/aus, Pop-up an/aus.

**Dateien:** `blocks/api-pdp-offer.liquid`, `snippets/apibavaria-offer-data.liquid`
(Angebotsdaten je Produkt, enthält die Prozentwerte und Codes),
`snippets/apibavaria-offer-popup.liquid`, `assets/apibavaria-offers.js`,
`layout/theme.liquid` (bindet das Pop-up ein), `templates/product.json`,
`config/settings_schema.json`.

**Wichtig:** Ändert sich ein Prozentwert, muss er im Shopify-Rabatt **und** in
`snippets/apibavaria-offer-data.liquid` sowie im PDP-Block angepasst werden.

### Aktivierung der Mengenrabatte

Die 8 automatischen Mengenrabatte sind angelegt, aber **geplant (Start 01.01.2099)**,
damit sie nicht schon im Live-Shop gelten, bevor das neue Theme sichtbar ist. Beim
Veröffentlichen des Themes: *Shopify-Admin > Rabatte*, die acht „Mengenrabatt …“-Einträge
öffnen und das Startdatum auf heute setzen. Die Set-Codes sind aktiv. Sie werden nur
vom neuen Theme eingelöst.

## Installation

Alle Dateien (Motion Graphics und PDP) sind bereits im unveröffentlichten Theme
**„Apibavaria – Motion Graphics 04.10.2026“** (Kopie des Live-Themes vom 04.10.2026)
eingespielt. Die PDP-Metafelder sind direkt an den Produkten gespeichert. So geht es weiter:

1. Shopify-Admin > Onlineshop > Themes > „Apibavaria – Motion Graphics 04.10.2026“ >
   **Vorschau**.
2. Wenn alles passt: **Veröffentlichen**.

So überträgst du die Änderungen manuell in ein anderes Theme: Im Code-Editor die Dateien
aus `theme/assets`, `theme/snippets` und `theme/sections` neu anlegen. Danach die
Änderungen an `layout/theme.liquid`, `sections/apibavaria-home-focus.liquid` und
`config/settings_schema.json` übernehmen. Die Stellen sind im Code kommentiert.

## Amazon-Bilder

`amazon/` erzeugt pro Amazon-Angebot ein **Hauptbild** (`<key>.MAIN.jpg`) und ein
**USP-Bild** (`<key>.PT01.jpg`) aus den Shopify-Produktfotos.

```
pip install Pillow numpy rembg onnxruntime
python3 amazon/build_images.py
```

Ergebnis: `amazon/output/<key>/`, dazu `uebersicht-hauptbilder.jpg` und `pruefbericht.json`.

**Hauptbild (Amazon-Regeln):** 2000 × 2000 px, Hintergrund exakt RGB 255/255/255, Produkt
füllt 88 % der Bildkante, kein Text, keine Badges, keine Grafiken. Was angeboten wird,
zeigt das Bild über die abgebildeten Artikel: 10 Rähmchen als Stapel mit sichtbaren
Kanten, 12 Gläser im Raster, im Bundle alle Teile zusammen. Mengenvarianten sind
deshalb eigene Angebote mit eigenem Hauptbild.

**USP-Bild (Bild 2):** CI-Farben (`#3f4a1f`, `#6b7d32`, `#d8dfbd`, `#f5f7ec`), Schrift
Poppins wie im Theme, Mengen- bzw. Set-Kachel, „Passt zu“-System und Vorteile aus
`apb.vorteile` bzw. der Lieferumfang beim Bundle.

**Bundles** (in `amazon/listings.py`, im Shop noch nicht angelegt):

| Bundle | Inhalt |
| --- | --- |
| `bundle-dnm-10-raehmchen-10-mittelwaende` | 10 × DNM-Rähmchen Hoffmann + 10 × DNM-Mittelwände 350 × 200 |
| `bundle-dnm-20-raehmchen-20-mittelwaende` | 20 × DNM-Rähmchen Hoffmann + 20 × DNM-Mittelwände 350 × 200 |
| `bundle-dnm-komplett-raehmchen-mittelwaende-trafoloeter` | 10 × Rähmchen + 10 × Mittelwände + Trafolöter 9 V |
| `bundle-zander-20-mittelwaende-trafoloeter` | 20 × Zander-Mittelwände 395 × 195 + Trafolöter 9 V |

Für Zander gibt es kein Rähmchen-Bundle: Im Shop gibt es nur Halbmaß-Rähmchen (110 mm),
und dazu passt keine der Mittelwände ohne Zuschnitt.

**Fotos:** Der Generator lädt die Shopify-Fotos aus `amazon/shop_export.json`. Ein
besseres Foto legst du als `amazon/src_override/<handle>__<bildindex>.jpg` ab, es hat
Vorrang. Im Prüfbericht steht `PRÜFEN`, wenn das Foto kleiner als 1000 px ist.
Betroffen sind `apiinvert-bienenfutter-14-kg-eimer` (300 px), `apifonda-…-5-2-5-kg`
(280 px), `neutrale-honigglaser-…` (455 px), `zander-halb-und-flachzargen-…` (577 px)
und `dnm-raehmchen-hoffmann-…` (657 px). Ohne Foto in Shopify und damit ohne Hauptbild:
Nicot Kunststoff-Fütterer Dadant und Apiinvert 28 kg Karton.
