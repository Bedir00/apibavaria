# API Bavaria – Shopify Theme-Erweiterungen

Dieses Repository enthält die eigenen Erweiterungen für das Shopify-Theme von
[apibavaria.de](https://apibavaria.de) (Basis: Horizon 4.1.4). Unter `theme/` liegen
nur die neuen oder geänderten Dateien, in derselben Ordnerstruktur wie im Theme.

## Motion Graphics

Ruhige Animationen, die zur kantigen, technischen CI passen.

| Element | Wo | Dateien |
| --- | --- | --- |
| Animierte Honigwabe: Zellen zeichnen sich, Honigzellen pulsieren, zwei Bienen fliegen Schleifen | Startseiten-Hero, Motion-Banner | `snippets/apibavaria-motion-hive.liquid` |
| Headline steigt ein, „Imkereibedarf“ bekommt einen Honig-Textmarker, das Hero-Bild zoomt sanft auf (nur Desktop) | Startseiten-Hero | `assets/apibavaria-motion.css` |
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

## Installation

Die Dateien sind bereits im unveröffentlichten Theme **„Apibavaria – Motion Graphics
04.10.2026“** (Kopie des Live-Themes vom 04.10.2026) eingespielt. So geht es weiter:

1. Shopify-Admin > Onlineshop > Themes > „Apibavaria – Motion Graphics 04.10.2026“ >
   **Vorschau**.
2. Wenn alles passt: **Veröffentlichen**.

So überträgst du die Änderungen manuell in ein anderes Theme: Im Code-Editor die Dateien
aus `theme/assets`, `theme/snippets` und `theme/sections` neu anlegen. Danach die
Änderungen an `layout/theme.liquid`, `sections/apibavaria-home-focus.liquid` und
`config/settings_schema.json` übernehmen. Die Stellen sind im Code kommentiert.
