---
description: Erstellt einen Wochenbericht mit Gewichtsverlauf, Tagesbilanzen und offenen Fragen fuer den Arzttermin
argument-hint: "[JJJJ-MM-TT]"
---

Erstelle den Wochenbericht mit dem Skill `verlauf-auswerten`. Argument
(`$ARGUMENTS`): letzter Tag des Berichts (JJJJ-MM-TT), ohne Argument heute.

1. Die Warnzeichen gemaess `commands/tagesabschluss.md` aktiv fuer den
   Berichtszeitraum abfragen; bei akuten Hinweisen zuerst den dort genannten
   medizinischen Weg gehen. Der Bericht darf Hilfe nicht verzoegern.
2. Vorhandene Gewichts- und Tagesdaten nutzen. Fehlende Messungen,
   Messumstaende und offene Fragen mit den Eltern klaeren. Keine Zahlen
   erfinden; ohne Ergaenzungen den unvollstaendigen Stand sichtbar lassen.
3. `PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -m fbt.wochenbericht --bis JJJJ-MM-TT`
   mit den zutreffenden Symptom- und Frageargumenten des Skills ausfuehren.
   Warnungen und Datenluecken zuerst zeigen. Aus historischen Hinweisen
   keinen aktuellen Zustand behaupten; nach bereits erfolgter Abklaerung fragen.
4. Mit `--speichern --diagramm` im privaten Datenordner ablegen und den
   HTML-Bericht verlinken. Matplotlib wird fuer die Grafik benoetigt (siehe
   `docs/stufe-2.md`); fehlt es, Text/HTML ohne Diagramm erzeugen und das
   fehlende Diagramm benennen. Zahlen und Berechnungen kommen aus dem Skript.

Nur fuer Eltern und Behandlungsteam. Kein automatischer Versand, keine
Tischansicht, keine Diagnose und keine neue medizinische Zielvorgabe.
