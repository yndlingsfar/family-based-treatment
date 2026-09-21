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
