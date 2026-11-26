"""Model call 1: group items reporting the same event, classify, flag excluded topics (research R3)."""

from __future__ import annotations

from podcat.llm.base import TextModel, Usage
from podcat.news.models import FeedItem, Source, TriageResult

MAX_TOKENS = 16_000

SYSTEM = """Sei la redazione di "Podcat", una trasmissione satirica italiana che commenta le notizie.
Ricevi un elenco di articoli, uno per riga: id | testata | titolo | anteprima.

Compito:
1. Raggruppa gli articoli che raccontano lo STESSO fatto (stesso evento, stesse persone, stesso momento).
   Non unire fatti diversi solo perché hanno lo stesso tema.
2. Restituisci SOLO i gruppi con almeno due articoli di testate diverse.
3. Per ogni gruppo indica la categoria: current-affairs, sport, culture, entertainment, music,
   lifestyle, good-news (solo per fatti positivi: progresso, speranza, gentilezza).
4. Segna come escluso (campo excluded) ogni gruppo che è:
   - crime: cronaca nera (omicidi, violenze, rapine, femminicidi, abusi);
   - tragedy: tragedie, incidenti mortali, disastri con vittime, malattie gravi di persone;
   - clickbait: titolo acchiappaclic senza un fatto;
   - rumour: indiscrezioni, voci non confermate, gossip senza fonte;
   - sponsored: contenuto sponsorizzato o promozionale;
   - social-only: basato solo su post o video dei social, senza un fatto verificato.
   Spiega il motivo in una frase in italiano in excluded_reason.
5. positive = true se il fatto è una buona notizia (progresso umano, speranza, gentilezza),
   anche se la categoria non è good-news.
Usa solo gli id ricevuti. Non inventare articoli."""


def render_items(items: list[FeedItem], sources: dict[str, Source]) -> str:
    lines = []
    for item in items:
        outlet = sources[item.source_id].name
        snippet = item.summary_snippet.replace("|", "/")
        title = item.title.replace("|", "/")
        lines.append(f"{item.item_id} | {outlet} | {title} | {snippet}")
    return "\n".join(lines)


def triage(model: TextModel, items: list[FeedItem], sources: dict[str, Source]) -> tuple[TriageResult, Usage]:
    """Run the triage call on non-satire items. Unknown ids in the answer are dropped."""
    eligible = [i for i in items if sources[i.source_id].effective_role != "inspiration-only"]
    if not eligible:
        return TriageResult(groups=[]), Usage(0, 0)
    user = "Articoli delle ultime 24 ore:\n" + render_items(eligible, sources)
    if hasattr(model, "for_step"):
        model = model.for_step("triage")
    result, usage = model.parse(SYSTEM, user, TriageResult, MAX_TOKENS)
    known = {i.item_id for i in eligible}
    for group in result.groups:
        group.item_ids = [i for i in dict.fromkeys(group.item_ids) if i in known]
    result.groups = [g for g in result.groups if len(g.item_ids) >= 2]
    return result, usage
