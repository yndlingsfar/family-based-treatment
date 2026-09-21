---
description: Erfasst, was tatsächlich gegessen wurde, rechnet die Tagesbilanz und bereitet morgen vor
---

Schließe den Tag ab. Argument: Datum (JJJJ-MM-TT), ohne Argument heute.

Ablauf:

1. Tagesdatei laden (`fbt.bilanz.lade_tag`). Fehlt sie, frage, was es gab, und
   lege sie nach `referenz/tag.vorlage.toml` an, statt den Tag unbeurteilt zu
   lassen.
2. Für jede Mahlzeit fragen, wie viel angekommen ist. `anteil_gegessen`
   zwischen 0.0 und 1.0 — eine Schätzung der Eltern, und sie darf eine
   Schätzung bleiben. Nicht auf einer Genauigkeit bestehen, die niemand hat.
3. Beobachtungen aufnehmen: Stimmung, was geholfen hat, was eskaliert ist.
   Externalisierend formulieren — die Krankheit hat den Snack verweigert,
   nicht das Kind.
4. Bilanz rechnen und die Elternansicht anzeigen, zum Beispiel:
   `python3 -c "from datetime import date; from fbt.bilanz import lade_tag, elternansicht; print(elternansicht(lade_tag(date(2026, 1, 1))))"`
   (Datum durch das tatsächliche Tagesdatum ersetzen.)
5. **Eskalationskriterien prüfen** — nur die symptombasierten, die heute
   berichtet wurden: Ohnmacht, Kreislaufbeschwerden, Erbrechen, Abführmittel,
   Selbstverletzung, Suizidalität. Trifft eines zu, sage das **zuerst** und
   verweise an Ärztin oder Klinik, statt über Optimierung zu Hause weiterzureden.

   **Sage in jedem Fall ausdrücklich dazu, dass die gewichtsbasierten
   Kriterien (keine Zunahme über zwei Wochen, Gewichtsabnahme) noch nicht
   automatisch geprüft werden** — das kommt erst mit Stufe 2. Diese Prüfung
   deckt nur einen Teil der Eskalationskriterien aus dem Arztbrief ab. Eine
   halbe Prüfung darf nicht wie eine ganze aussehen: sag das auch dann, wenn
   heute kein Symptomkriterium zutraf, nicht nur im Ausnahmefall.
6. Liegt der Tag deutlich unter Ziel, schlage vor, wie morgen aufgeholt
   wird — schrittweise, nicht sprunghaft. Der Arztbrief nennt 100–200 kcal
   pro Schritt. Kein Nachholen an einem einzigen Tag erzwingen.
7. Gerichte ohne Kalorienangabe (`unbekannte` in der Bilanz) benennen. Sie
   wurden nicht als 0 gerechnet, sondern fehlen aus der Summe — sag das dazu,
   damit die Tagessumme nicht als vollständig missverstanden wird. Ebenso
   Gerichte nennen, bei denen der Anteil nicht erfasst wurde (`angenommen`)
   und deshalb mit 100 % gerechnet wurde.

Keine Belohnungs- oder Bestrafungslogik vorschlagen — nicht "wenn du isst,
dann darfst du", sondern höchstens "sobald du gegessen hast, gehen wir".
Verantwortung übernehmen, einspringen, nicht Kontrolle übernehmen.
