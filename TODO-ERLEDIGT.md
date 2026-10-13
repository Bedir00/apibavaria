# Erledigt: API Bavaria & Naturaflakes (Claude Code)

Stand: 13.10.2026. Grundlage sind alle Claude-Code-Sitzungen im Repo `Bedir00/apibavaria`,
die Commits auf den `claude/*`-Branches und die README.

## Shopify-Theme apibavaria.de (04.10.2026)

Branch `claude/shopify-motion-graphics-n86f7f`, eingespielt ins unveröffentlichte Theme
„Apibavaria – Motion Graphics 04.10.2026“.

- [x] **Motion Graphics** (`51ec143`)
  - [x] Animierte Honigwabe mit zwei Bienen im Startseiten-Hero
  - [x] Headline-Einstieg mit Textmarker auf „Imkereibedarf“, sanfter Bild-Zoom (Desktop)
  - [x] Scroll-Reveals für Überschriften, Kategorie-/Produktkarten, Trust-Box, Produktraster
  - [x] Trust-Box-Icons zeichnen sich beim Einblenden, pulsierender Statuspunkt
  - [x] Neue Sektion „API Bavaria Motion-Banner“ für den Theme-Editor
  - [x] Zwei Schalter unter *Theme-Einstellungen > Animationen*
  - [x] „Bewegung reduzieren“ und Betrieb ohne JavaScript berücksichtigt
- [x] **Produktseiten neu, individuell je Produkt** (`e4b3fad`)
  - [x] 12 Produkt-Metafelder (`apb.*`), Bereiche ohne Daten werden ausgeblendet
  - [x] Sektion „API Bavaria Produktstory“, Block „Passt zu (Beutensystem)“, Vorteile, Technische Daten, Lieferumfang, FAQ
  - [x] Inhalte für alle 23 aktiven Produkte geschrieben (`content/pdp_content.py`) und als Metafelder an den Produkten gespeichert
- [x] **PDP und Motion Graphics an die CI angepasst** (Farben, eckige Formen, Hover ohne Bewegung) (`c005e49`)
- [x] **Mengen- und Set-Angebote mit Pop-up** (`54c6e88`)
  - [x] Mengenrabatt ab 2 Stück −5 %, ab 3 Stück −10 % für Bienenfutter, Gläser, Mittelwände, Rähmchen
  - [x] Set-Angebot für Fütterungszubehör und Trafolöter: Zubehör −10 %, beide Zubehörartikel −15 %
  - [x] PDP-Block „Mengen- & Set-Angebot“ und Pop-up nach „In den Warenkorb“
  - [x] 8 automatische Mengenrabatte in Shopify angelegt (geplant, Start 01.01.2099)
  - [x] 14 Set-Rabattcodes `APB-SET10/15-…` angelegt und aktiv
  - [x] Lokal im Browser durchgetestet, 1-Cent-Rundungsfehler zwischen PDP und Pop-up behoben
- [x] **Text „Warenkorb / 0 Artikel“ neben dem Warenkorb-Symbol entfernt**, in beiden Theme-Kopien (`d602e8c`)
- [x] **Rabatte per Probe-Berechnung geprüft:** Set-Rabatt greift (−10,86 € im Test), Mengenrabatt bewusst noch inaktiv
- [x] **Google-Kauf-Tracking geprüft:** nicht ins Theme eingebaut, weil es dort jeden Seitenaufruf als Kauf melden würde. Stattdessen Code für ein benutzerdefiniertes Pixel (*Einstellungen > Kundenereignisse*) vorbereitet.

## Amazon-Bilder für Rähmchen, Mittelwände und Bundles (05.10.2026)

- [x] **Bildgenerator mit Zusatzbildern** (Branch `claude/lucid-babbage-25ewg3`)
  - [x] 36 Rähmchen- und Mittelwand-Angebote: 144 Bilder, je ein Hauptbild (Vorschau) und drei Zusatzbilder (Menge/Lieferumfang, USP-Kacheln, Maße), 2000 × 2000 px
  - [x] Bilder als zwei ZIP-Dateien bereitgestellt
  - [x] Widersprüchliche Angaben in 9 Amazon-Angeboten gefunden und aufgelistet
  - [x] Skript `amazon/fotos_laden.py`: lädt Produktfotos aus dem Shopify-Export und entfernt den weißen Hintergrund
- [x] **Bildgenerator in der Live-CI mit Bundles** (Branch `claude/dreamy-wright-twm3ez`)
  - [x] 4 Bundles festgelegt: DNM-Set 10+10, DNM-Set 20+20, DNM-Komplett-Set 3in1 (mit Trafolöter), Zander-Set 2in1
  - [x] Pro Angebot Hauptbild (ohne Text, Menge sichtbar abgebildet) und USP-Bild in Poppins und Theme-Farben
  - [x] Automatische Prüfung der Hauptbilder auf Amazon-Vorgaben (Reinweiß, 88 % Füllung)
- [x] **Shopify-Konnektor geklärt:** verbunden mit dem Shop Apibavaria (apibavaria.de)
- [x] **Produktdaten geprüft:** 2 Produkte ohne Fotos, 3 Fotos unter Amazons Mindestgröße, wahrscheinlicher Preisfehler gefunden
- [x] **Shop-Zuordnung geklärt:** Repo = Shopify-Shop apibavaria.de, hochgeladener Kategorie-Angebotsbericht = Amazon Seller Central

## Naturaflakes

Zu Naturaflakes gibt es in Claude Code keine erledigten Aufgaben. Ich habe keine Sitzung,
keinen Commit, kein Repository und keine Erwähnung in den Transkripten gefunden.

## Noch offen (laut den Sitzungen)

- [ ] Theme „Apibavaria – Motion Graphics 04.10.2026“ in der Vorschau prüfen und veröffentlichen
- [ ] Danach die 8 Mengenrabatte auf heute stellen und einen Testkauf machen
- [ ] „Test Produkt“ (0 €) archivieren, es zählt sonst für den Mengenrabatt mit
- [ ] Aktiven Kaching-Bundles-Rabatt prüfen oder deaktivieren
- [ ] GA4- bzw. Google-Ads-Tag-ID für das Kauf-Pixel liefern
- [ ] Echte Produktfotos für die Amazon-Hauptbilder: `cdn.shopify.com` freigeben oder Fotos hochladen
- [ ] Preis 1,00 € bei „Zander Halb- und Flachzargen-Mittelwände – 20 Stück“ prüfen
- [ ] Widersprüche in den Amazon-Angeboten klären
- [ ] Einen der beiden Amazon-Generatoren auswählen (`lucid-babbage` oder `dreamy-wright`)

Hinweis: Die Sitzung „Videos mit Voice-over und Motion Graphics“ lief zwar im Repo
apibavaria, betraf aber den LIORA-Shop. Sie ist deshalb oben nicht aufgeführt.
