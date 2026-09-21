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

# joghurt-griech hat keine Dichte hinterlegt: in ml laesst sich daraus nichts
# rechnen, ohne eine Dichte zu erfinden.
OHNE_DICHTE = {
    "titel": "Testjoghurt",
    "portionen": 2,
    "kcal_pro_portion": 200,
    "zutaten": [
        {"menge": 200, "einheit": "ml", "was": "Griechischer Joghurt",
         "mittel": "joghurt-griech"},
    ],
}


def nachgerechnet(e, mittel) -> float:
    """Was beim Ausfuehren der Vorschlaege tatsaechlich herauskommt."""
    summe = 0.0
    for v in e.vorschlaege:
        pro_100g = mittel[v.mittel_id].kcal_100g
        if v.ersetzt is not None:
            pro_100g -= mittel[v.ersetzt].kcal_100g
        summe += pro_100g * v.menge_g / 100
    return summe


class AnreichernTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_ziel_unter_ausgang_ergibt_keine_vorschlaege(self):
        e = anreichern(MIT_MILCH, 150, self.mittel)
        self.assertEqual(e.vorschlaege, ())
        self.assertLessEqual(e.luecke_kcal_gesamt, 0)

    def test_warnt_wenn_das_rezept_ueber_dem_ziel_liegt(self):
        # Das Kochbuch ist auf eine hoehere Tagesmenge ausgelegt: der Fall
        # "Portion zu gross" muss wenigstens sichtbar sein.
        e = anreichern(MIT_MILCH, 150, self.mittel)
        self.assertTrue(any("ueber dem Ziel" in w for w in e.warnungen))
        self.assertTrue(any("50 kcal pro Portion" in w for w in e.warnungen))

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
        # erreicht_kcal_gesamt ist die Summe fuer ALLE Portionen, das Ziel gilt
        # pro Portion. Der Vergleich muss mit portionen multipliziert werden.
        portionen = OHNE_ERSETZBARES["portionen"]
        e = anreichern(OHNE_ERSETZBARES, 600, self.mittel)
        self.assertLessEqual(e.erreicht_kcal_gesamt, 600 * portionen * 1.05)

    def test_gemeldete_summe_entspricht_den_ausgegebenen_mengen(self):
        """Der Vorschlag darf nicht mehr liefern, als die Bilanz ausweist.

        Frueher wurde der gemeldete Gewinn gekappt, die Ersetzungsmenge aber
        nicht: 'die ganze Milch ersetzen' brachte 935 kcal, gemeldet waren 800.
        Genau dieser Fall (ein ersetzbares Mittel) fehlte im Test, weil
        OHNE_ERSETZBARES nur den Zugeben-Zweig laeuft.
        """
        e = anreichern(MIT_MILCH, 600, self.mittel)
        self.assertTrue(any(v.art == "ersetzen" for v in e.vorschlaege))
        basis = MIT_MILCH["kcal_pro_portion"] * MIT_MILCH["portionen"]
        tatsaechlich = basis + nachgerechnet(e, self.mittel)
        self.assertAlmostEqual(e.erreicht_kcal_gesamt, tatsaechlich,
                               delta=0.5 * len(e.vorschlaege) + 0.5)
        # und zugleich nicht deutlich ueber dem Ziel
        self.assertLessEqual(tatsaechlich, 600 * MIT_MILCH["portionen"] * 1.02)

    def test_ersetzen_ist_teilweise_wenn_die_luecke_kleiner_ist(self):
        """Ein kleiner Rest wird nicht mit der ganzen Milchmenge gestopft."""
        e = anreichern(MIT_MILCH, 240, self.mittel)  # Luecke: 80 kcal gesamt
        ersetzungen = [v for v in e.vorschlaege if v.art == "ersetzen"]
        self.assertEqual(len(ersetzungen), 1)
        # Die ganze Milch (412 g) braeuchte es nicht — nur ein Bruchteil.
        self.assertLess(ersetzungen[0].menge_g, 100)
        basis = MIT_MILCH["kcal_pro_portion"] * MIT_MILCH["portionen"]
        self.assertAlmostEqual(basis + nachgerechnet(e, self.mittel),
                               240 * MIT_MILCH["portionen"], delta=3)

    def test_zutat_ohne_dichte_wird_uebersprungen_und_genannt(self):
        """Keine geratene Dichte — lieber ein Vorschlag weniger und ein Hinweis."""
        e = anreichern(OHNE_DICHTE, 600, self.mittel)
        self.assertTrue(all(v.art == "zugeben" for v in e.vorschlaege))
        self.assertTrue(any("Joghurt" in w and "Dichte" in w for w in e.warnungen),
                        f"Warnung fehlt oder nennt die Zutat nicht: {e.warnungen}")

    def test_nutzt_maltodextrin_als_letztes_mittel_ausserhalb_der_refeeding_phase(self):
        e = anreichern(OHNE_ERSETZBARES, 2000, self.mittel)
        self.assertIn("maltodextrin", [v.mittel_id for v in e.vorschlaege])

    def test_meidet_maltodextrin_in_der_refeeding_phase(self):
        # Gleiches Ziel wie im Test darueber, nur mit refeeding_phase=True:
        # nur so zeigt sich, dass die Sperre wirkt und nicht bloss nie greift.
        e = anreichern(OHNE_ERSETZBARES, 2000, self.mittel, refeeding_phase=True)
        self.assertNotIn("maltodextrin", [v.mittel_id for v in e.vorschlaege])
        self.assertTrue(any("Maltodextrin" in w for w in e.warnungen))

    def test_warnt_wenn_das_ziel_nicht_erreichbar_ist(self):
        e = anreichern(OHNE_ERSETZBARES, 5000, self.mittel)
        self.assertTrue(any("nicht erreicht" in w for w in e.warnungen))

    def test_rechnet_pro_portion_nicht_pro_rezept(self):
        # 2 Portionen a 200 kcal, Ziel 400 -> Luecke sind 400 kcal insgesamt.
        e = anreichern(MIT_MILCH, 400, self.mittel)
        self.assertAlmostEqual(e.luecke_kcal_gesamt, (400 - 200) * 2, places=6)


if __name__ == "__main__":
    unittest.main()
