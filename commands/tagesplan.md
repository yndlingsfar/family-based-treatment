---
description: Plant einen Tag mit sechs Mahlzeiten auf die ärztlich vorgegebene Kalorienmenge
argument-hint: "[heute|morgen|JJJJ-MM-TT]"
---

Plane einen Tag für das Refeeding. Argument (`$ARGUMENTS`): `heute`, `morgen`
oder ein Datum (JJJJ-MM-TT). Ohne Argument: morgen.

Nutze die Skill `mahlzeit-planen`.

Ablauf:

1. Profil laden (`fbt.daten.lade_profil`). Fehlt `kcal_taeglich`, frage danach
   und plane nicht auf einer erfundenen Zahl — sag das offen, bevor irgendein
   Vorschlag kommt. Ist der Wert nur ein Platzhalter (siehe `kcal_quelle`),
   behandle ihn genauso, nicht als Vorgabe.
2. Die letzten drei Tagesdateien unter `$FBT_DATEN/tage/` ansehen, um
   Wiederholungen zu vermeiden und zu sehen, welche Gerichte gut ankamen und
   wo sich die Krankheit zuletzt breitgemacht hat (niedriges
   `anteil_gegessen`) — als Hinweis, was heute leichter oder schwerer werden
   könnte, nicht als Liste von Dingen, die das Kind verweigert hat.
3. Sechs Mahlzeiten vorschlagen, gemischt aus Netzwerk-Kochbuch und Cookidoo.
   Unverträglichkeiten und Fearfoods aus dem Profil ausschließen. Reicht ein
   Rezept nicht an die Zielkalorien heran, die Skill `rezept-anreichern`
   heranziehen statt die Portion frei zu schätzen.
4. Die Tagesdatei `$FBT_DATEN/tage/JJJJ-MM-TT.toml` nach dem Muster in
   `referenz/tag.vorlage.toml` schreiben. Alle Schlüssel der obersten Ebene
   (`datum`, `ziel_kcal`, `beobachtungen`) müssen vor der ersten
   `[[mahlzeit]]`-Tabelle stehen. Fehlt der ärztliche Wert, bleibt `ziel_kcal`
   ganz weg — kein Platzhalter, der wie eine Vorgabe aussieht.
5. **Beide Ausgaben von `fbt.bilanz` erzeugen lassen, nicht von Hand
   formulieren** — die Tagesdatei mit `fbt.bilanz.lade_tag(...)` einlesen und
   daraus `elternansicht(...)` (Zahlen) und `tischansicht(...)` (keine
   Zahlen) drucken. Die Funktion garantiert, dass keine Zahl durchrutscht;
   von Hand nachformuliert geht das irgendwann schief. Zeig zuerst die
   Elternansicht, dann die Tischansicht — und schreibe die Tischansicht
   zusätzlich nach `$FBT_DATEN/tage/JJJJ-MM-TT-tisch.txt`, damit sie
   ausgedruckt oder auf einem eigenen Gerät geöffnet werden kann. Diesen
   Bildschirm, auf dem die Elternansicht steht, dem Kind nie zeigen.
6. Fragen, ob die fehlenden Zutaten in die Cookidoo-Einkaufsliste sollen.
   `cookidoo_add_recipe_ingredients` (für tatsächlich gekochte
   Cookidoo-Rezepte — es nimmt alle Zutaten des Rezepts, nicht nur die
   fehlenden) bzw. `cookidoo_add_additional_items` für alles andere. Nur
   schieben, wenn zugestimmt wird, und Anreicherungsmittel dort neutral und
   ohne Mengenangabe eintragen — die Liste ist auch am Thermomix in der
   Küche sichtbar.

## Sprache

Externalisierend sprechen: die Krankheit hat den Snack verweigert, nicht das
Kind. Keine Belohnungs- oder Bestrafungslogik — nicht "wenn du isst, dann
darfst du", sondern höchstens "sobald du gegessen hast, gehen wir".
Verantwortung übernehmen, einspringen, nicht Kontrolle übernehmen.
