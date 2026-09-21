---
name: rezept-anreichern
description: Use when a recipe needs to reach a higher calorie target for refeeding - computing concrete ingredient changes in grams without making the portion look bigger
---

# Ein Rezept anreichern

## Rechnen, nicht schätzen

`refeeding_phase=True` ist die Vorgabe, solange nicht ausdrücklich geklärt
ist, dass die ersten Wochen des Refeedings vorbei sind. Im Zweifel `True` —
der einzige Preis ist ein Vorschlag weniger (Maltodextrin fällt weg).
**`[behandlung] phase` aus der `profil.toml` wird derzeit nicht ausgelesen** —
`fbt.daten.lade_profil` liest aus `[behandlung]` nur `wiegen`. Also nachfragen
statt annehmen, wenn unklar ist, ob die ersten zwei Wochen vorbei sind.

`fbt.kochbuch.lade_kochbuch()` liefert `Rezept`-Objekte, keine Dicts;
`anreichern` erwartet ein Dict mit denselben Feldnamen — erst umbauen:

```bash
python3 -c "
from fbt.anreicherung import lade_mittel
from fbt.anreichern import anreichern
from fbt.kochbuch import lade_kochbuch

r = lade_kochbuch()['power-porridge']
rezept = {'portionen': r.portionen, 'kcal_pro_portion': r.kcal_pro_portion,
          'zutaten': list(r.zutaten)}
e = anreichern(rezept, 700, lade_mittel(), refeeding_phase=True)
print(e)
"
```

Die Regel „Ersetzen vor Zugeben" greift nur bei Zutaten, die ein `mittel`-Feld
tragen — einen Schlüssel aus `anreicherung.json` (z. B. `vollmilch`, das sich
zu `sahne-30` ersetzen lässt). Zutaten aus dem Kochbuch tragen dieses Feld nur,
wenn es im Originaleintrag gepflegt wurde. Fehlt es, bleibt genau die Regel
stumm, die verhindert, dass die Portion sichtbar wächst — `anreichern` geht
dann direkt zum Zugeben über. Das ist kein Fehler des Skripts, aber ein Grund,
das Ergebnis kurz gegen die Zutatenliste zu lesen, bevor du es weitergibst.

Das Ziel (`700` in diesem Beispiel) ist **pro Portion**. `anreichern` rechnet
intern auf die Gesamtmenge über alle Portionen hoch — `luecke_kcal` und
`erreicht_kcal` in der Antwort sind deshalb Totalen, nicht Werte pro Portion.
**Dasselbe gilt für `menge_g` und `kcal` in jedem einzelnen `Vorschlag`** —
auch die sind für den ganzen Topf, nicht pro Teller. Bei vier Portionen kann
das Skript z. B. „Rapsöl, 120 g" ausgeben, und das sind 120 g insgesamt. Beim
Weitergeben so sagen: „insgesamt 120 g Rapsöl in die Sauce", nie „120 g pro
Portion" — sonst landet ein Mehrfaches der berechneten Menge im Topf.

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
  Absprache.** Das Skript lässt es bei `refeeding_phase=True` automatisch weg
  — deshalb ist das die Vorgabe, siehe oben.
- Kalorienangaben gehören nie in eine Ausgabe, die das Kind sehen kann — auch
  nicht als Gramm-Angabe einer Zutat, die auffällig groß wirkt.

## Sprache

Externalisierend sprechen: die Krankheit hat den Snack verweigert, nicht das
Kind. Keine Belohnungs- oder Bestrafungslogik — nicht "wenn du isst, dann
darfst du", sondern höchstens "sobald du gegessen hast, gehen wir".
Verantwortung übernehmen, einspringen, nicht Kontrolle übernehmen.
