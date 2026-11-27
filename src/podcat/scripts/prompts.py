"""Italian prompts for the writers' room, the head writer, the fix and the revision (research R2, R9)."""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from podcat.news.models import CATEGORY_IT
from podcat.scripts.bible import Bible
from podcat.scripts.models import CAT_NAMES, MODE_IT

SHOW = """"Podcat – Chiacchiere tra quattro gatti" è un canale YouTube italiano: quattro gatti grunge, in
quattro poltrone di pelle marrone in una taverna calda, commentano una notizia con ironia, sarcasmo e
intelligenza. Video verticali, stile cartoon 3D morbido, voci fisse per ogni gatto, sottotitoli."""

CAST_RULES = """Regole fisse del cast:
- Flanella ha la PRIMA e l'ULTIMA battuta: apre presentando la notizia, chiude con l'ultima parola.
- Feedback ha la PENULTIMA battuta: la battuta finale inattesa, lenta, spiazzante.
- Fuzz fa almeno un'escalation: prende la notizia e la porta all'assurdo.
- Vinile fa almeno un paragone con gli anni '90 (mai musicisti reali per nome) e guida le notizie di
  cultura, spettacolo e musica.
- Di base parlano tutti e quattro. Se la notizia rende meglio con meno voci, possono parlare solo
  Flanella, Feedback e uno o due tra Fuzz e Vinile; ma ogni gatto che non parla DEVE comparire con
  almeno una reazione (faccia o gesto) in una scena in cui si vede: campo largo, coppia di poltrone
  vicine o primo piano di reazione.
- I tic verbali si usano con parsimonia, non in ogni copione."""

CRAFT = """Mestiere comico (la cosa più importante):
- UNA sola premessa comica per copione, scelta dal dettaglio più assurdo della notizia. Niente elenco
  di battute staccate: ogni battuta risponde a quella prima ("sì, e allora...") e alza la posta.
- Arco: Flanella presenta il fatto con il dettaglio giusto; Fuzz lo porta all'assurdo; gli altri
  rilanciano o smontano la stessa idea; Feedback spiazza con una conclusione che sembra fuori tema e
  invece chiude il cerchio; Flanella chiude con una frase secca che riprende un'immagine dell'inizio
  (callback).
- Battute concrete e visive, con parole che si possono immaginare; niente giochi di parole deboli,
  niente battute spiegate. Meglio una battuta forte che tre medie."""

CONTENT_RULES = """Regole sui contenuti (non negoziabili):
- Si commentano i fatti del riassunto, senza inventare fatti nuovi e senza copiare testi di giornali.
- Satira sui fatti e sui potenti, mai su gruppi deboli, vittime, malati o persone comuni.
- Nessun gatto dà consigli medici, legali o finanziari.
- Politica mai di parte: si ride delle contraddizioni e del potere, non di uno schieramento. Niente
  nomi di partiti, niente battute su come votare o su chi votare.
- Persone reali: solo i personaggi pubblici della notizia, per il loro ruolo pubblico.
- Niente volgarità, niente contenuti scioccanti."""

REGISTER = {
    "comico": """Registro: COMICO. Battute rapide, immagini buffe, escalation assurda di Fuzz, battuta
finale di Feedback a sorpresa, chiusura secca di Flanella. Deve far ridere.""",
    "pungente": """Registro: PUNGENTE. Notizia più seria: satira e frecciate sui fatti e sui potenti, meno
gag. Si ride dell'ironia dei fatti; Fuzz si indigna per l'assurdità dei fatti, mai contro le vittime;
la battuta finale di Feedback è una riflessione con un colpo ironico che resta in testa; Flanella chiude
con una frecciata. Deve far sorridere e pensare.""",
}

THURSDAY = """Oggi è "Giovedì buone notizie": la notizia è positiva. Tono caldo e affettuoso: i gatti
restano spiritosi ma scherzano su se stessi e sulla situazione, MAI sulle persone della notizia.
L'indignazione di Fuzz diventa entusiasmo, o si sfoga su qualcosa di banale e innocuo.
La scena 1 è lo stacchetto "sting-gnocchi" senza battute; la battuta 1 di Flanella inizia esattamente
con la formula: «{formula}»."""

FLAGS = {
    "politics": "La notizia tocca la politica: satira sui fatti e sui potenti, mai di parte.",
    "health": "La notizia tocca la salute: nessun consiglio, nessuna battuta su malati.",
    "legal": "La notizia tocca la giustizia: nessun consiglio legale, nessun giudizio su colpevolezze.",
    "finance": "La notizia tocca i soldi: nessun consiglio finanziario.",
}

FORMAT = """Formato:
- lines: battute numerate da 1 in ordine (n, cat, text). cat è uno tra flanella, fuzz, vinile, feedback.
  Solo le parole dette, niente indicazioni di scena dentro il testo.
- scenes: scene numerate da 1 in ordine; ogni scena ha shot (un id dalla lista delle inquadrature),
  lines (i numeri delle battute dette lì, in ordine; ogni battuta in una sola scena), reactions (gatti
  che si vedono e reagiscono senza parlare: cat + direction, una breve indicazione in italiano).
  Nei primi piani "close-<gatto>" parla solo quel gatto. Le coppie "two-..." sono solo poltrone vicine.
- news_image: l'immagine dedicata alla notizia compare UNA sola volta, in una scena con l'inquadratura
  del suo modo (A: news-tv; B: news-cutin, con voce fuori campo o senza battute; C: news-held-<gatto>,
  e quel gatto parla nella scena, held_by = quel gatto). comment_line è la battuta che la commenta.
  subject è una frase sul soggetto dell'immagine, senza volti realistici di persone reali né loghi.
- Non scrivere durate: le calcola il programma."""


@dataclass
class Brief:
    """Everything the prompts need about one script."""

    kind: str
    story: dict
    thursday: bool
    tone: str
    allowed_modes: list[str]
    recent: list[dict] = field(default_factory=list)  # {first, last} of recent scripts
    reel_lines: list[str] = field(default_factory=list)  # weekly: lines of the reel on the same story


def _limits(bible: Bible, kind: str) -> str:
    w = bible.config["words"][kind]
    t = bible.config["target_s"][kind]
    if kind == "weekly":
        return (f"Puntata settimanale di circa {t} secondi: tra {w['min']} e {w['max']} parole dette in tutto, "
                "almeno due battute per ogni gatto (parlano tutti e quattro). Struttura: apertura a freddo, "
                "notizia raccontata e discussa, almeno un'escalation di Fuzz, una divagazione nostalgica di "
                "Vinile, battuta di Feedback, saluto di Flanella.")
    return (f"Reel di circa {t} secondi: tra {w['min']} e {w['max']} parole dette in tutto (conta bene: "
            "sono poche, ogni parola deve servire). Punta a circa "
            f"{(w['min'] + w['max']) // 2} parole: circa {round((w['min'] + w['max']) / 22)} battute brevi, quasi tutte "
            "sotto le 14 parole. Ritmo serrato.")


def system_prompt(bible: Bible, role: str) -> str:
    cast = "\n\n".join(f"### {CAT_NAMES[c]}\n{t}" for c, t in bible.characters.items())
    roles = {
        "room": "Sei un autore comico esperto della stanza degli autori di uno show satirico italiano.",
        "head": "Sei il capo autore di uno show satirico italiano: esperto di comicità, ritmo e televisione.",
        "revision": "Sei il capo autore di uno show satirico italiano e applichi le note del produttore.",
    }
    return "\n\n".join([
        roles[role], SHOW, "## I quattro gatti\n\n" + cast, CAST_RULES, CRAFT, CONTENT_RULES,
        "## Inquadrature\n" + bible.shot_list_text(), FORMAT,
    ])


def brief_text(bible: Bible, b: Brief) -> str:
    s = b.story
    parts = [
        "## Notizia",
        f"Titolo: {s.get('title')}",
        f"Riassunto: {s.get('summary')}",
        f"Categoria: {CATEGORY_IT.get(s.get('category', ''), s.get('category', ''))}",
        "",
        _limits(bible, b.kind),
        REGISTER[b.tone] if not b.thursday else THURSDAY.format(formula=bible.config["thursday_formula"]),
    ]
    for flag in s.get("flags") or []:
        if flag in FLAGS:
            parts.append(FLAGS[flag])
    modes = " oppure ".join(MODE_IT[m] for m in b.allowed_modes)
    parts.append(f"Immagine della notizia: usa {modes} (il video precedente ha usato l'altro).")
    if b.recent:
        rec = "\n".join(f"- apertura: «{r['first']}» / chiusura: «{r['last']}»" for r in b.recent)
        parts.append("Copioni recenti: NON ripetere aperture, chiusure, battute o tormentoni:\n" + rec)
    if b.reel_lines:
        parts.append("Questa notizia è già uscita in un reel: trova un angolo nuovo, non riusare queste battute:\n"
                     + "\n".join(f"- {l}" for l in b.reel_lines))
    return "\n\n".join(parts)


def room_user(bible: Bible, b: Brief) -> str:
    return brief_text(bible, b) + """

## Compito
Scrivi DUE copioni completi, con due angoli comici diversi (per esempio: prendere il fatto alla
lettera; il complotto di Fuzz; il paragone impossibile di Vinile; il dettaglio assurdo). Per ognuno
indica l'angolo in una frase (angle). Ogni copione rispetta già tutte le regole."""


def head_user(bible: Bible, b: Brief, drafts_yaml: str) -> str:
    return brief_text(bible, b) + f"""

## Bozze della stanza degli autori
{drafts_yaml}

## Compito
Scegli la bozza con la premessa comica più forte (fondi solo se resta UNA premessa), poi riscrivila
da capo autore: ogni battuta deve legarsi alla precedente, taglia quelle che non servono all'arco,
rendi più affilate le battute, controlla che ogni gatto suoni come se stesso, rispetta
il numero di parole e tutte le regole. Poi scrivi 2 finali alternativi (endings), ognuno con una
penultima battuta di Feedback e un'ultima di Flanella diverse da quelle del copione.
In notes (in italiano, brevi): cosa hai cambiato e perché, quale angolo hai scelto, chi resta zitto
e perché (se qualcuno resta zitto), e se la notizia ti sembra debole per un video."""


def fix_user(bible: Bible, b: Brief, current_yaml: str, problems: list[str], word_report: str = "") -> str:
    return brief_text(bible, b) + f"""

## Copione attuale
{current_yaml}

## Problemi trovati dal controllo automatico
{chr(10).join('- ' + x for x in problems)}
{word_report}

## Compito
Correggi SOLO quello che serve per risolvere i problemi, mantenendo le battute migliori. Restituisci
il copione completo con i 2 finali alternativi e le note aggiornate."""


def revision_user(bible: Bible, b: Brief, current_yaml: str, comments_yaml: str) -> str:
    return brief_text(bible, b) + f"""

## Copione attuale (le battute con manual: true le ha scritte Marco: non toccarle)
{current_yaml}

## Commenti di Marco
{comments_yaml}

## Compito
Applica i commenti cambiando SOLO le battute commentate. Se per tenere coerente una battuta devi
cambiarne un'altra, elencala in coherence_changes. Commenti sul copione intero: cambia il minimo
indispensabile. Rispetta il numero di parole e tutte le regole. Restituisci solo le battute cambiate
in changes; scenes e news_image solo se cambiano; endings solo se un commento li riguarda.
Rispondi a ogni commento con una frase in answers. Se un commento chiede un registro più leggero o
più pungente, indica il nuovo tone (comico o pungente)."""


def dump(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
