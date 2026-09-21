---
name: mahlzeit-planen
description: Use when planning meals for a day of family-based refeeding - building a day of six meals that reaches a prescribed calorie target, choosing recipes, and preparing the shopping list
---

# Einen Tag planen

## Vorab immer

1. Profil laden: `python3 -c "from fbt.daten import lade_profil; p = lade_profil(); print(p)"`
2. **Fehlt `kcal_taeglich`, frage danach und plane nicht auf einer erfundenen Zahl.**
   Die Menge gibt die Ärztin vor. Ohne sie kannst du Mahlzeiten vorschlagen, aber
   nicht behaupten, der Tag sei ausreichend. Steht in `kcal_quelle` ein Hinweis,
   dass der Wert ein Platzhalter ist, sag das dazu — er ist dann keine Vorgabe,
   sondern eine offene Frage an die Ärztin.
3. Unverträglichkeiten und Fearfoods aus dem Profil beachten.

## Wie ein Tag aufgebaut wird

Sechs Mahlzeiten nach dem Plan im Profil. Grobe Verteilung der Tagesmenge:
Frühstück und die beiden Hauptmahlzeiten tragen je etwa ein Fünftel, die drei
Snacks zusammen die restlichen zwei Fünftel. Getränke zählen mit — allein über
Säfte und angereicherte Milch sind 800–1000 kcal am Tag möglich.

## Rezepte auswählen

Zwei Quellen:

- **Netzwerk-Kochbuch** (`fbt.kochbuch.lade_kochbuch`) — erprobt, Kalorien bekannt.
  Die erste Wahl an schwierigen Tagen und wenn es schnell gehen muss. 74 der 79
  Rezepte sind mit `pruefen: true` markiert; das heißt, die Zahl ist einen Blick
  in `pruefnotiz` wert, nicht dass sie unzuverlässig wäre.
- **Cookidoo** über den Connector — für Abwechslung und wenn sich das Kind etwas
  Normales wünscht. `cookidoo_get_recipe_details` liefert `nutrition` mit
  Bezugsgröße. **Prüfe `basisUnit`:** steht dort `100 g` und nicht `Portion`,
  musst du umrechnen. Ist `nutrition` null, hat das Rezept keine Angabe — dann
  rechne über `fbt.anreichern`, statt eine Zahl anzunehmen.

Plane höchstens einen Tag im Voraus. Mut kommt in Wellen; ein Plan von gestern
verschenkt den Moment, in dem heute etwas geht.

## Regeln aus der Behandlung

- Die Eltern entscheiden, was auf den Teller kommt. Das Kind wählt nicht aus,
  wiegt nicht ab, sieht keine Kalorien.
- Keine Light- und Diätprodukte.
- Bei jeder Mahlzeit mindestens 300 ml Getränk anbieten, am besten Saft.
- In der Refeeding-Phase kein Maltodextrin ohne ärztliche Absprache.

## Ausgabe

Immer **zwei** Fassungen:

1. **Elternansicht** — mit kcal je Gericht und Tagessumme, plus was vorzukochen ist.
   Für die Eltern, nicht für den Kühlschrank.
2. **Tischansicht** — nur Uhrzeit und was es gibt. Keine Kalorien, kein Gewicht,
   kein Ziel. Diese Fassung darf ausgedruckt am Kühlschrank hängen oder dem Kind
   gezeigt werden.

Schreibe den Plan als `$FBT_DATEN/tage/JJJJ-MM-TT.toml` nach dem Muster in
`referenz/tag.vorlage.toml`. **Alle Schlüssel auf oberster Ebene vor die erste
`[[mahlzeit]]`-Tabelle**, sonst landet `beobachtungen` (oder `ziel_kcal`, oder
`datum`) in der letzten Mahlzeit statt auf Tagesebene — der Loader lehnt eine
solche Datei inzwischen mit einer klaren Fehlermeldung ab, aber es ist die eine
Art, wie eine Tagesdatei unbrauchbar geschrieben werden kann. Lieber einmal
gegen die Vorlage gegenprüfen, bevor die Datei steht.

## Einkauf

Fehlende Zutaten mit `cookidoo_add_recipe_ingredients` in die Cookidoo-Einkaufs-
liste schieben; was nicht aus einem Cookidoo-Rezept stammt, mit
`cookidoo_add_additional_items`.
