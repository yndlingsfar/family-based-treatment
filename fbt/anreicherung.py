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
