"""Liest eine Tagesdatei und rechnet die Bilanz.

Geplant und tatsaechlich werden getrennt ausgewiesen. anteil_gegessen ist eine
Schaetzung der Eltern; die Bilanz macht diese Unsicherheit sichtbar, statt eine
Scheingenauigkeit zu erzeugen.

Zwei Ausgabeformen, bewusst als zwei Funktionen: elternansicht() zeigt Zahlen,
tischansicht() nie. Eine Umschaltung waere eine Einstellung, die man vergessen
kann.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from fbt.daten import DatenFehler, daten_pfad

# Die Tagesdatei wird von Hand getippt. Jeder Schluessel, der hier nicht steht,
# ist ein Tippfehler — und ein Tippfehler in 'mahlzeit' wuerde einen normalen
# Tag als "nichts gegessen" in den Arztbericht tragen.
ERLAUBT_TAG = ("datum", "ziel_kcal", "beobachtungen", "mahlzeit")
ERLAUBT_MAHLZEIT = ("zeit", "name", "gericht")
ERLAUBT_GERICHT = ("titel", "quelle", "kcal_geplant", "anteil_gegessen")

# Eine Kalorienzahl im Titel landet ueber die Tischansicht vor dem Kind.
KCAL_IM_TITEL = re.compile(r"\d+\s*(kcal|kj)\b", re.IGNORECASE)


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
    angenommen: tuple[str, ...] = ()
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

    @property
    def vollstaendig(self) -> bool:
        """Weder fehlende Kalorienangaben noch angenommene Anteile."""
        return not self.unbekannte and not self.angenommen


def _fremde_schluessel(abschnitt: dict, erlaubt: tuple[str, ...], wo: str,
                       datei: Path) -> None:
    """Lehnt jeden Schluessel ab, der nicht in der Vorlage steht.

    Das faengt Beinahe-Treffer wie 'mahlzeiten', 'gerichte' oder 'Mahlzeit' —
    sie wuerden sonst stillschweigend als "nicht vorhanden" gelesen, und aus
    "nichts aufgeschrieben" wuerde "nichts gegessen".
    """
    fremd = sorted(s for s in abschnitt if s not in erlaubt)
    if fremd:
        raise DatenFehler(
            f"{datei}: unbekannter Schluessel '{fremd[0]}' {wo}"
            + (f" (ausserdem: {', '.join(fremd[1:])})" if len(fremd) > 1 else "")
            + f". Erlaubt sind hier nur: {', '.join(erlaubt)}. "
            f"Ein Tippfehler wie 'mahlzeiten' statt 'mahlzeit' wuerde sonst "
            f"als 'nichts gegessen' gelesen. Siehe referenz/tag.vorlage.toml."
        )


def _zahl(abschnitt: dict, schluessel: str, wo: str, datei: Path, *,
          ganz: bool = False, min_wert: float | None = None,
          max_wert: float | None = None) -> float | int | None:
    """Holt eine optionale Zahl und prueft ihren Typ, statt sie umzuwandeln.

    Fehlt der Schluessel, ist das None und niemals 0 — eine fehlende Angabe
    ist keine Null. Steht dort etwas, das keine Zahl ist, sagt die Meldung
    Datei, Ort und Wert, damit ein Elternteil die Stelle findet.
    """
    if schluessel not in abschnitt:
        return None
    wert = abschnitt[schluessel]
    # bool ist in Python eine int-Unterklasse; ohne diese Zeile wuerde
    # 'true' zu 1 kcal und saehe wie eine gemessene Angabe aus.
    if isinstance(wert, bool):
        raise DatenFehler(
            f"{datei}: '{schluessel}' {wo} muss eine Zahl sein, nicht "
            f"true/false. Aus 'true' wuerde sonst die Zahl 1."
        )
    if not isinstance(wert, int if ganz else (int, float)):
        raise DatenFehler(
            f"{datei}: '{schluessel}' {wo} muss eine "
            f"{'ganze Zahl' if ganz else 'Zahl'} sein, ist "
            f"{type(wert).__name__} ({wert!r}). Zahlen gehoeren ohne "
            f"Anfuehrungszeichen und ohne Zusaetze wie 'ca.' in die Datei."
        )
    if min_wert is not None and wert < min_wert:
        raise DatenFehler(
            f"{datei}: '{schluessel}' {wo} ist {wert}, erlaubt ist "
            f"{min_wert} bis {max_wert if max_wert is not None else 'aufwaerts'}."
        )
    if max_wert is not None and wert > max_wert:
        raise DatenFehler(
            f"{datei}: '{schluessel}' {wo} ist {wert}, erlaubt ist "
            f"{min_wert if min_wert is not None else 'hoechstens'} bis {max_wert}."
        )
    return wert


def _text(abschnitt: dict, schluessel: str, wo: str, datei: Path) -> str | None:
    if schluessel not in abschnitt:
        return None
    wert = abschnitt[schluessel]
    if not isinstance(wert, str):
        raise DatenFehler(
            f"{datei}: '{schluessel}' {wo} muss ein Text sein, ist "
            f"{type(wert).__name__} ({wert!r})."
        )
    return wert


def _datum(roh: dict, ersatz: date, datei: Path) -> date:
    """Das Datum steht auf dem Arztbericht — es muss ein Datum sein, kein Text."""
    if "datum" not in roh:
        return ersatz
    wert = roh["datum"]
    if isinstance(wert, datetime) or not isinstance(wert, date):
        raise DatenFehler(
            f"{datei}: 'datum' muss ein Datum ohne Uhrzeit sein (JJJJ-MM-TT, "
            f"ohne Anfuehrungszeichen), ist {type(wert).__name__} ({wert!r})."
        )
    return wert


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

    _fremde_schluessel(roh, ERLAUBT_TAG, "auf oberster Ebene", datei)

    roh_mahlzeiten = roh.get("mahlzeit")
    if not roh_mahlzeiten:
        raise DatenFehler(
            f"{datei}: keine einzige [[mahlzeit]]-Tabelle. Eine Tagesdatei ohne "
            f"Mahlzeiten wird nicht als 'null Kalorien gegessen' gerechnet — "
            f"sie ist unvollstaendig. Trage die Mahlzeiten nach dem Muster in "
            f"referenz/tag.vorlage.toml nach."
        )

    unbekannte: list[str] = []
    angenommen: list[str] = []
    mahlzeiten: list[Mahlzeit] = []
    for m in roh_mahlzeiten:
        # Pruefen ob oberste-Ebene-Schluessel verirrt sind
        verirrt = [s for s in ("beobachtungen", "ziel_kcal", "datum") if s in m]
        for gr in m.get("gericht", []):
            verirrt += [s for s in ("beobachtungen", "ziel_kcal", "datum") if s in gr]
        if verirrt:
            raise DatenFehler(
                f"{datei}: {', '.join(sorted(set(verirrt)))} steht unterhalb einer "
                f"[[mahlzeit]]-Tabelle und gehoert damit zur Mahlzeit statt zum Tag. "
                f"In TOML muessen alle Schluessel der obersten Ebene VOR der ersten "
                f"[[mahlzeit]] stehen. Siehe referenz/tag.vorlage.toml."
            )

        _fremde_schluessel(m, ERLAUBT_MAHLZEIT, "unterhalb einer [[mahlzeit]]", datei)
        name = _text(m, "name", "in einer [[mahlzeit]]", datei) or ""
        zeit = _text(m, "zeit", f"bei der Mahlzeit '{name or '?'}'", datei) or ""

        gerichte: list[Gericht] = []
        for g in m.get("gericht", []):
            titel = _text(g, "titel", f"bei einem Gericht ({name or '?'})", datei) or "?"
            wo = f"bei '{titel}' ({name or '?'})"
            _fremde_schluessel(g, ERLAUBT_GERICHT, wo, datei)
            kcal = _zahl(g, "kcal_geplant", wo, datei, min_wert=0)
            # Der Anteil ist eine Schaetzung der Eltern, aber keine Zahl
            # ausserhalb von 0 bis 1: 1.5 wuerde Kalorien erfinden, -0.5
            # wuerde andere Mahlzeiten stillschweigend wegkuerzen.
            anteil = _zahl(g, "anteil_gegessen", wo, datei,
                           min_wert=0.0, max_wert=1.0)
            if kcal is None:
                unbekannte.append(f"{name or '?'}: {titel}")
            elif anteil is None:
                angenommen.append(f"{name or '?'}: {titel}")
            gerichte.append(
                Gericht(
                    titel=titel,
                    quelle=_text(g, "quelle", wo, datei) or "frei",
                    kcal_geplant=None if kcal is None else float(kcal),
                    anteil_gegessen=None if anteil is None else float(anteil),
                )
            )
        mahlzeiten.append(Mahlzeit(zeit=zeit, name=name, gerichte=tuple(gerichte)))

    return Tagesbilanz(
        datum=_datum(roh, datum, datei),
        ziel_kcal=_zahl(roh, "ziel_kcal", "auf oberster Ebene", datei,
                        ganz=True, min_wert=1),
        mahlzeiten=tuple(mahlzeiten),
        unbekannte=tuple(unbekannte),
        angenommen=tuple(angenommen),
        beobachtungen=_text(roh, "beobachtungen", "auf oberster Ebene", datei) or "",
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
    zeilen.append("")
    # Totalen mit Vollstaendigkeitsmarker: unterscheide Arten der Luecken
    unvollstaendig_marker = ""
    if not b.vollstaendig:
        luecken = []
        if b.unbekannte:
            count = len(b.unbekannte)
            wort = "Gericht" if count == 1 else "Gerichte"
            luecken.append(f"{count} {wort} ohne Kalorienangabe")
        if b.angenommen:
            count = len(b.angenommen)
            wort = "Gericht" if count == 1 else "Gerichte"
            luecken.append(f"{count} {wort} ohne Anteil")
        unvollstaendig_marker = f"  (unvollstaendig: {', '.join(luecken)})"
    zeilen.append(f"geplant:     {b.kcal_geplant:.0f} kcal{unvollstaendig_marker}")
    zeilen.append(f"tatsaechlich: {b.kcal_tatsaechlich:.0f} kcal{unvollstaendig_marker}")
    if b.ziel_kcal is not None:
        zeilen.append(f"Ziel:        {b.ziel_kcal} kcal ({b.abstand_zum_ziel:+.0f})")
    else:
        zeilen.append("Ziel:        nicht hinterlegt — bitte aerztliche Vorgabe eintragen.")
    if b.angenommen:
        zeilen += ["", "Ohne Angabe, als vollstaendig gerechnet:"]
        zeilen += [f"    {u}" for u in b.angenommen]
    if b.unbekannte:
        zeilen += ["", "Ohne Kalorienangabe (nicht als 0 gerechnet):"]
        zeilen += [f"    {u}" for u in b.unbekannte]
    return "\n".join(zeilen)


def tischansicht(b: Tagesbilanz) -> str:
    """Was es wann gibt. Enthaelt keine Kalorien, kein Gewicht, kein Ziel.

    Der Titel kommt aus der Tagesdatei und wird am Tisch gelesen. Steht eine
    Kalorienzahl darin, wird das hier zum Fehler und nicht stillschweigend
    weggeputzt: die Zahl steht dann auch in der Datei, und dort gehoert sie
    heraus — sonst taucht sie beim naechsten Ausdruck wieder auf.
    """
    for m in b.mahlzeiten:
        for g in m.gerichte:
            if KCAL_IM_TITEL.search(g.titel):
                raise DatenFehler(
                    f"Der Titel '{g.titel}' ({m.name or '?'}) enthaelt eine "
                    f"Kalorienangabe. Die Tischansicht wird am Esstisch "
                    f"gelesen — bitte die Zahl aus dem Titel in der Tagesdatei "
                    f"entfernen, die Kalorien stehen in 'kcal_geplant'."
                )
    zeilen = [f"Plan fuer {b.datum.strftime('%d.%m.%Y')}", ""]
    for m in b.mahlzeiten:
        zeilen.append(f"{m.zeit}  {m.name}")
        zeilen += [f"    {g.titel}" for g in m.gerichte]
    return "\n".join(zeilen)
