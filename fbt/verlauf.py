"""Gewichtsdaten, datierte Verlaufswarnungen und BMI-Referenzwerte.

Die Regeln sind in docs/stufe-2.md festgelegt. Keine Diagnose, keine Ableitung
medizinischer Ziele aus Referenzperzentilen. Rechnen funktioniert offline.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist

from fbt.daten import DatenFehler, Profil, daten_pfad, lade_profil

SPALTEN = ('datum', 'gewicht_kg', 'uhrzeit', 'bedingungen', 'gewogen_von', 'blind')
REFERENZ = Path(__file__).resolve().parent.parent / 'referenz' / 'kiggs_bmi_lms.json'


@dataclass(frozen=True)
class Messung:
    datum: date
    gewicht_kg: Decimal
    uhrzeit: str = ''
    bedingungen: str = ''
    gewogen_von: str = ''
    blind: bool | None = None


@dataclass(frozen=True)
class Warnung:
    code: str
    von: date
    bis: date
    text: str


@dataclass(frozen=True)
class Verlauf:
    stichtag: date
    messungen: tuple[Messung, ...]
    warnungen: tuple[Warnung, ...]
    luecken: tuple[str, ...]
    vergleich_g_pro_woche: int

    @property
    def aenderung_kg(self) -> Decimal | None:
        if len(self.messungen) < 2:
            return None
        return self.messungen[-1].gewicht_kg - self.messungen[0].gewicht_kg

    @property
    def g_pro_woche(self) -> Decimal | None:
        if self.aenderung_kg is None:
            return None
        tage = (self.messungen[-1].datum - self.messungen[0].datum).days
        return self.aenderung_kg * 1000 * 7 / tage

    def vergleich_kg(self, datum: date) -> Decimal:
        start = self.messungen[0]
        return start.gewicht_kg + Decimal(self.vergleich_g_pro_woche) * (datum - start.datum).days / 7000


def lade_gewicht(basis: Path | None = None, *, heute: date | None = None) -> tuple[Messung, ...]:
    """Eine Messung pro Tag; Duplikate werden nicht gemittelt oder verworfen."""
    datei = (daten_pfad() if basis is None else basis) / 'gewicht.csv'
    heute = heute or date.today()
    try:
        with datei.open(encoding='utf-8-sig', newline='') as fh:
            reader = csv.DictReader(fh, strict=True)
            if reader.fieldnames is None or len(reader.fieldnames) != len(SPALTEN) or set(reader.fieldnames) != set(SPALTEN):
                raise DatenFehler(f'{datei}: erwartet CSV-Kopf {",".join(SPALTEN)}.')
            messungen = []
            tage = set()
            for r in reader:
                wo = f'{datei}, Zeile {reader.line_num}'
                if None in r or any(v is None for v in r.values()):
                    raise DatenFehler(f'{wo}: falsche Spaltenzahl; Kommas in Texten in Anfuehrungszeichen setzen.')
                r = {k: v.strip() for k, v in r.items()}
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['datum']):
                        raise ValueError()
                    tag = date.fromisoformat(r['datum'])
                    if not re.fullmatch(r'\d+(?:\.\d+)?', r['gewicht_kg']):
                        raise ValueError()
                    kg = Decimal(r['gewicht_kg'])
                    if not kg.is_finite() or kg <= 0:
                        raise ValueError()
                except (ValueError, InvalidOperation) as exc:
                    raise DatenFehler(f'{wo}: Datum JJJJ-MM-TT und positives Gewicht mit Dezimalpunkt erforderlich.') from exc
                if tag > heute:
                    raise DatenFehler(f'{wo}: Messdatum liegt in der Zukunft.')
                if tag in tage:
                    raise DatenFehler(f'{wo}: mehrere Messungen am {tag}; einen bestaetigten Tageswert festlegen.')
                if r['uhrzeit'] and not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', r['uhrzeit']):
                    raise DatenFehler(f'{wo}: uhrzeit muss HH:MM oder leer sein.')
                if r['blind'] not in ('true', 'false', ''):
                    raise DatenFehler(f'{wo}: blind muss true, false oder leer sein.')
                tage.add(tag)
                messungen.append(Messung(tag, kg, r['uhrzeit'], r['bedingungen'],
                                         r['gewogen_von'], {'true': True, 'false': False, '': None}[r['blind']]))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DatenFehler(f'{datei}: Gewichtsdaten nicht lesbar: {exc}') from exc
    return tuple(sorted(messungen, key=lambda m: m.datum))


def auswerten(messungen: tuple[Messung, ...], profil: Profil, stichtag: date) -> Verlauf:
    """Prueft alle Messintervalle bis zum Stichtag; keine Zukunftsdaten im Rueckblick."""
    if type(stichtag) is not date or stichtag > date.today():
        raise DatenFehler('Stichtag muss ein Datum sein und darf nicht in der Zukunft liegen.')
    m = tuple(sorted((x for x in messungen if x.datum <= stichtag), key=lambda x: x.datum))
    if len({x.datum for x in m}) != len(m):
        raise DatenFehler('Mehrere Messungen am selben Tag sind nicht auswertbar.')
    if any(x.datum < profil.geburtsdatum or not x.gewicht_kg.is_finite() or x.gewicht_kg <= 0 for x in m):
        raise DatenFehler('Messung vor der Geburt oder ungueltiges Gewicht.')
    if profil.zunahme_g_pro_woche <= 0:
        raise DatenFehler('Vergleichswert im Profil muss positiv sein.')
    warnungen, luecken = [], []
    if not m:
        luecken.append('Keine Gewichtsmessung bis zum Stichtag; Verlauf nicht pruefbar.')
    elif (stichtag - m[-1].datum).days > 7:
        luecken.append(f'Letzte Messung vom {m[-1].datum} ist aelter als 7 Tage; aktueller Verlauf nicht beurteilbar.')
    if len(m) < 2:
        luecken.append('Weniger als zwei Messungen; Gewichtsabnahme nicht pruefbar.')
    for a, b in zip(m, m[1:]):
        if b.gewicht_kg < a.gewicht_kg:
            warnungen.append(Warnung('abnahme', a.datum, b.datum,
                f'Gewichtsabnahme {a.datum} bis {b.datum}: {b.gewicht_kg - a.gewicht_kg:+.2f} kg.'))
        if (b.datum - a.datum).days > 7:
            luecken.append(f'Messluecke {a.datum} bis {b.datum}: mehr als 7 Tage; Zwischenverlauf unbekannt.')
        if (a.uhrzeit, a.bedingungen) != (b.uhrzeit, b.bedingungen):
            luecken.append(f'Messbedingungen/Uhrzeit unterscheiden sich am {a.datum} und {b.datum}.')
    if any(not x.uhrzeit or not x.bedingungen or not x.gewogen_von or x.blind is None for x in m):
        luecken.append('Messumstaende teilweise nicht dokumentiert (Uhrzeit, Bedingungen, gewogen_von oder blind).')
    letzter_vergleich = False
    for i, ende in enumerate(m):
        kandidaten = [x for x in m[:i] if (ende.datum - x.datum).days >= 14]
        if not kandidaten:
            continue
        start = kandidaten[-1]  # naechster tatsaechlicher Wert mindestens 14 Tage zuvor
        if i == len(m) - 1 and (ende.datum - start.datum).days <= 21:
            letzter_vergleich = True
        if ende.gewicht_kg <= start.gewicht_kg:
            warnungen.append(Warnung('keine_zunahme', start.datum, ende.datum,
                f'Keine Netto-Zunahme ueber {(ende.datum - start.datum).days} Tage '
                f'({start.datum} bis {ende.datum}, {ende.gewicht_kg - start.gewicht_kg:+.2f} kg).'))
    if not letzter_vergleich:
        luecken.append('Zweiwochenvergleich am letzten Messdatum nicht pruefbar: Vergleichsmessung 14–21 Tage zuvor fehlt.')
    return Verlauf(stichtag, m, tuple(warnungen), tuple(luecken), profil.zunahme_g_pro_woche)


def prueftext(v: Verlauf) -> str:
    zeilen = [w.text for w in v.warnungen]
    if v.warnungen:
        zeilen.append('Aerztlich besprechen; keine automatische Anpassung zu Hause. Historische Hinweise sind datiert; ihre Abklaerung ist nicht erfasst.')
    else:
        zeilen.append('In den pruefbaren Messintervallen kein gewichtsbasiertes Kriterium erkannt; keine medizinische Entwarnung.')
    zeilen.extend(v.luecken)
    zeilen.append('Symptome, Puls, Blutdruck und Labor werden durch diese Gewichtspruefung nicht beurteilt.')
    return '\n'.join(zeilen)


@lru_cache(maxsize=1)
def _kurven() -> dict:
    return json.loads(REFERENZ.read_text(encoding='utf-8'))['kurven']


def bmi_perzentil(bmi: float, alter_jahre: float, referenz: str) -> tuple[float, float]:
    """Naeherung durch lineare LMS-Interpolation; Rueckgabe Perzentil, z-Score."""
    if referenz not in ('maedchen', 'jungen'):
        raise DatenFehler('BMI-Referenzkurve fehlt oder ist unbekannt.')
    if not math.isfinite(bmi) or bmi <= 0 or not math.isfinite(alter_jahre) or not 2 <= alter_jahre <= 18:
        raise DatenFehler('BMI muss positiv und endlich sein; KiGGS-Altersbereich hier 2–18 Jahre.')
    werte = _kurven()[referenz]
    for a, b in zip(werte, werte[1:]):
        if a[0] <= alter_jahre <= b[0]:
            anteil = (alter_jahre - a[0]) / (b[0] - a[0])
            l, m, s = (a[i] + anteil * (b[i] - a[i]) for i in (1, 2, 3))
            z = math.log(bmi / m) / s if l == 0 else math.expm1(l * math.log(bmi / m)) / (s * l)
            return 100 * NormalDist().cdf(z), z
    raise DatenFehler('Keine passende KiGGS-Referenz.')


def alter_am(geburt: date, tag: date) -> float:
    """Exakte Geburtstage, Anteil am laufenden Lebensjahr; 29.2. -> 28.2."""
    def geburtstag(jahr):
        try:
            return geburt.replace(year=jahr)
        except ValueError:
            return date(jahr, 2, 28)
    jahre = tag.year - geburt.year - (tag < geburtstag(tag.year))
    start, ende = geburtstag(geburt.year + jahre), geburtstag(geburt.year + jahre + 1)
    return jahre + (tag - start).days / (ende - start).days


def bmi_text(v: Verlauf, profil: Profil) -> str:
    if not v.messungen:
        return 'BMI nicht berechenbar: Gewicht fehlt.'
    m = v.messungen[-1]
    groesse_tag = profil.groesse_gemessen_am
    if groesse_tag is None:
        return 'BMI nicht berechnet: Datum der Groessenmessung fehlt (groesse_gemessen_am).'
    if not 0 <= (m.datum - groesse_tag).days <= 90:
        return 'BMI nicht berechnet: Groessenmessung liegt nach dem Gewicht oder mehr als 90 Tage davor.'
    bmi = float(m.gewicht_kg) / (profil.groesse_cm / 100) ** 2
    text = f'BMI am {m.datum}: {bmi:.2f} kg/m² (Groesse {profil.groesse_cm} cm vom {groesse_tag}).'
    try:
        p, z = bmi_perzentil(bmi, alter_am(profil.geburtsdatum, m.datum), profil.bmi_referenz)
    except DatenFehler as exc:
        return f'{text} Perzentil nicht berechnet: {exc}'
    perzentil = '<0,2' if p < 0.2 else '>99,8' if p > 99.8 else f'{p:.1f}'
    return (f'{text} KiGGS ({profil.bmi_referenz}): ca. P{perzentil}, z={z:.2f}. '
            'Naeherung aus gerundeten LMS-Tabellen; Extrembereiche besonders unsicher. '
            'Kein Zielgewicht und keine Diagnose. Quelle: https://edoc.rki.de/handle/176904/3254')


def main() -> int:
    parser = argparse.ArgumentParser(description='Gewichtsbasierte Pruefung fuer die Eltern')
    parser.add_argument('--datum', type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        print(prueftext(auswerten(lade_gewicht(), lade_profil(), args.datum)))
    except DatenFehler as exc:
        print(f'Verlauf nicht pruefbar: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
