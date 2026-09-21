"""Tests für das Auffinden des Datenverzeichnisses und das Laden des Profils."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fbt.daten import STANDARD_DATEN, DatenFehler, daten_pfad, lade_profil

VOLLSTAENDIG = """
[kind]
rufname = "Testkind"
geburtsdatum = 2010-01-15
groesse_cm = 150

[ziele]
kcal_taeglich = 2800
kcal_quelle = "Kinderaerztin, Stand 2026-01-02"
zunahme_g_pro_woche = 500

[behandlung]
wiegen = "blind, 1-2x pro Woche"

[mahlzeiten]
plan = ["fruehstueck", "mittagessen", "abendessen"]

[praeferenzen]
unvertraeglichkeiten = ["Nuesse"]
fearfoods = ["Butter"]
"""

OHNE_KCAL = """
[kind]
rufname = "Testkind"
geburtsdatum = 2010-01-15
groesse_cm = 150

[ziele]
zunahme_g_pro_woche = 500

[mahlzeiten]
plan = ["fruehstueck"]
"""


def schreibe(inhalt: str) -> Path:
    """Legt ein Profil in einem temporären Verzeichnis mit Leerzeichen im Namen an."""
    basis = Path(tempfile.mkdtemp()) / "FBT Daten mit Leerzeichen"
    basis.mkdir()
    (basis / "profil.toml").write_text(inhalt, encoding="utf-8")
    return basis


class DatenPfadTest(unittest.TestCase):
    def test_nimmt_umgebungsvariable_wenn_gesetzt(self):
        self.assertEqual(
            daten_pfad({"FBT_DATEN": "/tmp/anderswo"}), Path("/tmp/anderswo")
        )

    def test_loest_tilde_auf(self):
        self.assertEqual(daten_pfad({"FBT_DATEN": "~/x"}), Path.home() / "x")

    def test_faellt_auf_standard_zurueck_wenn_leer(self):
        self.assertEqual(daten_pfad({"FBT_DATEN": "   "}), STANDARD_DATEN)

    def test_faellt_auf_standard_zurueck_wenn_nicht_gesetzt(self):
        self.assertEqual(daten_pfad({}), STANDARD_DATEN)


class ProfilTest(unittest.TestCase):
    def test_liest_ein_vollstaendiges_profil(self):
        profil = lade_profil(schreibe(VOLLSTAENDIG))
        self.assertEqual(profil.rufname, "Testkind")
        self.assertEqual(profil.geburtsdatum, date(2010, 1, 15))
        self.assertEqual(profil.groesse_cm, 150)
        self.assertEqual(profil.kcal_taeglich, 2800)
        self.assertTrue(profil.kcal_bekannt)
        self.assertEqual(profil.mahlzeiten, ("fruehstueck", "mittagessen", "abendessen"))
        self.assertEqual(profil.unvertraeglichkeiten, ("Nuesse",))
        self.assertEqual(profil.wiegen, "blind, 1-2x pro Woche")

    def test_fehlende_tageskcal_sind_none_nicht_null(self):
        profil = lade_profil(schreibe(OHNE_KCAL))
        self.assertIsNone(profil.kcal_taeglich)
        self.assertFalse(profil.kcal_bekannt)

    def test_meldet_fehlendes_profil_mit_pfad(self):
        leer = Path(tempfile.mkdtemp())
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(leer)
        self.assertIn(str(leer / "profil.toml"), str(fall.exception))

    def test_meldet_fehlende_pflichtangabe(self):
        # Die uebrigen Abschnitte sind absichtlich vollstaendig: sonst schlaegt
        # die Pruefung auf [mahlzeiten] zuerst an und das Fehlen von
        # geburtsdatum kaeme nie zur Sprache.
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(
                schreibe(
                    '[kind]\nrufname = "Testkind"\n\n[ziele]\n'
                    'zunahme_g_pro_woche = 500\n\n[mahlzeiten]\n'
                    'plan = ["fruehstueck"]\n'
                )
            )
        self.assertIn("geburtsdatum", str(fall.exception))

    def test_lehnt_wahrheitswert_als_zahl_ab(self):
        # bool ist in Python eine int-Unterklasse: isinstance(True, int) ist True.
        # Ohne eigene Pruefung wuerde groesse_cm = true stillschweigend zu 1.
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(
                schreibe(
                    '[kind]\nrufname = "T"\ngeburtsdatum = 2010-01-15\n'
                    "groesse_cm = true\n\n[ziele]\nzunahme_g_pro_woche = 500\n"
                    '\n[mahlzeiten]\nplan = ["fruehstueck"]\n'
                )
            )
        self.assertIn("groesse_cm", str(fall.exception))

    def test_meldet_kaputtes_toml_mit_pfad(self):
        basis = schreibe("[kind\nrufname =")
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(basis)
        self.assertIn("profil.toml", str(fall.exception))

    def test_lehnt_wahrheitswert_als_wiegen_ab(self):
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(
                schreibe(
                    '[kind]\nrufname = "T"\ngeburtsdatum = 2010-01-15\n'
                    'groesse_cm = 150\n\n[ziele]\nzunahme_g_pro_woche = 500\n'
                    '[behandlung]\nwiegen = true\n\n[mahlzeiten]\nplan = ["fruehstueck"]\n'
                )
            )
        self.assertIn("wiegen", str(fall.exception))

    def test_lehnt_zahl_als_kcal_quelle_ab(self):
        with self.assertRaises(DatenFehler) as fall:
            lade_profil(
                schreibe(
                    '[kind]\nrufname = "T"\ngeburtsdatum = 2010-01-15\n'
                    'groesse_cm = 150\n\n[ziele]\nzunahme_g_pro_woche = 500\n'
                    'kcal_quelle = 2026\n\n[mahlzeiten]\nplan = ["fruehstueck"]\n'
                )
            )
        self.assertIn("kcal_quelle", str(fall.exception))

    def test_liest_profil_ohne_optionale_strings(self):
        profil = lade_profil(
            schreibe(
                '[kind]\nrufname = "T"\ngeburtsdatum = 2010-01-15\n'
                'groesse_cm = 150\n\n[ziele]\nzunahme_g_pro_woche = 500\n'
                '[mahlzeiten]\nplan = ["fruehstueck"]\n'
            )
        )
        self.assertIsNone(profil.kcal_quelle)
        self.assertIsNone(profil.wiegen)


if __name__ == "__main__":
    unittest.main()
