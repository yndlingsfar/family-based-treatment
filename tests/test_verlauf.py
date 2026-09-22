"""Verlaufsgrenzen und Abgleich mit veroeffentlichten KiGGS-Werten."""
import csv
import tempfile
import unittest
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from fbt.daten import DatenFehler, Profil, lade_profil
from fbt.verlauf import (SPALTEN, Messung, alter_am, auswerten, bmi_perzentil,
                         bmi_text, lade_gewicht)

TAG = date(2026, 1, 22)
PROFIL = Profil('Testkind', date(2014, 1, 22), 150, 500, ('Fruehstueck',),
                bmi_referenz='maedchen', groesse_gemessen_am=date(2026, 1, 1))


def messung(tage, kg):
    return Messung(TAG - timedelta(days=tage), Decimal(str(kg)), '07:30', 'gleiche Waage', 'Eltern', True)


class CSVTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='FBT Test ')
        self.addCleanup(self.tmp.cleanup)
        self.basis = Path(self.tmp.name)

    def schreibe(self, zeilen, spalten=SPALTEN):
        with (self.basis / 'gewicht.csv').open('w', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(spalten)
            w.writerows(zeilen)

    def test_sortiert_ohne_messumstaende_zu_verlieren(self):
        self.schreibe([['2026-01-22', '40.25', '07:30', 'Waage A, leicht', 'Eltern', 'true'],
                       ['2026-01-01', '39.1', '', '', '', '']])
        m = lade_gewicht(self.basis, heute=TAG)
        self.assertEqual(m[1].gewicht_kg, Decimal('40.25'))
        self.assertEqual(m[1].bedingungen, 'Waage A, leicht')
        self.assertIsNone(m[0].blind)

    def test_leer_ist_keine_nullmessung(self):
        self.schreibe([])
        self.assertEqual(lade_gewicht(self.basis), ())

    def test_fehlerhafte_werte_werden_abgewiesen(self):
        for feld, werte in {'datum': ['20260122', '2026-02-30', '2026-01-23', ''],
                            'gewicht_kg': ['NaN', 'inf', '0', '-1', '40,2', 'true', ''],
                            'uhrzeit': ['24:00', '7:30'], 'blind': ['ja', '1']}.items():
            for wert in werte:
                with self.subTest(feld=feld, wert=wert):
                    r = dict(zip(SPALTEN, ['2026-01-22', '40', '07:30', '', '', 'true']))
                    r[feld] = wert
                    self.schreibe([list(r.values())])
                    with self.assertRaises(DatenFehler):
                        lade_gewicht(self.basis, heute=TAG)

    def test_duplikate_und_falsche_spalten(self):
        row = ['2026-01-22', '40', '', '', '', '']
        for rows, kopf in [([row, row], SPALTEN), ([row[:-1]], SPALTEN),
                           ([row], SPALTEN[:-1] + ('datum',)), ([row + ['extra']], SPALTEN)]:
            with self.subTest(rows=rows, kopf=kopf):
                self.schreibe(rows, kopf)
                with self.assertRaises(DatenFehler):
                    lade_gewicht(self.basis)


class VerlaufTest(unittest.TestCase):
    def test_konfigurierbare_linie_und_unregelmaessiger_abstand(self):
        v = auswerten((messung(10, 40), messung(0, 40.6)), replace(PROFIL, zunahme_g_pro_woche=700), TAG)
        self.assertEqual(v.aenderung_kg, Decimal('0.6'))
        self.assertEqual(v.g_pro_woche, Decimal('420'))
        self.assertEqual(v.vergleich_kg(TAG), Decimal('41'))
        self.assertTrue(any('Messluecke' in x for x in v.luecken))

    def test_abnahme_auch_wenn_gesamttrend_positiv(self):
        v = auswerten((messung(14, 40), messung(7, 41), messung(0, 40.8)), PROFIL, TAG)
        self.assertEqual(v.warnungen[0].code, 'abnahme')
        self.assertEqual(v.warnungen[0].von, TAG-timedelta(days=7))
        self.assertEqual(v.aenderung_kg, Decimal('0.8'))

    def test_plateau_genau_14_tage_nicht_schon_13(self):
        for tage in (13, 14, 15, 30):
            with self.subTest(tage=tage):
                v = auswerten((messung(tage, 40), messung(0, 40)), PROFIL, TAG)
                self.assertEqual(any(w.code == 'keine_zunahme' for w in v.warnungen), tage >= 14)

    def test_naechste_messung_vor_zweiwochengrenze(self):
        v = auswerten((messung(21, 39), messung(15, 40), messung(7, 40), messung(0, 40)), PROFIL, TAG)
        self.assertEqual(v.warnungen[-1].von, TAG-timedelta(days=15))
        self.assertEqual(v.warnungen[-1].code, 'keine_zunahme')

    def test_einzelmessung_und_veraltete_daten_sind_nicht_unauffaellig(self):
        for messungen in ((), (messung(8, 40),)):
            v = auswerten(messungen, PROFIL, TAG)
            self.assertIsNone(v.g_pro_woche)
            self.assertGreaterEqual(len(v.luecken), 2)

    def test_historischer_stichtag_ignoriert_spaetere_werte(self):
        v = auswerten((messung(21, 40), messung(14, 40.5), messung(0, 39)), PROFIL, TAG-timedelta(days=14))
        self.assertFalse(v.warnungen)
        self.assertEqual(len(v.messungen), 2)
        self.assertEqual(v.aenderung_kg, Decimal('0.5'))

    def test_wachstum_mit_woechentlichen_messungen_ohne_luecken(self):
        v = auswerten((messung(14, 40), messung(7, 40.5), messung(0, 41)), PROFIL, TAG)
        self.assertEqual(v.luecken, ())
        self.assertEqual(v.warnungen, ())

    def test_bedingungen_und_doppelte_daten(self):
        m = replace(messung(0, 41), bedingungen='andere Waage')
        v = auswerten((messung(7, 40), m), PROFIL, TAG)
        self.assertTrue(any('Messbedingungen' in x for x in v.luecken))
        with self.assertRaises(DatenFehler):
            auswerten((m, m), PROFIL, TAG)


class BMITest(unittest.TestCase):
    def test_veroeffentlichte_mediane_und_p3(self):
        # RKI 2013 S.40/41: unabhaengige Sollwerte der gedruckten Tabellen.
        for kurve, alter, median, p3 in [('maedchen', 12, 18.77, 14.59),
                                        ('jungen', 12, 18.60, 14.70),
                                        ('maedchen', 18, 21.95, 17.93),
                                        ('jungen', 2, 16.34, 14.15)]:
            with self.subTest(kurve=kurve, alter=alter):
                self.assertAlmostEqual(bmi_perzentil(median, alter, kurve)[0], 50)
                self.assertAlmostEqual(bmi_perzentil(p3, alter, kurve)[0], 3, delta=0.08)

    def test_interpolation_und_grenzen(self):
        self.assertAlmostEqual(bmi_perzentil((18.77+19.17)/2, 12.25, 'maedchen')[0], 50)
        for bmi, alter, kurve in [(0,12,'maedchen'), (float('nan'),12,'maedchen'),
                                  (18,1.99,'maedchen'), (18,18.01,'jungen'), (18,12,'unbekannt')]:
            with self.assertRaises(DatenFehler):
                bmi_perzentil(bmi, alter, kurve)

    def test_geburtstage_einschliesslich_schaltjahr(self):
        self.assertEqual(alter_am(date(2014,1,22), TAG), 12)
        self.assertEqual(alter_am(date(2012,2,29), date(2026,2,28)), 14)
        self.assertLess(alter_am(date(2014,1,22), TAG-timedelta(days=1)), 12)

    def test_bmi_fehlende_oder_unpassende_groesse(self):
        v = auswerten((messung(0,40),), PROFIL, TAG)
        for d in (None, TAG+timedelta(days=1), TAG-timedelta(days=91)):
            self.assertIn('nicht berechnet', bmi_text(v, replace(PROFIL, groesse_gemessen_am=d)))
        self.assertIn('Perzentil nicht berechnet', bmi_text(v, replace(PROFIL, bmi_referenz=None)))
        self.assertIn('ca. P', bmi_text(v, PROFIL))


class ProfilErweiterungTest(unittest.TestCase):
    def test_optionale_felder_und_validierung(self):
        from tests.test_wochenbericht import PROFIL as TOML
        with tempfile.TemporaryDirectory() as tmp:
            basis = Path(tmp)
            pfad = basis / 'profil.toml'
            pfad.write_text(TOML)
            profil = lade_profil(basis)
            self.assertEqual(profil.bmi_referenz, 'maedchen')
            self.assertEqual(profil.groesse_gemessen_am, date(2026, 1, 1))
            for alt, neu in [('"maedchen"', '"geraten"'),
                             ('groesse_cm = 150', 'groesse_cm = 0'),
                             ('zunahme_g_pro_woche = 500', 'zunahme_g_pro_woche = -1'),
                             ('groesse_gemessen_am = 2026-01-01', 'groesse_gemessen_am = "2026-01-01"'),
                             ('groesse_gemessen_am = 2026-01-01', 'groesse_gemessen_am = 2010-01-01')]:
                with self.subTest(neu=neu):
                    pfad.write_text(TOML.replace(alt, neu))
                    with self.assertRaises(DatenFehler):
                        lade_profil(basis)
