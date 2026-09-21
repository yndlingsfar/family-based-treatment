"""Tests fuer die Tagesbilanz und die beiden Ausgabeformen."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fbt.bilanz import elternansicht, lade_tag, tischansicht

TAG = """
datum = 2026-02-03
ziel_kcal = 3000
beobachtungen = "Snack am Nachmittag war schwierig."

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800
  anteil_gegessen = 1.0

[[mahlzeit]]
zeit = "10:00"
name = "Snack"

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
  anteil_gegessen = 0.6
"""

OHNE_KCAL = """
datum = 2026-02-03

[[mahlzeit]]
zeit = "12:00"
name = "Mittag"

  [[mahlzeit.gericht]]
  titel = "Unbekanntes Gericht"
  quelle = "frei"
"""


def schreibe(inhalt: str) -> Path:
    basis = Path(tempfile.mkdtemp()) / "FBT Daten"
    (basis / "tage").mkdir(parents=True)
    (basis / "tage" / "2026-02-03.toml").write_text(inhalt, encoding="utf-8")
    return basis


class BilanzTest(unittest.TestCase):
    def test_rechnet_geplant_und_tatsaechlich_getrennt(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(b.kcal_geplant, 1300)
        self.assertEqual(b.kcal_tatsaechlich, 800 + 300)

    def test_beobachtungen_landen_nicht_in_der_letzten_mahlzeit(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(len(b.mahlzeiten), 2)
        self.assertEqual(b.mahlzeiten[-1].name, "Snack")

    def test_fehlende_kcal_sind_unbekannt_nicht_null(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIn("Unbekanntes Gericht", " ".join(b.unbekannte))
        self.assertEqual(b.kcal_geplant, 0)

    def test_fehlendes_ziel_ist_none(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIsNone(b.ziel_kcal)


class AnsichtTest(unittest.TestCase):
    def setUp(self):
        self.b = lade_tag(date(2026, 2, 3), schreibe(TAG))

    def test_elternansicht_zeigt_zahlen(self):
        text = elternansicht(self.b)
        self.assertIn("3000", text)
        self.assertIn("1100", text)

    def test_tischansicht_enthaelt_keine_einzige_zahl_aus_dem_kalorienbereich(self):
        text = tischansicht(self.b)
        for verboten in ("3000", "1300", "1100", "800", "500", "kcal", "Kalorien"):
            self.assertNotIn(verboten, text, f"'{verboten}' darf am Tisch nicht auftauchen")

    def test_tischansicht_zeigt_trotzdem_was_es_gibt(self):
        text = tischansicht(self.b)
        self.assertIn("Porridge", text)
        self.assertIn("07:30", text)


if __name__ == "__main__":
    unittest.main()
