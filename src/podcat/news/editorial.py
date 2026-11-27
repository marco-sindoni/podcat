"""Model call 2: Italian summary, importance, comic and satirical potential, clarity, sensitivity,
flags, follow-ups (research R5, R13, R14, R19)."""

from __future__ import annotations

from podcat.llm.base import TextModel, Usage
from podcat.news.models import EditorialResult, Source
from podcat.news.verify import Verdict

MAX_TOKENS = 20_000  # per batch, below the SDK limit for non-streaming calls
MAX_GROUPS = 60  # budget guard only (FR-022, research R16)
BATCH = 30  # stories per call, so each answer fits in MAX_TOKENS

SYSTEM = """Sei caporedattore e autore di "Podcat – Chiacchiere tra quattro gatti": quattro gatti in una
taverna commentano UNA notizia in un reel di 30 secondi per il grande pubblico italiano su YouTube.
Guardi ogni notizia con due occhi:
- l'occhio comico cerca notizie "facili da usare": hanno già dentro un'immagine buffa, un paradosso,
  un'esagerazione, una gaffe, un'abitudine in cui tutti si riconoscono;
- l'occhio satirico cerca notizie più serie su cui dire qualcosa di pungente: potere, contraddizioni,
  ipocrisie, società, un pensiero che resta a chi guarda. Mai a spese delle vittime.
Le notizie sono già verificate.

Per ogni notizia (indicata da group_index) scrivi in italiano:
- title: un titolo breve con parole tue, mai copiato da una testata;
- summary: 2-3 frasi neutre con parole tue, solo i fatti, senza copiare frasi degli articoli;
- importance 1-5 e importance_reason: quanto è ripresa e quanto conta per il pubblico italiano;
- comic_potential 1-5 e comic_reason: 5 = la notizia fa già ridere da sola; 3 = c'è una battuta
  intelligente; 1 = non c'è niente da ridere. Mai battute su vittime, malati o persone vulnerabili;
- satirical_potential 1-5 e satirical_reason: 5 = offre un'osservazione pungente e chiara su potere,
  contraddizioni o società, o un pensiero che fa riflettere; 1 = non c'è niente da dire oltre il fatto;
- clarity 1-5 e clarity_reason: 5 = la capisce in pochi secondi anche chi non legge i giornali;
  1 = servono nomi, sigle, procedure o antefatti;
- sensitive: true se la notizia ruota su morti, feriti, malattie, infortuni o violenze subite da
  persone reali, anche famose. Una scelta di carriera come un ritiro NON è sensitive, anche se tra i
  motivi c'è la salute;
- flags: politics, health, legal, finance quando la notizia tocca questi temi;
- follow_up_of: l'id di una notizia già trattata se questa ne è uno sviluppo importante, altrimenti null;
- already_covered: true se è la stessa notizia di una già trattata, senza sviluppi importanti.
Politica: resta neutrale, nessun giudizio di parte nei riassunti e nei motivi.
Rispondi per tutte le notizie ricevute."""

THURSDAY = """
Oggi è giovedì, "Giovedì buone notizie": sono tutte notizie positive. Nei motivi del potenziale comico
pensa a un umorismo caldo e affettuoso, mai sarcastico verso le persone della notizia; il potenziale
satirico oggi non serve, mettilo a 1.
Le notizie arrivano dagli ultimi 7 giorni: se due gruppi raccontano lo stesso fatto, rispondi solo per
il primo. Preferisci i fatti che un pubblico italiano capisce subito."""


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


def rank_for_editorial(verdicts: list[Verdict]) -> tuple[list[Verdict], int]:
    """Every verified group is rated; above MAX_GROUPS the least confirmed are left out (FR-022).
    Returns the groups to rate and how many were left out."""
    ordered = sorted(verdicts, key=lambda v: (-len(v.effective_groups), -len(v.items)))
    return ordered[:MAX_GROUPS], max(0, len(ordered) - MAX_GROUPS)


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
    if hasattr(model, "for_step"):
        model = model.for_step("editorial")
    stories, total = [], Usage(0, 0)
    for offset in range(0, len(verdicts), BATCH):
        batch = verdicts[offset : offset + BATCH]
        user = (
            "Notizie già trattate negli ultimi 30 giorni:\n"
            + render_recent(recent)
            + "\n\nNotizie verificate di oggi:\n\n"
            + render_groups(batch, sources)
        )
        part, usage = model.parse(system, user, EditorialResult, MAX_TOKENS)
        total = Usage(total.input_tokens + usage.input_tokens, total.output_tokens + usage.output_tokens)
        for st in part.stories:
            if 0 <= st.group_index < len(batch):
                st.group_index += offset
                stories.append(st)
    result, usage = EditorialResult(stories=stories), total
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
