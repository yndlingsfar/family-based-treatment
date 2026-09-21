---
name: rezept-anreichern
description: Use when a recipe needs to reach a higher calorie target for refeeding - computing concrete ingredient changes in grams without making the portion look bigger
---

# Ein Rezept anreichern

## Rechnen, nicht schätzen

```bash
python3 -c "
from fbt.anreicherung import lade_mittel
from fbt.anreichern import anreichern
rezept = {'titel': '...', 'portionen': 4, 'kcal_pro_portion': 229, 'zutaten': [...]}
e = anreichern(rezept, 700, lade_mittel(), refeeding_phase=False)
print(e)
"
```

Das Ziel (`700` in diesem Beispiel) ist **pro Portion**. `anreichern` rechnet
intern auf die Gesamtmenge über alle Portionen hoch — `luecke_kcal` und
`erreicht_kcal` in der Antwort sind deshalb Totalen, nicht Werte pro Portion.
Beim Melden zurück auf die Portion teilen, sonst wirkt der Tag doppelt so groß
wie geplant.

Das Skript liefert konkrete Gramm-Angaben. Übernimm sie, statt eigene Zahlen zu
bilden — die Summe landet in der Tagesbilanz und damit im Arztbericht.

## Die Reihenfolge hat einen Grund

1. **Ersetzen vor Zugeben.** Milch durch Sahne, Wasser durch Brühe. Die Portion
   darf nicht sichtbar wachsen — sichtbar mehr auf dem Teller löst Angst aus.
2. **Fett und Protein vor Kohlenhydraten.** Refeeding-Syndrom-Prophylaxe.
3. **Geschmacksneutral bevorzugen.** Öl in der Sauce, Cashewmus in der Suppe.
4. **Nicht über das Ziel hinaus.** Lieber knapp darunter und ein Snack dazu.

## Unsichtbar machen

Aus dem Kochbuchkapitel „Allgemeine Tipps": Öl lässt sich mit Parmesan, Chia
oder Lecithin binden; Tomatenmark färbt sahnige Saucen zurück; Speck püriert
verschwindet in der Sauce; Butter zieht in warmes Gebäck ein; Reis in
Milch-Sahne statt Wasser quellen lassen sieht unverändert aus.

Sahne und Öl bei Shakes immer erst am Ende zugeben und nur kurz mischen — sonst
wird daraus Schlagsahne oder Mayonnaise.

## Grenzen

- Reicht ein Rezept nicht bis zum Ziel, gib nicht immer mehr hinein. Ein Shake
  dazu ist besser als eine Portion, die niemand schafft. Das Skript sagt über
  `warnungen` selbst, wenn es das Ziel nicht erreicht hat.
- **Maltodextrin in den ersten zwei Wochen des Refeedings nur nach ärztlicher
  Absprache.** Das Skript lässt es bei `refeeding_phase=True` automatisch weg.
- Kalorienangaben gehören nie in eine Ausgabe, die das Kind sehen kann — auch
  nicht als Gramm-Angabe einer Zutat, die auffällig groß wirkt.
