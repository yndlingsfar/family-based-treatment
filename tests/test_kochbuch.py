"""Tests fuer Schema und Plausibilitaetspruefung des Kochbuchs."""

import json
import tempfile
import unittest
from pathlib import Path

from fbt.anreicherung import lade_grundzutaten, lade_mittel
from fbt.kochbuch import lade_kochbuch, plausibilitaet, pruefe_rezept

TABELLE = Path(__file__).resolve().parent.parent / "referenz" / "anreicherung.json"
GRUNDZUTATEN = Path(__file__).resolve().parent.parent / "referenz" / "grundzutaten.json"

GUELTIG = {
    "titel": "Testshake",
    "kategorie": "getraenke",
    "portionen": 1,
    "kcal_pro_portion": 500,
    "zutaten": [
        {"menge": 100, "einheit": "g", "was": "Sahne", "mittel": "sahne-30"},
        {"menge": 50, "einheit": "g", "was": "Mascarpone", "mittel": "mascarpone"},
    ],
    "zubereitung": "Alles verruehren.",
    "zeit_min": 5,
    "geraete": [],
    "allergene": ["milch"],
    "quelle": "Netzwerk-Kochbuch S. 9",
}


class SchemaTest(unittest.TestCase):
    def test_gueltiges_rezept_hat_keine_fehler(self):
        self.assertEqual(pruefe_rezept(GUELTIG), [])

    def test_meldet_fehlendes_pflichtfeld(self):
        ohne = {k: v for k, v in GUELTIG.items() if k != "kcal_pro_portion"}
        self.assertIn("kcal_pro_portion", " ".join(pruefe_rezept(ohne)))

    def test_meldet_null_portionen(self):
        self.assertTrue(pruefe_rezept({**GUELTIG, "portionen": 0}))

    def test_meldet_unbekannte_einheit(self):
        kaputt = {**GUELTIG, "zutaten": [{"menge": 2, "einheit": "EL", "was": "Oel"}]}
        self.assertIn("EL", " ".join(pruefe_rezept(kaputt)))

    def test_meldet_unbekannte_kategorie(self):
        self.assertTrue(pruefe_rezept({**GUELTIG, "kategorie": "quatsch"}))

    def test_meldet_bool_fuer_portionen(self):
        self.assertIn("portionen", " ".join(pruefe_rezept({**GUELTIG, "portionen": True})))

    def test_meldet_bool_fuer_kcal_pro_portion(self):
        self.assertIn("kcal_pro_portion", " ".join(pruefe_rezept({**GUELTIG, "kcal_pro_portion": True})))

    def test_meldet_bool_fuer_zutat_menge(self):
        kaputt = {**GUELTIG, "zutaten": [{"menge": True, "einheit": "g", "was": "Test"}]}
        self.assertIn("menge", " ".join(pruefe_rezept(kaputt)))

    def test_meldet_string_fuer_zeit_min(self):
        self.assertIn("zeit_min", " ".join(pruefe_rezept({**GUELTIG, "zeit_min": "5 Min"})))

    def test_meldet_negative_zeit_min(self):
        self.assertIn("zeit_min", " ".join(pruefe_rezept({**GUELTIG, "zeit_min": -1})))

    def test_akzeptiert_zeit_min_null(self):
        self.assertEqual(pruefe_rezept({**GUELTIG, "zeit_min": 0}), [])

    def test_meldet_zahl_fuer_titel(self):
        self.assertIn("titel", " ".join(pruefe_rezept({**GUELTIG, "titel": 123})))

    def test_meldet_leerer_quelle(self):
        self.assertIn("quelle", " ".join(pruefe_rezept({**GUELTIG, "quelle": ""})))


class PlausibilitaetTest(unittest.TestCase):
    def setUp(self):
        self.mittel = lade_mittel(TABELLE)

    def test_stimmige_angabe_ergibt_keine_notiz(self):
        # 100 g Sahne (292) + 50 g Mascarpone (190) = 482, angegeben 500 -> 3,6 %
        self.assertIsNone(plausibilitaet(GUELTIG, self.mittel))

    def test_abweichung_ueber_zehn_prozent_wird_gemeldet(self):
        # Dieselben Zutaten, aber 900 kcal behauptet -> 87 % daneben.
        notiz = plausibilitaet({**GUELTIG, "kcal_pro_portion": 900}, self.mittel)
        self.assertIsNotNone(notiz)
        self.assertIn("900", notiz)

    def test_ohne_zuordenbare_zutaten_keine_falsche_sicherheit(self):
        # Sind die Zutaten nicht der Tabelle zuzuordnen, darf die Pruefung nicht
        # so tun, als haette sie geprueft.
        ohne = {**GUELTIG, "zutaten": [{"menge": 200, "einheit": "g", "was": "Kartoffeln"}]}
        notiz = plausibilitaet(ohne, self.mittel)
        self.assertIsNotNone(notiz)
        self.assertIn("nicht pruefbar", notiz)

    def test_grundzutaten_machen_ein_reines_staple_rezept_pruefbar(self):
        # Ein Rezept nur aus Grundzutaten (Kartoffeln, Zwiebel) ist ueber die
        # Anreicherungstabelle allein "nicht pruefbar", wird aber zu einem
        # echten Befund, sobald die Grundzutaten-Tabelle mit herangezogen wird.
        grund = lade_grundzutaten(GRUNDZUTATEN)
        nur_staples = {
            **GUELTIG,
            "kcal_pro_portion": 100,
            "zutaten": [
                {"menge": 200, "einheit": "g", "was": "Kartoffeln", "mittel": "kartoffeln"},
                {"menge": 100, "einheit": "g", "was": "Zwiebel", "mittel": "zwiebel"},
            ],
        }
        notiz = plausibilitaet(nur_staples, self.mittel, grund)
        self.assertIsNotNone(notiz)
        self.assertNotIn("nicht pruefbar", notiz)

    def test_grundzutaten_aendern_nichts_wenn_nichts_zuordenbar_ist(self):
        # Stehen Zutaten in keiner der beiden Tabellen, bleibt es "nicht
        # pruefbar" -- die zweite Tabelle erweitert die Abdeckung, erfindet
        # aber keine.
        grund = lade_grundzutaten(GRUNDZUTATEN)
        ohne = {**GUELTIG, "zutaten": [{"menge": 200, "einheit": "g", "was": "Einhornstaub"}]}
        notiz = plausibilitaet(ohne, self.mittel, grund)
        self.assertIsNotNone(notiz)
        self.assertIn("nicht pruefbar", notiz)

    def test_plausibilitaet_ohne_drittes_argument_bleibt_rueckwaertskompatibel(self):
        # Bestehende Aufrufe mit nur (roh, mittel) muessen unveraendert
        # funktionieren.
        self.assertIsNone(plausibilitaet(GUELTIG, self.mittel))
        notiz = plausibilitaet({**GUELTIG, "kcal_pro_portion": 900}, self.mittel)
        self.assertIsNotNone(notiz)


class LadenTest(unittest.TestCase):
    def test_laedt_und_meldet_kaputte_eintraege_mit_id(self):
        basis = Path(tempfile.mkdtemp())
        datei = basis / "kochbuch.json"
        datei.write_text(
            json.dumps({"testshake": GUELTIG, "kaputt": {"titel": "X"}}),
            encoding="utf-8",
        )
        with self.assertRaises(Exception) as fall:
            lade_kochbuch(datei)
        self.assertIn("kaputt", str(fall.exception))

    def test_portionen_geschaetzt_wird_geladen(self):
        basis = Path(tempfile.mkdtemp())
        datei = basis / "kochbuch.json"
        datei.write_text(
            json.dumps({"testshake": {**GUELTIG, "portionen_geschaetzt": True}}),
            encoding="utf-8",
        )
        rezepte = lade_kochbuch(datei)
        self.assertTrue(rezepte["testshake"].portionen_geschaetzt is True)

    def test_portionen_geschaetzt_ist_ohne_angabe_false(self):
        basis = Path(tempfile.mkdtemp())
        datei = basis / "kochbuch.json"
        datei.write_text(json.dumps({"testshake": GUELTIG}), encoding="utf-8")
        rezepte = lade_kochbuch(datei)
        self.assertTrue(rezepte["testshake"].portionen_geschaetzt is False)


if __name__ == "__main__":
    unittest.main()
