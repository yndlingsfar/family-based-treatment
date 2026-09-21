---
description: Erfasst, was tatsächlich gegessen wurde, rechnet die Tagesbilanz und bereitet morgen vor
argument-hint: "[JJJJ-MM-TT]"
---

Schließe den Tag ab. Argument (`$ARGUMENTS`): Datum (JJJJ-MM-TT), ohne
Argument heute.

Das ist ein Gespräch zwischen den Eltern. Nicht am Tisch, nicht mit dem Kind
im Raum — die Elternansicht enthält Zahlen.

Alle Python-Aufrufe mit `PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}"` beginnen —
sonst findet Python die Module unter `fbt/` nicht, weil sie im
Plugin-Verzeichnis liegen und nicht im Arbeitsordner der Eltern.

**Was dieser Befehl nicht leistet:** Er hält fest, was war, und bereitet
morgen vor. Eine laufende Mahlzeit begleitet er nicht — dafür gibt es dieses
Werkzeug noch nicht. Schreibt jemand mitten in einer eskalierenden Mahlzeit
hier hinein, sag das zuerst und in einem Satz: Hilfe im Moment kommt aus dem,
was mit dem Elternnetzwerk und der Praxis besprochen ist, nicht aus diesem
Chat. Und die oben abgefragten Warnzeichen gelten jederzeit, nicht nur am
Abend: bei Ohnmacht, Erbrechen, Selbstverletzung oder Äußerungen über Suizid
sofort den unten genannten Weg gehen (Praxis, außerhalb der Sprechzeiten die
Kinderklinik, bei Suizidalität Notaufnahme oder 112).

Ablauf:

1. **Zuerst fragen, nicht darauf warten, dass es erwähnt wird.** Noch bevor
   die Tagesdatei geladen wird, ausdrücklich und einzeln abfragen, ob heute
   etwas davon vorkam:

   - Ohnmacht oder Schwarzwerden beim Aufstehen
   - auffällig langsamer Puls
   - Erbrechen
   - Abführmittel
   - Selbstverletzung
   - Äußerungen über Suizid
   - dazu, gerade in den ersten Refeeding-Wochen: Ödeme (geschwollene Füße
     oder Unterschenkel), Verwirrtheit, Atemnot

   **Trifft eines zu: sag es als Erstes, nenne den konkreten Weg, und brich
   hier ab. Die weiteren Schritte entfallen — kein Aufholplan, keine Bilanz,
   bevor jemand sie gesehen hat.** Der konkrete Weg: Praxis; außerhalb der
   Sprechzeiten die Kinderklinik; bei Suizidalität sofort Notaufnahme oder
   112. Sprich in diesem Moment nicht zugleich über Stufe 2 oder
   Kalorienzahlen — wer gerade an die Klinik verwiesen wird, braucht keinen
   Nebensatz über den Stand des Werkzeugs.

   **Trifft keines zu**, sag trotzdem ausdrücklich dazu: das war nur die
   symptombasierte Prüfung. Die gewichtsbasierten Kriterien (keine Zunahme
   über zwei Wochen, Gewichtsabnahme) werden noch nicht automatisch
   geprüft — das kommt erst mit Stufe 2. Diese Prüfung deckt nur einen Teil
   der Eskalationskriterien aus dem Arztbrief ab, und das sagst du an jedem
   Abschluss, nicht nur im Ausnahmefall — sonst sieht ein unauffälliger Tag
   wie eine vollständige Prüfung aus, obwohl er es nicht ist. Erst danach
   weiter mit den nächsten Schritten.

2. Tagesdatei laden (`fbt.bilanz.lade_tag`). Fehlt sie, frage, was es gab, und
   lege sie nach `referenz/tag.vorlage.toml` an, statt den Tag unbeurteilt zu
   lassen. Lehnt der Loader die Datei ab (Tippfehler im Schlüssel, Text statt
   Zahl, `anteil_gegessen` außerhalb 0.0–1.0), nenne die Meldung wörtlich und
   korrigiere die Datei — **niemals die Zahl im Kopf ersetzen und weiterrechnen**.
   Die Meldung nennt Datei und Stelle; genau dafür ist sie da.
3. Für jede Mahlzeit fragen, wie viel angekommen ist. `anteil_gegessen`
   zwischen 0.0 und 1.0 — eine Schätzung der Eltern, und sie darf eine
   Schätzung bleiben. Nicht auf einer Genauigkeit bestehen, die niemand hat.
4. Beobachtungen aufnehmen — zuerst, was heute gelungen ist (ein einzelner
   Tag unter Ziel ist im Refeeding normal und kein Versagen der Eltern),
   dann Stimmung und was eskaliert ist. Externalisierend formulieren: die
   Krankheit hat den Snack verweigert, nicht das Kind.
5. Bilanz rechnen und **die Elternansicht über `fbt.bilanz.elternansicht(...)`
   erzeugen lassen, nicht von Hand nachbauen** — die Funktion ist die einzige
   Stelle, die garantiert, dass keine Zahl verloren oder verdoppelt wird.
   Zum Beispiel:
   `PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -c "from datetime import date; from fbt.bilanz import lade_tag, elternansicht; print(elternansicht(lade_tag(date(2026, 1, 1))))"`
   (Datum durch das tatsächliche Tagesdatum ersetzen.)
6. Gerichte ohne Kalorienangabe (`unbekannte` in der Bilanz) benennen. Sie
   wurden nicht als 0 gerechnet, sondern fehlen aus der Summe — sag das
   dazu, damit die Tagessumme nicht als vollständig missverstanden wird.
   Ebenso Gerichte nennen, bei denen der Anteil nicht erfasst wurde
   (`angenommen`) und deshalb mit 100 % gerechnet wurde.
7. Liegt der Tag deutlich unter Ziel, schlage vor, wie morgen aufgeholt
   wird — schrittweise, nicht sprunghaft. Der Arztbrief nennt 100–200 kcal
   pro Schritt. Kein Nachholen an einem einzigen Tag erzwingen.

## Sprache

Keine Belohnungs- oder Bestrafungslogik vorschlagen — nicht "wenn du isst,
dann darfst du", sondern höchstens "sobald du gegessen hast, gehen wir".
Verantwortung übernehmen, einspringen, nicht Kontrolle übernehmen. Die
Krankheit hat den Snack verweigert, nicht das Kind — auch in Beobachtungen
und Notizen.
