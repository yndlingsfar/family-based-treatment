---
name: mahlzeit-planen
description: Use when planning meals for a day of family-based refeeding - building a day of six meals that reaches a prescribed calorie target, choosing recipes, and preparing the shopping list
---

# Einen Tag planen

## Voraussetzungen

Die Module unter `fbt/` liegen im Plugin-Verzeichnis, nicht im Arbeitsordner
der Eltern. Ohne Pfadangabe findet Python sie nicht (`ModuleNotFoundError: No
module named 'fbt'`). Deshalb **jeden** Aufruf so beginnen:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -c "..."
```

`CLAUDE_PLUGIN_ROOT` setzt Claude Code selbst; `:-.` ist der Rückfall für den
Fall, dass direkt im Repository gearbeitet wird.

## Was diese Stufe nicht tut

Stufe 1 **plant und protokolliert** — sie begleitet keine laufende Mahlzeit.
Wenn gerade ein voller Teller auf dem Tisch steht und es eskaliert, ist dieses
Werkzeug nicht die Hilfe: dann gilt, was im Elternnetzwerk und mit der Praxis
besprochen ist (ruhig bleiben, bei der Mahlzeit bleiben, später essen lassen,
Ersatz in flüssiger Form anbieten), nicht ein Chat. Geht es um Ohnmacht,
Erbrechen, Selbstverletzung oder Äußerungen über Suizid: Praxis, außerhalb der
Sprechzeiten die Kinderklinik, bei Suizidalität sofort Notaufnahme oder 112.
Sag das offen, statt im Moment der Eskalation eine Planungsantwort zu geben.

## Vorab immer

1. Profil laden:
   `PYTHONPATH="${CLAUDE_PLUGIN_ROOT:-.}" python3 -c "from fbt.daten import lade_profil; p = lade_profil(); print(p)"`
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
  Die erste Wahl an schwierigen Tagen und wenn es schnell gehen muss. Trägt ein
  Rezept `pruefen: true`, lies `pruefnotiz` und unterscheide zwei Fälle: "nicht
  prüfbar" heißt, es ließ sich keine Zutat zuordnen — das ist weder bestätigt
  noch widerlegt, nur ungeprüft; eine Abweichung in Prozent heißt, die Zahl ist
  tatsächlich in Zweifel. Nur im zweiten Fall die Zahl mit Vorsicht behandeln
  oder gegenrechnen.
- **Cookidoo** über den Connector — für Abwechslung und wenn sich das Kind etwas
  Normales wünscht. `cookidoo_get_recipe_details` liefert `nutrition` mit
  `basisQuantity`/`basisUnit`. Steht dort `1 Portion`, den Wert direkt
  übernehmen. Steht dort `100 g`, **nicht** umrechnen — dafür bräuchtest du das
  Portionsgewicht, und das liefert Cookidoo meist nicht mit. Ist `nutrition`
  null oder die Basis nicht auf die Portion umlegbar, hat das Rezept effektiv
  keine verlässliche Angabe: rechne die Zutaten dann selbst zusammen über
  `fbt.anreicherung.lade_grundzutaten()` und `lade_mittel()` (beide liefern
  `Mittel.kcal(menge, einheit)`). Lässt sich ein nennenswerter Teil der Zutaten
  keiner der beiden Tabellen zuordnen, sag das offen — das Gericht kommt dann
  ohne `kcal_geplant` in die Tagesdatei, nicht mit einer geschätzten Zahl.
  `fbt.anreichern.anreichern` ist für dieses Problem der falsche Weg: es setzt
  `kcal_pro_portion` als bekannten Ausgangswert voraus und kann ihn nicht
  ermitteln — es rechnet nur aus, was zusätzlich hineinmuss, um ein Ziel zu
  erreichen.

Plane höchstens einen Tag im Voraus. Mut kommt in Wellen; ein Plan von gestern
verschenkt den Moment, in dem heute etwas geht.

## Regeln aus der Behandlung

- Die Eltern entscheiden, was auf den Teller kommt. Das Kind wählt nicht aus,
  wiegt nicht ab, sieht keine Kalorien.
- Keine Light- und Diätprodukte.
- Bei jeder Mahlzeit mindestens 300 ml Getränk anbieten, am besten Saft.
- In der Refeeding-Phase kein Maltodextrin ohne ärztliche Absprache.
- Kann eine Mahlzeit nicht geschafft werden, sind dieselben Kalorien in
  anderer Form (ein Shake) ein Ersatz — kein Ausgleich für ein Fehlverhalten
  und nie als Konsequenz formuliert.

## Ausgabe

Immer **zwei** Fassungen, beide von `fbt.bilanz` erzeugen lassen, nicht von
Hand nachbauen — nur so ist sichergestellt, dass keine Zahl durchrutscht:

1. **Elternansicht** (`fbt.bilanz.elternansicht(tagesbilanz)`) — mit kcal je
   Gericht und Tagessumme, plus was vorzukochen ist. Für die Eltern, nicht für
   den Kühlschrank, und nie auf dem Bildschirm, wenn das Kind mitliest.
2. **Tischansicht** (`fbt.bilanz.tischansicht(tagesbilanz)`) — nur Uhrzeit und
   was es gibt. Keine Kalorien, kein Gewicht, kein Ziel. Schreibe sie
   zusätzlich als Datei, damit sie ausgedruckt oder auf einem eigenen Gerät
   geöffnet werden kann, ohne dass jemand auf den Bildschirm mit der
   Elternansicht sieht — **aber niemals nach `$FBT_DATEN`**. Standard:
   `~/Desktop/JJJJ-MM-TT-tisch.txt`, sonst das aktuelle Arbeitsverzeichnis.
   Das Datenverzeichnis enthält jede Tagesdatei mit `kcal_geplant`, den
   Gewichtsverlauf und das Profil. Einen Pfad dorthin weiterzugeben heißt,
   dem Kind den Weg in die Kalorienakte zu zeigen — und ein Kind mit
   Anorexie geht diesen Weg. Die Tischansicht ist die eine Ausgabe, die das
   Kind sehen darf; sie gehört deshalb genau dorthin, wo sonst nichts liegt.
   `tischansicht` bricht ab, wenn ein Gerichttitel eine Kalorienangabe trägt
   — dann gehört die Zahl aus dem Titel in der Tagesdatei entfernt.

Schreibe den Plan als `$FBT_DATEN/tage/JJJJ-MM-TT.toml` nach dem Muster in
`referenz/tag.vorlage.toml`. **Alle Schlüssel auf oberster Ebene vor die erste
`[[mahlzeit]]`-Tabelle**, sonst landet `beobachtungen` (oder `ziel_kcal`, oder
`datum`) in der letzten Mahlzeit statt auf Tagesebene — der Loader lehnt eine
solche Datei inzwischen mit einer klaren Fehlermeldung ab, aber es ist die eine
Art, wie eine Tagesdatei unbrauchbar geschrieben werden kann. Lieber einmal
gegen die Vorlage gegenprüfen, bevor die Datei steht.

Fehlt der ärztliche Wert, bleibt `ziel_kcal` in der Datei ganz weg — keine
Rechengröße, mit der du die sechs Mahlzeiten verteilt hast, darf dort als Zahl
landen, auch kein Platzhalter. Ist der einzige vorhandene Wert laut
`kcal_quelle` selbst ein Platzhalter, gehört seine Herkunft in den
`beobachtungen`-Freitext ("kcal_taeglich laut Profil ist ein Platzhalter, noch
nicht ärztlich bestätigt"), nicht als bare `ziel_kcal`-Zahl, die wie eine
Vorgabe aussähe.

## Einkauf

`cookidoo_add_recipe_ingredients` fügt **alle** Zutaten eines Rezepts hinzu,
nicht nur die fehlenden — nutze es für Rezepte, die tatsächlich gekocht
werden, nicht als Filter für offene Posten. Für alles, was nicht aus einem
Cookidoo-Rezept stammt, `cookidoo_add_additional_items`.

**Die Cookidoo-Liste liegt auf dem Familienkonto und ist auch am Thermomix in
der Küche sichtbar.** Anreicherungsmittel dort neutral und ohne Mengenangabe
eintragen (z. B. „Sahne", nicht „Sahne 30 % 6 Becher"; kein „Maltodextrin
500 g" mit Menge) — die Anreicherungsstrategie gehört nicht auf ein Gerät, vor
dem das Kind stehen kann.

## Sprache

Externalisierend sprechen: die Krankheit hat den Snack verweigert, nicht das
Kind. Keine Belohnungs- oder Bestrafungslogik — nicht "wenn du isst, dann
darfst du", sondern höchstens "sobald du gegessen hast, gehen wir".
Verantwortung übernehmen, einspringen, nicht Kontrolle übernehmen.
