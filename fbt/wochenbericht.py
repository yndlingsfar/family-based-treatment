"""Sieben Tage Bilanz plus gesamter Gewichtsverlauf bis zum Stichtag.

Standardbibliothek fuer Text/HTML; Matplotlib nur fuer das optionale Diagramm.
Ausgaben bleiben im privaten Datenverzeichnis. Kein automatischer Versand.
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from fbt.bilanz import Tagesbilanz, lade_tag
from fbt.daten import DatenFehler, Profil, daten_pfad, lade_profil
from fbt.verlauf import Verlauf, auswerten, bmi_text, lade_gewicht, prueftext

WARNZEICHEN = {
    'ohnmacht': 'Ohnmacht', 'orthostase': 'Schwarzwerden beim Aufstehen',
    'puls': 'auffaellig langsamer Puls', 'erbrechen': 'Erbrechen',
    'abfuehrmittel': 'Abfuehrmittelgebrauch', 'selbstverletzung': 'Selbstverletzung',
    'suizidalitaet': 'Aeusserungen ueber Suizid', 'oedeme': 'Oedeme',
    'verwirrtheit': 'Verwirrtheit', 'atemnot': 'Atemnot',
}


@dataclass(frozen=True)
class Berichtstag:
    datum: date
    bilanz: Tagesbilanz | None
    luecken: tuple[str, ...]

    @property
    def vollstaendig(self) -> bool:
        return self.bilanz is not None and self.bilanz.vollstaendig and not self.luecken


@dataclass(frozen=True)
class Wochenbericht:
    profil: Profil
    verlauf: Verlauf
    tage: tuple[Berichtstag, ...]
    symptome: tuple[str, ...] | None  # None: nicht abgefragt; (): ausdruecklich verneint
    fragen: tuple[str, ...]

    @property
    def mittel_kcal(self) -> float | None:
        tage = [t.bilanz for t in self.tage if t.vollstaendig]
        return sum(t.kcal_tatsaechlich for t in tage) / len(tage) if tage else None


def erstelle_bericht(stichtag: date, basis: Path | None = None, *,
                     symptome: tuple[str, ...] | None = None,
                     fragen: tuple[str, ...] = ()) -> Wochenbericht:
    basis = daten_pfad() if basis is None else basis
    if type(stichtag) is not date or stichtag > date.today():
        raise DatenFehler('Berichtsstichtag darf nicht in der Zukunft liegen.')
    if symptome is not None and any(s not in WARNZEICHEN for s in symptome):
        raise DatenFehler('Unbekanntes Warnzeichen.')
    profil = lade_profil(basis)
    # Fehlende Gewichtsdaten lassen den Bericht zu, korrupte Daten dagegen nicht.
    messungen = lade_gewicht(basis) if (basis / 'gewicht.csv').exists() else ()
    verlauf = auswerten(messungen, profil, stichtag)
    tage = []
    for i in range(6, -1, -1):
        datum = stichtag - timedelta(days=i)
        if not (basis / 'tage' / f'{datum}.toml').exists():
            tage.append(Berichtstag(datum, None, ('Tagesdatei fehlt',)))
            continue
        b = lade_tag(datum, basis)
        luecken = []
        # Der Loader kann Zahlen pruefen, kennt aber den Mahlzeitenplan nicht.
        if len(b.mahlzeiten) != len(profil.mahlzeiten):
            luecken.append(f'{len(b.mahlzeiten)} von {len(profil.mahlzeiten)} vorgesehenen Mahlzeiten erfasst')
        if any(not m.gerichte for m in b.mahlzeiten):
            luecken.append('Mahlzeit ohne Gerichte')
        if len({m.name for m in b.mahlzeiten}) != len(b.mahlzeiten):
            luecken.append('Doppelte Mahlzeitennamen; Zuordnung zum Plan pruefen')
        if b.unbekannte:
            luecken.append('kcal fehlen: ' + ', '.join(b.unbekannte))
        if b.angenommen:
            luecken.append('Anteil fehlt (bisher als 100 % gerechnet): ' + ', '.join(b.angenommen))
        tage.append(Berichtstag(datum, b, tuple(luecken)))
    return Wochenbericht(profil, verlauf, tuple(tage), symptome, fragen)


def _zelle(text: object) -> str:
    # Freitexte duerfen weder Markdown-Struktur noch HTML einschleusen.
    return html.escape(str(text), quote=False).replace('|', '&#124;').replace('\n', ' / ').replace('\r', '')


def bericht_markdown(b: Wochenbericht) -> str:
    v = b.verlauf
    z = ['# Hinweise zur aerztlichen Besprechung', '']
    if b.symptome:
        z += ['WARNZEICHEN berichtet: ' + ', '.join(WARNZEICHEN[s] for s in b.symptome) + '.',
              'Jetzt medizinische Hilfe organisieren: Praxis, ausserhalb der Sprechzeiten Kinderklinik; '
              'bei akuter Gefahr oder Suizidalitaet Notaufnahme / 112. Kein Aufholplan. Dieser Bericht darf Hilfe nicht verzoegern.', '']
    elif b.symptome is None:
        z += ['Symptombasierte Pruefung NICHT durchgefuehrt. Beobachtungs-Freitexte werden nicht automatisch medizinisch ausgewertet.', '']
    else:
        z += ['Die abgefragten Warnzeichen wurden fuer den Berichtszeitraum ausdruecklich verneint (Elternangabe).', '']
    z += [prueftext(v), '', f'# Wochenbericht {b.tage[0].datum} bis {v.stichtag}',
          '', f'Eltern / Behandlungsteam — {_zelle(b.profil.rufname)}. Enthaelt vertrauliche Zahlen; keine Tischansicht.',
          '', '## Gewicht', '']
    if v.messungen:
        z += [f'Gesamter erfasster Verlauf: {v.messungen[0].datum} bis {v.messungen[-1].datum}.']
        if v.aenderung_kg is not None:
            z += [f'Veraenderung: {v.aenderung_kg:+.2f} kg; auf sieben Tage umgerechnet: {v.g_pro_woche:+.0f} g/Woche '
                  '(Endpunktvergleich ueber den gesamten Zeitraum, keine Prognose).']
        quelle = b.profil.zunahme_quelle
        z += [f'Vergleichslinie: {v.vergleich_g_pro_woche} g/Woche ab erster Messung. '
              + (f'Quelle laut Profil: {_zelle(quelle)}.' if quelle else 'Aerztliche Bestaetigung/Quelle im Profil fehlt.'),
              'Die aktuelle Profilvorgabe wird als Vergleich ueber den gesamten Zeitraum gezeigt; fruehere Zielaenderungen sind nicht erfasst.', '',
              '| Datum | kg | Vergleich kg | Uhrzeit | Bedingungen | Gewogen von | Blind |',
              '| --- | ---: | ---: | --- | --- | --- | --- |']
        for m in v.messungen:
            blind = 'unbekannt' if m.blind is None else 'ja' if m.blind else 'nein'
            z.append(f'| {m.datum} | {m.gewicht_kg:.2f} | {v.vergleich_kg(m.datum):.2f} | '
                     f'{_zelle(m.uhrzeit or "unbekannt")} | {_zelle(m.bedingungen or "unbekannt")} | '
                     f'{_zelle(m.gewogen_von or "unbekannt")} | {blind} |')
    z += ['', bmi_text(v, b.profil), '', '## Mahlzeiten und Energie', '',
          'Gegessene Anteile sind Schaetzungen der Eltern. Teilwerte sind keine vollstaendigen Tagessummen.', '',
          '| Datum | Geplant kcal | Gegessen kcal (Schaetzung) | Tagesziel kcal | Datenlage |',
          '| --- | ---: | ---: | ---: | --- |']
    for t in b.tage:
        if t.bilanz is None:
            z.append(f'| {t.datum} | — | — | unbekannt | Tagesdatei fehlt |')
        else:
            tag = t.bilanz
            status = 'erfasst' if t.vollstaendig else 'UNVOLLSTAENDIG: ' + '; '.join(t.luecken)
            marker = '' if t.vollstaendig else ' (Teilwert/Annahme)'
            z.append(f'| {t.datum} | {tag.kcal_geplant:.0f}{marker} | {tag.kcal_tatsaechlich:.0f}{marker} | '
                     f'{tag.ziel_kcal if tag.ziel_kcal is not None else "unbekannt"} | {_zelle(status)} |')
    n = sum(t.vollstaendig for t in b.tage)
    z += ['', f'Vollstaendig erfasste Tage: {n}/7.']
    if b.mittel_kcal is None:
        z += ['Kein Durchschnitt berechenbar; kein vollstaendig erfasster Tag.']
    else:
        z += [f'Durchschnitt gegessen ausschliesslich dieser {n} Tage: {b.mittel_kcal:.0f} kcal/Tag.'
              + (' Kein Durchschnitt der ganzen Woche.' if n < 7 else '')]
    z += ['Tagesziele stammen ausschliesslich aus den jeweiligen Tagesdateien; fehlende Ziele werden nicht aus dem heutigen Profil ersetzt.',
          '', '## Beobachtungen der Eltern', '']
    beobachtungen = [f'- {t.datum}: {_zelle(t.bilanz.beobachtungen)}' for t in b.tage if t.bilanz and t.bilanz.beobachtungen]
    z += beobachtungen or ['Keine Beobachtungen dokumentiert; das bedeutet nicht, dass keine Auffaelligkeiten bestanden.']
    z += ['', '## Offene Fragen fuer den Termin', '']
    z += [f'- {_zelle(f)}' for f in b.fragen] or ['Keine Fragen dokumentiert.']
    z += ['', 'Die Auswertung beschreibt dokumentierte Angaben. Sie legt weder Zielgewicht noch Behandlung fest.', '']
    return '\n'.join(z)


def diagramm_png(b: Wochenbericht) -> bytes:
    """Messpunkte und Vergleich; Messluecken >7 Tage werden nicht verbunden."""
    try:
        from matplotlib.figure import Figure
        from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
    except ImportError as exc:
        raise DatenFehler('Diagramm benoetigt Matplotlib: python3 -m pip install -r requirements-diagramm.txt. Text/HTML funktioniert ohne --diagramm.') from exc
    fig = Figure(figsize=(9, 4.5), layout='constrained')
    ax = fig.subplots()
    v = b.verlauf
    if v.messungen:
        m = v.messungen
        ax.plot([x.datum for x in m], [float(x.gewicht_kg) for x in m], 'o', color='#185b75', label='Messwerte')
        for a, c in zip(m, m[1:]):
            if (c.datum - a.datum).days <= 7:
                ax.plot([a.datum, c.datum], [float(a.gewicht_kg), float(c.gewicht_kg)], color='#185b75')
        ende = v.stichtag if v.stichtag > m[0].datum else v.stichtag + timedelta(days=1)
        ax.plot([m[0].datum, ende], [float(v.vergleich_kg(m[0].datum)), float(v.vergleich_kg(ende))],
                '--', color='#826024', label=f'Profil-Vergleich: {v.vergleich_g_pro_woche} g/Woche')
        locator = AutoDateLocator(minticks=3, maxticks=7)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
        ax.legend(loc='best')
    else:
        ax.text(0.5, 0.5, 'Keine Gewichtsmessungen vorhanden', transform=ax.transAxes, ha='center')
    ax.set_ylabel('Gewicht (kg)')
    ax.set_title('Gewichtsverlauf — Eltern / Behandlungsteam')
    ax.grid(alpha=0.2)
    output = io.BytesIO()
    fig.savefig(output, format='png', dpi=160)
    return output.getvalue()


def bericht_html(markdown: str, png: bytes | None = None) -> str:
    """Kleine, sichere Darstellung nur der vom Renderer erzeugten Markdown-Formen."""
    teile, tabelle = [], False
    for zeile in markdown.splitlines():
        if zeile.startswith('|'):
            if zeile.startswith('| ---'):
                continue
            if not tabelle:
                teile.append('<table>')
                tabelle = True
                element = 'th'
            else:
                element = 'td'
            teile.append('<tr>' + ''.join(f'<{element}>{html.escape(html.unescape(x.strip()))}</{element}>'
                                          for x in zeile.strip('|').split('|')) + '</tr>')
            continue
        if tabelle:
            teile.append('</table>')
            tabelle = False
        if not zeile:
            continue
        ebene = len(zeile) - len(zeile.lstrip('#'))
        inhalt = html.escape(html.unescape(zeile[ebene:].strip() if ebene else zeile))
        teile.append(f'<h{ebene}>{inhalt}</h{ebene}>' if ebene in (1, 2) else f'<p>{inhalt}</p>')
    if tabelle:
        teile.append('</table>')
    if png:
        teile.append('<img alt="Gewichtsmessungen und Profil-Vergleichslinie" src="data:image/png;base64,'
                     + base64.b64encode(png).decode('ascii') + '">')
    return ('<!doctype html><html lang="de"><meta charset="utf-8"><title>FBT Wochenbericht – Eltern</title>'
            '<style>body{font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#172b35}'
            'h1{font-size:24px}h2{font-size:20px;margin-top:30px}table{border-collapse:collapse;width:100%;font-size:12px}'
            'td,th{border-bottom:1px solid #ccd5d9;text-align:left;padding:8px;overflow-wrap:anywhere}'
            'th{background:#eef3f4}img{width:100%}p{white-space:pre-wrap;overflow-wrap:anywhere}'
            '@media print{body{margin:0;font-size:11px}table{font-size:9px}h1,h2{break-after:avoid}tr,img{break-inside:avoid}}'
            '</style><body>' + '\n'.join(teile) + '</body></html>')


def speichere(b: Wochenbericht, basis: Path | None = None, *, diagramm: bool = False) -> tuple[Path, ...]:
    basis = (daten_pfad() if basis is None else basis).resolve()
    repo = Path(__file__).resolve().parent.parent
    ziel = (basis / 'berichte').resolve()
    if ziel.is_relative_to(repo) or not ziel.is_relative_to(basis):
        raise DatenFehler('Berichte muessen ausserhalb des Plugin-Repositories im privaten Datenverzeichnis liegen.')
    markdown = bericht_markdown(b)
    png = diagramm_png(b) if diagramm else None
    dateien = {'.md': markdown.encode('utf-8'), '.html': bericht_html(markdown, png).encode('utf-8')}
    if png:
        dateien['.png'] = png
    ziel.mkdir(parents=True, exist_ok=True, mode=0o700)
    pfade = []
    for suffix, inhalt in dateien.items():
        pfad = ziel / f'wochenbericht-{b.verlauf.stichtag}{suffix}'
        # Atomarer Austausch statt teilgeschriebener Dateien; keine Symlink-Ziele verfolgen.
        fd, name = tempfile.mkstemp(dir=ziel, prefix='.bericht-')
        try:
            with os.fdopen(fd, 'wb') as fh:
                fh.write(inhalt)
            os.replace(name, pfad)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        pfade.append(pfad)
    return tuple(pfade)


def main() -> int:
    parser = argparse.ArgumentParser(description='Wochenbericht fuer Eltern und Behandlungsteam')
    parser.add_argument('--bis', type=date.fromisoformat, default=date.today())
    parser.add_argument('--symptome-geprueft', action='store_true')
    parser.add_argument('--warnzeichen', action='append', choices=tuple(WARNZEICHEN), default=[])
    parser.add_argument('--frage', action='append', default=[])
    parser.add_argument('--speichern', action='store_true')
    parser.add_argument('--diagramm', action='store_true', help='PNG und eingebettete Grafik im HTML (Matplotlib)')
    args = parser.parse_args()
    if args.diagramm and not args.speichern:
        parser.error('--diagramm benoetigt --speichern')
    try:
        symptome = tuple(dict.fromkeys(args.warnzeichen)) if args.warnzeichen or args.symptome_geprueft else None
        bericht = erstelle_bericht(args.bis, symptome=symptome, fragen=tuple(args.frage))
        print(bericht_markdown(bericht))
        if args.speichern:
            for pfad in speichere(bericht, diagramm=args.diagramm):
                print(f'Gespeichert: {pfad}', file=sys.stderr)
    except (DatenFehler, OSError) as exc:
        print(f'Wochenbericht nicht erstellt: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
