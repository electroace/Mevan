"""Fontovi za PDF izvještaje i grafikone.

Tri datoteke u direktoriju `fonts/` (Source Sans 3 i Source Serif 4, licenca SIL OFL 1.1,
tekst licence je u `fonts/OFL-LICENSE.md`) daju isti izgled na svakom serveru. Ako direktorij
nedostaje, koristi se raniji sistemski font, pa izvještaj i dalje nastaje.
"""
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from project_reports import FONT as FALLBACK

DIR = Path(__file__).parent / 'fonts'
FILES = {'body': 'SourceSans3-Regular.ttf', 'bold': 'SourceSans3-Semibold.ttf', 'display': 'SourceSerif4-Semibold.ttf'}


def font_paths():
    """Putanje za tri uloge: tekst, istaknuti tekst i naslovi."""
    paths = {role: DIR / name for role, name in FILES.items()}
    if all(path.is_file() for path in paths.values()):
        return {role: str(path) for role, path in paths.items()}
    return {role: FALLBACK for role in FILES}


def register_pdf_fonts():
    """Registruje fontove u ReportLabu i vraća njihova imena po ulozi."""
    names = {}
    for role, path in font_paths().items():
        names[role] = 'Mevan-' + role
        pdfmetrics.registerFont(TTFont(names[role], path))
    return names
