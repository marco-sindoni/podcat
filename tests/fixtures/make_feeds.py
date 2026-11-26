"""Regenerate the fixture feeds: `uv run python tests/fixtures/make_feeds.py`."""

from pathlib import Path

HERE = Path(__file__).parent / "feeds"
RECENT = "Thu, 26 Nov 2026 18:00:00 +0100"
OLD = "Fri, 20 Nov 2026 09:00:00 +0100"

FEEDS = {
    "ansa": [("Sciopero nazionale dei treni venerdì, le fasce garantite", "(ANSA) - Roma, 26 nov - Stop di 24 ore per i treni.", RECENT)],
    "corriere": [
        ("Treni, sciopero di 24 ore: cosa sapere", "Fasce di garanzia dalle 6 alle 9.", RECENT),
        ("Rapina in banca a Milano, arrestati due uomini", "I due erano armati.", RECENT),
        ("Biblioteca di quartiere riaperta grazie ai volontari", "Trenta volontari hanno sistemato gli scaffali.", RECENT),
        ("Vecchia notizia sul meteo", "Pioggia al nord.", OLD),
    ],
    "skytg24": [("Sciopero dei treni, le info utili per i viaggiatori", "Stop dalle 21 di giovedì.", RECENT)],
    "repubblica": [
        ("Vinili, vendite record in Italia", "(ANSA) - I vinili superano i cd per la prima volta.", RECENT),
        ("Caravaggio, a Roma la grande mostra", "Quaranta opere a Palazzo Barberini.", RECENT),
    ],
    "lastampa": [("Il vinile batte il cd: vendite record", "(ANSA) - Il sorpasso nel 2026.", RECENT)],
    "fanpage": [
        ("Rapina a Milano, presi i due banditi", "Arrestati dopo un inseguimento.", RECENT),
        ("Non crederai a cosa ha fatto il sindaco", "Video virale.", RECENT),
    ],
    "artribune": [("Caravaggio a Palazzo Barberini: la mostra dell'anno", "Apre sabato.", RECENT)],
    "gazzetta": [("Sinner vince le Finals di Torino", "Battuto Alcaraz in due set.", RECENT)],
    "corrieredellosport": [("Sinner trionfa a Torino", "Il numero uno del mondo vince le Finals.", RECENT)],
    "skysport": [("Finals, Sinner campione", "Secondo titolo di fila.", RECENT)],
    "italiachecambia": [("Volontari riaprono la biblioteca di quartiere", "Un progetto partito dal basso.", RECENT)],
    "lercio": [("Sciopero dei treni: i pendolari scioperano a loro volta", "Satira.", RECENT)],
}


def rss(source: str, entries) -> str:
    items = "\n".join(
        f"""  <item><title>{t}</title><link>https://example.org/{source}/{i}</link>
    <description>{d}</description><pubDate>{p}</pubDate></item>"""
        for i, (t, d, p) in enumerate(entries)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{source}</title><link>https://example.org/{source}</link>
<description>fixture</description>
{items}
</channel></rss>
"""


if __name__ == "__main__":
    HERE.mkdir(exist_ok=True)
    for source, entries in FEEDS.items():
        (HERE / f"{source}.xml").write_text(rss(source, entries), encoding="utf-8")
