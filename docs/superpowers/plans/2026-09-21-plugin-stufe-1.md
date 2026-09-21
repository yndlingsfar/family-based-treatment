# FBT-Plugin Stufe 1: Kalorientracking und Mahlzeitenplanung — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eine Familie kann einen Tag mit sechs Mahlzeiten auf eine ärztlich vorgegebene Kalorienmenge planen, Rezepte gezielt anreichern und abends verlässlich sehen, wie viel tatsächlich angekommen ist.

**Architecture:** Ein Claude-Code-Plugin ohne personenbezogene Daten, plus ein Paket reiner Python-Standardbibliothek für alles, was gerechnet wird. Die Skills und Commands führen das Gespräch; die Skripte liefern die Zahlen. Personenbezogene Daten und die Kochbuchrezepte liegen außerhalb des Repos in `$FBT_DATEN`.

**Tech Stack:** Python 3.11+ (nur Standardbibliothek: `tomllib`, `json`, `csv`, `pathlib`, `unittest`), Markdown für Skills und Commands, Cookidoo über den MCP-Connector.

**Spec:** `/Users/danielsteiner/Projects/family-based-treatment/docs/superpowers/specs/2026-09-21-fbt-plugin-design.md`

**Vorgänger:** `docs/superpowers/plans/2026-09-21-cookidoo-mcp-naehrwerte.md` — dessen Nachtrag ist Pflichtlektüre, siehe „Lehre aus Plan 1" unten.

## Global Constraints

- **Keine Abhängigkeiten außerhalb der Standardbibliothek.** Kein `pip install`, kein venv, kein PyYAML, kein `jsonschema`. Eine Familie im Refeeding kann keine kaputte Python-Umgebung gebrauchen. Deshalb TOML statt YAML (`tomllib` ist ab 3.11 stdlib) und `unittest` statt pytest.
- **Python 3.11+.** Jedes Einstiegsskript prüft das und bricht mit klarer Meldung ab.
- **Kein personenbezogener Datenpunkt im Repo.** Weder in Code, Tests, Fixtures noch Beispielen. Testdaten heißen `Testkind`, nie `Leni`. Datum, Größe, Gewicht in Tests sind frei erfunden.
- **Die Kochbuchrezepte gehören nicht ins Repo.** Das Netzwerk-Kochbuch untersagt Weitergabe. Im Plugin liegen Schema und Validator; die Rezepte liegen in `$FBT_DATEN/kochbuch.json`.
- **Datenpfad:** `$FBT_DATEN`, Vorgabe `~/Library/Mobile Documents/com~apple~CloudDocs/FBT-Daten`. **Der Pfad enthält Leerzeichen** — immer `pathlib`, nie String-Verkettung, und in Shell-Beispielen immer quoten.
- **Zwei Ausgabeformen.** Jede Funktion, die etwas Anzeigbares erzeugt, hat eine Elternansicht (mit Zahlen) und eine Tischansicht (ohne Kalorien, ohne Gewicht, ohne Zielwerte). Zwei getrennte Codepfade, keine Einstellung.
- **Rechnen statt schätzen.** Unbekannte oder mehrdeutige Werte werden gemeldet, nie geraten. Keine stille Vorgabe, keine Typumwandlung, die einen Wert erfindet.
- **`None` ist nicht `0`.** Eine fehlende Kalorienangabe ist `None` und muss bis zur Ausgabe als „unbekannt" erkennbar bleiben.
- **Keine medizinischen Vorgaben erfinden.** Tages-kcal und Zielgewicht kommen aus `profil.toml` und stammen von der Ärztin. Fehlen sie, fragt das System danach, statt einen Wert anzunehmen.
- **Sprache:** Bezeichner, Kommentare, Docstrings und Commit-Messages auf Deutsch, passend zur Domäne und zu den Nutzern. Das weicht bewusst von `cookidoo-mcp` ab — das ist ein anderes Repo mit anderem Publikum.
- **TDD durchgehend.** Erst der fehlschlagende Test, dann der Code.
- Branch: `feat/stufe-1-mahlzeiten`, ausgehend von `main`.

### Lehre aus Plan 1 — bindend

Drei task-lokale Reviews haben in Plan 1 drei echte Defekte durchgelassen, weil jeder Task exakt dem Plan entsprach, inklusive der Planfehler. Gefunden hat sie erst der Durchlauf gegen echte Daten in der Breite. Konkret für diesen Plan:

- Die Plausibilitätsprüfung des Kochbuchs läuft gegen **alle** Rezepte, nicht gegen eine Stichprobe (Task 4).
- Wo eine Zahl aus einer fremden Quelle stammt, wird sie geprüft statt gecastet. `int('')` wirft zwar, aber `bool` ist in Python eine `int`-Unterklasse: `isinstance(True, int)` ist `True`. Das ist exakt derselbe Fehlertyp wie `Number('') === 0` in Plan 1 und wird in Task 1 explizit abgefangen.

## File Structure

| Datei | Verantwortung |
|---|---|
| `.claude-plugin/plugin.json` | Plugin-Manifest |
| `fbt/__init__.py` | Paketmarker, Versionskonstante |
| `fbt/daten.py` | Datenverzeichnis finden, `profil.toml` laden und validieren |
| `fbt/anreicherung.py` | Anreicherungsmittel laden, kcal für eine Menge rechnen |
| `fbt/kochbuch.py` | Kochbuch laden, Struktur prüfen, Plausibilität prüfen |
| `fbt/anreichern.py` | Rezept + Ziel-kcal → konkrete Zutatenänderungen |
| `fbt/bilanz.py` | Tagesdatei → Bilanz, Eltern- und Tischansicht |
| `referenz/anreicherung.json` | ~30 Anreicherungsmittel mit kcal/100 g |
| `referenz/kochbuch.schema.json` | Struktur eines Kochbucheintrags |
| `referenz/profil.vorlage.toml` | Vorlage zum Ausfüllen |
| `referenz/tag.vorlage.toml` | Vorlage einer Tagesdatei |
| `skills/mahlzeit-planen/SKILL.md` | Wie ein Tag geplant wird |
| `skills/rezept-anreichern/SKILL.md` | Wie ein Rezept auf Ziel-kcal kommt |
| `commands/tagesplan.md` | `/tagesplan` |
| `commands/tagesabschluss.md` | `/tagesabschluss` |
| `tests/test_*.py` | je ein Modul pro Testdatei |

Jedes `fbt`-Modul bleibt unter etwa 150 Zeilen. Wächst eines darüber hinaus, ist das ein Signal, dass es zwei Aufgaben hat — dann melden, nicht selbst aufteilen.

Testlauf durchgehend: `python3 -m unittest discover -s tests -v`

---

### Task 0: Branch und Gerüst

**Files:**
- Create: `.claude-plugin/plugin.json`, `fbt/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Branch anlegen**

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
git status --short
git checkout -b feat/stufe-1-mahlzeiten
python3 --version
```

Erwartet: sauberer Arbeitsbaum; Python meldet 3.11 oder höher. Ist Python älter, melden und stoppen — der Plan setzt `tomllib` voraus.

- [ ] **Step 2: Manifest und Paketmarker anlegen**

`.claude-plugin/plugin.json`:

```json
{
  "name": "family-based-treatment",
  "description": "Unterstützt Eltern beim Family-Based Treatment: Mahlzeitenplanung, Kalorienbilanz und Rezeptanreicherung für das Refeeding zu Hause.",
  "version": "0.1.0"
}
```

`fbt/__init__.py`:

```python
"""Werkzeuge für das familienbasierte Refeeding.

Dieses Paket enthält ausschließlich Logik und Referenzwerte. Alle
personenbezogenen Daten liegen außerhalb des Repositories, siehe fbt.daten.
"""

VERSION = "0.1.0"
```

`tests/__init__.py`: leere Datei.

- [ ] **Step 3: Committen**

```bash
git add .claude-plugin/plugin.json fbt/__init__.py tests/__init__.py
git commit -m "chore: Plugin-Gerüst und Paketstruktur"
```

---

### Task 1: Datenverzeichnis und Profil

**Files:**
- Create: `fbt/daten.py`, `referenz/profil.vorlage.toml`, `tests/test_daten.py`

**Interfaces:**
- Consumes: nichts.
- Produces:
  - `STANDARD_DATEN: Path`
  - `class DatenFehler(Exception)`
  - `@dataclass(frozen=True) class Profil` mit `rufname: str`, `geburtsdatum: date`, `groesse_cm: int`, `zunahme_g_pro_woche: int`, `mahlzeiten: tuple[str, ...]`, `kcal_taeglich: int | None`, `kcal_quelle: str | None`, `wiegen: str | None`, `unvertraeglichkeiten: tuple[str, ...]`, `fearfoods: tuple[str, ...]`, Property `kcal_bekannt: bool`
  - `daten_pfad(umgebung: dict | None = None) -> Path`
  - `lade_profil(basis: Path | None = None) -> Profil`

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`tests/test_daten.py`:

```python
"""Tests für das Auffinden des Datenverzeichnisses und das Laden des Profils."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fbt.daten import STANDARD_DATEN, DatenFehler, daten_pfad, lade_profil

VOLLSTAENDIG = """
[kind]
rufname = "Testkind"
geburtsdatum = 2010-01-15
groesse_cm = 150

[ziele]
kcal_taeglich = 2800
kcal_quelle = "Kinderaerztin, Stand 2026-01-02"
zunahme_g_pro_woche = 500

[behandlung]
wiegen = "blind, 1-2x pro Woche"

[mahlzeiten]
plan = ["fruehstueck", "mittagessen", "abendessen"]

[praeferenzen]
unvertraeglichkeiten = ["Nuesse"]
fearfoods = ["Butter"]
"""

OHNE_KCAL = """
[kind]
rufname = "Testkind"
geburtsdatum = 2010-01-15
groesse_cm = 150

[ziele]
zunahme_g_pro_woche = 500

[mahlzeiten]
plan = ["fruehstueck"]
"""


def schreibe(inhalt: str) -> Path:
    """Legt ein Profil in einem temporären Verzeichnis mit Leerzeichen im Namen an."""
    basis = Path(tempfile.mkdtemp()) / "FBT Daten mit Leerzeichen"
    basis.mkdir()
    (basis / "profil.toml").write_text(inhalt, encoding="utf-8")
    return basis


class DatenPfadTest(unittest.TestCase):
    def test_nimmt_umgebungsvariable_wenn_gesetzt(self):
        self.assertEqual(
            daten_pfad({"FBT_DATEN": "/tmp/anderswo"}), Path("/tmp/anderswo")
        )

    def test_loest_tilde_auf(self):
        self.assertEqual(daten_pfad({"FBT_DATEN": "~/x"}), Path.home() / "x")

    def test_faellt_auf_standard_zurueck_wenn_leer(self):
        self.assertEqual(daten_pfad({"FBT_DATEN": "   "}), STANDARD_DATEN)

    def test_faellt_auf_standard_zurueck_wenn_nicht_gesetzt(self):
        self.assertEqual(daten_pfad({}), STANDARD_DATEN)


class ProfilTest(unittest.TestCase):
    def test_liest_ein_vollstaendiges_profil(self):
        profil = lade_profil(schreibe(VOLLSTAENDIG))
        self.assertEqual(profil.rufname, "Testkind")
        self.assertEqual(profil.geburtsdatum, date(2010, 1, 15))
        self.assertEqual(profil.groesse_cm, 150)
        self.assertEqual(profil.kcal_taeglich, 2800)
        self.assertTrue(profil.kcal_bekannt)
        self.assertEqual(profil.mahlzeiten, ("fruehstueck", "mittagessen", "abendessen"))
        self.assertEqual(profil.unvertraeglichkeiten, ("Nuesse",))
        self.assertEqual(profil.wiegen, "blind, 1-2x pro Woche")

    def test_fehlende_tageskcal_sind_none_nicht_null(self):
        profil = lade_profil(schreibe(OHNE_KCAL))
        self.assertIsNone(profil.kcal_taeglich)
        self.assertFalse(profil.kcal_bekannt)

    def test_meldet_fehlendes_profil_mit_pfad(self):
        leer = Path(tempfile.mkdtemp())
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(leer)
        self.assertIn(str(leer / "profil.toml"), str(fall.exception))

    def test_meldet_fehlende_pflichtangabe(self):
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(schreibe('[kind]\nrufname = "Testkind"\n'))
        self.assertIn("geburtsdatum", str(fall.exception))

    def test_lehnt_wahrheitswert_als_zahl_ab(self):
        # bool ist in Python eine int-Unterklasse: isinstance(True, int) ist True.
        # Ohne eigene Pruefung wuerde groesse_cm = true stillschweigend zu 1.
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(
                schreibe(
                    '[kind]\nrufname = "T"\ngeburtsdatum = 2010-01-15\n'
                    "groesse_cm = true\n\n[ziele]\nzunahme_g_pro_woche = 500\n"
                    '\n[mahlzeiten]\nplan = ["fruehstueck"]\n'
                )
            )
        self.assertIn("groesse_cm", str(fall.exception))

    def test_meldet_kaputtes_toml_mit_pfad(self):
        basis = schreibe("[kind\nrufname =")
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(basis)
        self.assertIn("profil.toml", str(fall.exception))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag bestätigen**

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
python3 -m unittest tests.test_daten -v
```

Erwartet: FAIL mit `ModuleNotFoundError: No module named 'fbt.daten'`.

- [ ] **Step 3: `fbt/daten.py` implementieren**

```python
"""Findet das private Datenverzeichnis der Familie und liest das Profil.

Dieses Plugin enthaelt keine personenbezogenen Daten. Alles Persoenliche liegt
ausserhalb des Repositories, in einem Verzeichnis, das die Umgebungsvariable
FBT_DATEN benennt. Die Vorgabe zeigt auf iCloud Drive und enthaelt Leerzeichen;
Pfade werden deshalb ausschliesslich mit pathlib gebaut.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

STANDARD_DATEN = (
    Path.home()
    / "Library"
    / "Mobile Documents"
    / "com~apple~CloudDocs"
    / "FBT-Daten"
)


class DatenFehler(Exception):
    """Das Datenverzeichnis oder das Profil ist so nicht benutzbar."""


@dataclass(frozen=True)
class Profil:
    """Die Vorgaben, unter denen geplant wird.

    kcal_taeglich ist bewusst optional: Die Menge gibt die Aerztin vor. Solange
    sie fehlt, ist sie None und niemals 0 — planen laesst sich trotzdem, nur
    beurteilen nicht.
    """

    rufname: str
    geburtsdatum: date
    groesse_cm: int
    zunahme_g_pro_woche: int
    mahlzeiten: tuple[str, ...]
    kcal_taeglich: int | None = None
    kcal_quelle: str | None = None
    wiegen: str | None = None
    unvertraeglichkeiten: tuple[str, ...] = ()
    fearfoods: tuple[str, ...] = ()

    @property
    def kcal_bekannt(self) -> bool:
        return self.kcal_taeglich is not None


def daten_pfad(umgebung: dict[str, str] | None = None) -> Path:
    """Liefert das Datenverzeichnis: FBT_DATEN, sonst die iCloud-Vorgabe."""
    umgebung = os.environ if umgebung is None else umgebung
    roh = umgebung.get("FBT_DATEN", "").strip()
    return Path(roh).expanduser() if roh else STANDARD_DATEN


def lade_profil(basis: Path | None = None) -> Profil:
    """Liest profil.toml aus dem Datenverzeichnis."""
    basis = daten_pfad() if basis is None else basis
    datei = basis / "profil.toml"
    if not datei.is_file():
        raise DatenFehler(
            f"Kein Profil unter {datei}. Lege es nach dem Muster in "
            f"referenz/profil.vorlage.toml an."
        )
    try:
        with datei.open("rb") as fh:
            roh = tomllib.load(fh)
    except tomllib.TOMLDecodeError as fehler:
        raise DatenFehler(f"{datei} ist kein gueltiges TOML: {fehler}") from fehler
    return _profil_aus_toml(roh, datei)


def _pflicht(abschnitt: dict, schluessel: str, typ: type, datei: Path):
    """Holt eine Pflichtangabe und prueft ihren Typ, statt sie umzuwandeln."""
    if schluessel not in abschnitt:
        raise DatenFehler(f"{datei}: Pflichtangabe '{schluessel}' fehlt.")
    wert = abschnitt[schluessel]
    # bool ist eine int-Unterklasse; ohne diese Zeile wuerde true zu 1.
    if typ is int and isinstance(wert, bool):
        raise DatenFehler(f"{datei}: '{schluessel}' muss eine Zahl sein, nicht true/false.")
    if not isinstance(wert, typ):
        raise DatenFehler(
            f"{datei}: '{schluessel}' muss {typ.__name__} sein, "
            f"ist {type(wert).__name__}."
        )
    return wert


def _optional_int(abschnitt: dict, schluessel: str, datei: Path) -> int | None:
    """Wie _pflicht, aber fehlend ist erlaubt und ergibt None — niemals 0."""
    if schluessel not in abschnitt:
        return None
    return _pflicht(abschnitt, schluessel, int, datei)


def _texte(abschnitt: dict, schluessel: str, datei: Path) -> tuple[str, ...]:
    werte = abschnitt.get(schluessel, [])
    if not isinstance(werte, list) or not all(isinstance(w, str) for w in werte):
        raise DatenFehler(f"{datei}: '{schluessel}' muss eine Liste von Texten sein.")
    return tuple(werte)


def _profil_aus_toml(roh: dict, datei: Path) -> Profil:
    kind = roh.get("kind", {})
    ziele = roh.get("ziele", {})
    behandlung = roh.get("behandlung", {})
    mahlzeiten = roh.get("mahlzeiten", {})
    praeferenzen = roh.get("praeferenzen", {})

    geplant = _texte(mahlzeiten, "plan", datei)
    if not geplant:
        raise DatenFehler(f"{datei}: '[mahlzeiten] plan' darf nicht leer sein.")

    return Profil(
        rufname=_pflicht(kind, "rufname", str, datei),
        geburtsdatum=_pflicht(kind, "geburtsdatum", date, datei),
        groesse_cm=_pflicht(kind, "groesse_cm", int, datei),
        zunahme_g_pro_woche=_pflicht(ziele, "zunahme_g_pro_woche", int, datei),
        mahlzeiten=geplant,
        kcal_taeglich=_optional_int(ziele, "kcal_taeglich", datei),
        kcal_quelle=ziele.get("kcal_quelle"),
        wiegen=behandlung.get("wiegen"),
        unvertraeglichkeiten=_texte(praeferenzen, "unvertraeglichkeiten", datei),
        fearfoods=_texte(praeferenzen, "fearfoods", datei),
    )
```

- [ ] **Step 4: Test laufen lassen und Erfolg bestätigen**

```bash
python3 -m unittest tests.test_daten -v
```

Erwartet: PASS, 11 Tests.

- [ ] **Step 5: Profilvorlage anlegen**

`referenz/profil.vorlage.toml`:

```toml
# Vorlage fuer $FBT_DATEN/profil.toml
# Diese Datei gehoert NICHT ins Repository, sondern ins Datenverzeichnis.
# Alles hier ist Beispiel und muss ersetzt werden.

[kind]
rufname = "Vorname"
geburtsdatum = 2012-01-01   # fuer das BMI-Altersperzentil
groesse_cm = 150

[ziele]
# kcal_taeglich gibt die Aerztin vor. Solange die Zeile fehlt oder
# auskommentiert ist, plant das Plugin, beurteilt aber nicht.
# kcal_taeglich = 2800
# kcal_quelle = "wer, wann"
zunahme_g_pro_woche = 500

[behandlung]
phase = 1
wiegen = "blind, 1-2x pro Woche"
# aerztin = ""
# naechster_termin = 2026-01-01

[mahlzeiten]
plan = [
  "fruehstueck",
  "snack_vormittag",
  "mittagessen",
  "snack_nachmittag",
  "abendessen",
  "snack_abend",
]

[praeferenzen]
unvertraeglichkeiten = []
fearfoods = []
abneigungen = []
```

- [ ] **Step 6: Committen**

```bash
git add fbt/daten.py referenz/profil.vorlage.toml tests/test_daten.py
git commit -m "feat(daten): Datenverzeichnis finden und Profil laden"
```

---

### Task 2: Anreicherungsmittel

**Files:**
- Create: `referenz/anreicherung.json`, `fbt/anreicherung.py`, `tests/test_anreicherung.py`

**Interfaces:**
- Consumes: nichts aus Task 1.
- Produces:
  - `class AnreicherungFehler(Exception)`
  - `@dataclass(frozen=True) class Mittel` mit `id, name, kcal_100g, dichte_g_ml, neutral, einsatz, hinweis, warnung` und `kcal(menge: float, einheit: str) -> float`
  - `lade_mittel(datei: Path | None = None) -> dict[str, Mittel]`

Die Tabelle bekommt **eigene, gegen Standardnährwerttabellen geprüfte Werte**. Sie erbt ausdrücklich keine Zahlen aus einzelnen Kochbuchrezepten — dort widersprechen sich die Angaben (Sahne zwischen 200 und 312 kcal/100 ml, siehe Spec 6.4).

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`tests/test_anreicherung.py`:

```python
"""Tests fuer die Anreicherungstabelle."""

import unittest
from pathlib import Path

from fbt.anreicherung import AnreicherungFehler, lade_mittel

TABELLE = Path(__file__).resolve().parent.parent / "referenz" / "anreicherung.json"


class TabelleTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_enthaelt_die_kernmittel(self):
        for schluessel in (
            "sahne-30",
            "mascarpone",
            "butter",
            "rapsoel",
            "maltodextrin",
            "creme-double",
        ):
            self.assertIn(schluessel, self.mittel)

    def test_alle_eintraege_sind_vollstaendig_und_plausibel(self):
        for schluessel, m in self.mittel.items():
            with self.subTest(mittel=schluessel):
                self.assertTrue(m.name)
                self.assertTrue(m.einsatz)
                # Kein Lebensmittel hat mehr als 900 kcal/100 g — reines Fett
                # liegt bei 884. Ein hoeherer Wert ist ein Tippfehler.
                self.assertGreater(m.kcal_100g, 0)
                self.assertLessEqual(m.kcal_100g, 900)
                if m.dichte_g_ml is not None:
                    self.assertGreater(m.dichte_g_ml, 0.5)
                    self.assertLess(m.dichte_g_ml, 1.5)

    def test_maltodextrin_traegt_die_refeeding_warnung(self):
        self.assertIsNotNone(self.mittel["maltodextrin"].warnung)
        self.assertIn("Refeeding", self.mittel["maltodextrin"].warnung)


class RechnenTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_rechnet_gramm(self):
        sahne = self.mittel["sahne-30"]
        self.assertAlmostEqual(sahne.kcal(200, "g"), sahne.kcal_100g * 2, places=6)

    def test_rechnet_milliliter_ueber_die_dichte(self):
        oel = self.mittel["rapsoel"]
        erwartet = oel.kcal_100g * (100 * oel.dichte_g_ml) / 100
        self.assertAlmostEqual(oel.kcal(100, "ml"), erwartet, places=6)

    def test_meldet_fehlende_dichte_statt_zu_raten(self):
        ohne = [m for m in self.mittel.values() if m.dichte_g_ml is None]
        self.assertTrue(ohne, "Die Tabelle braucht mindestens ein Mittel ohne Dichte")
        with self.assertRaises(AnreicherungFehler) as fall:
            ohne[0].kcal(100, "ml")
        self.assertIn("Dichte", str(fall.exception))

    def test_lehnt_unbekannte_einheit_ab(self):
        with self.assertRaises(AnreicherungFehler):
            self.mittel["butter"].kcal(1, "EL")

    def test_lehnt_negative_menge_ab(self):
        with self.assertRaises(AnreicherungFehler):
            self.mittel["butter"].kcal(-5, "g")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag bestätigen**

```bash
python3 -m unittest tests.test_anreicherung -v
```

Erwartet: FAIL mit `ModuleNotFoundError: No module named 'fbt.anreicherung'`.

- [ ] **Step 3: `referenz/anreicherung.json` anlegen**

Jeder Eintrag: `name`, `kcal_100g`, `dichte_g_ml` (oder `null`), `neutral` (ob geschmacksneutral), `einsatz` (wo es unsichtbar bleibt), optional `hinweis`, optional `warnung`.

```json
{
  "sahne-30":       {"name": "Schlagsahne 30 % Fett", "kcal_100g": 292, "dichte_g_ml": 1.0, "neutral": false, "einsatz": "ersetzt Milch und Wasser in fast jedem Rezept"},
  "sahne-36":       {"name": "Schlagsahne 36 % Fett", "kcal_100g": 337, "dichte_g_ml": 1.0, "neutral": false, "einsatz": "wie Sahne 30 %, wenn mehr Dichte noetig ist"},
  "creme-double":   {"name": "Creme double 40 %", "kcal_100g": 450, "dichte_g_ml": 1.0, "neutral": false, "einsatz": "in Suppen und Saucen, ersetzt saure Sahne"},
  "creme-fraiche":  {"name": "Creme fraiche 30 %", "kcal_100g": 292, "dichte_g_ml": 1.0, "neutral": false, "einsatz": "ersetzt saure Sahne und Joghurt"},
  "mascarpone":     {"name": "Mascarpone", "kcal_100g": 380, "dichte_g_ml": null, "neutral": false, "einsatz": "in Shakes, Saucen und falschem Joghurt"},
  "ricotta":        {"name": "Ricotta", "kcal_100g": 170, "dichte_g_ml": null, "neutral": false, "einsatz": "gibt Masse ohne viel Geschmack"},
  "butter":         {"name": "Butter", "kcal_100g": 741, "dichte_g_ml": null, "neutral": false, "einsatz": "in warmem Gebaeck und in Teigen unsichtbar"},
  "ghee":           {"name": "Butterschmalz", "kcal_100g": 892, "dichte_g_ml": null, "neutral": true, "einsatz": "zum Anbraten, geschmacklich unauffaellig"},
  "rapsoel":        {"name": "Rapsoel", "kcal_100g": 884, "dichte_g_ml": 0.92, "neutral": true, "einsatz": "1 EL (ca. 14 g) bringt rund 124 kcal, in Saucen unsichtbar"},
  "sonnenblumenoel":{"name": "Sonnenblumenoel", "kcal_100g": 884, "dichte_g_ml": 0.92, "neutral": true, "einsatz": "wie Rapsoel"},
  "beikostoel":     {"name": "Beikostoel fuer Babys", "kcal_100g": 884, "dichte_g_ml": 0.92, "neutral": true, "einsatz": "geschmacksneutral, laesst sich in fast alles ruehren"},
  "olivenoel":      {"name": "Olivenoel", "kcal_100g": 884, "dichte_g_ml": 0.91, "neutral": false, "einsatz": "in Pesto, Hummus und Nudelgerichten"},
  "leinoel":        {"name": "Leinoel", "kcal_100g": 884, "dichte_g_ml": 0.93, "neutral": false, "einsatz": "kalt in Shakes und Suppen, nicht erhitzen"},
  "lecithin":       {"name": "Lecithin", "kcal_100g": 763, "dichte_g_ml": null, "neutral": true, "einsatz": "bindet Oel, damit keine Fettaugen sichtbar sind"},
  "maltodextrin":   {"name": "Maltodextrin 6", "kcal_100g": 385, "dichte_g_ml": null, "neutral": true, "einsatz": "in Getraenken und Tee, kaum suess",
                     "warnung": "Kohlenhydratpulver. In den ersten zwei Wochen des Refeedings nur nach aerztlicher Absprache — Refeeding-Syndrom."},
  "mandelmus":      {"name": "Mandelmus", "kcal_100g": 630, "dichte_g_ml": null, "neutral": false, "einsatz": "in Porridge, Shakes und Saucen"},
  "erdnussbutter":  {"name": "Erdnussbutter", "kcal_100g": 590, "dichte_g_ml": null, "neutral": false, "einsatz": "in Shakes und auf Brot"},
  "cashewmus":      {"name": "Cashewmus", "kcal_100g": 600, "dichte_g_ml": null, "neutral": true, "einsatz": "bindet und verdichtet Suppen fast geschmacksneutral"},
  "walnuesse":      {"name": "Walnuesse", "kcal_100g": 654, "dichte_g_ml": null, "neutral": false, "einsatz": "gemahlen in Shakes, gehackt als Topping"},
  "haselnuesse":    {"name": "Haselnuesse", "kcal_100g": 628, "dichte_g_ml": null, "neutral": false, "einsatz": "gemahlen in Teigen und Shakes"},
  "mandeln":        {"name": "Mandeln", "kcal_100g": 575, "dichte_g_ml": null, "neutral": false, "einsatz": "gemahlen in Smoothie Bowls"},
  "cashewkerne":    {"name": "Cashewkerne", "kcal_100g": 553, "dichte_g_ml": null, "neutral": true, "einsatz": "mitpuerieren, macht Suppen cremig"},
  "parmesan":       {"name": "Parmesan", "kcal_100g": 400, "dichte_g_ml": null, "neutral": false, "einsatz": "bindet Oel in Saucen und Risotto"},
  "gouda-48":       {"name": "Gouda 48 %", "kcal_100g": 356, "dichte_g_ml": null, "neutral": false, "einsatz": "ueberbacken auf Auflaeufen"},
  "schmelzkaese":   {"name": "Sahneschmelzkaese", "kcal_100g": 300, "dichte_g_ml": null, "neutral": false, "einsatz": "in Nudelsaucen und Auflaeufen"},
  "vollmilch":      {"name": "Vollmilch 3,5 %", "kcal_100g": 65, "dichte_g_ml": 1.03, "neutral": false, "einsatz": "Grundlage, die durch Sahne ersetzt werden kann"},
  "jerseymilch":    {"name": "Jersey-Milch 5,8 %", "kcal_100g": 85, "dichte_g_ml": 1.03, "neutral": false, "einsatz": "ersetzt normale Milch unauffaellig"},
  "joghurt-griech": {"name": "Griechischer Joghurt 10 %", "kcal_100g": 130, "dichte_g_ml": null, "neutral": false, "einsatz": "ersetzt normalen Joghurt"},
  "kondensmilch":   {"name": "Gezuckerte Kondensmilch", "kcal_100g": 330, "dichte_g_ml": 1.28, "neutral": false, "einsatz": "in French Toast, Shakes und Desserts"},
  "kokosmilch":     {"name": "Kokosmilch aus der Dose", "kcal_100g": 200, "dichte_g_ml": 1.0, "neutral": false, "einsatz": "in Suppen und Currys"},
  "avocado":        {"name": "Avocado", "kcal_100g": 160, "dichte_g_ml": null, "neutral": true, "einsatz": "puerieren, verschwindet in Tomatensauce"},
  "datteln":        {"name": "Datteln", "kcal_100g": 280, "dichte_g_ml": null, "neutral": false, "einsatz": "suesst Shakes und Smoothies"},
  "zucker":         {"name": "Zucker", "kcal_100g": 400, "dichte_g_ml": null, "neutral": false, "einsatz": "in Getraenken und Gebaeck"},
  "honig":          {"name": "Honig", "kcal_100g": 300, "dichte_g_ml": 1.42, "neutral": false, "einsatz": "in warmer Milch und auf Brot"},
  "ahornsirup":     {"name": "Ahornsirup", "kcal_100g": 260, "dichte_g_ml": 1.33, "neutral": false, "einsatz": "auf French Toast und Porridge"},
  "traubensaft":    {"name": "Traubensaft", "kcal_100g": 68, "dichte_g_ml": 1.05, "neutral": false, "einsatz": "als Getraenk zu jeder Mahlzeit"},
  "orangensaft":    {"name": "Orangensaft", "kcal_100g": 45, "dichte_g_ml": 1.04, "neutral": false, "einsatz": "als Getraenk und in Smoothies"}
}
```

> **Diese Werte sind Standardnährwerte und vor der produktiven Nutzung einmal
> mit den Packungsangaben der tatsächlich gekauften Produkte abzugleichen.**
> Marken unterscheiden sich, besonders bei Sahne, Mascarpone und Nussmus. Der
> Abgleich gehört in Task 4 Step 5.

- [ ] **Step 4: `fbt/anreicherung.py` implementieren**

```python
"""Anreicherungsmittel und die Rechnung von Menge zu Kalorien.

Die Werte in referenz/anreicherung.json sind gepruefte Standardnaehrwerte. Sie
stammen bewusst nicht aus einzelnen Kochbuchrezepten — deren Angaben
widersprechen sich (Sahne zwischen 200 und 312 kcal/100 ml).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

STANDARD_TABELLE = Path(__file__).resolve().parent.parent / "referenz" / "anreicherung.json"


class AnreicherungFehler(Exception):
    """Eine Menge laesst sich mit den vorhandenen Angaben nicht umrechnen."""


@dataclass(frozen=True)
class Mittel:
    """Ein Lebensmittel, mit dem sich ein Gericht verdichten laesst."""

    id: str
    name: str
    kcal_100g: float
    dichte_g_ml: float | None
    neutral: bool
    einsatz: str
    hinweis: str | None = None
    warnung: str | None = None

    def kcal(self, menge: float, einheit: str) -> float:
        """Kalorien fuer eine Menge in 'g' oder 'ml'.

        Fehlt fuer 'ml' die Dichte, wird das gemeldet statt geschaetzt: eine
        geratene Dichte verfaelscht jede Bilanz, die darauf aufbaut.
        """
        if menge < 0:
            raise AnreicherungFehler(f"{self.name}: negative Menge {menge} {einheit}.")
        if einheit == "g":
            return self.kcal_100g * menge / 100
        if einheit == "ml":
            if self.dichte_g_ml is None:
                raise AnreicherungFehler(
                    f"{self.name}: keine Dichte hinterlegt, ml laesst sich nicht "
                    f"umrechnen. Bitte in Gramm angeben."
                )
            return self.kcal_100g * (menge * self.dichte_g_ml) / 100
        raise AnreicherungFehler(
            f"{self.name}: Einheit '{einheit}' wird nicht unterstuetzt, nur 'g' und 'ml'."
        )


def lade_mittel(datei: Path | None = None) -> dict[str, Mittel]:
    """Liest die Anreicherungstabelle."""
    datei = STANDARD_TABELLE if datei is None else datei
    roh = json.loads(datei.read_text(encoding="utf-8"))
    return {
        schluessel: Mittel(
            id=schluessel,
            name=eintrag["name"],
            kcal_100g=float(eintrag["kcal_100g"]),
            dichte_g_ml=(
                None if eintrag.get("dichte_g_ml") is None
                else float(eintrag["dichte_g_ml"])
            ),
            neutral=bool(eintrag.get("neutral", False)),
            einsatz=eintrag["einsatz"],
            hinweis=eintrag.get("hinweis"),
            warnung=eintrag.get("warnung"),
        )
        for schluessel, eintrag in roh.items()
    }
```

- [ ] **Step 5: Test laufen lassen und Erfolg bestätigen**

```bash
python3 -m unittest tests.test_anreicherung -v
```

Erwartet: PASS.

- [ ] **Step 6: Committen**

```bash
git add referenz/anreicherung.json fbt/anreicherung.py tests/test_anreicherung.py
git commit -m "feat(anreicherung): Tabelle der Anreicherungsmittel mit Mengenrechnung"
```

---

### Task 3: Kochbuch-Schema und Validator

**Files:**
- Create: `referenz/kochbuch.schema.json`, `fbt/kochbuch.py`, `tests/test_kochbuch.py`

**Interfaces:**
- Consumes: `fbt.daten.daten_pfad`, `fbt.daten.DatenFehler`
- Produces:
  - `@dataclass(frozen=True) class Rezept` mit `id, titel, kategorie, portionen, kcal_pro_portion, zutaten, zubereitung, zeit_min, geraete, allergene, quelle, pruefen, pruefnotiz`
  - `lade_kochbuch(datei: Path | None = None) -> dict[str, Rezept]`
  - `pruefe_rezept(roh: dict) -> list[str]` — Strukturfehler als Klartextliste
  - `plausibilitaet(roh: dict, mittel: dict) -> str | None` — Notiz, wenn Summe und Gesamtangabe um mehr als 10 % auseinanderliegen

**Warum Validator und nicht Importer:** Die Spec sprach von einem Importer. Rezepttexte aus einem PDF zu strukturieren ist Urteilsarbeit, keine Parserarbeit — Mengen stehen als „2 geh. TL", Kalorien mal pro Portion, mal fürs ganze Rezept. Das macht Claude einmalig (Task 4); das Plugin liefert das Schema und den Validator, der das Ergebnis prüft. Das erspart zugleich eine PDF-Abhängigkeit.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`tests/test_kochbuch.py`:

```python
"""Tests fuer Schema und Plausibilitaetspruefung des Kochbuchs."""

import json
import tempfile
import unittest
from pathlib import Path

from fbt.anreicherung import lade_mittel
from fbt.kochbuch import lade_kochbuch, plausibilitaet, pruefe_rezept

TABELLE = Path(__file__).resolve().parent.parent / "referenz" / "anreicherung.json"

GUELTIG = {
    "titel": "Testshake",
    "kategorie": "getraenke",
    "portionen": 1,
    "kcal_pro_portion": 500,
    "zutaten": [
        {"menge": 100, "einheit": "g", "was": "Sahne", "mittel": "sahne-30"},
        {"menge": 50, "einheit": "g", "was": "Mascarpone", "mittel": "mascarpone"},
    ],
    "zubereitung": "Alles verruehren.",
    "zeit_min": 5,
    "geraete": [],
    "allergene": ["milch"],
    "quelle": "Netzwerk-Kochbuch S. 9",
}


class SchemaTest(unittest.TestCase):
    def test_gueltiges_rezept_hat_keine_fehler(self):
        self.assertEqual(pruefe_rezept(GUELTIG), [])

    def test_meldet_fehlendes_pflichtfeld(self):
        ohne = {k: v for k, v in GUELTIG.items() if k != "kcal_pro_portion"}
        self.assertIn("kcal_pro_portion", " ".join(pruefe_rezept(ohne)))

    def test_meldet_null_portionen(self):
        self.assertTrue(pruefe_rezept({**GUELTIG, "portionen": 0}))

    def test_meldet_unbekannte_einheit(self):
        kaputt = {**GUELTIG, "zutaten": [{"menge": 2, "einheit": "EL", "was": "Oel"}]}
        self.assertIn("EL", " ".join(pruefe_rezept(kaputt)))

    def test_meldet_unbekannte_kategorie(self):
        self.assertTrue(pruefe_rezept({**GUELTIG, "kategorie": "quatsch"}))


class PlausibilitaetTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_stimmige_angabe_ergibt_keine_notiz(self):
        # 100 g Sahne (292) + 50 g Mascarpone (190) = 482, angegeben 500 -> 3,6 %
        self.assertIsNone(plausibilitaet(GUELTIG, self.mittel))

    def test_abweichung_ueber_zehn_prozent_wird_gemeldet(self):
        # Dieselben Zutaten, aber 900 kcal behauptet -> 87 % daneben.
        notiz = plausibilitaet({**GUELTIG, "kcal_pro_portion": 900}, self.mittel)
        self.assertIsNotNone(notiz)
        self.assertIn("900", notiz)

    def test_ohne_zuordenbare_zutaten_keine_falsche_sicherheit(self):
        # Sind die Zutaten nicht der Tabelle zuzuordnen, darf die Pruefung nicht
        # so tun, als haette sie geprueft.
        ohne = {**GUELTIG, "zutaten": [{"menge": 200, "einheit": "g", "was": "Kartoffeln"}]}
        notiz = plausibilitaet(ohne, self.mittel)
        self.assertIsNotNone(notiz)
        self.assertIn("nicht pruefbar", notiz)


class LadenTest(unittest.TestCase):
    def test_laedt_und_meldet_kaputte_eintraege_mit_id(self):
        basis = Path(tempfile.mkdtemp())
        datei = basis / "kochbuch.json"
        datei.write_text(
            json.dumps({"testshake": GUELTIG, "kaputt": {"titel": "X"}}),
            encoding="utf-8",
        )
        with self.assertRaises(Exception) as fall:
            lade_kochbuch(datei)
        self.assertIn("kaputt", str(fall.exception))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag bestätigen**

```bash
python3 -m unittest tests.test_kochbuch -v
```

Erwartet: FAIL mit `ModuleNotFoundError: No module named 'fbt.kochbuch'`.

- [ ] **Step 3: Schema und Modul implementieren**

`referenz/kochbuch.schema.json` dokumentiert die Struktur für Menschen (es wird nicht maschinell ausgewertet — der Validator in `fbt/kochbuch.py` ist die ausführbare Wahrheit):

```json
{
  "beschreibung": "Struktur eines Eintrags in $FBT_DATEN/kochbuch.json. Die Rezeptdaten selbst gehoeren nicht ins Repository.",
  "schluessel": "kebab-case-id, aus dem Titel abgeleitet",
  "felder": {
    "titel": "Text, Pflicht",
    "kategorie": "eine von: getraenke, fruehstueck, suppen, nudeln, fleisch, vegetarisch, backen, dessert, snack",
    "portionen": "ganze Zahl > 0, Pflicht",
    "kcal_pro_portion": "Zahl > 0, Pflicht",
    "zutaten": "Liste aus {menge: Zahl, einheit: 'g'|'ml'|'stueck', was: Text, mittel: optionaler Schluessel aus anreicherung.json}",
    "zubereitung": "Text, Pflicht",
    "zeit_min": "ganze Zahl >= 0, Pflicht",
    "geraete": "Liste von Texten, z. B. ['thermomix', 'mixer']",
    "allergene": "Liste von Texten, z. B. ['milch', 'nuesse', 'ei', 'gluten']",
    "quelle": "Text mit Seitenangabe, Pflicht",
    "pruefen": "optional true, wenn die Plausibilitaetspruefung angeschlagen hat",
    "pruefnotiz": "optionaler Text mit dem Befund"
  }
}
```

`fbt/kochbuch.py`:

```python
"""Laedt das Kochbuch der Familie und prueft es auf Struktur und Plausibilitaet.

Die Rezeptdaten liegen in $FBT_DATEN/kochbuch.json und nicht im Repository: Das
Netzwerk-Kochbuch untersagt die Weitergabe an Dritte. Hier stehen nur Schema und
Pruefung.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from fbt.daten import DatenFehler, daten_pfad

KATEGORIEN = frozenset(
    {"getraenke", "fruehstueck", "suppen", "nudeln", "fleisch",
     "vegetarisch", "backen", "dessert", "snack"}
)
EINHEITEN = frozenset({"g", "ml", "stueck"})
TOLERANZ = 0.10


@dataclass(frozen=True)
class Rezept:
    id: str
    titel: str
    kategorie: str
    portionen: int
    kcal_pro_portion: float
    zutaten: tuple[dict, ...]
    zubereitung: str
    zeit_min: int
    geraete: tuple[str, ...] = ()
    allergene: tuple[str, ...] = ()
    quelle: str = ""
    pruefen: bool = False
    pruefnotiz: str | None = None

    @property
    def kcal_gesamt(self) -> float:
        return self.kcal_pro_portion * self.portionen


def _zahl(wert, name: str, fehler: list[str], *, ganz: bool = False) -> None:
    if isinstance(wert, bool) or not isinstance(wert, int if ganz else (int, float)):
        fehler.append(f"'{name}' muss eine Zahl sein, ist {type(wert).__name__}.")
    elif wert <= 0:
        fehler.append(f"'{name}' muss groesser als 0 sein, ist {wert}.")


def pruefe_rezept(roh: dict) -> list[str]:
    """Prueft die Struktur eines Rezepts. Leere Liste heisst: in Ordnung."""
    fehler: list[str] = []
    for pflicht in ("titel", "kategorie", "portionen", "kcal_pro_portion",
                    "zutaten", "zubereitung", "zeit_min", "quelle"):
        if pflicht not in roh:
            fehler.append(f"Pflichtfeld '{pflicht}' fehlt.")
    if fehler:
        return fehler

    if roh["kategorie"] not in KATEGORIEN:
        fehler.append(
            f"Unbekannte Kategorie '{roh['kategorie']}', erlaubt: "
            f"{', '.join(sorted(KATEGORIEN))}."
        )
    _zahl(roh["portionen"], "portionen", fehler, ganz=True)
    _zahl(roh["kcal_pro_portion"], "kcal_pro_portion", fehler)

    if not isinstance(roh["zutaten"], list) or not roh["zutaten"]:
        fehler.append("'zutaten' muss eine nicht-leere Liste sein.")
    else:
        for i, zutat in enumerate(roh["zutaten"]):
            if not isinstance(zutat, dict):
                fehler.append(f"Zutat {i} ist kein Objekt.")
                continue
            if zutat.get("einheit") not in EINHEITEN:
                fehler.append(
                    f"Zutat {i} ('{zutat.get('was', '?')}'): Einheit "
                    f"'{zutat.get('einheit')}' nicht erlaubt, nur "
                    f"{', '.join(sorted(EINHEITEN))}."
                )
            _zahl(zutat.get("menge"), f"zutaten[{i}].menge", fehler)
    return fehler


def plausibilitaet(roh: dict, mittel: dict) -> str | None:
    """Vergleicht die angegebenen Kalorien mit der Summe der zuordenbaren Zutaten.

    Gibt None zurueck, wenn beides zusammenpasst. Sonst eine Notiz. Laesst sich
    keine Zutat zuordnen, wird das ausdruecklich gesagt — eine Pruefung, die
    nichts geprueft hat, darf nicht wie eine bestandene aussehen.
    """
    summe = 0.0
    zugeordnet = 0
    for zutat in roh.get("zutaten", []):
        schluessel = zutat.get("mittel")
        if schluessel is None or schluessel not in mittel:
            continue
        einheit = zutat.get("einheit")
        if einheit not in ("g", "ml"):
            continue
        try:
            summe += mittel[schluessel].kcal(zutat["menge"], einheit)
        except Exception:  # noqa: BLE001 — Fehlerdetails haengen am Mittel
            continue
        zugeordnet += 1

    if zugeordnet == 0:
        return "nicht pruefbar: keine Zutat liess sich der Anreicherungstabelle zuordnen."

    behauptet = roh["kcal_pro_portion"] * roh["portionen"]
    if summe == 0:
        return f"nicht pruefbar: zugeordnete Zutaten ergeben 0 kcal, behauptet sind {behauptet:.0f}."
    abweichung = abs(behauptet - summe) / summe
    if abweichung <= TOLERANZ:
        return None
    return (
        f"Abweichung {abweichung * 100:.0f} %: {zugeordnet} zugeordnete Zutaten "
        f"ergeben {summe:.0f} kcal, angegeben sind {behauptet:.0f} kcal. "
        f"Unzugeordnete Zutaten koennen die Differenz erklaeren — bitte pruefen."
    )


def lade_kochbuch(datei: Path | None = None) -> dict[str, Rezept]:
    """Liest $FBT_DATEN/kochbuch.json und bricht bei Strukturfehlern ab."""
    datei = (daten_pfad() / "kochbuch.json") if datei is None else datei
    if not datei.is_file():
        raise DatenFehler(f"Kein Kochbuch unter {datei}.")
    roh = json.loads(datei.read_text(encoding="utf-8"))

    fehler: list[str] = []
    rezepte: dict[str, Rezept] = {}
    for schluessel, eintrag in roh.items():
        eintrags_fehler = pruefe_rezept(eintrag)
        if eintrags_fehler:
            fehler.append(f"{schluessel}: " + " ".join(eintrags_fehler))
            continue
        rezepte[schluessel] = Rezept(
            id=schluessel,
            titel=eintrag["titel"],
            kategorie=eintrag["kategorie"],
            portionen=eintrag["portionen"],
            kcal_pro_portion=float(eintrag["kcal_pro_portion"]),
            zutaten=tuple(eintrag["zutaten"]),
            zubereitung=eintrag["zubereitung"],
            zeit_min=eintrag["zeit_min"],
            geraete=tuple(eintrag.get("geraete", ())),
            allergene=tuple(eintrag.get("allergene", ())),
            quelle=eintrag.get("quelle", ""),
            pruefen=bool(eintrag.get("pruefen", False)),
            pruefnotiz=eintrag.get("pruefnotiz"),
        )
    if fehler:
        raise DatenFehler(
            f"{datei} enthaelt {len(fehler)} fehlerhafte Rezepte:\n"
            + "\n".join(fehler)
        )
    return rezepte
```

- [ ] **Step 4: Test laufen lassen und Erfolg bestätigen**

```bash
python3 -m unittest tests.test_kochbuch -v
```

Erwartet: PASS.

- [ ] **Step 5: Committen**

```bash
git add referenz/kochbuch.schema.json fbt/kochbuch.py tests/test_kochbuch.py
git commit -m "feat(kochbuch): Schema, Strukturpruefung und Plausibilitaetspruefung"
```

---

### Task 4: Kochbuchdaten übertragen (einmalige Datenarbeit)

**Files:**
- Create: `$FBT_DATEN/kochbuch.json` (**außerhalb des Repos**, wird nicht committet)
- Create: `docs/kochbuch-import.md` (Protokoll der Übertragung, ohne Rezeptinhalte)

**Interfaces:**
- Consumes: `fbt.kochbuch.pruefe_rezept`, `fbt.kochbuch.plausibilitaet`, `fbt.anreicherung.lade_mittel`
- Produces: `$FBT_DATEN/kochbuch.json` mit allen Rezepten des Netzwerk-Kochbuchs

Dies ist Urteilsarbeit, kein Parsing. Der Kochbuchtext ist uneinheitlich: Kalorien stehen mal pro Portion, mal fürs ganze Rezept, mal gar nicht; Mengen als „2 geh. TL" oder „1 Becher"; Portionsangaben fehlen oft.

- [ ] **Step 1: Kochbuchtext extrahieren**

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
python3 -m venv /tmp/fbt-import-venv
/tmp/fbt-import-venv/bin/pip install --quiet pypdf
/tmp/fbt-import-venv/bin/python -c "
from pypdf import PdfReader
r = PdfReader('DOC-20260417-WA0000_260909_132609.pdf')
open('/tmp/kochbuch.txt','w').write('\n'.join(p.extract_text() or '' for p in r.pages))
print('Seiten:', len(r.pages))
"
```

Erwartet: 39 Seiten. Das venv ist Wegwerfware und wird in Step 6 gelöscht; `pypdf` wird **nicht** Abhängigkeit des Plugins.

- [ ] **Step 2: Zielverzeichnis vorbereiten**

```bash
mkdir -p "${FBT_DATEN:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/FBT-Daten}/tage"
```

- [ ] **Step 3: Rezepte in Stapeln zu je 10 übertragen**

Für jedes Rezept aus `/tmp/kochbuch.txt`:

- `id` in kebab-case aus dem Titel, eindeutig. Kommt ein Titel doppelt vor (z. B. zwei „Kartoffelsuppe"), Suffix `-2`.
- `kcal_pro_portion`: Steht im Kochbuch eine Gesamtangabe **und** eine Portionszahl, durch die Portionen teilen. Steht nur eine Gesamtangabe ohne Portionen, `portionen: 1` setzen und die Gesamtangabe übernehmen.
- **Fehlt die Kalorienangabe ganz: Rezept mit `"pruefen": true` und `"pruefnotiz": "keine kcal-Angabe im Kochbuch"` aufnehmen und `kcal_pro_portion` aus den Zutaten über die Anreicherungstabelle rechnen.** Nicht raten, nicht überspringen.
- `zutaten[].mittel` setzen, wo eine Zutat einem Schlüssel aus `anreicherung.json` entspricht. Das ist die Grundlage der Plausibilitätsprüfung — je mehr zugeordnet, desto belastbarer.
- Mengen wie „2 geh. TL" oder „1 Becher" in Gramm umrechnen und den Originalwortlaut in `was` behalten, z. B. `{"menge": 10, "einheit": "g", "was": "Gemuesebruehpaste (2 geh. TL)"}`.
- `quelle` mit Seitenzahl.

- [ ] **Step 4: Plausibilität über ALLE Rezepte prüfen**

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
python3 -c "
import json, os, pathlib
from fbt.anreicherung import lade_mittel
from fbt.kochbuch import pruefe_rezept, plausibilitaet
from fbt.daten import daten_pfad

datei = daten_pfad() / 'kochbuch.json'
roh = json.loads(datei.read_text(encoding='utf-8'))
mittel = lade_mittel()
struktur = {k: f for k, v in roh.items() if (f := pruefe_rezept(v))}
notizen = {k: n for k, v in roh.items() if not pruefe_rezept(v) and (n := plausibilitaet(v, mittel))}
print(f'Rezepte gesamt:      {len(roh)}')
print(f'Strukturfehler:      {len(struktur)}')
print(f'Plausibilitaetsnotiz:{len(notizen)}')
for k, f in struktur.items(): print(' STRUKTUR', k, f)
for k, n in notizen.items(): print(' NOTIZ   ', k, n)
"
```

**Abnahme:** `Strukturfehler: 0`. Jede Plausibilitätsnotiz wird einzeln angesehen: entweder die Übertragung korrigieren oder, wenn die Kochbuchangabe selbst der Ausreißer ist, `"pruefen": true` mit `"pruefnotiz"` setzen. Keine Notiz bleibt unkommentiert. Dies läuft über **alle** Rezepte — das ist die Lehre aus Plan 1.

- [ ] **Step 5: Anreicherungstabelle gegen die tatsächlichen Produkte abgleichen**

Für die Mittel, die in den übertragenen Rezepten am häufigsten vorkommen, die Packungsangaben der zu Hause verwendeten Produkte prüfen und `referenz/anreicherung.json` korrigieren, wo sie abweichen. Abweichungen im Protokoll festhalten.

- [ ] **Step 6: Protokoll schreiben und aufräumen**

`docs/kochbuch-import.md` — **ohne Rezeptinhalte**, nur Zahlen und Befunde: Anzahl Rezepte je Kategorie, Anzahl mit `pruefen: true` und warum, Abweichungen der Anreicherungstabelle, Rezepte ohne Original-kcal.

```bash
rm -rf /tmp/fbt-import-venv /tmp/kochbuch.txt
git add docs/kochbuch-import.md
git commit -m "docs: Protokoll der Kochbuchuebertragung"
```

- [ ] **Step 7: Bestätigen, dass keine Rezeptdaten im Repo liegen**

```bash
git status --short
grep -rl "kcal_pro_portion" --include="*.json" . | grep -v node_modules || echo "keine Rezeptdaten im Repo"
```

Erwartet: `referenz/anreicherung.json` taucht **nicht** auf (es hat kein `kcal_pro_portion`), und `kochbuch.json` liegt nicht im Repo.

---

### Task 5: Rezept auf Ziel-Kalorien bringen

**Files:**
- Create: `fbt/anreichern.py`, `tests/test_anreichern.py`

**Interfaces:**
- Consumes: `fbt.anreicherung.Mittel`, `fbt.anreicherung.lade_mittel`
- Produces:
  - `@dataclass(frozen=True) class Vorschlag` mit `art: str` (`"ersetzen"` oder `"zugeben"`), `mittel_id: str`, `menge_g: float`, `kcal: float`, `ersetzt: str | None`, `begruendung: str`
  - `@dataclass(frozen=True) class Anreicherung` mit `ausgangs_kcal: float`, `ziel_kcal: float`, `luecke_kcal: float`, `vorschlaege: tuple[Vorschlag, ...]`, `erreicht_kcal: float`, `warnungen: tuple[str, ...]`
  - `anreichern(rezept: dict, ziel_kcal_pro_portion: float, mittel: dict, *, refeeding_phase: bool = False) -> Anreicherung`

Regeln, abgeleitet aus dem Kochbuchkapitel „Allgemeine Tipps":

1. **Ersetzen vor Zugeben.** Ist Milch oder Wasser im Rezept, wird sie durch Sahne ersetzt, bevor etwas hinzukommt — sichtbar mehr auf dem Teller löst Angst aus.
2. **Fett und Protein vor Kohlenhydraten**, wegen der Refeeding-Syndrom-Prophylaxe.
3. **Geschmacksneutrale Mittel bevorzugen.**
4. **In der Refeeding-Phase kein Maltodextrin** ohne ärztliche Absprache.
5. **Nie über das Ziel hinausschießen.** Lieber knapp darunter als darüber.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`tests/test_anreichern.py`:

```python
"""Tests fuer die Anreicherungslogik."""

import unittest
from pathlib import Path

from fbt.anreicherung import lade_mittel
from fbt.anreichern import anreichern

TABELLE = Path(__file__).resolve().parent.parent / "referenz" / "anreicherung.json"

MIT_MILCH = {
    "titel": "Testbrei",
    "portionen": 2,
    "kcal_pro_portion": 200,
    "zutaten": [
        {"menge": 400, "einheit": "ml", "was": "Vollmilch", "mittel": "vollmilch"},
        {"menge": 60, "einheit": "g", "was": "Haferflocken"},
    ],
}

OHNE_ERSETZBARES = {
    "titel": "Testsuppe",
    "portionen": 2,
    "kcal_pro_portion": 150,
    "zutaten": [{"menge": 500, "einheit": "g", "was": "Kuerbis"}],
}


class AnreichernTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_ziel_unter_ausgang_ergibt_keine_vorschlaege(self):
        e = anreichern(MIT_MILCH, 150, self.mittel)
        self.assertEqual(e.vorschlaege, ())
        self.assertLessEqual(e.luecke_kcal, 0)

    def test_ersetzt_milch_durch_sahne_bevor_es_zugibt(self):
        e = anreichern(MIT_MILCH, 600, self.mittel)
        self.assertTrue(e.vorschlaege)
        erster = e.vorschlaege[0]
        self.assertEqual(erster.art, "ersetzen")
        self.assertEqual(erster.ersetzt, "vollmilch")
        self.assertEqual(erster.mittel_id, "sahne-30")

    def test_gibt_neutrales_fett_zu_wenn_nichts_zu_ersetzen_ist(self):
        e = anreichern(OHNE_ERSETZBARES, 600, self.mittel)
        self.assertTrue(e.vorschlaege)
        self.assertTrue(all(v.art == "zugeben" for v in e.vorschlaege))
        self.assertTrue(self.mittel[e.vorschlaege[0].mittel_id].neutral)

    def test_schiesst_nicht_ueber_das_ziel_hinaus(self):
        e = anreichern(OHNE_ERSETZBARES, 600, self.mittel)
        self.assertLessEqual(e.erreicht_kcal, 600 * 1.05)

    def test_meidet_maltodextrin_in_der_refeeding_phase(self):
        e = anreichern(OHNE_ERSETZBARES, 900, self.mittel, refeeding_phase=True)
        self.assertNotIn("maltodextrin", [v.mittel_id for v in e.vorschlaege])
        self.assertTrue(any("Maltodextrin" in w for w in e.warnungen))

    def test_warnt_wenn_das_ziel_nicht_erreichbar_ist(self):
        e = anreichern(OHNE_ERSETZBARES, 5000, self.mittel)
        self.assertTrue(any("nicht erreicht" in w for w in e.warnungen))

    def test_rechnet_pro_portion_nicht_pro_rezept(self):
        # 2 Portionen a 200 kcal, Ziel 400 -> Luecke sind 400 kcal insgesamt.
        e = anreichern(MIT_MILCH, 400, self.mittel)
        self.assertAlmostEqual(e.luecke_kcal, (400 - 200) * 2, places=6)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag bestätigen**

```bash
python3 -m unittest tests.test_anreichern -v
```

Erwartet: FAIL mit `ModuleNotFoundError: No module named 'fbt.anreichern'`.

- [ ] **Step 3: `fbt/anreichern.py` implementieren**

```python
"""Bringt ein Rezept auf eine Ziel-Kalorienmenge pro Portion.

Die Regeln stammen aus dem Kapitel 'Allgemeine Tipps zum kalorienverdichteten
Kochen' des Netzwerk-Kochbuchs: ersetzen statt zugeben, damit die Portion nicht
sichtbar waechst; Fett und Protein vor Kohlenhydraten; geschmacksneutral
bevorzugen.
"""

from __future__ import annotations

from dataclasses import dataclass

from fbt.anreicherung import Mittel

# Womit sich eine vorhandene Zutat 1:1 ersetzen laesst.
ERSATZ = {
    "vollmilch": "sahne-30",
    "jerseymilch": "sahne-30",
    "joghurt-griech": "mascarpone",
    "creme-fraiche": "creme-double",
}

# Reihenfolge, in der zugegeben wird: neutrales Fett zuerst, dann fettreiche
# Milchprodukte, dann Nussmus. Kohlenhydrate stehen bewusst am Ende.
ZUGABE_REIHENFOLGE = ("rapsoel", "cashewmus", "mascarpone", "creme-double", "mandelmus")

MAX_ZUGABE_G = {"rapsoel": 40, "cashewmus": 40, "mascarpone": 100,
                "creme-double": 100, "mandelmus": 50}


@dataclass(frozen=True)
class Vorschlag:
    art: str
    mittel_id: str
    menge_g: float
    kcal: float
    ersetzt: str | None
    begruendung: str


@dataclass(frozen=True)
class Anreicherung:
    ausgangs_kcal: float
    ziel_kcal: float
    luecke_kcal: float
    vorschlaege: tuple[Vorschlag, ...]
    erreicht_kcal: float
    warnungen: tuple[str, ...]


def anreichern(
    rezept: dict,
    ziel_kcal_pro_portion: float,
    mittel: dict[str, Mittel],
    *,
    refeeding_phase: bool = False,
) -> Anreicherung:
    """Schlaegt konkrete Zutatenaenderungen vor, um das Ziel zu erreichen."""
    portionen = rezept["portionen"]
    ausgang = rezept["kcal_pro_portion"]
    luecke = (ziel_kcal_pro_portion - ausgang) * portionen

    warnungen: list[str] = []
    if refeeding_phase:
        warnungen.append(
            "Refeeding-Phase: Maltodextrin wird nicht vorgeschlagen — "
            "Kohlenhydratpulver nur nach aerztlicher Absprache."
        )
    if luecke <= 0:
        return Anreicherung(ausgang, ziel_kcal_pro_portion, luecke, (),
                            ausgang * portionen, tuple(warnungen))

    vorschlaege: list[Vorschlag] = []
    offen = luecke

    # 1. Ersetzen, solange es etwas zu ersetzen gibt.
    for zutat in rezept.get("zutaten", []):
        if offen <= 0:
            break
        alt = zutat.get("mittel")
        neu = ERSATZ.get(alt)
        if neu is None or neu not in mittel or alt not in mittel:
            continue
        einheit = zutat.get("einheit")
        if einheit not in ("g", "ml"):
            continue
        menge_g = zutat["menge"] * (mittel[alt].dichte_g_ml or 1.0 if einheit == "ml" else 1.0)
        gewinn = (mittel[neu].kcal_100g - mittel[alt].kcal_100g) * menge_g / 100
        if gewinn <= 0:
            continue
        gewinn = min(gewinn, offen)
        vorschlaege.append(
            Vorschlag(
                art="ersetzen",
                mittel_id=neu,
                menge_g=round(menge_g),
                kcal=round(gewinn),
                ersetzt=alt,
                begruendung=(
                    f"{mittel[alt].name} durch {mittel[neu].name} ersetzen — "
                    f"gleiche Menge, die Portion waechst nicht sichtbar."
                ),
            )
        )
        offen -= gewinn

    # 2. Zugeben, in fester Reihenfolge und mit Obergrenze je Mittel.
    for schluessel in ZUGABE_REIHENFOLGE:
        if offen <= 0:
            break
        m = mittel.get(schluessel)
        if m is None or (refeeding_phase and m.warnung):
            continue
        noetig_g = offen / m.kcal_100g * 100
        menge_g = min(noetig_g, MAX_ZUGABE_G.get(schluessel, 50) * portionen)
        if menge_g < 1:
            continue
        gewinn = m.kcal(menge_g, "g")
        vorschlaege.append(
            Vorschlag(
                art="zugeben",
                mittel_id=schluessel,
                menge_g=round(menge_g),
                kcal=round(gewinn),
                ersetzt=None,
                begruendung=f"{m.name}: {m.einsatz}.",
            )
        )
        offen -= gewinn

    if offen > 1:
        warnungen.append(
            f"Ziel nicht erreicht: es fehlen noch {offen:.0f} kcal. "
            f"Ein zweites Gericht oder ein Shake dazu ist sinnvoller, "
            f"als noch mehr in dieses Rezept zu ruehren."
        )

    erreicht = ausgang * portionen + sum(v.kcal for v in vorschlaege)
    return Anreicherung(
        ausgangs_kcal=ausgang,
        ziel_kcal=ziel_kcal_pro_portion,
        luecke_kcal=luecke,
        vorschlaege=tuple(vorschlaege),
        erreicht_kcal=erreicht,
        warnungen=tuple(warnungen),
    )
```

- [ ] **Step 4: Test laufen lassen und Erfolg bestätigen**

```bash
python3 -m unittest tests.test_anreichern -v
```

Erwartet: PASS.

- [ ] **Step 5: Committen**

```bash
git add fbt/anreichern.py tests/test_anreichern.py
git commit -m "feat(anreichern): Rezept auf Ziel-Kalorien bringen"
```

---

### Task 6: Tagesbilanz

**Files:**
- Create: `fbt/bilanz.py`, `referenz/tag.vorlage.toml`, `tests/test_bilanz.py`

**Interfaces:**
- Consumes: `fbt.daten.daten_pfad`, `fbt.daten.DatenFehler`
- Produces:
  - `@dataclass(frozen=True) class Gericht` mit `titel, quelle, kcal_geplant: float | None, anteil_gegessen: float | None`
  - `@dataclass(frozen=True) class Mahlzeit` mit `zeit, name, gerichte: tuple[Gericht, ...]`, `kcal_geplant`, `kcal_tatsaechlich`
  - `@dataclass(frozen=True) class Tagesbilanz` mit `datum, ziel_kcal: int | None, mahlzeiten, kcal_geplant, kcal_tatsaechlich, unbekannte: tuple[str, ...]`
  - `lade_tag(datum: date, basis: Path | None = None) -> Tagesbilanz`
  - `elternansicht(b: Tagesbilanz) -> str`
  - `tischansicht(b: Tagesbilanz) -> str`

**TOML-Fallstrick, zwingend beachten:** In TOML gehören alle Schlüssel auf oberster Ebene **vor** die erste Tabelle. Steht `beobachtungen` nach `[[mahlzeit]]`, wird es Teil der letzten Mahlzeit. Die Vorlage macht das vor, und ein Test sichert es ab.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`tests/test_bilanz.py`:

```python
"""Tests fuer die Tagesbilanz und die beiden Ausgabeformen."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fbt.bilanz import elternansicht, lade_tag, tischansicht

TAG = """
datum = 2026-02-03
ziel_kcal = 3000
beobachtungen = "Snack am Nachmittag war schwierig."

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800
  anteil_gegessen = 1.0

[[mahlzeit]]
zeit = "10:00"
name = "Snack"

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
  anteil_gegessen = 0.6
"""

OHNE_KCAL = """
datum = 2026-02-03

[[mahlzeit]]
zeit = "12:00"
name = "Mittag"

  [[mahlzeit.gericht]]
  titel = "Unbekanntes Gericht"
  quelle = "frei"
"""


def schreibe(inhalt: str) -> Path:
    basis = Path(tempfile.mkdtemp()) / "FBT Daten"
    (basis / "tage").mkdir(parents=True)
    (basis / "tage" / "2026-02-03.toml").write_text(inhalt, encoding="utf-8")
    return basis


class BilanzTest(unittest.TestCase):
    def test_rechnet_geplant_und_tatsaechlich_getrennt(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(b.kcal_geplant, 1300)
        self.assertEqual(b.kcal_tatsaechlich, 800 + 300)

    def test_beobachtungen_landen_nicht_in_der_letzten_mahlzeit(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(len(b.mahlzeiten), 2)
        self.assertEqual(b.mahlzeiten[-1].name, "Snack")

    def test_fehlende_kcal_sind_unbekannt_nicht_null(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIn("Unbekanntes Gericht", " ".join(b.unbekannte))
        self.assertEqual(b.kcal_geplant, 0)

    def test_fehlendes_ziel_ist_none(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIsNone(b.ziel_kcal)


class AnsichtTest(unittest.TestCase):
    def setUp(self):
        self.b = lade_tag(date(2026, 2, 3), schreibe(TAG))

    def test_elternansicht_zeigt_zahlen(self):
        text = elternansicht(self.b)
        self.assertIn("3000", text)
        self.assertIn("1100", text)

    def test_tischansicht_enthaelt_keine_einzige_zahl_aus_dem_kalorienbereich(self):
        text = tischansicht(self.b)
        for verboten in ("3000", "1300", "1100", "800", "500", "kcal", "Kalorien"):
            self.assertNotIn(verboten, text, f"'{verboten}' darf am Tisch nicht auftauchen")

    def test_tischansicht_zeigt_trotzdem_was_es_gibt(self):
        text = tischansicht(self.b)
        self.assertIn("Porridge", text)
        self.assertIn("07:30", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag bestätigen**

```bash
python3 -m unittest tests.test_bilanz -v
```

Erwartet: FAIL mit `ModuleNotFoundError: No module named 'fbt.bilanz'`.

- [ ] **Step 3: Vorlage und Modul implementieren**

`referenz/tag.vorlage.toml`:

```toml
# Vorlage fuer $FBT_DATEN/tage/JJJJ-MM-TT.toml
#
# ACHTUNG TOML: Alle Schluessel auf oberster Ebene muessen VOR der ersten
# [[mahlzeit]]-Tabelle stehen. Steht beobachtungen weiter unten, gehoert es
# plotzlich zur letzten Mahlzeit.

datum = 2026-01-01
ziel_kcal = 3000
beobachtungen = """
Freitext: Stimmung, was geholfen hat, was eskaliert ist, Auffaelligkeiten.
"""

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Power-Porridge"
  quelle = "kochbuch:power-porridge"   # oder "cookidoo:r16687" oder "frei"
  kcal_geplant = 800
  anteil_gegessen = 1.0                # 0.0 bis 1.0, Schaetzung der Eltern
```

`fbt/bilanz.py`:

```python
"""Liest eine Tagesdatei und rechnet die Bilanz.

Geplant und tatsaechlich werden getrennt ausgewiesen. anteil_gegessen ist eine
Schaetzung der Eltern; die Bilanz macht diese Unsicherheit sichtbar, statt eine
Scheingenauigkeit zu erzeugen.

Zwei Ausgabeformen, bewusst als zwei Funktionen: elternansicht() zeigt Zahlen,
tischansicht() nie. Eine Umschaltung waere eine Einstellung, die man vergessen
kann.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from fbt.daten import DatenFehler, daten_pfad


@dataclass(frozen=True)
class Gericht:
    titel: str
    quelle: str
    kcal_geplant: float | None
    anteil_gegessen: float | None

    @property
    def kcal_tatsaechlich(self) -> float | None:
        if self.kcal_geplant is None:
            return None
        anteil = 1.0 if self.anteil_gegessen is None else self.anteil_gegessen
        return self.kcal_geplant * anteil


@dataclass(frozen=True)
class Mahlzeit:
    zeit: str
    name: str
    gerichte: tuple[Gericht, ...]

    @property
    def kcal_geplant(self) -> float:
        return sum(g.kcal_geplant or 0 for g in self.gerichte)

    @property
    def kcal_tatsaechlich(self) -> float:
        return sum(g.kcal_tatsaechlich or 0 for g in self.gerichte)


@dataclass(frozen=True)
class Tagesbilanz:
    datum: date
    ziel_kcal: int | None
    mahlzeiten: tuple[Mahlzeit, ...]
    unbekannte: tuple[str, ...]
    beobachtungen: str = ""

    @property
    def kcal_geplant(self) -> float:
        return sum(m.kcal_geplant for m in self.mahlzeiten)

    @property
    def kcal_tatsaechlich(self) -> float:
        return sum(m.kcal_tatsaechlich for m in self.mahlzeiten)

    @property
    def abstand_zum_ziel(self) -> float | None:
        if self.ziel_kcal is None:
            return None
        return self.kcal_tatsaechlich - self.ziel_kcal


def lade_tag(datum: date, basis: Path | None = None) -> Tagesbilanz:
    """Liest $FBT_DATEN/tage/JJJJ-MM-TT.toml."""
    basis = daten_pfad() if basis is None else basis
    datei = basis / "tage" / f"{datum.isoformat()}.toml"
    if not datei.is_file():
        raise DatenFehler(f"Keine Tagesdatei unter {datei}.")
    try:
        with datei.open("rb") as fh:
            roh = tomllib.load(fh)
    except tomllib.TOMLDecodeError as fehler:
        raise DatenFehler(f"{datei} ist kein gueltiges TOML: {fehler}") from fehler

    unbekannte: list[str] = []
    mahlzeiten: list[Mahlzeit] = []
    for m in roh.get("mahlzeit", []):
        gerichte: list[Gericht] = []
        for g in m.get("gericht", []):
            kcal = g.get("kcal_geplant")
            if kcal is None:
                unbekannte.append(f"{m.get('name', '?')}: {g.get('titel', '?')}")
            gerichte.append(
                Gericht(
                    titel=g.get("titel", "?"),
                    quelle=g.get("quelle", "frei"),
                    kcal_geplant=None if kcal is None else float(kcal),
                    anteil_gegessen=g.get("anteil_gegessen"),
                )
            )
        mahlzeiten.append(
            Mahlzeit(zeit=m.get("zeit", ""), name=m.get("name", ""),
                     gerichte=tuple(gerichte))
        )

    return Tagesbilanz(
        datum=roh.get("datum", datum),
        ziel_kcal=roh.get("ziel_kcal"),
        mahlzeiten=tuple(mahlzeiten),
        unbekannte=tuple(unbekannte),
        beobachtungen=roh.get("beobachtungen", ""),
    )


def elternansicht(b: Tagesbilanz) -> str:
    """Vollstaendige Bilanz mit Zahlen. Nicht fuer den Esstisch."""
    zeilen = [f"Bilanz {b.datum.isoformat()}", ""]
    for m in b.mahlzeiten:
        zeilen.append(f"{m.zeit}  {m.name}")
        for g in m.gerichte:
            if g.kcal_geplant is None:
                zeilen.append(f"    {g.titel}: kcal unbekannt")
                continue
            anteil = "" if g.anteil_gegessen in (None, 1.0) else f" ({g.anteil_gegessen:.0%})"
            zeilen.append(
                f"    {g.titel}: {g.kcal_geplant:.0f} geplant"
                f"{anteil} -> {g.kcal_tatsaechlich:.0f}"
            )
    zeilen += ["", f"geplant:     {b.kcal_geplant:.0f} kcal",
               f"tatsaechlich: {b.kcal_tatsaechlich:.0f} kcal"]
    if b.ziel_kcal is not None:
        zeilen.append(f"Ziel:        {b.ziel_kcal} kcal ({b.abstand_zum_ziel:+.0f})")
    else:
        zeilen.append("Ziel:        nicht hinterlegt — bitte aerztliche Vorgabe eintragen.")
    if b.unbekannte:
        zeilen += ["", "Ohne Kalorienangabe (nicht als 0 gerechnet):"]
        zeilen += [f"    {u}" for u in b.unbekannte]
    return "\n".join(zeilen)


def tischansicht(b: Tagesbilanz) -> str:
    """Was es wann gibt. Enthaelt keine Kalorien, kein Gewicht, kein Ziel."""
    zeilen = [f"Plan fuer {b.datum.strftime('%d.%m.%Y')}", ""]
    for m in b.mahlzeiten:
        zeilen.append(f"{m.zeit}  {m.name}")
        zeilen += [f"    {g.titel}" for g in m.gerichte]
    return "\n".join(zeilen)
```

- [ ] **Step 4: Test laufen lassen und Erfolg bestätigen**

```bash
python3 -m unittest tests.test_bilanz -v
```

Erwartet: PASS.

- [ ] **Step 5: Gesamte Suite laufen lassen**

```bash
python3 -m unittest discover -s tests -v
```

Erwartet: alle Tests grün.

- [ ] **Step 6: Committen**

```bash
git add fbt/bilanz.py referenz/tag.vorlage.toml tests/test_bilanz.py
git commit -m "feat(bilanz): Tagesbilanz mit getrennter Eltern- und Tischansicht"
```

---

### Task 7: Skills

**Files:**
- Create: `skills/mahlzeit-planen/SKILL.md`, `skills/rezept-anreichern/SKILL.md`

**Interfaces:**
- Consumes: alle Module aus Tasks 1–6, der Cookidoo-MCP-Connector
- Produces: nichts für spätere Tasks

- [ ] **Step 1: `skills/mahlzeit-planen/SKILL.md` schreiben**

```markdown
---
name: mahlzeit-planen
description: Use when planning meals for a day of family-based refeeding - building a day of six meals that reaches a prescribed calorie target, choosing recipes, and preparing the shopping list
---

# Einen Tag planen

## Vorab immer

1. Profil laden: `python3 -c "from fbt.daten import lade_profil; p = lade_profil(); print(p)"`
2. **Fehlt `kcal_taeglich`, frage danach und plane nicht auf einer erfundenen Zahl.**
   Die Menge gibt die Ärztin vor. Ohne sie kannst du Mahlzeiten vorschlagen, aber
   nicht behaupten, der Tag sei ausreichend.
3. Unverträglichkeiten und Fearfoods aus dem Profil beachten.

## Wie ein Tag aufgebaut wird

Sechs Mahlzeiten nach dem Plan im Profil. Grobe Verteilung der Tagesmenge:
Frühstück und die beiden Hauptmahlzeiten tragen je etwa ein Fünftel, die drei
Snacks zusammen die restlichen zwei Fünftel. Getränke zählen mit — allein über
Säfte und angereicherte Milch sind 800–1000 kcal am Tag möglich.

## Rezepte auswählen

Zwei Quellen:

- **Netzwerk-Kochbuch** (`fbt.kochbuch.lade_kochbuch`) — erprobt, Kalorien bekannt.
  Die erste Wahl an schwierigen Tagen und wenn es schnell gehen muss.
- **Cookidoo** über den Connector — für Abwechslung und wenn sich das Kind etwas
  Normales wünscht. `cookidoo_get_recipe_details` liefert `nutrition` mit
  Bezugsgröße. **Prüfe `basisUnit`:** steht dort `100 g` und nicht `Portion`,
  musst du umrechnen. Ist `nutrition` null, hat das Rezept keine Angabe — dann
  rechne über `fbt.anreichern`, statt eine Zahl anzunehmen.

Plane höchstens einen Tag im Voraus. Mut kommt in Wellen; ein Plan von gestern
verschenkt den Moment, in dem heute etwas geht.

## Regeln aus der Behandlung

- Die Eltern entscheiden, was auf den Teller kommt. Das Kind wählt nicht aus,
  wiegt nicht ab, sieht keine Kalorien.
- Keine Light- und Diätprodukte.
- Bei jeder Mahlzeit mindestens 300 ml Getränk anbieten, am besten Saft.
- In der Refeeding-Phase kein Maltodextrin ohne ärztliche Absprache.

## Ausgabe

Immer **zwei** Fassungen:

1. **Elternansicht** — mit kcal je Gericht und Tagessumme, plus was vorzukochen ist.
2. **Tischansicht** — nur Uhrzeit und was es gibt. Keine Kalorien, kein Gewicht,
   kein Ziel. Diese Fassung darf ausgedruckt am Kühlschrank hängen.

Schreibe den Plan als `$FBT_DATEN/tage/JJJJ-MM-TT.toml` nach dem Muster in
`referenz/tag.vorlage.toml`. **Alle Schlüssel auf oberster Ebene vor die erste
`[[mahlzeit]]`-Tabelle**, sonst landet `beobachtungen` in der letzten Mahlzeit.

## Einkauf

Fehlende Zutaten mit `cookidoo_add_recipe_ingredients` in die Cookidoo-Einkaufs-
liste schieben; was nicht aus einem Cookidoo-Rezept stammt, mit
`cookidoo_add_additional_items`.
```

- [ ] **Step 2: `skills/rezept-anreichern/SKILL.md` schreiben**

```markdown
---
name: rezept-anreichern
description: Use when a recipe needs to reach a higher calorie target for refeeding - computing concrete ingredient changes in grams without making the portion look bigger
---

# Ein Rezept anreichern

## Rechnen, nicht schätzen

```bash
python3 -c "
from fbt.anreicherung import lade_mittel
from fbt.anreichern import anreichern
rezept = {'titel': '...', 'portionen': 4, 'kcal_pro_portion': 229, 'zutaten': [...]}
e = anreichern(rezept, 700, lade_mittel(), refeeding_phase=False)
print(e)
"
```

Das Skript liefert konkrete Gramm-Angaben. Übernimm sie, statt eigene Zahlen zu
bilden — die Summe landet in der Tagesbilanz und damit im Arztbericht.

## Die Reihenfolge hat einen Grund

1. **Ersetzen vor Zugeben.** Milch durch Sahne, Wasser durch Brühe. Die Portion
   darf nicht sichtbar wachsen — sichtbar mehr auf dem Teller löst Angst aus.
2. **Fett und Protein vor Kohlenhydraten.** Refeeding-Syndrom-Prophylaxe.
3. **Geschmacksneutral bevorzugen.** Öl in der Sauce, Cashewmus in der Suppe.
4. **Nicht über das Ziel hinaus.** Lieber knapp darunter und ein Snack dazu.

## Unsichtbar machen

Aus dem Kochbuchkapitel „Allgemeine Tipps": Öl lässt sich mit Parmesan, Chia
oder Lecithin binden; Tomatenmark färbt sahnige Saucen zurück; Speck püriert
verschwindet in der Sauce; Butter zieht in warmes Gebäck ein; Reis in
Milch-Sahne statt Wasser quellen lassen sieht unverändert aus.

Sahne und Öl bei Shakes immer erst am Ende zugeben und nur kurz mischen — sonst
wird daraus Schlagsahne oder Mayonnaise.

## Grenzen

- Reicht ein Rezept nicht bis zum Ziel, gib nicht immer mehr hinein. Ein Shake
  dazu ist besser als eine Portion, die niemand schafft.
- **Maltodextrin in den ersten zwei Wochen des Refeedings nur nach ärztlicher
  Absprache.** Das Skript lässt es bei `refeeding_phase=True` automatisch weg.
- Kalorienangaben gehören nie in eine Ausgabe, die das Kind sehen kann.
```

- [ ] **Step 3: Committen**

```bash
git add skills/
git commit -m "feat(skills): Mahlzeitenplanung und Rezeptanreicherung"
```

---

### Task 8: Commands

**Files:**
- Create: `commands/tagesplan.md`, `commands/tagesabschluss.md`

- [ ] **Step 1: `commands/tagesplan.md` schreiben**

```markdown
---
description: Plant einen Tag mit sechs Mahlzeiten auf die ärztlich vorgegebene Kalorienmenge
---

Plane einen Tag für das Refeeding. Argument: `heute`, `morgen` oder ein Datum
(JJJJ-MM-TT). Ohne Argument: morgen.

Nutze die Skill `mahlzeit-planen`.

Ablauf:

1. Profil laden. Fehlt `kcal_taeglich`, frage danach und plane nicht auf einer
   erfundenen Zahl.
2. Die letzten drei Tagesdateien ansehen, um Wiederholungen zu vermeiden und zu
   sehen, was zuletzt gut lief.
3. Sechs Mahlzeiten vorschlagen, gemischt aus Netzwerk-Kochbuch und Cookidoo.
4. Die Tagesdatei `$FBT_DATEN/tage/JJJJ-MM-TT.toml` schreiben.
5. **Beide Ausgaben zeigen** — Elternansicht mit Zahlen, Tischansicht ohne.
6. Fragen, ob die fehlenden Zutaten in die Cookidoo-Einkaufsliste sollen.
```

- [ ] **Step 2: `commands/tagesabschluss.md` schreiben**

```markdown
---
description: Erfasst, was tatsächlich gegessen wurde, rechnet die Tagesbilanz und bereitet morgen vor
---

Schließe den Tag ab. Argument: Datum (JJJJ-MM-TT), ohne Argument heute.

Ablauf:

1. Tagesdatei laden. Fehlt sie, frage, was es gab, und lege sie an.
2. Für jede Mahlzeit fragen, wie viel angekommen ist. `anteil_gegessen` zwischen
   0.0 und 1.0 — eine Schätzung, und sie darf eine bleiben.
3. Beobachtungen aufnehmen: Stimmung, was geholfen hat, was eskaliert ist.
4. Bilanz rechnen:
   `python3 -c "from datetime import date; from fbt.bilanz import lade_tag, elternansicht; print(elternansicht(lade_tag(date(...))))"`
5. **Eskalationskriterien prüfen** — nur die symptombasierten, die heute
   berichtet wurden: Ohnmacht, Kreislaufbeschwerden, Erbrechen, Abführmittel,
   Selbstverletzung, Suizidalität. Trifft eines zu, sage das **zuerst** und
   verweise an Ärztin oder Klinik, statt über Optimierung zu Hause weiterzureden.
   **Sage ausdrücklich dazu, dass die gewichtsbasierten Kriterien (keine Zunahme
   über zwei Wochen, Abnahme) noch nicht automatisch geprüft werden** — das
   kommt mit Stufe 2. Eine halbe Prüfung darf nicht wie eine ganze aussehen.
6. Liegt der Tag deutlich unter Ziel, schlage vor, wie morgen aufgeholt wird —
   schrittweise, nicht sprunghaft. Der Arztbrief nennt 100–200 kcal pro Schritt.
7. Gerichte ohne Kalorienangabe benennen. Sie wurden nicht als 0 gerechnet.

Keine Belohnungs- oder Bestrafungslogik vorschlagen. Externalisierend sprechen:
die Krankheit hat den Snack verweigert, nicht das Kind.
```

- [ ] **Step 3: Gesamte Suite und Abschluss**

```bash
cd /Users/danielsteiner/Projects/family-based-treatment
python3 -m unittest discover -s tests -v
git add commands/
git commit -m "feat(commands): /tagesplan und /tagesabschluss"
```

- [ ] **Step 4: Ergebnis berichten**

Berichte an Daniel: die Commits, das Ergebnis der Testsuite, und was in
`$FBT_DATEN` angelegt wurde. **Nicht pushen, nicht mergen** — die Entscheidung
liegt bei ihm.

---

## Self-Review

**Spec-Abdeckung (Stufe 1 laut Spec Abschnitt 9):**

| Spec-Anforderung | Task |
|---|---|
| Trennung Plugin / Daten (5.1) | Task 1 (`fbt/daten.py`), Task 4 Step 7 (Nachweis) |
| `profil.toml` (6.1) | Task 1 |
| Tagesdateien (6.3) | Task 6 |
| `kochbuch.json` bei den Daten, Schema im Plugin (6.4) | Tasks 3 und 4 |
| Plausibilitätsprüfung mit 10-%-Schwelle (6.4) | Task 3, Task 4 Step 4 |
| `anreicherung.json` mit Maltodextrin-Warnung (6.5) | Task 2 |
| Anreicherungsregeln (7.1) | Task 5 |
| `bilanz.py`, geplant vs. tatsächlich (7.2) | Task 6 |
| Zwei Ausgabeformen (3.1) | Task 6 (`elternansicht`/`tischansicht`), Tasks 7 und 8 |
| Symptombasierte Eskalationsprüfung (3.2) | Task 8, `/tagesabschluss` Schritt 5 |
| Sprache und Externalisierung (3.3) | Tasks 7 und 8 |
| Rechnen statt schätzen (3.4) | Tasks 1, 2, 3, 6 — je ein Test |
| Cookidoo-Einkaufsliste (8) | Task 7, Task 8 |

Keine Lücke für Stufe 1. Gewichtsverlauf, BMI-Perzentile und Wochenbericht sind
Stufe 2 und hier bewusst nicht enthalten.

**Platzhalter:** keine. Jeder Codeschritt enthält den einzusetzenden Code, jeder
Testschritt Befehl und erwartete Ausgabe. Task 4 ist Datenarbeit; dort stehen
Verfahren und Abnahmekriterium statt Code, weil es nichts zu programmieren gibt.

**Typkonsistenz:** `Profil`, `Mittel`, `Rezept`, `Vorschlag`, `Anreicherung`,
`Gericht`, `Mahlzeit`, `Tagesbilanz` sind je genau einmal definiert. Feldnamen
`kcal_100g`, `dichte_g_ml`, `kcal_pro_portion`, `kcal_geplant`,
`anteil_gegessen`, `mittel`, `portionen` sind über alle Tasks identisch.
`DatenFehler` stammt aus `fbt.daten` und wird von `fbt.kochbuch` und
`fbt.bilanz` wiederverwendet.

**Abweichungen von der Spec, bewusst:**

1. **TOML statt YAML** für Profil und Tagesdateien. Grund: `tomllib` ist ab
   Python 3.11 Standardbibliothek, PyYAML nicht. Damit bleibt das Plugin ohne
   jede Installation lauffähig. Die Spec ist entsprechend nachzuziehen.
2. **Validator statt Importer** für das Kochbuch (Begründung in Task 3). Spart
   zugleich die PDF-Abhängigkeit.
3. **Deutsch im Code**, anders als in `cookidoo-mcp`. Anderes Repo, anderes
   Publikum, und die Domänenbegriffe sind deutsch.

**Risiko, das ich benennen will:** Task 4 ist mit Abstand der größte Posten und
der einzige, dessen Qualität sich nicht durch Unit-Tests sichern lässt — 80
Rezepte von Hand zu übertragen ist fehleranfällig. Die Plausibilitätsprüfung
über alle Rezepte ist das Netz, aber sie fängt nur, was der
Anreicherungstabelle zuzuordnen ist. Rezepte aus überwiegend nicht zuordenbaren
Zutaten (Gemüse, Mehl, Fleisch) kommen als „nicht prüfbar" durch. Das ist
bewusst so: eine Prüfung, die nichts geprüft hat, sagt das, statt zu bestehen.
