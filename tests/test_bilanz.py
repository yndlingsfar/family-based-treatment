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

BEOBACHTUNGEN_VERIRRT = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800
  anteil_gegessen = 1.0

beobachtungen = "Diese Notiz gehoert zur Mahlzeit, nicht zum Tag!"
"""

OHNE_ANTEIL = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
  anteil_gegessen = 0.6
"""

NUR_UNBEKANNTE = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "12:00"
name = "Mittag"

  [[mahlzeit.gericht]]
  titel = "Unbekanntes Gericht"
  quelle = "frei"
"""

NUR_ANGENOMMEN = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
  anteil_gegessen = 1.0
"""

BEIDE_UNBEKANNT = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "12:00"
name = "Mittag"

  [[mahlzeit.gericht]]
  titel = "Gekochtes"
  quelle = "frei"

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
"""

ZWEI_UNBEKANNTE = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "12:00"
name = "Mittag"

  [[mahlzeit.gericht]]
  titel = "Gekochtes"
  quelle = "frei"

  [[mahlzeit.gericht]]
  titel = "Eintopf"
  quelle = "frei"
"""

ZWEI_ANGENOMMEN = """
datum = 2026-02-03
ziel_kcal = 3000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
  kcal_geplant = 800

  [[mahlzeit.gericht]]
  titel = "Shake"
  quelle = "kochbuch:shake"
  kcal_geplant = 500
"""


KOPF = """
datum = 2026-02-03
ziel_kcal = 2000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gericht]]
  titel = "Porridge"
  quelle = "kochbuch:porridge"
"""


def mit_gericht(*zeilen: str) -> str:
    """KOPF mit zusaetzlichen Zeilen im ersten Gericht."""
    return KOPF + "".join(f"  {z}\n" for z in zeilen)


OHNE_MAHLZEIT = """
datum = 2026-02-03
ziel_kcal = 2000
beobachtungen = "Ein ganz normaler Tag."
"""

MAHLZEIT_PLURAL = """
datum = 2026-02-03
ziel_kcal = 2000

[[mahlzeiten]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeiten.gericht]]
  titel = "Porridge"
  kcal_geplant = 800
  anteil_gegessen = 1.0
"""

GERICHTE_PLURAL = """
datum = 2026-02-03
ziel_kcal = 2000

[[mahlzeit]]
zeit = "07:30"
name = "Fruehstueck"

  [[mahlzeit.gerichte]]
  titel = "Porridge"
  kcal_geplant = 800
"""

KCAL_IM_TITEL = """
datum = 2026-02-03
ziel_kcal = 2000

[[mahlzeit]]
zeit = "18:00"
name = "Abendessen"

  [[mahlzeit.gericht]]
  titel = "Kaesepolenta (1250 kcal)"
  quelle = "kochbuch:kaesepolenta-mit-joghurt"
  kcal_geplant = 1250
  anteil_gegessen = 1.0
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

    def test_beobachtungen_in_der_richtigen_ebene(self):
        """beobachtungen auf oberster Ebene wird korrekt geladen."""
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(b.beobachtungen, "Snack am Nachmittag war schwierig.")

    def test_beobachtungen_unter_mahlzeit_werden_abgelehnt(self):
        """beobachtungen unterhalb [[mahlzeit]] wird als Fehler erkannt."""
        from fbt.daten import DatenFehler
        with self.assertRaises(DatenFehler) as ctx:
            lade_tag(date(2026, 2, 3), schreibe(BEOBACHTUNGEN_VERIRRT))
        self.assertIn("beobachtungen", str(ctx.exception))
        self.assertIn("obersten Ebene", str(ctx.exception))

    def test_fehlende_kcal_sind_unbekannt_nicht_null(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIn("Unbekanntes Gericht", " ".join(b.unbekannte))
        self.assertEqual(b.kcal_geplant, 0)

    def test_fehlendes_ziel_ist_none(self):
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_KCAL))
        self.assertIsNone(b.ziel_kcal)

    def test_anteil_ohne_angabe_wird_angenommen(self):
        """Ein Gericht mit kcal_geplant aber ohne anteil_gegessen wird in angenommen gelistet."""
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_ANTEIL))
        self.assertIn("Fruehstueck: Porridge", " ".join(b.angenommen))
        self.assertNotIn("Shake", " ".join(b.angenommen))

    def test_tag_ist_unvollstaendig_wenn_anteil_angenommen(self):
        """vollstaendig ist False wenn es angenommene Anteile gibt."""
        b = lade_tag(date(2026, 2, 3), schreibe(OHNE_ANTEIL))
        self.assertFalse(b.vollstaendig)

    def test_tag_ist_vollstaendig_wenn_alle_angegeben(self):
        """vollstaendig ist True wenn kein anteil angenommen wurde."""
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertTrue(b.vollstaendig)


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

    def test_vollstaendig_false_wenn_nur_unbekannte(self):
        """Fall 1: nur unbekannte — vollstaendig ist False."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_UNBEKANNTE))
        self.assertFalse(b.vollstaendig)
        text = elternansicht(b)
        self.assertIn("unvollstaendig", text)
        self.assertIn("Kalorienangabe", text)
        # Marker sollte nicht "Anteil" erwaehnen wenn nur kcal fehlt
        lines = text.split("\n")
        marker_lines = [l for l in lines if "unvollstaendig" in l]
        self.assertTrue(any("Kalorienangabe" in l for l in marker_lines))

    def test_vollstaendig_false_wenn_nur_angenommen(self):
        """Fall 2: nur angenommen — vollstaendig ist False."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_ANGENOMMEN))
        self.assertFalse(b.vollstaendig)
        text = elternansicht(b)
        self.assertIn("unvollstaendig", text)
        self.assertIn("Anteil", text)
        # Marker sollte nicht "Kalorienangabe" erwaehnen wenn nur Anteil fehlt
        lines = text.split("\n")
        marker_lines = [l for l in lines if "unvollstaendig" in l]
        self.assertFalse(any("Kalorienangabe" in l for l in marker_lines if "Anteil" not in l))

    def test_vollstaendig_false_wenn_beide(self):
        """Fall 3: beide unbekannte und angenommen — vollstaendig ist False."""
        b = lade_tag(date(2026, 2, 3), schreibe(BEIDE_UNBEKANNT))
        self.assertFalse(b.vollstaendig)
        text = elternansicht(b)
        self.assertIn("unvollstaendig", text)
        self.assertIn("Kalorienangabe", text)
        self.assertIn("Anteil", text)

    def test_vollstaendig_true_wenn_leer(self):
        """Fall 4: keine unbekannte, keine angenommen — vollstaendig ist True."""
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertTrue(b.vollstaendig)
        text = elternansicht(b)
        # Keine unvollstaendig-Marker auf den Totalen
        lines = text.split("\n")
        geplant_line = [l for l in lines if l.startswith("geplant:")][0]
        tatsaechlich_line = [l for l in lines if l.startswith("tatsaechlich:")][0]
        self.assertNotIn("unvollstaendig", geplant_line)
        self.assertNotIn("unvollstaendig", tatsaechlich_line)

    def test_anteil_1_0_landet_nicht_in_angenommen(self):
        """Explicit anteil_gegessen = 1.0 wird nicht als angenommen gezaehlt."""
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(len(b.angenommen), 0)
        text = elternansicht(b)
        self.assertNotIn("Ohne Angabe, als vollstaendig gerechnet", text)

    def test_singular_plural_unbekannte_eins(self):
        """Genau 1 unbekannte → 'Gericht' (singular)."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_UNBEKANNTE))
        text = elternansicht(b)
        self.assertIn("1 Gericht ohne Kalorienangabe", text)
        self.assertNotIn("1 Gerichte", text)

    def test_singular_plural_unbekannte_zwei(self):
        """Genau 2 unbekannte → 'Gerichte' (plural)."""
        b = lade_tag(date(2026, 2, 3), schreibe(ZWEI_UNBEKANNTE))
        text = elternansicht(b)
        self.assertIn("2 Gerichte ohne Kalorienangabe", text)

    def test_singular_plural_angenommen_eins(self):
        """Genau 1 angenommen → 'Gericht' (singular)."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_ANGENOMMEN))
        text = elternansicht(b)
        self.assertIn("1 Gericht ohne Anteil", text)
        self.assertNotIn("1 Gerichte", text)

    def test_singular_plural_angenommen_zwei(self):
        """Genau 2 angenommen → 'Gerichte' (plural)."""
        b = lade_tag(date(2026, 2, 3), schreibe(ZWEI_ANGENOMMEN))
        text = elternansicht(b)
        self.assertIn("2 Gerichte ohne Anteil", text)

    def test_marker_auf_beiden_total_zeilen(self):
        """Marker muss auf BEIDEN Zeilen erscheinen (geplant und tatsaechlich)."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_UNBEKANNTE))
        text = elternansicht(b)
        lines = text.split("\n")
        geplant_line = [l for l in lines if l.startswith("geplant:")][0]
        tatsaechlich_line = [l for l in lines if l.startswith("tatsaechlich:")][0]
        self.assertIn("unvollstaendig", geplant_line, "Marker fehlt auf geplant-Zeile")
        self.assertIn("unvollstaendig", tatsaechlich_line, "Marker fehlt auf tatsaechlich-Zeile")

    def test_ohne_angabe_sektion_rendern(self):
        """'Ohne Angabe, als vollstaendig gerechnet:' Sektion mit Gerichten rendern."""
        b = lade_tag(date(2026, 2, 3), schreibe(NUR_ANGENOMMEN))
        text = elternansicht(b)
        self.assertIn("Ohne Angabe, als vollstaendig gerechnet:", text)
        self.assertIn("Fruehstueck: Porridge", text)


class PruefungTest(unittest.TestCase):
    """Die Tagesdatei wird von Hand getippt — jeder Tippfehler muss auffallen.

    Alle Faelle hier sind am Zweig reproduziert worden und ergaben vorher
    entweder eine falsche Zahl im Arztbericht oder einen rohen Traceback.
    """

    def laden(self, inhalt: str):
        from fbt.daten import DatenFehler
        with self.assertRaises(DatenFehler) as ctx:
            lade_tag(date(2026, 2, 3), schreibe(inhalt))
        meldung = str(ctx.exception)
        self.assertIn("2026-02-03.toml", meldung,
                      "Jede Meldung muss die Datei nennen, damit die Eltern sie finden.")
        return meldung

    def test_ziel_kcal_true_wird_nicht_zu_eins(self):
        # bool ist eine int-Unterklasse: true waere sonst ein Ziel von 1 kcal.
        meldung = self.laden(KOPF.replace("ziel_kcal = 2000",
                                          "ziel_kcal = true"))
        self.assertIn("ziel_kcal", meldung)
        self.assertIn("true/false", meldung)

    def test_kcal_geplant_true_wird_nicht_zu_eins(self):
        meldung = self.laden(mit_gericht("kcal_geplant = true"))
        self.assertIn("kcal_geplant", meldung)
        self.assertIn("Porridge", meldung)

    def test_ziel_kcal_als_text_ist_ein_fehler_keine_ausnahme(self):
        meldung = self.laden(KOPF.replace("ziel_kcal = 2000",
                                          'ziel_kcal = "2000"'))
        self.assertIn("ziel_kcal", meldung)

    def test_kcal_geplant_als_text_ist_ein_fehler_keine_ausnahme(self):
        meldung = self.laden(mit_gericht('kcal_geplant = "ca. 800"'))
        self.assertIn("kcal_geplant", meldung)
        self.assertIn("str", meldung)

    def test_anteil_ueber_eins_erfindet_keine_kalorien(self):
        meldung = self.laden(mit_gericht("kcal_geplant = 800",
                                         "anteil_gegessen = 1.5"))
        self.assertIn("anteil_gegessen", meldung)
        self.assertIn("Porridge", meldung)

    def test_negativer_anteil_kuerzt_nicht_andere_mahlzeiten_weg(self):
        meldung = self.laden(mit_gericht("kcal_geplant = 800",
                                         "anteil_gegessen = -0.5"))
        self.assertIn("anteil_gegessen", meldung)

    def test_datum_als_text_ist_ein_fehler_keine_ausnahme(self):
        meldung = self.laden(KOPF.replace("datum = 2026-02-03",
                                          'datum = "2026-02-03"'))
        self.assertIn("datum", meldung)

    def test_fehlende_mahlzeiten_sind_nicht_null_kalorien(self):
        meldung = self.laden(OHNE_MAHLZEIT)
        self.assertIn("mahlzeit", meldung)

    def test_mahlzeiten_im_plural_wird_als_tippfehler_erkannt(self):
        meldung = self.laden(MAHLZEIT_PLURAL)
        self.assertIn("mahlzeiten", meldung)

    def test_gerichte_im_plural_wird_als_tippfehler_erkannt(self):
        meldung = self.laden(GERICHTE_PLURAL)
        self.assertIn("gerichte", meldung)

    def test_gueltige_datei_bleibt_gueltig(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertEqual(b.kcal_tatsaechlich, 1100)


class TischansichtSchutzTest(unittest.TestCase):
    def test_kalorienangabe_im_titel_bricht_ab(self):
        from fbt.daten import DatenFehler
        b = lade_tag(date(2026, 2, 3), schreibe(KCAL_IM_TITEL))
        with self.assertRaises(DatenFehler) as ctx:
            tischansicht(b)
        self.assertIn("Kaesepolenta", str(ctx.exception))

    def test_titel_ohne_zahl_geht_durch(self):
        b = lade_tag(date(2026, 2, 3), schreibe(TAG))
        self.assertIn("Porridge", tischansicht(b))


if __name__ == "__main__":
    unittest.main()
