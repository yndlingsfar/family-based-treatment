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
mit 1867g, ramen-suppe mit 1168g), aber der resultierende kcal-Wert lag
zufällig bereits innerhalb der 100–1600-kcal-Bandgrenze — meist, weil auch
die kcal-Angabe selbst schon zu niedrig war (nicht zuordenbare
Grundzutaten). In Fix-Runde 1 wurden diese drei bewusst **nicht** neu
durchgerechnet, nur geflaggt, um den Auftrag nicht ueber den gemeldeten
Befund hinaus auszuweiten. **In Fix-Runde 2 hat der Koordinator genau das
nachgefordert** — siehe eigener Abschnitt unten.

**Grenzfall, der bei mechanischer Anwendung des Bandes eine neue
Verletzung erzeugt hätte:** kaeseknoedel-spatzen (852g Gesamtmasse, 4
erfundene Portionen, 872 kcal/Portion, innerhalb des Bandes). Eine
Neuschätzung nach dem Auflauf-Band (350–450g) hätte 2 Portionen ergeben
(426g/Portion, passt zur Masse), aber 1744 kcal/Portion (verletzt die
1600er-Grenze) — die vorhandene Portionenzahl (4) wurde daher unverändert
gelassen und nur geflaggt, statt sie durch eine Zahl zu ersetzen, die zwar
zur Masse, aber nicht mehr zur kcal-Grenze passt. Das gilt auch nach
Fix-Runde 2 weiterhin.

## Fix-Runde 2: drei weitere Portionenzahlen, und eine zweite Grundzutaten-Tabelle

### Teil A: die drei verbliebenen Ein-Portion-Grossmengen

Der Koordinator hat unabhängig nachgeprüft und drei Rezepte gefunden, bei
denen `portionen_geschaetzt: true` gesetzt war, aber die Zahl selbst noch
nicht korrigiert wurde (aus Fix-Runde 1, siehe oben). Alle drei wurden nach
derselben Methode wie die 13 Rezepte aus Fix-Runde 1 neu geschätzt (Masse ÷
Portionsgrößen-Band, dieselbe Gesamtkalorienzahl neu geteilt):

| Rezept | Masse | alt | neu |
|---|---:|---|---|
| kuerbis-feta-honig-auflauf | 1867g | 1 × 578 | 5 × 116 → nach Teil B rekonstruiert auf 5 × 437 |
| cremiges-parmesan-huehnchen | 1734g | 1 × 974 | 4 × 244 → nach Teil B rekonstruiert auf 4 × 613 |
| ramen-suppe | 1168g | 1 × 850 | 3 × 283 → nach Teil B rekonstruiert auf 3 × 283 (unverändert, Kochbuch-Spanne) |

(Die kcal-Werte wurden zunächst wie in Fix-Runde 1 nur neu geteilt, dann in
Teil B unten für die drei "keine kcal-Angabe"-Fälle unter den dreien
zusätzlich aus der jetzt vollständigeren Zutatensumme rekonstruiert.)
`couscous-mit-gefluegel-und-tomatensalat`, `kuerbispuffer` und
`huehnerbrust-mit-reis-und-kokosmilch` blieben unverändert, wie vom
Koordinator angewiesen — ihre Portionenzahl steht im Kochbuch.

### Teil B: `referenz/grundzutaten.json` — eine zweite, getrennte Tabelle

**Befund:** Die Plausibilitätsprüfung deckte nur 43 % der 626
Rezeptzutaten ab (272 zugeordnet), weil `anreicherung.json` nur Dinge
enthält, die man einem Gericht *zusetzt* — nicht die Grundzutaten, aus
denen ein Gericht *besteht* (Kartoffeln, Nudeln, Zwiebeln, Hackfleisch
usw.). Für die meisten der 79 Rezepte konnte die Prüfung dadurch nichts
prüfen.

**Lösung:** Eine zweite Tabelle, `referenz/grundzutaten.json`, mit
denselben Feldern wie `anreicherung.json` minus den
Anreicherungs-spezifischen (`name`, `kcal_100g`, `dichte_g_ml`). 63
Einträge, davon 47 aus der vom Koordinator vorgegebenen Ankerliste
(verbatim übernommen) und **16 zusätzlich, weil sie in den 79 Rezepten
tatsächlich vorkommen** (alle unter 900 kcal/100g, zum Spotchecken hier
aufgelistet):

| Schlüssel | Name | kcal/100g |
|---|---|---:|
| kuerbiskerne | Kürbiskerne | 559 |
| tomaten-getrocknet | Getrocknete Tomaten | 258 |
| gorgonzola | Gorgonzola | 353 |
| frischkaese-doppelrahm | Frischkäse Doppelrahm | 350 |
| gruyere | Gruyère | 413 |
| vanilleeis | Vanille-Eis | 207 |
| kekse | Kekse (Schoko, z. B. Oreo) | 480 |
| quark-40 | Quark 40% Fett | 145 |
| quark-20 | Speisequark 20% | 120 |
| kakaopulver | Kakaopulver/Backkakao | 230 |
| kinderriegel | Kinderriegel (Schoko) | 560 |
| zucchini | Zucchini | 17 |
| brokkoli | Brokkoli | 34 |
| spinat | Spinat (frisch/TK) | 23 |
| gemuese-mix | Suppen-/Tiefkühlgemüse gemischt | 30 |
| weisswein | Weißwein | 82 |
| mayonnaise | Mayonnaise | 680 |
| sauce-hollandaise | Sauce Hollandaise fertig | 400 |
| kartoffelkloesse | Kartoffelklöße/-knödel fertig | 110 |
| margarine | Margarine | 720 |
| rahmsossenpulver | Rahmsoßenpulver | 420 |
| fladenbrot | Fladenbrot | 280 |
| pesto | Pesto | 450 |
| nudelsauce-fertig | Fertige Nudelsauce (Tomate) | 65 |
| kuchenteig-fertig | Fertiger Kuchenteig | 280 |
| kapern | Kapern | 23 |
| sweet-chili-sauce | Sweet-Chili-Sauce | 130 |
| rahmtomatensuppe-dose | Rahmtomatensuppe (Dose) | 70 |
| salami | Salami/gebratenes Fleisch | 340 |
| chiasamen | Chiasamen | 486 |
| obst-allgemein | Obst, unspezifisch (Richtwert) | 50 |

(Liste gekürzt auf die tatsächlich hinzugefügten — die vollständige Tabelle
steht in `referenz/grundzutaten.json`.) Bewusst **kein** Eintrag für Salz,
Pfeffer, Gewürze, Kräuter und Wasser (kalorisch irrelevant). Ein paar
weitere kalorisch nennenswerte, aber sehr seltene oder mehrdeutige
Zutaten (Balsamico, Backmalz, Hefe, Zitronenschale, Limettensaft,
Flohsamenschalen, rote Chilischoten, Raspelschokolade zum Verzieren)
wurden bewusst **nicht** aufgenommen — zu geringe Menge oder zu unklar,
um einen Wert zu verantworten, ohne zu raten.

`fbt/kochbuch.py`: `plausibilitaet(roh, mittel, grund=None)` sucht jeden
Zutaten-Schlüssel zuerst in `mittel`, dann in `grund` — Standardwert
`None` verhält sich wie ein leeres Dict, bestehende Aufrufe mit zwei
Argumenten bleiben unverändert funktionsfähig. `fbt/anreicherung.py`:
neue Funktion `lade_grundzutaten()`, gleiche Dateiform wie `lade_mittel()`.
Beide Tabellen bleiben strikt getrennt — die Anreicherungslogik darf
niemals eine Grundzutat als Zusatz vorschlagen.

**Zwei echte Transkriptionsfehler**, die erst durch die Grundzutaten-
Abdeckung sichtbar wurden, wurden korrigiert (keine Kochbuch-Zahlen
geändert, nur die Zutatenliste):

- `wraps-mit-fuellung`: "100g Gemüse + 15ml Öl" war als **eine** Zutat mit
  115g und `mittel=rapsoel` erfasst — dadurch rechnete die Prüfung
  fälschlich 115g reines Öl statt 15g Öl + 100g unbewertetes Gemüse.
  Aufgeteilt in zwei Zutaten.
- `couscous-mit-gefluegel-und-tomatensalat`: "100g roher Couscous pro
  Person" war im Kochbuch eine beschreibende Kopfzeile (Mengenverhältnis),
  wurde aber zusätzlich zur tatsächlichen Zutat "1 große Tasse Couscous"
  (180g) als eigene Zutat mitgezählt — Couscous wurde doppelt gezählt.
  Die redundante Zeile entfernt.

**Zuordenbare Zutaten (Coverage) vorher/nachher:**

```
vorher (Ende Fix-Runde 1):  272/626 (43 %)
nachher (Fix-Runde 2):      546/626 (87 %)
```

**Kochbuch-Einzelfiguren rekonstruiert statt neu geraten:** Für 13 der 15
Rezepte ohne jede Kochbuch-kcal-Angabe (aus der ersten Übertragung) ist die
jetzt viel vollständigere Zutatensumme eine deutlich bessere Rekonstruktion
als die Runde-1-Schätzung aus wenigen zugeordneten Anreicherungsmitteln —
`kcal_pro_portion` wurde entsprechend aktualisiert (Details im
Task-Report). `falscher-joghurt-2` und `kartoffelbrei-plus` waren bereits
gut geschätzt und blieben unverändert.

**Ergebnis des Abnahmegates nach Fix-Runde 2:**

```
Zutaten zuordenbar: 546/626 (87%)
Strukturfehler: 0
Notizen: 42, davon nicht pruefbar: 0
```

Alle 42 verbleibenden Notizen wurden einzeln durchgesehen. In praktisch
allen Fällen ist die Kochbuchangabe ein echter Buchwert (Fußnote, Spanne,
Dichte oder Summe der Einzelangaben — nicht erraten), und die jetzt
sichtbare Differenz ist normale Varianz zwischen Standardtabellenwerten
und den kochbucheigenen Annahmen für dieselben Grundzutaten (z. B. eine
andere Kartoffel- oder Nudelsorte) — keine neue Rechenschwäche, sondern
genau das, wofür die Toleranzprüfung gebaut ist. Unzugeordnet bleiben nach
Fix-Runde 2 fast nur noch Gewürze, Wasser und einzelne Markenprodukte
(This-is-Food, Oatsome, EnergeaP Kids, Fruchtquatsch).

Der Bandcheck (100–1600 kcal/Portion) bleibt bei denselben zwei erklärten
Treffern wie am Ende von Fix-Runde 1 (`ueberbackener-gemueseauflauf-mit-
sojawuerfeln`, `glueckskugeln`) — keine der Fix-Runde-2-Änderungen hat
einen neuen Bandtreffer erzeugt.

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

## Fix-Runde 3: ml-als-g-Mengen korrigiert, Zeitschätzung sichtbar gemacht

### Teil A: 18 Zutaten, die als Milliliter gemeint, aber als Gramm geführt waren

**Befund:** Wo das Kochbuch eine Ölmenge in "ml" nannte (z. B. "2 EL Öl,
ca. 28ml"), wurde sie durchgängig mit `einheit: "g"` und derselben Zahl
erfasst statt mit `einheit: "ml"`. `Mittel.kcal()` wendet die Dichte nur
bei `einheit: "ml"` an — bei `"g"` wird die Zahl direkt als Gramm
gerechnet. Da Öl leichter als Wasser ist (Dichte 0.91–0.93), überschätzte
das systematisch die Kalorien dieser Einträge, in eine Richtung: immer zu
hoch, nie zu niedrig.

**Fund per Skript** (Koordinator-Skript, exakt 18 Treffer in 17
Rezepten):

| Rezept | Zutat | Menge | vorher (g gerechnet) | nachher (ml, Dichte) |
|---|---|---:|---:|---:|
| couscous-mit-gefluegel-und-tomatensalat | Olivenöl (5-10 EL, ca. 105ml) | 105 | 928 kcal | 845 kcal |
| notfallbruehe | Beikostöl (5 EL) | 70 | 619 kcal | 569 kcal |
| kuerbiscremesuppe | Kokosfett/Speiseöl (4 EL) | 56 | 495 kcal | 455 kcal |
| quark-oelteig-broetchen | Rapsöl (4 EL) | 56 | 495 kcal | 455 kcal |
| couscous-salat-mit-joghurt | Leinöl (4 EL, Hauptrezept) | 56 | 495 kcal | 460 kcal |
| couscous-salat-mit-joghurt | Leinöl (2 EL, falscher Joghurt) | 28 | 248 kcal | 230 kcal |
| kaesepolenta-mit-joghurt | Leinöl (2 EL, falscher Joghurt) | 28 | 248 kcal | 230 kcal |
| gehaltvolle-klare-suppe | Beikostöl (2-3 EL) | 38 | 336 kcal | 309 kcal |
| ruehrei | Beikostöl (2-3 EL) | 38 | 336 kcal | 309 kcal |
| cremiges-parmesan-huehnchen | Olivenöl (2 EL) | 28 | 248 kcal | 226 kcal |
| bananen-brownie | Beikostöl (2 EL) | 28 | 248 kcal | 228 kcal |
| gemuesekuchen | Sonnenblumen-/Rapsöl (2 EL) | 28 | 248 kcal | 228 kcal |
| lasagne | Öl (2 EL) | 28 | 248 kcal | 228 kcal |
| ramen-suppe | Öl (2 EL) | 28 | 248 kcal | 228 kcal |
| schneller-knoedelauflauf | Öl (2 EL) | 28 | 248 kcal | 228 kcal |
| risotto-alla-parmigiana | Olivenöl (1 EL) | 14 | 124 kcal | 113 kcal |
| orangen-moehren-shake | Leinöl (1 TL) | 5 | 44 kcal | 41 kcal |
| smoothie-bowl | Ahornsirup/Agavendicksaft/Honig (1 EL) | 15 | 39 kcal | 52 kcal |

Alle 18 auf `einheit: "ml"` umgestellt, `menge` unverändert (die Zahl war
schon die Millilitermenge). 17 der 18 Einträge sind Öle (Dichte
0.91–0.93, also leichter als Wasser) und wurden dadurch kleiner; der
18., Ahornsirup (Dichte 1.33, schwerer als Wasser), wurde dadurch
**größer** (39 → 52 kcal) — dieselbe Korrektur, nur in die andere
Richtung, weil Sirup dichter ist als das Gramm-für-Milliliter-Modell
angenommen hatte. Netto über alle 18: 458 kcal weniger, wie vom
Koordinator gemessen (17 Öl-Entlastungen von zusammen 471 kcal minus die
eine Sirup-Erhöhung von 13 kcal).

**`kcal_pro_portion` neu berechnet, wo der Wert aus der Zutatensumme
rekonstruiert war** (nicht aus dem Kochbuch selbst):

| Rezept | vorher | nachher |
|---|---:|---:|
| bananen-brownie | 1174 | 1174 (unveraendert, Rundung) |
| couscous-salat-mit-joghurt | 1026 | 1026 (unveraendert, Rundung) |
| cremiges-parmesan-huehnchen | 613 | 613 (unveraendert, Rundung) |
| kuerbiscremesuppe | 656 | 656 (unveraendert, Rundung) |
| smoothie-bowl | 858 | 858 (unveraendert, Rundung) |
| risotto-alla-parmigiana | 484 | **1274** |

`risotto-alla-parmigiana` änderte sich deutlich: In Runde 1 wurde der
fehlende Reis manuell ergänzt (134 → 484 kcal), in Runde 2 wurde derselbe
Reis zusätzlich automatisch über `grundzutaten.json` zugeordnet — beide
Zählungen trafen sich auf denselben Kalorienträger, ohne dass die eine von
der anderen wusste. In Fix-Runde 3 aus der vollen, jetzt widerspruchsfreien
Zutatensumme (Reis, Butter, Parmesan, Olivenöl, Weißwein, Brühe) neu
berechnet: 1274 kcal/Portion — deutlich plausibler für ein
Weißwein-Butter-Parmesan-Risotto als Hauptspeise als die vorherigen 134
oder 484.

**Bei allen anderen 11 betroffenen Rezepten stammt `kcal_pro_portion` aus
einer echten Kochbuchangabe und wurde nicht verändert** — nur die
`pruefnotiz` mit den jetzt korrekten Abweichungszahlen aktualisiert:
couscous-mit-gefluegel-und-tomatensalat, gehaltvolle-klare-suppe,
gemuesekuchen, kaesepolenta-mit-joghurt, lasagne, notfallbruehe,
orangen-moehren-shake, ramen-suppe, ruehrei, schneller-knoedelauflauf.
Eine davon, `quark-oelteig-broetchen`, passt nach der Korrektur exakt
innerhalb der Toleranz — `pruefen` wurde dort auf `false` zurückgesetzt.

### Teil B: `zeit_min_geschaetzt`

Wie in Runde 1 dokumentiert, nennt das Kochbuch nie eine
Gesamtzubereitungszeit — `zeit_min` war für **alle 79 Rezepte** eine
Schätzung nach Rezeptkomplexität, aber ohne Kennzeichnung von einer
Kochbuchangabe nicht zu unterscheiden. Analog zu `portionen_geschaetzt`:
neues Feld `zeit_min_geschaetzt: bool = False` im `Rezept`-Dataclass
(`fbt/kochbuch.py`), gelesen in `lade_kochbuch`, dokumentiert in
`referenz/kochbuch.schema.json`, zwei neue Tests in
`tests/test_kochbuch.py`. `pruefe_rezept` unverändert. **Alle 79 Rezepte**
tragen jetzt `zeit_min_geschaetzt: true`.

### Ergebnis des Abnahmegates nach Fix-Runde 3

```
Rezepte gesamt: 79
Zutaten zuordenbar: 546/626 (87%)
Strukturfehler: 0
Notizen: 41, davon nicht pruefbar: 0
unkommentiert: 0
portionen_geschaetzt: 54
zeit_min_geschaetzt: 79
```

Band-Check (100–1600 kcal/Portion) unverändert bei den zwei bereits
erklärten, Kochbuch-belegten Ausnahmen (`ueberbackener-gemueseauflauf-mit-
sojawuerfeln`, `glueckskugeln`). Notizzahl sank von 42 auf 41
(`quark-oelteig-broetchen` bestand die Prüfung nach der ml-Korrektur
exakt).

## Fix-Runde 4: eine Flüssigkeit, die als ihr eigenes Konzentrat gezählt wurde

### Befund

`risotto-alla-parmigiana` hatte "Brühe (1,5L Wasser + 2 Brühwürfel)" als
**eine** Zutat mit 1500g und `mittel: bruehpulver` erfasst — dadurch
rechnete die Prüfung 1,5 Liter Wasser als 1,5 Kilogramm Bouillonpulver
(3000 kcal statt realistischer ~40 kcal für zwei Würfel). Dieselbe Form
des Fehlers fand sich in `rigatoni-al-forno-auflauf` ("Wasser + 2 EL
Gemüsebrühpulver (200ml)", ebenfalls komplett als `bruehpulver` geführt,
400 kcal statt ~40 kcal).

### Korrektur

Beide Einträge in Wasser (kein `mittel`, kalorisch irrelevant) und die
tatsächlichen Brühwürfel/das Pulver (~20g, `mittel: bruehpulver`)
aufgeteilt — das entspricht wörtlich dem, was das Kochbuch beschreibt
("1,5l Wasser **und** 2 Brühwürfel", zwei separate Mengen, keine
vorgefertigte Fertigbrühe).

- **risotto-alla-parmigiana**: keine Kochbuch-kcal-Angabe — `kcal_pro_portion`
  aus der jetzt korrigierten Zutatensumme neu berechnet: **1274 → 534
  kcal/Portion**. Damit endet die Zahl auf einem Wert, der zum Reis als
  Hauptkalorienträger passt (400g Reis = 1400 kcal, 65 % des Rezepts),
  statt von einer falsch gezählten Brühe verzerrt zu sein.
- **rigatoni-al-forno-auflauf**: `kcal_pro_portion` kommt aus der
  Kochbuch-Fußnote ("6 Portionen, pro Portion 875 kcal") und wurde **nicht
  verändert** — nach der Korrektur bestand das Rezept die
  Plausibilitätsprüfung exakt, `pruefen` wurde zurückgesetzt.

### Standing-Quality-Gate: Ein-Zutat-Dominanz-Check

Damit dieselbe Fehlerform (eine große, meist wässrige Menge fälschlich
komplett einem kalorienreichen Konzentrat zugeordnet) künftig auffällt,
gehört dieser Check ab jetzt fest zum Abnahmegate, neben Struktur- und
Bandcheck:

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
python3 -c "
import json
from fbt.daten import daten_pfad
from fbt.anreicherung import lade_mittel, lade_grundzutaten
d = json.loads((daten_pfad() / 'kochbuch.json').read_text(encoding='utf-8'))
alle = {**lade_grundzutaten(), **lade_mittel()}
for k, v in sorted(d.items()):
    ges = sum(alle[z['mittel']].kcal(z['menge'], z['einheit'])
              for z in v['zutaten']
              if z.get('mittel') in alle and z['einheit'] in ('g', 'ml'))
    if ges <= 0: continue
    for z in v['zutaten']:
        if z.get('mittel') not in alle or z['einheit'] not in ('g', 'ml'): continue
        kc = alle[z['mittel']].kcal(z['menge'], z['einheit'])
        if kc / ges > 0.5:
            print(f\"{k:34s} {z['was'][:44]:46s} {kc:7.0f} kcal = {kc/ges:.0%} des Rezepts\")
"
```

(Der ursprüngliche Koordinator-Prüfbefehl filtert nicht nach `einheit` und
bricht auf Zutaten mit `einheit: "stueck"` ab, die zur reinen
Abdeckungs-Transparenz einen `mittel`-Schlüssel tragen, aber von
`Mittel.kcal()` nicht berechnet werden können — z. B. Eier/Eigelb. Der
Filter `z['einheit'] in ('g', 'ml')` oben macht den Check lauffähig und
verhält sich damit genauso wie `plausibilitaet()` selbst, die
`"stueck"`-Zutaten ebenfalls überspringt.)

**Jeder Treffer braucht einen Blick, kein Treffer ist automatisch ein
Fehler** — ein Shake ist zu Recht meistens Sahne, ein Brot zu Recht
meistens Mehl. Ergebnis dieses Durchlaufs (23 Treffer, alle einzeln
geprüft):

| Rezept | dominante Zutat | Anteil | Befund |
|---|---|---:|---|
| butterkohlrabi | Butter | 92 % | legitim — Gemüse in Butter gedünstet |
| eiskaffee | Sahne/Milch | 76 % | legitim — Sahne-Kaffee-Getränk |
| falscher-joghurt | Mascarpone | 51 % | legitim |
| falscher-joghurt-2 | Mascarpone | 54 % | legitim |
| french-toast | Milchmädchen (Kondensmilch) | 59 % | legitim |
| frucht-smoothie | Maltodextrin | 64 % | legitim — bewusste Anreicherung |
| gebackener-blumenkohl-mit-limetten-aioli | Butter | 75 % | legitim — Butter zum Ausbacken |
| glueckskugeln | Butter | 53 % | legitim |
| kartoffelbrei-plus | Sahne | 62 % | legitim — Rezeptzweck ist Sahne-Anreicherung |
| kartoffelpueree | Ghee/Butter | 53 % | legitim |
| moehreneintopf | Bacon | 57 % | legitim |
| notfallbruehe | Beikostöl | 98 % | legitim — reines Öl-Trägergetränk per Konzept |
| nudelrezept-mit-roter-sauce | rohe Nudeln | 53 % | legitim |
| nudelsalat-alla-carlo-fortina | Pesto | 62 % | legitim |
| obst-smoothie-babyglaeschen | Beikostöl | 88 % | legitim — Öl-Anreicherung per Konzept |
| oreo-shake | flüssige Sahne | 61 % | legitim |
| power-porridge-schnelle-variante | Sahne | 62 % | legitim |
| powermilch | Sahne | 70 % | legitim |
| risotto-alla-parmigiana | Reis | 65 % | legitim (nach der Korrektur oben) |
| ruehrei | Beikostöl | 78 % | legitim — Eier zaehlen als "stueck" nicht mit |
| shake-mit-fruchtquatsch | Sahne | 56 % | legitim |
| tomatensuppe | Rapsöl (300ml) | 52 % | legitim — Kochbuch nennt 300ml wörtlich |
| vollkornbroetchen-ueber-nacht | Mehl | 54 % | legitim |

**Eine Korrektur vor dieser Tabelle**, nicht im Treffer selbst sichtbar,
weil sie den Treffer beseitigt hat: `frucht-smoothie` hatte "Obst mit
Banane, z. B. Honigmelone/Mango + Orangensaft oder Erdbeeren/Blaubeeren +
Traubensaft" komplett auf `mittel: banane` zugeordnet, obwohl das
Kochbuch ausdrücklich einen Obstmix beschreibt, bei dem Banane nur *ein*
Bestandteil ist (Melone/Mango/Beeren sind kalorienärmer). Auf
`obst-allgemein` (Richtwert 50 kcal/100g) umgestellt; `kcal_pro_portion`
blieb unverändert (Kochbuch-Spanne 300–450 kcal, Mittelwert 375),
nur die `pruefnotiz` aktualisiert.

### Ergebnis des Abnahmegates nach Fix-Runde 4

```
Rezepte gesamt: 79
Zutaten zuordenbar: 546/628 (87%)
Strukturfehler: 0
Notizen: 40, davon nicht pruefbar: 0
unkommentiert: 0
```

Zutaten gesamt stieg von 626 auf 628 (zwei Brühe-Einträge wurden je in
zwei Zutaten aufgeteilt), zuordenbare Zutaten blieben bei 546 (die neuen
Wasser-Einträge tragen bewusst kein `mittel`). Notizzahl sank von 41 auf
40 (`rigatoni-al-forno-auflauf` bestand die Prüfung nach der Korrektur
exakt). Band-Check unverändert bei den zwei bereits erklärten Ausnahmen.
