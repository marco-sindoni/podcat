"""Model call 2: Italian summary, importance and comic potential, flags, follow-ups (research R5)."""

from __future__ import annotations

from podcat.llm.base import TextModel, Usage
from podcat.news.models import EditorialResult, Source
from podcat.news.verify import Verdict

MAX_TOKENS = 12_000
MAX_GROUPS = 20

SYSTEM = """Sei il caporedattore di "Podcat – Chiacchiere tra quattro gatti", un programma italiano in cui
quattro gatti commentano le notizie con ironia. Ricevi notizie già verificate su almeno due fonti.

Per ogni notizia (indicata da group_index) scrivi in italiano:
- title: un titolo breve con parole tue, mai copiato da una testata;
- summary: 2-3 frasi neutre con parole tue, solo i fatti, senza copiare frasi degli articoli;
- importance 1-5 e importance_reason: quanto è ripresa e quanto conta per il pubblico italiano;
- comic_potential 1-5 e comic_reason: quanto si presta a battute intelligenti su fatti e potenti,
  mai su persone vulnerabili o vittime;
- flags: politics, health, legal, finance quando la notizia tocca questi temi;
- follow_up_of: l'id di una notizia già trattata se questa ne è uno sviluppo importante, altrimenti null;
- already_covered: true se è la stessa notizia di una già trattata, senza sviluppi importanti.
Politica: resta neutrale, nessun giudizio di parte nei riassunti e nei motivi.
Rispondi per tutte le notizie ricevute."""

THURSDAY = """
Oggi è giovedì, "Giovedì buone notizie": sono tutte notizie positive. Nei motivi del potenziale comico
pensa a un umorismo caldo e affettuoso, mai sarcastico verso le persone della notizia."""


def render_groups(verdicts: list[Verdict], sources: dict[str, Source]) -> str:
    blocks = []
    for index, v in enumerate(verdicts):
        lines = [f"[{index}] categoria: {v.group.category}; fonti indipendenti: {len(v.effective_groups)}"]
        for item in v.items:
            lines.append(f"  - {sources[item.source_id].name}: {item.title} — {item.summary_snippet}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def render_recent(recent: list[dict]) -> str:
    if not recent:
        return "Nessuna."
    return "\n".join(f"- {r['id']}: {r['title']}" for r in recent)


def rank_for_editorial(verdicts: list[Verdict]) -> list[Verdict]:
    """Keep the most widely confirmed groups when there are too many."""
    return sorted(verdicts, key=lambda v: (-len(v.effective_groups), -len(v.items)))[:MAX_GROUPS]


def editorial(
    model: TextModel,
    verdicts: list[Verdict],
    sources: dict[str, Source],
    recent: list[dict],
    thursday: bool = False,
) -> tuple[EditorialResult, Usage]:
    if not verdicts:
        return EditorialResult(stories=[]), Usage(0, 0)
    system = SYSTEM + (THURSDAY if thursday else "")
    user = (
        "Notizie già trattate negli ultimi 30 giorni:\n"
        + render_recent(recent)
        + "\n\nNotizie verificate di oggi:\n\n"
        + render_groups(verdicts, sources)
    )
    if hasattr(model, "for_step"):
        model = model.for_step("editorial")
    result, usage = model.parse(system, user, EditorialResult, MAX_TOKENS)
    valid = {r["id"] for r in recent}
    seen = set()
    stories = []
    for s in result.stories:
        if 0 <= s.group_index < len(verdicts) and s.group_index not in seen:
            seen.add(s.group_index)
            if s.follow_up_of not in valid:
                s.follow_up_of = None
            stories.append(s)
    result.stories = stories
    return result, usage
