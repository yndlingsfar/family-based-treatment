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
