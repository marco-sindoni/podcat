"""Model call 1: group items reporting the same event, classify, flag excluded topics (research R3)."""

from __future__ import annotations

from podcat.llm.base import TextModel, Usage
from podcat.news.models import LIGHT_CATEGORIES, FeedItem, Source, TriageResult

MAX_TOKENS = 20_000  # below the SDK limit for non-streaming calls
THURSDAY_CHUNK = 600  # items per call on Thursdays, when the window is 7 days

SYSTEM = """Sei la redazione di "Podcat", una trasmissione satirica italiana che commenta le notizie.
Ricevi un elenco di articoli, uno per riga: id | testata | titolo | anteprima.

Compito:
1. Raggruppa gli articoli che raccontano lo STESSO fatto (stesso evento, stesse persone, stesso momento).
   Non unire fatti diversi solo perché hanno lo stesso tema.
2. Restituisci i gruppi con almeno due articoli di testate diverse. Restituisci anche i gruppi di
   un solo articolo quando la categoria è entertainment, music, lifestyle oppure oddities.
3. Per ogni gruppo indica la categoria: current-affairs, sport, culture, entertainment, music,
   lifestyle, oddities (curiosità e stranezze: fatti bizzarri, record assurdi, animali, gaffe,
   abitudini in cui tutti si riconoscono), good-news (solo per fatti positivi: progresso, speranza,
   gentilezza).
4. Segna come escluso (campo excluded) ogni gruppo che è:
   - crime: cronaca nera (omicidi, violenze, rapine, femminicidi, abusi);
   - tragedy: tragedie, incidenti mortali, disastri con vittime, malattie gravi di persone;
   - harm: notizie che ruotano su malattie, ferite, infortuni o violenze subite da persone reali,
     anche famose (scontri con feriti, una persona famosa ricoverata, un atleta infortunato).
     Una scelta di carriera come un ritiro NON è harm, anche se tra i motivi c'è la salute;
   - clickbait: titolo acchiappaclic senza un fatto;
   - rumour: indiscrezioni, voci non confermate, gossip senza fonte;
   - sponsored: contenuto sponsorizzato o promozionale;
   - social-only: basato solo su post o video dei social, senza un fatto verificato.
   Spiega il motivo in una frase in italiano in excluded_reason.
5. positive = true se il fatto è una buona notizia (progresso umano, speranza, gentilezza),
   anche se la categoria non è good-news.
Usa solo gli id ricevuti. Non inventare articoli."""

THURSDAY = """

Oggi è giovedì, "Giovedì buone notizie". Cambia il punto 2: restituisci SOLO i gruppi con
positive = true, anche quelli di un solo articolo. Ignora tutti gli altri fatti.
Continua a segnare come escluso ogni gruppo positivo che rientra nel punto 4.
Segna come escluso anche ogni fatto positivo che nasce da un lutto, una morte, una violenza o un
crimine contro persone (per esempio un premio o un incontro per le vittime di un femminicidio):
usa tragedy o crime e spiega il motivo. Un furto d'arte ritrovato o una truffa sventata vanno bene."""


def render_items(items: list[FeedItem], sources: dict[str, Source]) -> str:
    lines = []
    for item in items:
        outlet = sources[item.source_id].name
        snippet = item.summary_snippet.replace("|", "/")
        title = item.title.replace("|", "/")
        lines.append(f"{item.item_id} | {outlet} | {title} | {snippet}")
    return "\n".join(lines)


def triage(
    model: TextModel,
    items: list[FeedItem],
    sources: dict[str, Source],
    thursday: bool = False,
) -> tuple[TriageResult, Usage]:
    """Run the triage call on non-satire items. Unknown ids in the answer are dropped.

    Weekdays: one call, groups of at least two items, or one item in a light category
    (spec 001 A1). Thursdays: the 7-day window is split into chunks, and single-item positive
    groups are kept (one reliable source is enough).
    """
    eligible = [i for i in items if sources[i.source_id].effective_role != "inspiration-only"]
    if not eligible:
        return TriageResult(groups=[]), Usage(0, 0)
    if hasattr(model, "for_step"):
        model = model.for_step("triage")
    if not thursday:
        chunks, system, header = [eligible], SYSTEM, "Articoli delle ultime 24 ore:\n"
    else:
        ordered = sorted(eligible, key=lambda i: i.published_at, reverse=True)
        chunks = [ordered[n : n + THURSDAY_CHUNK] for n in range(0, len(ordered), THURSDAY_CHUNK)]
        system, header = SYSTEM + THURSDAY, "Articoli degli ultimi 7 giorni:\n"
    groups, total = [], Usage(0, 0)
    for chunk in chunks:
        result, usage = model.parse(system, header + render_items(chunk, sources), TriageResult, MAX_TOKENS)
        total = Usage(total.input_tokens + usage.input_tokens, total.output_tokens + usage.output_tokens)
        known = {i.item_id for i in chunk}
        for group in result.groups:
            group.item_ids = [i for i in dict.fromkeys(group.item_ids) if i in known]
        for g in result.groups:
            minimum = 1 if thursday or g.category in LIGHT_CATEGORIES else 2
            if len(g.item_ids) >= minimum and (g.positive or not thursday):
                groups.append(g)
    return TriageResult(groups=groups), total
