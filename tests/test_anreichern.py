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
        # erreicht_kcal ist die Summe fuer ALLE Portionen, das Ziel gilt pro
        # Portion. Der Vergleich muss mit portionen multipliziert werden.
        portionen = OHNE_ERSETZBARES["portionen"]
        e = anreichern(OHNE_ERSETZBARES, 600, self.mittel)
        self.assertLessEqual(e.erreicht_kcal, 600 * portionen * 1.05)

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
        self.assertAlmostEqual(e.luecke_kcal, (400 - 200) * 2, places=6)


if __name__ == "__main__":
    unittest.main()
