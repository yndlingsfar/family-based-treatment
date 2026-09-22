---
name: verlauf-auswerten
description: Wertet dokumentierte Gewichts- und Mahlzeitenverlaeufe fuer Eltern aus und erstellt einen Wochenbericht fuer Arzttermine beim Family-Based Treatment.
---

# Verlauf auswerten

Nutze `fbt.verlauf` und `fbt.wochenbericht` im Plugin-Verzeichnis. Alle
Aufrufe beginnen mit `PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}"`. Daten liegen
unter `FBT_DATEN`, ausserhalb des Repositories. Bericht und Diagramm sind
nur fuer Eltern und Behandlungsteam; es gibt keine Tischansicht.

## Vor der Auswertung

Frage ausdruecklich nach den Warnzeichen aus `commands/tagesabschluss.md`,
fuer den angefragten Berichtszeitraum und nach ihrem aktuellen Bestehen.
Bei akuten Warnzeichen zuerst medizinische Hilfe organisieren, nicht erst
einen Bericht erzeugen. Bei bereits abgeklärten Ereignissen Zeitpunkt und
ärztliche Rückmeldung als Elternbeobachtung festhalten, nicht selbst entwarnen.

- `profil.toml` laden. Fehlende Daten nennen, nicht erfinden.
- `gewicht.csv` nach der Vorlage in `docs/stufe-2.md` erfassen: bestaetigte
  Werte, Datum, Uhrzeit und Messumstaende. Keine Messungen auslassen,
  mitteln oder durch Vermutungen ersetzen. Bei zwei Werten am selben Tag
  klaeren, welcher bestaetigte Tageswert fuer den Verlauf gelten soll.
- Fuer BMI: Datum der Groessenmessung und `bmi_referenz` im Profil explizit
  erfragen, sofern sie fehlen. Die Referenzkurve nicht aus Rufnamen ableiten.
  Ein Bericht ohne BMI bleibt nutzbar.

## Rechnen und berichten

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -m fbt.wochenbericht --bis JJJJ-MM-TT
```

Der Zeitraum umfasst den Stichtag und sechs Tage davor; fuer Gewicht und
Warnungen werden alle vorhandenen Messungen bis zum Stichtag betrachtet.
`--symptome-geprueft` nur verwenden, wenn alle abgefragten Warnzeichen fuer
diesen Zeitraum ausdruecklich verneint wurden. Berichtete Zeichen mit
`--warnzeichen` uebergeben; die gueltigen Namen zeigt `--help`. Ohne Angaben
steht im Bericht, dass die Pruefung fehlt. Freitext wird nicht automatisch
auf Symptome untersucht.

`--frage "..."` sammelt offene Fragen. Daten und Zahlen immer aus dem
Skript uebernehmen; keine eigenen Mittelwerte oder Perzentile berechnen.
Fehler des Loaders zuerst beheben. Fehlende Tage und unvollstaendige
Summen nicht als null oder vollstaendige Woche darstellen.

Mit `--speichern` entstehen Markdown und druckbares HTML im privaten
Unterordner `berichte/`; ein vorhandener Bericht fuer denselben Stichtag
wird ersetzt. `--diagramm` erzeugt zusaetzlich eine PNG-Kurve und bettet sie
ins HTML ein. Dafuer ist die optionale Abhaengigkeit aus
`requirements-diagramm.txt` noetig. Ein fehlendes Diagramm ist zu benennen.
Keine Berichte eigenstaendig versenden.

Die gewichtsbasierten Hinweise sind datiert und bleiben sichtbar, auch
wenn sie historisch sind. Bei aktuellen oder noch ungeklärten Hinweisen
an die Praxis verweisen, keine Optimierung zu Hause ableiten. Eine bereits
erfolgte Abklaerung als Elternangabe in den Bericht aufnehmen.

## Grenzen

Vergleichslinie ist die Profilvorgabe, kein neu festgelegtes Zielgewicht.
Die Quelle `zunahme_quelle` nennen; fehlt sie, nicht als aerztlich bestaetigt
bezeichnen. KiGGS-Perzentile sind eine beschreibende Naeherung, keine
Behandlungsempfehlung. Details zu Interpolation, Messluecken und den
technischen Zeitgrenzen stehen in `docs/stufe-2.md`.
