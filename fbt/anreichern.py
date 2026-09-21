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
# Milchprodukte, dann Nussmus. Maltodextrin steht als reines Kohlenhydrat ganz
# am Ende (Refeeding-Syndrom-Prophylaxe) und faellt bei refeeding_phase=True
# ueber seine Warnung aus der Auswahl.
ZUGABE_REIHENFOLGE = ("rapsoel", "cashewmus", "mascarpone", "creme-double",
                      "mandelmus", "maltodextrin")

MAX_ZUGABE_G = {"rapsoel": 40, "cashewmus": 40, "mascarpone": 100,
                "creme-double": 100, "mandelmus": 50, "maltodextrin": 40}


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
