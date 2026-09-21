"""Laedt das Kochbuch der Familie und prueft es auf Struktur und Plausibilitaet.

Die Rezeptdaten liegen in $FBT_DATEN/kochbuch.json und nicht im Repository: Das
Netzwerk-Kochbuch untersagt die Weitergabe an Dritte. Hier stehen nur Schema und
Pruefung.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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
    portionen_geschaetzt: bool = False

    @property
    def kcal_gesamt(self) -> float:
        return self.kcal_pro_portion * self.portionen


def _zahl(wert, name: str, fehler: list[str], *, ganz: bool = False,
          null_erlaubt: bool = False) -> None:
    if isinstance(wert, bool) or not isinstance(wert, int if ganz else (int, float)):
        fehler.append(f"'{name}' muss eine Zahl sein, ist {type(wert).__name__}.")
    elif null_erlaubt and wert < 0:
        fehler.append(f"'{name}' darf nicht negativ sein, ist {wert}.")
    elif not null_erlaubt and wert <= 0:
        fehler.append(f"'{name}' muss groesser als 0 sein, ist {wert}.")


def _text(wert, name: str, fehler: list[str]) -> None:
    if not isinstance(wert, str) or not wert.strip():
        fehler.append(f"'{name}' muss ein nicht-leerer Text sein.")


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
    _zahl(roh["zeit_min"], "zeit_min", fehler, ganz=True, null_erlaubt=True)
    for name in ("titel", "zubereitung", "quelle"):
        _text(roh[name], name, fehler)

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


def plausibilitaet(roh: dict, mittel: dict, grund: dict | None = None) -> str | None:
    """Vergleicht die angegebenen Kalorien mit der Summe der zuordenbaren Zutaten.

    Sucht jeden Zutaten-Schluessel zuerst in der Anreicherungstabelle
    (`mittel`), dann in der Grundzutaten-Tabelle (`grund`) -- Dinge, die
    zugesetzt werden, und Dinge, aus denen das Gericht besteht, bleiben
    getrennte Tabellen, werden hier aber gemeinsam zum Pruefen herangezogen.

    Gibt None zurueck, wenn beides zusammenpasst. Sonst eine Notiz. Laesst sich
    keine Zutat zuordnen, wird das ausdruecklich gesagt — eine Pruefung, die
    nichts geprueft hat, darf nicht wie eine bestandene aussehen.
    """
    grund = grund or {}
    summe = 0.0
    zugeordnet = 0
    for zutat in roh.get("zutaten", []):
        schluessel = zutat.get("mittel")
        if schluessel in mittel:
            tabelle = mittel
        elif schluessel in grund:
            tabelle = grund
        else:
            continue
        einheit = zutat.get("einheit")
        if einheit not in ("g", "ml"):
            continue
        try:
            summe += tabelle[schluessel].kcal(zutat["menge"], einheit)
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
            portionen_geschaetzt=bool(eintrag.get("portionen_geschaetzt", False)),
        )
    if fehler:
        raise DatenFehler(
            f"{datei} enthaelt {len(fehler)} fehlerhafte Rezepte:\n"
            + "\n".join(fehler)
        )
    return rezepte
