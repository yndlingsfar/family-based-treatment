import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from fbt.daten import DatenFehler
from fbt.wochenbericht import (bericht_html, bericht_markdown, diagramm_png,
                               erstelle_bericht, speichere)

TAG = date(2026, 1, 22)
PROFIL = '''[kind]
rufname = "Testkind"
geburtsdatum = 2014-01-22
groesse_cm = 150
bmi_referenz = "maedchen"
groesse_gemessen_am = 2026-01-01
[ziele]
zunahme_g_pro_woche = 500
[mahlzeiten]
plan = ["Fruehstueck", "Mittagessen"]
'''


class BerichtTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='FBT Bericht ')
        self.addCleanup(self.tmp.cleanup)
        self.basis = Path(self.tmp.name)
        (self.basis / 'profil.toml').write_text(PROFIL)
        (self.basis / 'tage').mkdir()

    def tag(self, datum=TAG, anteil='1', kcal='800', zweite=True, extra=''):
        s = f'datum = {datum}\nbeobachtungen = "<script>alert(1)</script> | Notiz"\n'
        s += '[[mahlzeit]]\nname = "Fruehstueck"\n[[mahlzeit.gericht]]\ntitel = "Gericht"\n'
        if kcal is not None:
            s += f'kcal_geplant = {kcal}\n'
        if anteil is not None:
            s += f'anteil_gegessen = {anteil}\n'
        if zweite:
            s += '[[mahlzeit]]\nname = "Mittagessen"\n[[mahlzeit.gericht]]\ntitel = "Gericht"\nkcal_geplant = 1000\nanteil_gegessen = 0.5\n'
        (self.basis / 'tage' / f'{datum}.toml').write_text(s+extra)

    def test_sieben_tage_mit_luecken_und_durchschnitt_richtigem_nenner(self):
        self.tag()
        self.tag(TAG-timedelta(days=1), anteil=None)
        self.tag(TAG-timedelta(days=2), kcal=None)
        self.tag(TAG-timedelta(days=3), zweite=False)
        b = erstelle_bericht(TAG, self.basis)
        self.assertEqual(len(b.tage), 7)
        self.assertEqual(b.tage[0].datum, TAG-timedelta(days=6))
        self.assertEqual(b.mittel_kcal, 1300)
        self.assertEqual(sum(t.vollstaendig for t in b.tage), 1)
        text = bericht_markdown(b)
        self.assertIn('1/7', text)
        self.assertIn('Kein Durchschnitt der ganzen Woche', text)
        self.assertIn('NICHT durchgefuehrt', text)
        self.assertIn('Teilwert/Annahme', text)
        self.assertIn('unbekannt', text)

    def test_leere_woche_hat_keinen_null_durchschnitt(self):
        b = erstelle_bericht(TAG, self.basis)
        self.assertIsNone(b.mittel_kcal)
        self.assertIn('Keine Gewichtsmessung', bericht_markdown(b))

    def test_symptome_vor_gewicht_und_keine_automatische_freitextpruefung(self):
        b = erstelle_bericht(TAG, self.basis, symptome=('erbrechen',))
        s = bericht_markdown(b)
        self.assertLess(s.index('WARNZEICHEN'), s.index('## Gewicht'))
        self.assertIn('ausdruecklich verneint', bericht_markdown(erstelle_bericht(TAG, self.basis, symptome=())))
        with self.assertRaises(DatenFehler):
            erstelle_bericht(TAG, self.basis, symptome=('xyz',))

    def test_korrupte_tagesdatei_nicht_als_fehlend_verschlucken(self):
        for kcal in ('nan', 'inf', '-1', '"800"'):
            self.tag(kcal=kcal)
            with self.subTest(kcal=kcal), self.assertRaises(DatenFehler):
                erstelle_bericht(TAG, self.basis)
        self.tag()
        p = self.basis / 'tage' / f'{TAG}.toml'
        p.write_text(p.read_text().replace(str(TAG), '2026-01-21'))
        with self.assertRaises(DatenFehler):
            erstelle_bericht(TAG, self.basis)

    def test_korrupte_gewichtsdatei_stoppt_bericht(self):
        (self.basis / 'gewicht.csv').write_text('datum,kg\n2026-01-22,40\n')
        with self.assertRaises(DatenFehler):
            erstelle_bericht(TAG, self.basis)

    def test_falsche_tabellenformen_geben_datenfehler(self):
        for text in ('mahlzeit = "Fruehstueck"',
                     '[[mahlzeit]]\nname="Fruehstueck"\ngericht="Brot"'):
            (self.basis / 'tage' / f'{TAG}.toml').write_text(text)
            with self.subTest(text=text), self.assertRaises(DatenFehler):
                erstelle_bericht(TAG, self.basis)

    def test_sicherer_html_export_ohne_externe_assets(self):
        self.tag()
        b = erstelle_bericht(TAG, self.basis, fragen=('<img src=x onerror=alert(1)>',))
        pfade = speichere(b, self.basis)
        self.assertEqual(len(pfade), 2)
        s = pfade[1].read_text()
        self.assertNotIn('<script>', s)
        self.assertNotIn('<img src=x', s)
        self.assertIn('&lt;script&gt;', s)
        self.assertIn('<table>', s)
        self.assertEqual(pfade[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(speichere(b, self.basis), pfade)

    def test_export_folgt_keinem_verzeichnis_symlink(self):
        (self.basis / 'berichte').symlink_to(self.basis.parent, target_is_directory=True)
        with self.assertRaises(DatenFehler):
            speichere(erstelle_bericht(TAG, self.basis), self.basis)

    def test_cli_aus_fremdem_arbeitsordner(self):
        env = dict(os.environ, FBT_DATEN=str(self.basis), PYTHONPATH=str(Path(__file__).resolve().parent.parent))
        r = subprocess.run([sys.executable, '-m', 'fbt.wochenbericht', '--bis', str(TAG), '--speichern'],
                           cwd=self.basis, env=env, text=True, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.basis/'berichte'/f'wochenbericht-{TAG}.html').exists())
        (self.basis/'gewicht.csv').write_text('ungueltig')
        r = subprocess.run([sys.executable, '-m', 'fbt.wochenbericht', '--bis', str(TAG)],
                           cwd=self.basis, env=env, text=True, capture_output=True)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn('Traceback', r.stderr)

    @unittest.skipUnless(importlib.util.find_spec('matplotlib'), 'Optionale Diagramm-Abhaengigkeit fehlt')
    def test_diagramm_eingebettet_und_exportiert(self):
        (self.basis/'gewicht.csv').write_text('datum,gewicht_kg,uhrzeit,bedingungen,gewogen_von,blind\n'
                                            '2026-01-01,40,07:30,gleiche Waage,Eltern,true\n'
                                            '2026-01-22,41,07:30,gleiche Waage,Eltern,true\n')
        b = erstelle_bericht(TAG, self.basis)
        png = diagramm_png(b)
        self.assertTrue(png.startswith(b'\x89PNG'))
        self.assertIn('data:image/png;base64,', bericht_html(bericht_markdown(b), png))
        self.assertEqual(len(speichere(b, self.basis, diagramm=True)), 3)
