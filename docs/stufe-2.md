# Stufe 2: Verlauf und Wochenbericht

Implementiert am 22.09.2026. Python >=3.11. Zahlenberechnung und Text/HTML
benoetigen nur die Standardbibliothek; die optionale Kurve Matplotlib:

```bash
python3 -m pip install -r requirements-diagramm.txt
```

## Private Eingaben

`FBT_DATEN` zeigt auf den privaten Eltern-Datenordner ausserhalb des Repos.
Vorhandene Tagesdateien bleiben kompatibel. `gewicht.csv` ist UTF-8 mit
Komma als Trennzeichen und genau diesem Kopf (eine bestaetigte Messung je Tag):

```csv
datum,gewicht_kg,uhrzeit,bedingungen,gewogen_von,blind
```

Datum: `JJJJ-MM-TT`; Gewicht: positive Zahl mit Dezimalpunkt; Uhrzeit:
`HH:MM`; blind: `true`, `false` oder leer. Texte mit Kommas in doppelte
Anfuehrungszeichen setzen. Fehlende Messumstaende sind erlaubt, werden aber
im Bericht als Luecke benannt. Keine Leerwerte beim Datum oder Gewicht,
keine Duplikate, unendlichen Zahlen oder zukuenftigen Messungen.

Im Profil unter `[kind]` optional ergaenzen:

```toml
# Auswahl der RKI-Referenzkurve; keine Ableitung aus dem Rufnamen:
# bmi_referenz = "maedchen"  # alternativ: "jungen"
# groesse_gemessen_am = JJJJ-MM-TT
```

Unter `[ziele]` kann `zunahme_quelle = "wer, wann"` ergaenzt werden. Die
vorhandene `zunahme_g_pro_woche` steuert die Vergleichslinie. Ohne Quelle
steht im Bericht ausdruecklich, dass die aerztliche Bestaetigung fehlt.
Die aktuelle Vorgabe wird ab der ersten Gewichtsmessung aufgetragen;
Zielaenderungen im Verlauf werden noch nicht historisiert.

## Befehle

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -m fbt.verlauf --datum 2026-09-22
PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -m fbt.wochenbericht --bis 2026-09-22 --speichern --diagramm
```

Ohne `--bis`/`--datum`: heute. Berichtszeitraum: sieben Kalendertage
inklusive Stichtag, nicht zwingend Montag–Sonntag. Gewichtsdaten werden
bis zum Stichtag aus dem gesamten Bestand ausgewertet. Spaetere Messungen
fliessen nicht in einen rueckblickenden Bericht ein.

Die Symptompruefung erfolgt im Gespraech: ohne Argument ist sie unbekannt;
`--symptome-geprueft` dokumentiert ausdrueckliches Verneinen aller Zeichen;
`--warnzeichen erbrechen` etc. dokumentiert berichtete Zeichen (Liste in
`--help`). Freitext-Beobachtungen sind keine maschinenlesbare Symptompruefung.
`--frage "..."` kann mehrfach angegeben werden.

Export nach `berichte/wochenbericht-JJJJ-MM-TT.md` und `.html`, optional
`.png`. HTML enthaelt die Grafik selbst und ist offline druckbar (auch als
PDF ueber den Browser). Vorhandene Exporte desselben Stichtags werden ersetzt.
Kein Versand, keine Daten im Repository, keine Tischansicht.

## Festgelegte Rechenregeln

- Gewichtsabnahme: jeder Rueckgang zwischen zwei aufeinanderfolgenden
  Messungen wird mit Datum und Differenz benannt. Es wird keine Ursache
  vermutet; unterschiedliche Messumstaende werden separat genannt.
- Keine Zunahme ueber zwei Wochen: fuer jede Messung Vergleich mit dem
  zeitlich naechsten vorhandenen Wert mindestens 14 Tage zuvor. Bei gleicher
  oder geringerer Masse wird fehlende Netto-Zunahme im tatsaechlichen
  Intervall gemeldet, nicht behauptet, jeder Zwischentag sei unveraendert.
- Mehr als sieben Tage zwischen Messungen oder seit der letzten Messung
  werden als Datenluecke markiert. Fuer einen aktuellen Zweiwochenvergleich
  muss ein Vergleichswert 14–21 Tage vor der letzten Messung vorliegen.
  Diese Grenzen sind technische Regeln fuer Datenabdeckung, keine neue
  medizinische Vorgabe zum Wiegen. Fehlende Abdeckung ist keine Entwarnung.
- Historische Warnungen bleiben datiert sichtbar. Das System kennt ihren
  aerztlichen Abklaerungsstatus nicht. Dokumentierte Rueckmeldungen der
  Eltern gehoeren in Beobachtungen, nicht in eine automatische Entwarnung.
- Trend: Differenz zwischen erstem und letztem Messwert, geteilt durch die
  tatsaechlich vergangenen Tage und auf sieben Tage umgerechnet. Keine
  Regression, Prognose oder automatische Anpassung des Essensplans.
- Tagesdurchschnitt nur ueber vollstaendig erfasste Tage; Nenner wird
  angegeben. Fehlende Tagesdateien, Mahlzeiten, kcal oder Anteile sind
  Luecken. Bei fehlendem Anteil liefert Stufe 1 einen 100-%-Annahmewert;
  dieser erscheint markiert und geht nicht in den Durchschnitt ein.
  Die Mahlzeitenzahl wird gegen das Profil geprueft; ihre inhaltliche
  Vollstaendigkeit muessen die Eltern bestaetigen.
- Tagesziele werden aus der historischen Tagesdatei gelesen; keine
  Ersetzung durch das heutige Profil. Freitexte bleiben Elternangaben.

## BMI und Quellen

[RKI, Referenzperzentile, 2. Auflage 2013](https://edoc.rki.de/handle/176904/3254),
Methodik gedruckte Seiten 9–10, BMI-Tabellen Seiten 40–41. Die Zahlen in
`referenz/kiggs_bmi_lms.json` wurden direkt aus den beiden PDF-Tabellen
extrahiert (Altersbereich 2 bis 18 Jahre, je 33 Stuetzstellen). Quelle und
SHA-256 des Ursprungs-PDFs sind enthalten; keine personenbezogenen Daten.

BMI wird nur fuer die letzte Messung ausgewiesen, mit Datum und Groesse.
Ohne Groessendatum, bei Groesse nach dem Wiegedatum oder mehr als 90 Tage
zuvor wird kein BMI ausgegeben. 90 Tage ist eine konservative technische
Gueltigkeitsgrenze, keine klinische Aussage ueber Messintervalle.

Alter wird am Wiegedatum als vollendete Lebensjahre plus Anteil am laufenden
Lebensjahr berechnet; fuer Geburt am 29. Februar gilt im Nichtschaltjahr der
28. Februar. L, M und S werden zwischen den halbjaehrlichen Stuetzstellen
linear interpoliert. Das ist eine **Naeherung**, keine Rekonstruktion der
urspruenglichen RKI-Splines. z = ((BMI/M)^L - 1)/(S*L), bei L=0 logarithmisch;
Perzentil ueber die Standardnormalverteilung. Unter P0,2 bzw. ueber P99,8
wird nur der Randbereich angegeben, weil dort die Unsicherheit besonders
gross ist. Referenzkurve muss explizit angegeben werden. Keine Extrapolation
unter 2 oder ueber 18 Jahre, kein daraus abgeleitetes Zielgewicht.

[NICE NG69](https://www.nice.org.uk/guidance/ng69/chapter/Recommendations)
fordert koerperliche und psychische Ueberwachung im Behandlungskontext.
Die hier umgesetzten Gewichtsregeln stammen aus dem bestehenden Projektentwurf;
sie ersetzen keine Beurteilung von Symptomen, Kreislauf, Labor oder Gesamtzustand.
