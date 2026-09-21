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
