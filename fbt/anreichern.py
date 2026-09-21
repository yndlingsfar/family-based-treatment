"""Bringt ein Rezept auf eine Ziel-Kalorienmenge pro Portion.

Die Regeln stammen aus dem Kapitel 'Allgemeine Tipps zum kalorienverdichteten
Kochen' des Netzwerk-Kochbuchs: ersetzen statt zugeben, damit die Portion nicht
sichtbar waechst; Fett und Protein vor Kohlenhydraten; geschmacksneutral
bevorzugen.
"""

from __future__ import annotations

from dataclasses import dataclass

from fbt.anreicherung import AnreicherungFehler, Mittel

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
    """Die Namen tragen ihre Bezugsgroesse, weil die Verwechslung teuer ist.

    Ausgang und Ziel gelten je Portion, Luecke und Erreichtes fuer den ganzen
    Topf. Dasselbe gilt fuer jeden Vorschlag: menge_g und kcal sind Gesamtmengen.
    """

    ausgangs_kcal_pro_portion: float
    ziel_kcal_pro_portion: float
    luecke_kcal_gesamt: float
    vorschlaege: tuple[Vorschlag, ...]
    erreicht_kcal_gesamt: float
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
        if luecke < 0:
            # Das Kochbuch ist auf 2800-3500 kcal/Tag ausgelegt; bei einer
            # niedrigeren Verordnung liegen viele Rezepte ueber dem, was eine
            # Mahlzeit tragen soll. Halbe Portionen kennt Stufe 1 noch nicht —
            # sichtbar muss der Fall trotzdem sein.
            warnungen.append(
                f"Das Rezept liegt bereits {-luecke / portionen:.0f} kcal pro "
                f"Portion ueber dem Ziel ({ausgang:.0f} statt "
                f"{ziel_kcal_pro_portion:.0f}). Nichts anzureichern — pruefe, "
                f"ob eine kleinere Portion oder ein anderes Rezept passt."
            )
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
        try:
            # Nicht selbst umrechnen: Mittel.kcal ist die Stelle, die ueber die
            # Dichte urteilt, und sie meldet eine fehlende, statt 1.0 zu raten.
            mittel[alt].kcal(zutat["menge"], einheit)
            menge_g_ganz = (zutat["menge"] if einheit == "g"
                            else zutat["menge"] * mittel[alt].dichte_g_ml)
            gewinn_ganz = (mittel[neu].kcal(menge_g_ganz, "g")
                           - mittel[alt].kcal(menge_g_ganz, "g"))
        except AnreicherungFehler as fehler:
            warnungen.append(
                f"{zutat.get('was', alt)} bleibt unveraendert: {fehler}"
            )
            continue
        if gewinn_ganz <= 0:
            continue

        # Nur so viel ersetzen, wie die Luecke hergibt. Frueher wurde die
        # gemeldete Zahl gekappt, die Menge aber nicht — der Vorschlag lieferte
        # dann mehr Kalorien, als die Bilanz auswies.
        menge_g = menge_g_ganz
        if gewinn_ganz > offen:
            menge_g = menge_g_ganz * (offen / gewinn_ganz)
        menge_g = round(menge_g)
        if menge_g < 1:
            continue
        # Aus der gerundeten Menge zurueckrechnen: gemeldet wird genau das, was
        # beim Ausfuehren des Vorschlags herauskommt.
        gewinn = mittel[neu].kcal(menge_g, "g") - mittel[alt].kcal(menge_g, "g")
        teilweise = menge_g < round(menge_g_ganz)
        vorschlaege.append(
            Vorschlag(
                art="ersetzen",
                mittel_id=neu,
                menge_g=menge_g,
                kcal=round(gewinn),
                ersetzt=alt,
                begruendung=(
                    f"{mittel[alt].name} durch {mittel[neu].name} ersetzen — "
                    + (f"{menge_g} g von insgesamt {round(menge_g_ganz)} g, "
                       f"der Rest bleibt {mittel[alt].name}. "
                       if teilweise else "gleiche Menge, ")
                    + "die Portion waechst nicht sichtbar."
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
        menge_g = round(min(noetig_g, MAX_ZUGABE_G.get(schluessel, 50) * portionen))
        if menge_g < 1:
            continue
        # Aus der gerundeten Menge rechnen, nicht aus der ungerundeten.
        gewinn = m.kcal(menge_g, "g")
        vorschlaege.append(
            Vorschlag(
                art="zugeben",
                mittel_id=schluessel,
                menge_g=menge_g,
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

    # Genau die Summe der Vorschlaege, wie sie ausgegeben werden — kein
    # gekappter Wert, der weniger verspricht, als im Topf landet.
    erreicht = ausgang * portionen + sum(v.kcal for v in vorschlaege)
    return Anreicherung(
        ausgangs_kcal_pro_portion=ausgang,
        ziel_kcal_pro_portion=ziel_kcal_pro_portion,
        luecke_kcal_gesamt=luecke,
        vorschlaege=tuple(vorschlaege),
        erreicht_kcal_gesamt=erreicht,
        warnungen=tuple(warnungen),
    )
