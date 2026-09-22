# FBT-Plugin — Design

Stand: 2026-09-21

**Umsetzungsstand 22.09.2026:** Stufe 1 ist gemergt, einschliesslich der
Digitalisierung von 79 Kochbuchrezepten (siehe `docs/kochbuch-import.md`).
Stufe 2 ist implementiert: Gewichtsverlauf, BMI/KiGGS-Naeherung und
Wochenbericht. Verbindliche Rechenregeln, Datenformat, technische Grenzen
und Bedienung stehen in [`docs/stufe-2.md`](../../stufe-2.md).
Insbesondere ist die Vergleichslinie konfigurierbar statt fest 500 g/Woche;
BMI braucht eine datierte Groesse und eine explizite Referenzkurve.
Die folgenden Abschnitte dokumentieren den urspruenglichen Entwurf;
Hinweise wie „kommt mit Stufe 2“ und die offene Kochbuch-Digitalisierung
sind damit ueberholt. Stufe 3 bleibt offen.

## 1. Kontext und Ziel

Eine Familie führt das Family-Based Treatment (FBT) für ihre 12-jährige Tochter
zu Hause durch. Das Refeeding läuft bereits. Dieses Projekt baut ein Plugin, das
die Eltern im Alltag entlastet.

Benannte Schmerzpunkte, in dieser Reihenfolge:

1. **Kalorientracking und Mahlzeitenplanung** — jeden Tag sechs Mahlzeiten mit
   ausreichend Energie planen, einkaufen und hinterher wissen, was tatsächlich
   angekommen ist.
2. **Überblick und Verlauf** — Gewichtsentwicklung, Trend, Bericht für die Ärztin.
3. **Die Mahlzeit selbst** — Widerstand, Verhandeln, Verweigern am Tisch.

Genutzt wird das Plugin am Laptop: vor der Mahlzeit zum Planen, abends zum
Abschluss, wöchentlich zur Vorbereitung von Arztterminen. **Nicht** am Handy in
der akuten Situation. Hilfe für den Moment am Tisch nimmt deshalb die Form von
Vorbereitetem an (gedruckter Spickzettel), nicht von Live-Interaktion.

### Erfolgskriterium

Die Eltern verbringen weniger Zeit mit Logistik und Rechnen, und haben zu jedem
Zeitpunkt eine belastbare Antwort auf: *Hat sie heute genug bekommen?* und
*Geht es voran?*

## 2. Nicht-Ziele

- Kein Ersatz für ärztliche Begleitung. FBT setzt somatische Überwachung voraus
  (wöchentlich Gewicht, Puls, Blutdruck, Labor; in der Startphase Phosphat,
  Kalium, Magnesium wegen Refeeding-Syndrom).
- Keine Diagnostik, keine Festlegung von Zielgewichten (macht die Ärztin).
- Keine App für die Erkrankte. Das Plugin ist ein Elternwerkzeug.
- Keine Handy-/Echtzeit-Oberfläche in dieser Ausbaustufe.

## 3. Leitplanken

Diese Punkte sind nicht verhandelbar und gelten für jede Komponente.

### 3.1 Zwei Ausgabeformen

- **Elternansicht** — mit Kalorien, Gewicht, Zielwerten.
- **Tischansicht** — Tagesplan zum Aushängen, Spickzettel, Einkaufszettel.
  Enthält **nie** Kalorien, Gewicht oder Zielwerte.

Das ist keine umschaltbare Einstellung, sondern zwei getrennte Ausgabepfade.
Eine Einstellung kann man vergessen; einen fehlenden Codepfad nicht.

Begründung: Beide Elternnetzwerk-Dokumente empfehlen unabhängig voneinander,
Kalorienangaben vor der Erkrankten zu verbergen (Verpackungsangaben schwärzen,
Produkte umfüllen). Ein sichtbarer Kalorienzähler arbeitet gegen die Therapie.

### 3.2 Eskalationskriterien

Automatisch geprüft bei jedem Tagesabschluss und Wochenbericht:

- keine Gewichtszunahme über zwei Wochen
- Gewichtsabnahme
- Bradykardie, Ohnmacht, orthostatische Beschwerden
- Erbrechen, Abführmittelgebrauch
- Selbstverletzung, Suizidalität

Trifft eines zu, nennt das Plugin dies **zuerst** und berät nicht über
Optimierung zu Hause weiter, sondern verweist an Ärztin/Klinik.

Die Kriterien zerfallen in zwei Gruppen, die zu unterschiedlichen Zeitpunkten
verfügbar werden:

- **Symptombasiert** (Ohnmacht, Erbrechen, Selbstverletzung, Suizidalität) —
  von den Eltern berichtet, ab Stufe 1 prüfbar.
- **Verlaufsbasiert** (keine Zunahme über zwei Wochen, Abnahme) — braucht
  `verlauf.py` und damit Stufe 2.

Bis Stufe 2 steht, weist der Tagesabschluss ausdrücklich darauf hin, dass die
verlaufsbasierten Kriterien noch nicht automatisch geprüft werden. Eine
unvollständige Prüfung darf nicht wie eine vollständige aussehen.

### 3.3 Sprache

- Externalisierung durchgängig: „die Krankheit will das", nicht „<Name> will das".
- „Verantwortung übernehmen" / „einspringen", nicht „Kontrolle übernehmen"
  (Le Grange vermeidet Letzteres bewusst).
- „Sobald–dann", nicht „wenn–dann".
- Keine Belohnungs-/Bestrafungslogik. FEAST und FBT-Manual sind hier deutlich:
  Drohungen eskalieren einen Machtkampf, den das Kind durch Weniger-Essen
  gewinnt.

### 3.4 Rechnen statt schätzen

Jede Zahl, die in einer Tagesbilanz oder einem Arztbericht landet, kommt aus
einem Skript, nicht aus einem Sprachmodell. Unbekannte oder mehrdeutige Werte
werden **gemeldet, nicht geraten**.

## 4. Teil A — Erweiterung von `cookidoo-mcp`

Voraussetzung für alles Weitere. Eigener Branch und PR im Repo
`/Users/danielsteiner/Projects/cookidoo-mcp`, TDD.

### 4.1 Befund

Der Endpunkt `RECIPE_PATH` (`cookidoo.de/recipes/recipe/{language}/{id}`),
den `getRecipeDetails` bereits aufruft, liefert `nutritionGroups` und
`recipeStepGroups` mit. `recipeDetailsFromJson` in `cookidoo.mappers.ts:169`
mappt beide nicht.

Belegt an `r16687` (Kartoffelsuppe, 4 Portionen):

```json
"nutritionGroups": [{ "recipeNutritions": [{
  "quantity": 1, "unitNotation": "Portion",
  "nutritions": [
    { "type": "kcal",         "number": 229, "unittype": "kcal" },
    { "type": "protein",      "number": 5,   "unittype": "g" },
    { "type": "fat",          "number": 14,  "unittype": "g" },
    { "type": "carb2",        "number": 19,  "unittype": "g" },
    { "type": "dietaryFibre", "number": 5.9, "unittype": "g" },
    { "type": "kJ",           "number": 959, "unittype": "kJ" }]}]}]
```

### 4.2 Änderungen

Neue Typen in `cookidoo-recipe.type.ts`:

```ts
export interface CookidooNutritionValue {
  readonly type: string;   // 'kcal' | 'protein' | 'fat' | 'carb2' | ...
  readonly number: number;
  readonly unit: string;
}

export interface CookidooNutrition {
  readonly basisQuantity: number;   // z. B. 1
  readonly basisUnit: string;       // 'Portion' | '100 g'
  readonly values: CookidooNutritionValue[];
}

export interface CookidooRecipeStep {
  readonly group: string | null;
  readonly number: string | null;   // Schrittnummer, kommt als `title`
  readonly text: string;
}
```

In `CookidooRecipeDetails` ergänzen:

```ts
readonly nutrition: CookidooNutrition | null;
readonly steps: CookidooRecipeStep[];
```

`recipeDetailsFromJson` erweitern; Tests in `cookidoo.mappers.spec.ts` im Stil
der bestehenden Fälle.

### 4.3 Entwurfsentscheidungen

- **Bezugsgröße bleibt erhalten.** `basisUnit` wird durchgereicht, nicht auf
  „Portion" normalisiert. Andernfalls droht ein Rechenfehler um ein Vielfaches
  in einer Bilanz, die zur Ärztin geht. Die Stichprobe über 12 Rezepte zeigt,
  wie nötig das ist: vorgefunden wurden `Portion`, `Stück`, `ración`, `portion`,
  `porce`, `porci` und `dose`. Ein Mapper, der „pro Portion" annimmt, liegt
  allein bei `Stück` schon falsch.

- **Mehrere Bezugsgrößen: die beschriftete gewinnt.** Manche Rezepte liefern
  mehrere `recipeNutritions`-Einträge. `r12345` etwa hat
  `{quantity: 1, unitNotation: "dose", 548 kcal}` **und**
  `{quantity: 16, unitNotation: null, 8768 kcal}` — pro Portion und fürs ganze
  Rezept, Faktor 16. Der Mapper wählt explizit den Eintrag mit nicht-leerer
  Bezeichnung, nie nach Array-Position. Ein `basisUnit: ""` wird nie
  ausgegeben: eine unbeschriftete Bezugsgröße heißt „wir kennen die
  Bezugsgröße nicht" und gehört damit in denselben Topf wie fehlende Werte,
  also nach `null`.

- **Zahlen werden geprüft, nicht gecastet.** `Number()` ist hier verboten:
  `Number('') === 0` und `Number.isNaN(0) === false`, ein leerer Upstream-Wert
  würde also als selbstbewusste **0 kcal** durchgereicht — genau das
  „fehlend ≠ null", das diese Leitplanke verhindern soll, nur durch die
  Wertefilter-Tür statt durch die Null-Tür. Geprüft wird mit
  `typeof x === 'number' && Number.isFinite(x)`. Eine vorhandene, aber
  nicht-numerische `quantity` macht den Eintrag unbrauchbar, statt still auf 1
  zu defaulten — ein Default würde „pro eine Einheit" behaupten, ohne Beleg.
- **Cookidoos Typnamen bleiben roh.** Kein Umbenennen von `carb2` oder `kJ`.
- **`nutrition` ist nullable.** Nicht jedes Rezept hat Nährwerte; fehlend ist
  nicht dasselbe wie null Kalorien, und das Plugin muss den Unterschied sehen.
- **Schritttexte werden zu reinem Text.** Alle HTML-Tags werden entfernt und die
  gängigen Entities dekodiert. Thermomix-Angaben wie „14 Min./Varoma/Stufe 1"
  sind Inhalt und bleiben erhalten; Hervorhebungen gehen bewusst verloren, weil
  dieser Text am Küchentisch vorgelesen und auf den Spickzettel gedruckt wird.

  *Korrektur vom 21.09.2026:* Hier stand ursprünglich, `<NOBR>` sei das einzige
  Markup und „der übrige Text bleibt unverändert". Das war empirisch falsch. Eine
  Stichprobe über 12 Live-Rezepte ergab `nobr` ×58, `strong` ×46, `&nbsp;` ×20,
  dazu `<p>`, `<i>`, `&deg;`, `&ccedil;`, `&eacute;`, `&quot;`. Ein Rezept lieferte
  `"Pr&eacute;-aque&ccedil;a o forno a 180&deg;C."`. Auch das Abnahmerezept
  `r16687` enthält in Schritt 5 ein `<strong>`.
- **Suchendpunkt bleibt unangetastet** — liefert keine Nährwerte, Scope bleibt
  eng.

### 4.4 Offen gelassen: mehrere Bezugsgrößen gleichzeitig

`CookidooNutrition` hält genau eine Bezugsgröße. Für `r12345` heißt das, dass die
Angabe fürs ganze Rezept verworfen wird — richtig für unseren Zweck, aber der
Typ kann nicht abbilden, was die API dort tatsächlich liefert. Falls ein
späterer Verbraucher beide braucht, wäre `bases: CookidooNutrition[]` die
Erweiterung. Bewusst nicht in dieser Ausbaustufe: die Auswahlregel oben macht
die einfache Form sicher, und wir brauchen genau eine Zahl pro Mahlzeit.

### 4.5 Abnahme

`get_recipe_details` für `r16687` gibt 229 kcal pro Portion und die
Zubereitungsschritte zurück. Bestehende Tests bleiben grün.

## 5. Teil B — Aufbau des Plugins

```
family-based-treatment/
├─ .claude-plugin/plugin.json
├─ skills/
│   ├─ fbt-grundlagen/           Phasen, Prinzipien, Externalisierung, Sprache
│   ├─ mahlzeit-planen/          Tag aus 6 Mahlzeiten bauen, kcal-Ziel treffen
│   ├─ rezept-anreichern/        Rezept auf Ziel-kcal bringen
│   ├─ mahlzeit-nachbesprechen/  Debrief, was half, was morgen anders
│   ├─ verlauf-auswerten/        Gewicht, kcal, Trend, Warnsignale
│   └─ schwierige-situation/     Beratung + Eskalationsprüfung
├─ commands/
│   ├─ tagesplan.md              /tagesplan [morgen|heute]
│   ├─ tagesabschluss.md         /tagesabschluss
│   ├─ wochenbericht.md          /wochenbericht
│   └─ spickzettel.md            /spickzettel
├─ referenz/
│   ├─ kochbuch.schema.json      Schema + Importer, NICHT die Rezepte selbst
│   ├─ anreicherung.json         ~30 Anreicherungsmittel, kcal/100 g
│   ├─ formulierungen.md         Connect-before-Direct, Sätze für den Tisch
│   ├─ eskalation.md             harte Kriterien
│   └─ haus-sichern.md           Checkliste aus dem Netzwerk-PDF
└─ scripts/
    ├─ bilanz.py                 Tagesbilanz aus dem Protokoll
    ├─ verlauf.py                Gewichtskurve, BMI-Perzentil, 500-g-Linie
    └─ anreichern.py             Rezept + Ziel-kcal → Zutatenänderung
```

### 5.1 Trennung Plugin / Daten

Das Repo enthält **keinen einzigen personenbezogenen Datenpunkt** — auch nicht
in Beispielen, Vorlagen oder Tests. Testdaten tragen erfundene Namen und Werte.

*Nachtrag vom 21.09.2026:* In den ersten Fassungen dieser Spec stand der Rufname
des Kindes in einem Beispielblock. Er ist jetzt ersetzt, steht aber weiterhin in
der Git-Historie der Commits f4a4e1d/536f30e. Ein vollständiges Entfernen
erforderte ein Umschreiben der Historie — eine Entscheidung, die Daniel trifft.

Die Daten liegen unter:

```
~/Library/Mobile Documents/com~apple~CloudDocs/FBT-Daten/
```

Konfigurierbar über `FBT_DATEN` (Umgebungsvariable), Vorgabe wie oben. Der Pfad
enthält Leerzeichen — alle Skripte müssen ihn korrekt quoten; ein Test deckt das
ab.

Bewusst **kein** `.gitignore`-Unterordner: ein `.gitignore` ist durch ein
versehentliches `git add -f` oder einen Copy-Vorgang ausgehebelt. Ein anderer
Ordner ist strukturell sicher.

Abwägung, die die Familie getroffen hat: iCloud gibt beiden Elternteilen
denselben Stand — dafür liegen Gesundheitsdaten eines Kindes bei einem
Cloud-Anbieter.

## 6. Datenmodell

### 6.1 `profil.toml`

*Korrektur vom 21.09.2026:* ursprünglich als YAML geplant. TOML, weil `tomllib`
Standardbibliothek ist. Das folgende Beispiel bleibt in YAML-Notation stehen,
weil es nur die Felder zeigt; verbindlich ist `referenz/profil.vorlage.toml`.

```yaml
kind:
  rufname: Vorname
  geburtsdatum: null        # für BMI-Perzentil (KiGGS) nötig
  groesse_cm: null
ziele:
  kcal_taeglich: null       # ärztlich vorgegeben
  kcal_quelle: null         # wer, wann — Nachvollziehbarkeit
  zunahme_g_pro_woche: 500
  zielgewicht_kg: null      # legt die Ärztin fest
behandlung:
  phase: 1
  aerztin: null
  naechster_termin: null
  wiegen: null              # z. B. "blind, montags 7:30, Unterwäsche"
mahlzeiten:
  - fruehstueck
  - snack_vormittag
  - mittagessen
  - snack_nachmittag
  - abendessen
  - snack_abend
unvertraeglichkeiten: []
fearfoods: []
```

Alle Felder mit `null` füllt die Familie aus. Das Plugin erfindet keine
medizinischen Vorgaben; fehlt `kcal_taeglich`, fragt es danach, statt einen Wert
anzunehmen.

### 6.2 `gewicht.csv`

```
datum,gewicht_kg,uhrzeit,bedingungen,gewogen_von,blind
```

`bedingungen` als Freitext (Kleidung, Waage), weil der Arztbrief ausdrücklich
gleichbleibende Bedingungen verlangt und Abweichungen die Kurve erklären.

### 6.3 `tage/JJJJ-MM-TT.toml`

Maschinenlesbarer Kopf, menschenlesbarer Rumpf:

```markdown
---
datum: 2026-09-21
ziel_kcal: 3000
mahlzeiten:
  - zeit: "07:30"
    name: Frühstück
    gerichte:
      - titel: Power-Porridge
        quelle: kochbuch:power-porridge-schnell
        kcal_geplant: 800
        anteil_gegessen: 1.0
  - zeit: "10:00"
    name: Snack Vormittag
    gerichte:
      - titel: Melli-Shake
        quelle: kochbuch:melli-shake
        kcal_geplant: 500
        anteil_gegessen: 0.6
---

## Beobachtungen

Freitext: Stimmung, was half, was eskalierte, Auffälligkeiten.
```

`anteil_gegessen` ist eine Schätzung der Eltern (0.0–1.0). Die Bilanz weist
Geplant und Tatsächlich **getrennt** aus und macht die Unsicherheit sichtbar,
statt eine Scheingenauigkeit zu erzeugen.

### 6.4 `kochbuch.json` — liegt bei den Daten, nicht im Plugin

Das Vorwort des Netzwerk-Kochbuchs lautet: *„Es ist nur für den privaten Zweck
des ‚Refeedings' zu nutzen und darf nicht veröffentlicht oder an Dritte
weitergegeben werden."*

Die Rezeptdaten dürfen deshalb **nicht Teil des Plugins** sein — das wäre die
untersagte Weitergabe, sobald das Plugin geteilt wird. Aufteilung:

- **Im Plugin:** `kochbuch.schema.json` (Struktur) und ein Importer, der ein
  Kochbuch-PDF in diese Struktur überführt.
- **Bei den Daten** (`$FBT_DATEN/kochbuch.json`): die Rezepte selbst. Jede
  Familie importiert ihr eigenes Exemplar.

Der Importer bleibt bewusst allgemein genug, dass auch ein anderes Kochbuch
oder eine spätere Fassung eingelesen werden kann.

Struktur:

Je Rezept: `id`, `titel`, `kategorie`, `kcal_gesamt`, `portionen`,
`kcal_pro_portion`, `zutaten[]`, `zubereitung`, `zeit_min`, `geraete[]`,
`allergene[]`, `quelle_seite`.

**Datenqualität:** Die kcal-Angaben im PDF sind teilweise widersprüchlich. Zum
Beispiel Sahne:

| Rezept | Angabe | ergibt |
|---|---|---|
| Melli-Shake | 100 ml = 200 kcal | **200 kcal/100 ml** |
| Shake mit Fruchtquatsch | 100 g = 292 kcal | 292 |
| Bananen-Shake | 200 ml = 622 kcal | 311 |
| Nuss-Shake | 60 g = 187 kcal | 312 |
| Powermilch | 400 ml = 1212 kcal | 303 |

Der Melli-Shake-Wert ist ein Ausreißer. Beim Digitalisieren gilt deshalb:

- Die im PDF angegebene Gesamt-kcal pro Rezept wird übernommen (sie ist
  erprobt), aber gegen die Summe der Einzelzutaten geprüft.
- Weicht die Summe um mehr als 10 % ab, bekommt das Rezept
  `pruefen: true` und eine Notiz. Kein stilles Korrigieren.
- Einzelzutatenwerte aus Rezepten fließen **nicht** in
  `anreicherung.json` ein. Diese Tabelle bekommt eigene, geprüfte Werte.

### 6.5 `referenz/anreicherung.json`

Die ~30 Mittel aus dem Kochbuch-Kapitel „Allgemeine Tipps": Sahne (nach Fettstufe
getrennt), Crème double, Crème fraîche, Mascarpone, Butter, Öle, Maltodextrin,
Nussmus, Parmesan, Trinknahrung, Säfte. Je Eintrag `kcal_100g`, `dichte_g_ml`
(für ml-Angaben), `neutral_im_geschmack`, `einsatz` (wo es unsichtbar bleibt),
`hinweis`.

**Maltodextrin trägt einen Warnhinweis**: in den ersten zwei Wochen des
Refeedings nur nach ärztlicher Absprache (Warnhinweis 2 des Kochbuchs).

## 7. Rechenlogik

### 7.1 `anreichern.py`

Eingabe: Rezept (Kochbuch oder Cookidoo) und Ziel-kcal pro Portion.
Ausgabe: konkrete Zutatenänderungen mit Gramm-Angaben und neuer Bilanz.

Regeln, abgeleitet aus dem Kochbuch:
- Fett und Protein vor Kohlenhydraten (Refeeding-Syndrom-Prophylaxe).
- Ersetzen vor Hinzufügen (Milch → Sahne, Wasser → Brühe), weil sichtbare
  Mengenzunahme Angst auslöst.
- Geschmacksneutrale Mittel bevorzugen.
- Volumen möglichst konstant halten.
- Bei unklaren Mengen (`"1 TL"`, `"3 Prisen"`, `"1"`): **melden, nicht
  schätzen.**

### 7.2 `bilanz.py`

Liest ein Tagesprotokoll, gibt aus: geplant vs. tatsächlich, Abstand zum Ziel,
Verteilung über die sechs Mahlzeiten. Bei deutlicher Unterschreitung ein
Vorschlag, wie am Folgetag aufgeholt wird — schrittweise, nicht sprunghaft
(Arztbrief: Steigerung in 100–200-kcal-Schritten).

### 7.3 `verlauf.py`

Gewichtskurve gegen die Soll-Linie von 500 g/Woche, BMI und BMI-Altersperzentil
nach KiGGS, Prüfung der Eskalationskriterien. Gibt Warnungen als erstes Element
der Ausgabe zurück, nicht als Fußnote.

## 8. Abläufe

**Abends vorher — `/tagesplan morgen`**
Sechs Mahlzeiten mit Summe, gemischt aus Kochbuch (verlässlich) und Cookidoo
(Abwechslung). Berücksichtigt `fearfoods`, Unverträglichkeiten, Vorrat und
Wochentag. Fehlende Zutaten gehen per `cookidoo_add_recipe_ingredients` in die
Cookidoo-Einkaufsliste. Ausgabe in beiden Formen: Elternansicht mit Zahlen,
Tischansicht ohne.

**Am Tisch** — der gedruckte Spickzettel aus `/spickzettel`. Kein Gerät.

**Abends — `/tagesabschluss`**
Erfasst, was tatsächlich gegessen wurde, rechnet die Bilanz, nimmt
Beobachtungen auf, prüft die symptombasierten Eskalationskriterien (siehe 3.2)
und schlägt die Anpassung für morgen vor. Die inhaltliche Nachbesprechung der
Mahlzeit — was half, was eskalierte — kommt mit Stufe 3 dazu; bis dahin
erfasst der Tagesabschluss sie als Freitext.

**Wöchentlich — `/wochenbericht`**
Dokument für die Ärztin: Gewichtsverlauf gegen die 500-g-Linie, kcal-Verlauf,
Auffälligkeiten, offene Fragen. Enthält nie Interpretationen, die einer
ärztlichen Beurteilung vorgreifen.

## 9. Ausbaustufen

**Stufe 1 — Kalorientracking und Mahlzeitenplanung** (Priorität der Familie)
MCP-Erweiterung · Kochbuch-Importer + `kochbuch.json` in den Daten ·
`anreicherung.json` · `anreichern.py` ·
`bilanz.py` · Skills `mahlzeit-planen` und `rezept-anreichern` ·
`/tagesplan` · `/tagesabschluss` · Cookidoo-Einkaufsliste

**Stufe 2 — Überblick und Verlauf**
`verlauf.py` · Skill `verlauf-auswerten` · `/wochenbericht` · Eskalationsprüfung
über den gesamten Verlauf

**Stufe 3 — Die Mahlzeit selbst**
`formulierungen.md` · `/spickzettel` · Skills `mahlzeit-nachbesprechen` und
`schwierige-situation` · `fbt-grundlagen`

Jede Stufe ist für sich nutzbar. Stufe 1 muss ohne Stufe 2 und 3 funktionieren.

## 10. Offene Punkte

- **`profil.toml` ausfüllen.** Geburtsdatum, Größe, ärztlich vorgegebene
  Tages-kcal, Wiegemodus. Ohne diese Angaben kann Stufe 1 planen, aber keine
  Zielerreichung beurteilen.
- **am-esstis.ch.** Der Bereich hinter dem Login (Dokumente, Kochbuch, Forum)
  ist nicht erschlossen. Gezielte Recherche per Playwright, sobald klar ist,
  wonach gesucht wird — insbesondere, ob dort eine aktuellere oder korrigierte
  Fassung des Kochbuchs liegt.
- **Digitalisierung des Kochbuchs.** Der Textauszug ist vollständig verfügbar;
  die Umsetzung in `kochbuch.json` inklusive Plausibilitätsprüfung ist der
  größte Einzelposten von Stufe 1.

## 11. Quellen

- Elternnetzwerk Magersucht e. V. / Prof. Dr. J. Hebebrand:
  *Information für Kinder- und Hausärzte*, Stand 02/2025 (im Projektordner)
- Elternnetzwerk Magersucht e. V.: *Haus sichern für Elternbasiertes Refeeding*
  (im Projektordner)
- Elternnetzwerk Magersucht e. V.: *Kochbuch*, Stand 03/2024 (im Projektordner)
- Lock J., Le Grange D.: *Treatment Manual for Anorexia Nervosa: A Family-Based
  Approach*, 2. Aufl., Guilford Press 2015
- Haas V. et al.: *Die Familien-Basierte Therapie für junge Menschen mit
  Anorexia nervosa*, PSYCH up2date 2025; 19(01): 61–80
- Eva Musby, anorexiafamily.com — Mahlzeitenbegleitung, „Connect before you
  Direct", Magic Plate
- FEAST (feast-ed.org) — Mahlzeitendauer, Umgang mit Konsequenzen
- FIAT-Studie, Charité (fbt-fiat.de) — telemedizinische FBT im deutschsprachigen
  Raum
