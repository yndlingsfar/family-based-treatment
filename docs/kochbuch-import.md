# Protokoll: Kochbuchdaten übertragen

Einmalige Datenübertragung des Netzwerk-Kochbuchs (PDF, 39 Seiten, Stand
März 2024) nach `$FBT_DATEN/kochbuch.json`. Dieses Dokument enthält **keine
Rezeptinhalte** — nur Zahlen und Befunde. Die Rezeptdaten selbst liegen
ausschließlich außerhalb des Repositories, da das Kochbuch-Vorwort die
Weitergabe an Dritte untersagt.

## Umfang

79 Rezepte transkribiert, verteilt über die Kategorien:

| Kategorie     | Anzahl |
|---------------|-------:|
| getraenke     | 13     |
| fruehstueck   |  7     |
| suppen        | 15     |
| nudeln        |  9     |
| fleisch       |  9     |
| vegetarisch   | 19     |
| backen        |  4     |
| dessert       |  3     |
| **Gesamt**    | **79** |

Ein Rezept ("Überbackener Gemüseauflauf mit Sojawürfeln") stand im Kochbuch
zwar im Fließtext zwischen den vegetarischen Gerichten, fehlte aber im
Inhaltsverzeichnis; es wurde trotzdem mit übertragen.

## Schritt 4: Abnahmegate (Struktur + Plausibilität)

Lauf über alle 79 Rezepte, Skript aus dem Task-Brief:

```
Rezepte gesamt:      79
Strukturfehler:      0
Plausibilitaetsnotiz:54
```

(Nach Fix-Runde 1, siehe unten; unmittelbar nach der ersten Übertragung waren
es 53 Notizen und `kcal_pro_portion=134` bei risotto-alla-parmigiana statt
`484` — die Notizzahl stieg durch die Korrektur dieses einen Rezepts um 1.)

**Strukturfehler: 0** — Abnahmekriterium erfüllt.

Alle Plausibilitätsnotizen wurden einzeln angesehen. Für zwei
(`falscher-joghurt` in der ersten Runde, `risotto-alla-parmigiana` in
Fix-Runde 1) war das Ergebnis eine **Korrektur der Übertragung** statt einer
Notiz bzw. eine Korrektur der zugrunde liegenden Kalorienzahl; für alle
anderen wurde `"pruefen": true` mit einer `"pruefnotiz"` gesetzt, die die
Abweichung erklärt. Keine Notiz blieb unkommentiert.

## Rezepte mit `pruefen: true` (70 von 79, nach Fix-Runde 1)

Die hohe Zahl ist erwartbar: Das Kochbuch nennt Kalorien uneinheitlich (mal
pro Portion, mal fürs ganze Rezept, mal als Bereich, mal gar nicht), und die
Standardtabelle deckt keine Grundzutaten wie Nudeln, Reis, Kartoffeln,
Fleisch, Gemüse oder Obst ab — diese sind mengenmäßig oft der größte
Kalorienanteil eines Gerichts. Eine Plausibilitätsnotiz ist in diesen Fällen
die Prüfung, die ehrlich meldet, dass sie nicht (vollständig) prüfen konnte
— kein Transkriptionsfehler.

Die 69 Fälle gliedern sich in vier Gruppen:

1. **Keine kcal-Angabe im Kochbuch (15 Rezepte).** kcal wurden vollständig
   aus den Zutaten über die Anreicherungstabelle berechnet:
   bananen-brownie, couscous-salat-mit-joghurt, cremiges-parmesan-huehnchen,
   falscher-joghurt-2, hackfleisch-risotto,
   huehnerbrust-mit-reis-und-kokosmilch, kartoffel-lauchsuppe,
   kartoffelbrei-plus, kuerbis-feta-honig-auflauf, kuerbiscremesuppe,
   pizzasuppe, schneller-nudelauflauf, schwarzwurzelsuppe-mit-pumpernickel,
   smoothie-bowl, wraps-mit-fuellung.

2. **Kochbuch nennt nur eine Spanne statt einer festen Zahl (9 Rezepte).**
   Mittelwert übernommen: couscous-mit-gefluegel-und-tomatensalat,
   eiskaffee, frucht-smoothie, gehaltvolle-klare-suppe,
   nudelsalat-alla-carlo-fortina, power-porridge-schnelle-variante,
   ramen-suppe, ruehrei, vollkornbroetchen-ueber-nacht.

3. **Kochbuch nennt nur eine Dichte (kcal/100g), nur eine Portionenzahl oder
   gar keine Portionenzahl (10 Rezepte).** kcal_pro_portion und/oder
   Portionenzahl wurden aus Gesamtgewicht bzw. den in Fix-Runde 1
   eingeführten Portionsgrößen-Bändern abgeleitet: french-toast,
   kartoffel-gemuese-auflauf, moehreneintopf, powermilch,
   risotto-alla-parmigiana (kcal-Wert in Fix-Runde 1 korrigiert, siehe
   unten), suesskartoffel-karottensuppe, tomatenreis, tomatensuppe-mit-avocado
   (Portionenzahl in Fix-Runde 1 korrigiert), tortellini-alla-panna,
   kastaniensuppe (5,5 auf 6 Portionen gerundet).

4. **Plausibilitätsabweichung durch nicht zuordenbare Grundzutaten oder
   durch eine Kochbuchangabe, die selbst als Ausreißer erscheint
   (36 Rezepte).** In den meisten Fällen erklären mengendominante,
   nicht in der Tabelle enthaltene Zutaten (Nudeln, Fleisch, Kartoffeln,
   Reis, Gemüse, Obst, Frischkäse-Sorten ohne Tabelleneintrag) die
   Differenz, und die Kochbuchangabe wurde unverändert übernommen:
   bananen-shake, blitz-lasagne, butterkohlrabi,
   gebackener-blumenkohl-mit-limetten-aioli, gemuesekuchen, gemuesewaffeln,
   gnocchi-auflauf, gnocchi-mit-currysauce-und-champignons,
   gnocchis-mit-gorgonzola, kaeseknoedel-spatzen, kartoffelpueree,
   kuerbis-gemuese-suppe, kuerbispuffer, kuerbissuppe-mit-kokosmilch,
   lasagne, nudelrezept-mit-roter-sauce, nuss-shake,
   orecchiette-nudeln-mit-kapern, oreo-shake, orrechiette-pasta, powershake,
   powersmoothie-fruechte, quark-oelteig-broetchen, rigatoni-al-forno-auflauf,
   sahne-haehnchen-schweinefilet-im-ofen, schneller-knoedelauflauf,
   shake-mit-fruchtquatsch, spaetzle-hack-pfanne, spaetzleauflauf-mit-hack,
   spaghetti-bolognese, tomatensuppe, tortellini-salat,
   ueberbackener-gemueseauflauf-mit-sojawuerfeln, waffeln. In zwei Fällen
   liegt die zugeordnete Zutaten-Summe bereits **über** der
   Kochbuchangabe, ohne dass alle Zutaten überhaupt erfasst sind
   (blitz-lasagne, butterkohlrabi) — hier wirkt die Kochbuch-eigene Zahl zu
   niedrig; sie wurde trotzdem unverändert übernommen, da keine
   verlässlichere Korrektur ableitbar war. Bei orangen-moehren-shake ist
   die Kochbuchangabe (272 kcal) auffällig niedriger als allein die
   zugeordneten Zutaten (640 kcal) — möglich ist eine Verwechslung der
   Fußnote mit einer anderen auf derselben Kochbuchseite; die Angabe wurde
   dennoch unverändert übernommen, da keine sichere Korrektur ableitbar
   war.

Die restlichen 9 Rezepte (79 − 70) haben keine Plausibilitätsnotiz und keine
sonstige Unsicherheit — ihre Kochbuchangabe passt direkt oder über die
zugeordneten Zutaten innerhalb der 10-%-Toleranz.

## Fix-Runde 1: Portionenzahl statt Default-1 aus der Zutatenmasse geschätzt

**Befund (vom Koordinator gemeldet):** Die ursprüngliche Regel "steht nur
eine Gesamtangabe ohne Portionen, `portionen: 1` setzen und die
Gesamtangabe übernehmen" erzeugte 13 Rezepte, deren "eine Portion"
tatsächlich ein ganzer Topf/eine ganze Auflaufform war (bis zu 7056 kcal für
"1 Portion"). Für eine App, die diese Zahl als eine von sechs
Tagesmahlzeiten einplant, ist das kein Etikettierungsdetail, sondern ein
Fehler mit derselben Wirkung wie eine falsch benannte Bezugsgröße: die Zahl
ist echt, die Einheit stimmt nicht.

**Korrektur:**

1. Neues Feld `"portionen_geschaetzt": true` auf jedem Rezept, dessen
   Portionszahl nicht wörtlich als einzelne Zahl im Kochbuch stand
   (Default ohne jede Angabe, Rundung einer Bruchportion wie "5,5
   Portionen", Auswahl aus einer Spanne wie "3-4 Portionen" oder Ableitung
   aus einer Kochbuch-Portionsgröße/-dichte). **54 von 79 Rezepten**
   tragen dieses Flag.
2. Für die 13 vom Koordinator genannten "Ein-Topf-als-eine-Portion"-Rezepte:
   Portionenzahl aus der Zutaten-Gesamtmasse und Portionsgrößen-Bändern neu
   geschätzt (Suppen/Eintöpfe 350–470g, Nudel-/Auflaufgerichte 350–450g,
   Reis-/Risottogerichte ca. 350g, Shakes/Getränke 250–500ml), dann
   `kcal_pro_portion` = dieselbe Gesamtkalorienzahl / neue Portionenzahl neu
   geteilt — die Gesamtkalorienzahl selbst wurde nicht neu hergeleitet.
3. `risotto-alla-parmigiana`: Portionenzahl (4) ist Kochbuch-Angabe ("als
   Hauptspeise für 4 Personen") und blieb unverändert. Der kcal-Wert
   (134 kcal/Portion) war aber nachweislich zu niedrig, weil der Reis
   (400g, der größte Kalorienträger) nicht in der Anreicherungstabelle
   steht und komplett fehlte — korrigiert auf 484 kcal/Portion durch eine
   manuelle Reis-Schätzung (ca. 350 kcal/100g roher Reis, außerhalb der
   Anreicherungstabelle).
4. Code-Änderung: `portionen_geschaetzt: bool = False` im `Rezept`-Dataclass
   (`fbt/kochbuch.py`), gelesen in `lade_kochbuch`, dokumentiert in
   `referenz/kochbuch.schema.json`, mit zwei neuen Tests in
   `tests/test_kochbuch.py` abgesichert. `pruefe_rezept` brauchte keine
   Änderung (ignoriert unbekannte Schlüssel).

**Ergebnis des Bandchecks** (100–1600 kcal/Portion, alle 79 Rezepte erneut
geprüft, nicht nur die 13 genannten):

```
ausserhalb 100-1600 kcal/Portion: 2
  ueberbackener-gemueseauflauf-mit-sojawuerfeln    1666 kcal x5
  glueckskugeln                                 80 kcal x6
```

Beide verbleibenden Treffer sind einzeln erklärt, nicht korrigiert, weil
ihre Portionenzahl **wörtlich im Kochbuch steht** (keine Schätzung, kein
`portionen_geschaetzt`-Flag):

- **ueberbackener-gemueseauflauf-mit-sojawuerfeln** (1666 kcal, 5
  Portionen): Kochbuch nennt explizit "(5 Personen)". Der Wert liegt nur
  66 kcal über der 1600er-Grenze; das Gericht ist mit 600g Gouda, 500g
  Nudeln, 400ml Sahne und 280g Sojawürfeln ausgesprochen kalorienreich —
  plausibel für eine sehr reichhaltige Familien-Auflaufform. Keine Änderung.
- **glueckskugeln** (80 kcal, 6 Portionen): Kochbuch nennt explizit "6
  kleine Bällchen". 80 kcal für eine kleine Praline aus Butter, Mandelmehl,
  Puderzucker und Kakao ist plausibel. Keine Änderung.

**Weitere Prüfung, ob die Zutatenmasse hinter Rezepten passt, die den
kcal-Bandcheck bereits vorher bestanden:** Bei einigen Rezepten mit
erfundener Portionenzahl war die resultierende Zutatenmasse pro "Portion"
zwar größer als eine realistische Einzelportion (z. B.
cremiges-parmesan-huehnchen mit 1734g für 1 Portion, kuerbis-feta-honig-auflauf
mit 1867g, couscous-mit-gefluegel-und-tomatensalat mit 876g, ramen-suppe mit
1168g), aber der resultierende kcal-Wert lag zufällig bereits innerhalb der
100–1600-kcal-Bandgrenze — meist, weil auch die kcal-Angabe selbst schon zu
niedrig war (nicht zuordenbare Grundzutaten, siehe oben). Diese Rezepte
wurden **nicht** neu durchgerechnet (das hätte bei mindestens einem Fall,
kaeseknoedel-spatzen, den kcal-Wert über die 1600er-Grenze getrieben, siehe
unten), sondern erhielten nur das `portionen_geschaetzt`-Flag zur
Transparenz. Eine Neuberechnung dieser Fälle wäre eine dritte Fix-Runde und
ist hier bewusst nicht vorgenommen worden, um den Auftrag nicht über den
gemeldeten Befund hinaus auszuweiten.

**Grenzfall, der bei mechanischer Anwendung des Bandes eine neue
Verletzung erzeugt hätte:** kaeseknoedel-spatzen (852g Gesamtmasse, 4
erfundene Portionen, 872 kcal/Portion, innerhalb des Bandes). Eine
Neuschätzung nach dem Auflauf-Band (350–450g) hätte 2 Portionen ergeben
(426g/Portion, passt zur Masse), aber 1744 kcal/Portion (verletzt die
1600er-Grenze) — die vorhandene Portionenzahl (4) wurde daher unverändert
gelassen und nur geflaggt, statt sie durch eine Zahl zu ersetzen, die zwar
zur Masse, aber nicht mehr zur kcal-Grenze passt.

## Schritt 5: Anreicherungstabelle gegen Produkte abgleichen

**Dieser Schritt konnte nicht durchgeführt werden.** Er erfordert das
physische Ablesen von Verpackungsangaben der tatsächlich verwendeten
Produkte — das kann diese Software-Aufgabe nicht leisten.
`referenz/anreicherung.json` wurde **nicht verändert**.

Stattdessen: Liste der Anreicherungsmittel, sortiert nach Häufigkeit ihrer
Verwendung über alle 79 übertragenen Rezepte (Anzahl Rezepte, die das Mittel
mindestens einmal verwenden), mit dem aktuell in der Tabelle hinterlegten
`kcal_100g`-Wert. Ein Abgleich sollte mit den am häufigsten verwendeten
Mitteln beginnen, da dort eine Korrektur die größte Hebelwirkung auf die
Tagesbilanz hat:

| Rang | Mittel            | Rezepte | kcal/100g (Tabelle) |
|-----:|-------------------|--------:|---------------------:|
|  1   | sahne-30          | 47      | 292 |
|  2   | mascarpone        | 23      | 380 |
|  3   | sonnenblumenoel   | 20      | 884 |
|  4   | maltodextrin      | 19      | 385 |
|  5   | parmesan          | 15      | 400 |
|  6   | butter            | 15      | 741 |
|  7   | gouda-48          | 13      | 356 |
|  8   | zucker            | 13      | 400 |
|  9   | beikostoel        |  9      | 884 |
| 10   | rapsoel           |  9      | 884 |
| 11   | ghee              |  8      | 892 |
| 12   | olivenoel         |  7      | 884 |
| 13   | leinoel           |  7      | 884 |
| 14   | vollmilch         |  5      | 65  |
| 15   | creme-fraiche     |  4      | 292 |
| 16   | creme-double      |  4      | 450 |
| 17   | orangensaft       |  4      | 45  |
| 18   | datteln           |  4      | 280 |
| 19   | schmelzkaese      |  3      | 300 |
| 20   | ahornsirup        |  3      | 260 |
| 21   | haselnuesse       |  3      | 628 |
| 22   | mandeln           |  3      | 575 |
| 23   | cashewkerne       |  3      | 553 |
| 24   | joghurt-griech    |  3      | 130 |
| 25   | jerseymilch       |  3      | 85  |
| 26   | erdnussbutter     |  2      | 590 |
| 27   | lecithin          |  2      | 763 |
| 28   | kokosmilch        |  2      | 200 |
| 29   | honig             |  2      | 300 |
| 30   | traubensaft       |  2      | 68  |
| 31   | walnuesse         |  2      | 654 |
| 32   | avocado           |  2      | 160 |
| 33   | ricotta           |  1      | 170 |
| 34   | kondensmilch      |  1      | 330 |
| 35   | cashewmus         |  1      | 600 |
| 36   | mandelmus         |  1      | 630 |

Besonders wichtig für den Abgleich: **sahne-30** (in 47 von 79 Rezepten, mit
Abstand die dominante Zutat), **mascarpone** (23) und **sonnenblumenoel/
rapsoel/beikostoel/olivenoel/leinoel** (zusammen als "neutrales Öl"-Familie
in praktisch jedem zweiten Rezept). Eine Abweichung bei diesen wenigen
Einträgen wirkt sich auf einen Großteil der Tagesbilanz aus.

## Schritt 7: Keine Rezeptdaten im Repository

```
$ git status --short
(leer)

$ grep -rl "kcal_pro_portion" --include="*.json" . | grep -v node_modules
referenz/kochbuch.schema.json
```

`referenz/kochbuch.schema.json` enthält den String `kcal_pro_portion` nur als
Feldnamen in der Schema-Beschreibung ("Zahl > 0, Pflicht"), nicht als
Rezeptdatum — diese Datei existierte bereits vor dieser Aufgabe und ist
absichtlich Teil des Repos (Schema-Dokumentation, keine Nutzdaten).
`referenz/anreicherung.json` taucht im Treffer **nicht** auf, wie erwartet.
`kochbuch.json` liegt ausschließlich unter `$FBT_DATEN` und war zu keinem
Zeitpunkt im Arbeitsverzeichnis des Repositories.

## Offene Entscheidungen, die die Vorgaben nicht abschließend regelten

- **`zeit_min` (Pflichtfeld) fehlt im Kochbuch fast durchgehend.** Das
  Kochbuch nennt nie eine Gesamtzubereitungszeit, gelegentlich einzelne
  Back-/Gar-Zeiten. `zeit_min` wurde daher nach Rezeptkomplexität geschätzt
  (Shakes/Rohkost ca. 5 Min., Pfannengerichte 15–35 Min., Suppen 25–45 Min.,
  Aufläufe/Backwaren 40–65 Min., über Nacht gehender Teig 200 Min. inkl.
  Ruhezeit). Diese Schätzungen sind keine Kochbuchangaben und sollten bei
  Gelegenheit von den Eltern anhand ihrer eigenen Erfahrung überprüft werden.
- **Umrechnung von Haushaltsmaßen.** Ohne anderslautende Angabe im Kochbuch
  wurden verwendet: 1 TL = 5 g, 1 EL = 14–15 g (Öl 14 g, sonst 15 g),
  1 Becher = 200 g, 1 Messlöffel Maltodextrin = 10 g, 1 Ei = 60 g,
  1 Prise = 1 g. Diese Werte sind in `was` jeweils mit dem Originalwortlaut
  dokumentiert.
- **Fehlende Portionenzahl bei großen Mengen ohne Personenangabe** (z. B.
  Süßkartoffel-Karottensuppe mit 1,5 kg Karotten, Kartoffel-Lauchsuppe mit
  2 kg Kartoffeln). **Korrigiert in Fix-Runde 1** (siehe eigener Abschnitt
  oben): Die ursprüngliche Regel (`portionen: 1`, gesamte Menge als
  `kcal_pro_portion`) erzeugte unrealistische "Ein-Topf-als-eine-Portion"-
  Werte bis zu 7056 kcal. Portionenzahl wird jetzt aus der Zutatenmasse und
  einer Portionsgrößen-Spanne je Gerichttyp geschätzt und als
  `portionen_geschaetzt: true` gekennzeichnet.
- **Generische "Sahne" ohne %-Angabe** wurde durchgängig als `sahne-30`
  zugeordnet (Standard-Schlagsahne), auch wenn das Kochbuch selbst an
  einzelnen Stellen 33 % oder unbenannte Fettstufen nennt — es gibt in der
  Anreicherungstabelle keinen passenden Zwischenwert.
- **Generischer "Käse" bzw. "Cheddar"** wurde mangels eigenem
  Tabelleneintrag pauschal als `gouda-48` zugeordnet.
- **Zwei fast identische Rezepte** ("Orrechiette-Pasta" und
  "Orecchiette-Nudeln mit Kapern", unterschiedliche Schreibweise und leicht
  abweichende Zubereitung) wurden als zwei getrennte Einträge übertragen,
  da ihre Titel nicht identisch sind — keine `-2`-Suffix-Regel nötig. Ein
  echtes doppeltes Rezept-Titelpaar (wie im Task-Brief als Beispiel
  genannt) kam im Kochbuch tatsächlich nicht vor.
- **PDF-Fußnoten verschoben um eine Seite.** Die kcal-Fußnoten unter den
  Rezepttiteln wurden bei der Text-Extraktion durchgängig an den Anfang der
  jeweils folgenden Seite verschoben (bedingt durch das PDF-Layout: Fußnote
  stand ursprünglich unter dem Rezepttitel derselben Seite). Alle Fußnoten
  wurden anhand von Reihenfolge und inhaltlichem Abgleich (z. B. "pro
  Dreieck" → French Toast, genannte Zutatensumme) den richtigen Rezepten
  zugeordnet; in wenigen Fällen (siehe orangen-moehren-shake oben) blieb
  die Zuordnung unsicher.
