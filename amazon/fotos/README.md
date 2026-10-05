# Produktfotos für die Amazon-Bilder

Hier liegen freigestellte Fotos (PNG mit transparentem Hintergrund, mind. 1500 px breit,
frontal, gleichmäßig ausgeleuchtet). Sobald ein Foto da ist, verwendet der Generator es
statt der Zeichnung, und das Hauptbild landet in `output/upload/` statt in
`output/vorschau/`.

Ein Foto pro Teil reicht, der Generator ordnet es für 10, 12 oder 20 Stück an.
Besser für das Hauptbild ist trotzdem ein echtes Foto des ganzen Pakets (z. B. alle
10 Rähmchen aufgefächert): Dann den fertigen Hauptbild-JPG direkt verwenden.

| Datei | Inhalt |
| --- | --- |
| `raehmchen-dnm.png` | 1 leeres Rähmchen Deutsch Normalmaß, gedrahtet |
| `raehmchen-zander.png` | 1 leeres Rähmchen Zander, gedrahtet |
| `raehmchen-zander-halbmass.png` | 1 leeres Rähmchen Zander Halbmaß 110 mm |
| `raehmchen-dadant-us-brutraum.png` | 1 leeres Rähmchen Dadant US Brutraum |
| `raehmchen-dnm-mittelwand.png` | 1 DNM-Rähmchen mit eingebauter Mittelwand |
| `raehmchen-zander-mittelwand.png` | 1 Zander-Rähmchen mit eingebauter Mittelwand |
| `raehmchen-dadant-us-brutraum-mittelwand.png` | 1 Dadant-US-Brutraum-Rähmchen mit Mittelwand |
| `raehmchen-dadant-us-honigraum-mittelwand.png` | 1 Dadant-US-Honigraum-Rähmchen mit Mittelwand |
| `mittelwand-dnm.png` | 1 Mittelwand 350 × 200 mm |
| `mittelwand-zander.png` | 1 Mittelwand 395 × 195 mm |
| `mittelwand-zander-flachzarge.png` | 1 Mittelwand 410 × 145 mm |
| `mittelwand-dadant-us-brutraum.png` | 1 Mittelwand 420 × 260 mm |

## Fotos aus Shopify laden

```
python3 amazon/fotos_laden.py products_export.csv
```

Lädt alle Bilder der Rähmchen- und Mittelwand-Produkte aus dem Shopify-Produktexport
nach `fotos/shopify/` und legt zu jedem Bild eine freigestellte PNG daneben (weißer
Hintergrund wird transparent). Das passende Bild dann unter dem Namen aus der Tabelle
oben nach `fotos/` kopieren.
