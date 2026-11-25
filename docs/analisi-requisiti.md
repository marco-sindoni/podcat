# Podcat – Analisi e bozza requisiti

> Snapshot exported on 2026-11-25 from the Claude Doc https://claude.ai/artifact/WKEYiyksxVdkVquzMk6U5f (revision 58). The live doc may change; decisions that matter are also in the constitution and `docs/decisions.md`. The pipeline diagram is not included in this export.

Nov 25, 2026 · @Marco

## Sintesi

Podcat si può automatizzare quasi tutto a un costo stimato tra 20 e 50 USD al mese, ma **non con CapCut via API**: CapCut non ha un'API pubblica ufficiale e i suoi termini vietano l'automazione. Propongo di usare il modello video di CapCut (Seedance) o alternative più economiche tramite API ufficiali, e di montare tutto in automatico con FFmpeg.

**Decisione del 25/11/2026: si parte con una fase 1 manuale.** Il software raccoglie le notizie e scrive i copioni; ogni copione arriva a Marco come documento commentabile per la revisione editoriale. Il copione approvato, con le indicazioni di scena, si incolla in CapCut, dove Marco crea e scarica il video finale. Voci, clip, montaggio e sottotitoli automatici passano alla fase 2.

Le raccomandazioni principali:

- **Framework spec-driven:** GitHub Spec Kit, l'unico con una vera "costituzione" e integrazione nativa con Claude Code.
- **Stack:** Python 3.12 con uv, CLI a riga di comando, FFmpeg per montaggio e sottotitoli, Claude per i testi, ElevenLabs per le voci, Fotor OpenAPI per le immagini di riferimento.
- **Video a basso costo:** una libreria riusabile di clip per ogni gatto (parla, ride, sbuffa, ascolta) generata una volta sola, più poche clip nuove per puntata. Il costo marginale di un reel scende quasi a zero.
- **Policy YouTube:** il rischio vero non è l'AI in sé ma il contenuto "generico o ripetitivo". La difesa è la scrittura: ogni puntata deve avere battute, angolo e arco narrativo propri.
- **Tracciamento:** file Markdown con intestazione YAML in una cartella `tracking/` del repo; gli asset in una cartella esterna indicata da una variabile d'ambiente.

Le decisioni che servono da te sono nell'ultima sezione, "Ipotesi e domande aperte". Le più urgenti: lingua del canale, stile visivo dei gatti, se accetti di rinunciare all'automazione di CapCut, e dove creare il repository.

## Policy YouTube su AI e monetizzazione

YouTube monetizza i video AI, ma esclude dal Programma Partner i canali con troppo contenuto "inautentico". La tua intuizione è corretta: conta la sostanza editoriale, non lo strumento.

**Contenuto inautentico.** Il 15 luglio 2025 la policy "repetitious content" è stata rinominata "inauthentic content" ([policy ufficiale](https://support.google.com/youtube/answer/1311392?hl=en)). Il criterio: la sostanza di ogni video deve essere "materially varied" e dare valore creativo o educativo. È ammesso riusare la stessa sigla e chiusura se il contenuto principale cambia. A luglio 2026 YouTube ha chiarito tre categorie non monetizzabili ([TechCrunch, 20/07/2026](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/); [Tubefilter, 13/07/2026](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/)):

1. Contenuti generici, ripetitivi o da template, facili da produrre in serie con AI, con poca variazione tra un video e l'altro.
2. Contenuti "sgradevoli" o angoscianti fatti per inseguire visualizzazioni.
3. Persone AI che si presentano come esperti umani su temi sensibili (salute, legge, finanza, politica).

La valutazione è a livello di canale: "any YouTube channel that has too much of any of these three types of content will not be able to monetize".

**Contenuto riutilizzato.** Prendere materiale altrui è ammesso solo con una "meaningful difference", per esempio commento critico o reazione. Vale anche con il permesso dell'autore. Per Podcat significa: niente clip o foto prese dalle testate, solo i fatti riscritti e commentati dai gatti.

**Etichetta AI.** La dichiarazione è obbligatoria solo per contenuti AI che sembrano reali ([Disclosing use of GenAI content](https://support.google.com/youtube/answer/14328491?hl=en)). Quattro gatti antropomorfi in stile cartoon rientrano negli esempi "non realistici" esenti. YouTube precisa che dichiarare "alone won't limit a video's audience or impact its eligibility to earn money", mentre non dichiarare quando serve può portare alla sospensione dal Programma Partner.

**Cosa ne deriva per Podcat:**

- Il rischio principale è la categoria 1: un reel quotidiano con stessa scena e stessa struttura può sembrare un template. Ogni puntata deve avere battute originali, un punto di vista e un piccolo arco narrativo.
- I gatti non devono mai sembrare esperti che danno consigli su salute, soldi o legge. Il tono satirico e l'aspetto cartoon aiutano.
- Propongo di attivare comunque la voce "AI use" in YouTube Studio: costa nulla e azzera il rischio.
- Non generare mai immagini o voci realistiche di persone reali citate nelle notizie.

Ipotesi da verificare: alcuni blog parlano di soglie del Programma Partner raddoppiate dal 2027 (8.000 ore di visualizzazione). Non l'ho trovato su fonti ufficiali YouTube, quindi non lo considero.

## Framework spec-driven

Raccomando **GitHub Spec Kit**: è l'unico dei principali framework con un file di costituzione esplicito, si integra con Claude Code e è pensato per progetti nuovi come Podcat.

| Framework | Licenza | Costituzione | Claude Code | Peso (file creati all'init) | Adatto a |
| --- | --- | --- | --- | --- | --- |
| [GitHub Spec Kit](https://www.testmuai.com/blog/spec-driven-development-tools/) | MIT, v1.3.1 (nov 2026) | Sì, `/speckit-constitution` | Sì, `specify init --integration claude` | 29 | Progetti nuovi |
| [OpenSpec](https://www.testmuai.com/blog/spec-driven-development-tools/) | MIT, v1.16.0 | No, solo un file di convenzioni | Sì | 15 | Codice esistente, modifiche incrementali |
| [BMAD](https://securityboulevard.com/2026/06/7-spec-driven-development-tools-spec-kit-kiro-openspec-tessl-more/) | MIT, v6.12.4 | No | Sì | 235 | Prodotti grandi con molti ruoli |
| [Kiro](https://securityboulevard.com/2026/06/7-spec-driven-development-tools-spec-kit-kiro-openspec-tessl-more/) | Proprietaria, da 20 USD/mese | No | No, ha un IDE suo | n/d | Chi usa l'IDE Kiro |

**Come funziona Spec Kit per Podcat.** Il ciclo è costituzione, specifica, piano, task, implementazione. Ogni funzionalità (per esempio "raccolta news" o "montaggio reel") ha una cartella `specs/NNN-nome/` con `spec.md`, `plan.md`, `research.md` e `tasks.md`. Le scelte che prendiamo qui finiscono nella costituzione e nei `research.md`, così ogni decisione resta tracciata nel repo.

Alternativa se Spec Kit ti sembra troppo pesante: OpenSpec, più leggero, ma la costituzione andrebbe tenuta a mano in un file a parte.

## Stack tecnologico consigliato

Propongo un'applicazione Python a riga di comando, senza server e senza database, che gira sul tuo computer o in cloud.

| Componente | Scelta | Perché |
| --- | --- | --- |
| Linguaggio | Python 3.12, gestito con `uv` | Ecosistema migliore per AI, audio e video; Spec Kit richiede già Python 3.11+ |
| Interfaccia | CLI con Typer (`podcat news`, `podcat write`, `podcat render`...) | Ogni passo si lancia e si ripete da solo |
| Modelli dati | Pydantic, salvati come YAML nei file Markdown | Struttura validata senza database |
| Testi | Claude via API (Sonnet 5.5 per le bozze, Opus 5.5 per la revisione finale) | Qualità della scrittura comica; costo di pochi centesimi a puntata |
| News | Feed RSS di testate italiane e internazionali | Gratuito, stabile, senza scraping |
| Voci | ElevenLabs API, una voce progettata e salvata per gatto | Italiano supportato, Flash a [0,04 USD ogni 1.000 caratteri](https://elevenlabs.io/pricing/api), restituisce anche i tempi parola per parola |
| Immagini di riferimento | [Fotor OpenAPI](https://docs.fotor.com/) con immagini di riferimento per la coerenza | Hai già l'account; l'API supporta esplicitamente "character consistency" |
| Clip video | Adattatore verso un fornitore API (fal.ai, WaveSpeed, BytePlus) | Si cambia modello senza toccare il resto |
| Montaggio | FFmpeg | Concatena scene, sigla, audio e sottotitoli; gratuito e scriptabile |
| Sottotitoli | File ASS generati dai tempi delle parole, impressi nel video | Sempre presenti, anche dove i sottotitoli YouTube non si vedono |
| Test | pytest | Standard |

Ipotesi: il codice gira sul tuo computer, nella cartella `/home/marco/Projects/podcat` che vedo già collegata. Le chiavi API stanno in un file `.env` mai versionato.

## CapCut, modelli video e alternative economiche

CapCut non offre un'API pubblica per montare o generare video, e i suoi termini vietano l'automazione. Il suo modello video, Seedance di ByteDance, è invece raggiungibile via API ufficiali di terze parti.

**CapCut via API: cosa esiste davvero.**

- Nessuna API ufficiale: "ByteDance publishes no editing or rendering API for CapCut and no developer portal" ([Voyager, 23/10/2026](https://voyager.so/resources/apps/capcut)).
- Gli strumenti della community modificano i file di progetto di CapCut decodificati a mano, non esportano senza interfaccia e si rompono a ogni aggiornamento. I termini vietano "reverse engineering and automated interaction".
- Servizi come [useapi.net](https://github.com/useapi/dreamina-api) pilotano il tuo account Dreamina/CapCut personale a 15 USD al mese. È la via più economica sulla carta ma rischi il blocco dell'account. La sconsiglio.
- Seedance 2.5 sarà disponibile via API ufficiale su BytePlus ModelArk ([CapCut, 07/08/2026](https://www.capcut.com/resource/seedance-2-5-api-latest-updates-and-capcut-workflows)); Seedance 2.0 è già su fornitori come [Atlas Cloud](https://www.atlascloud.ai/blog/tips/seedance-2.0-complete-guide) a 0,08-0,10 USD al secondo.

Decisione (25/11/2026): in fase 1 i video si fanno a mano in CapCut, partendo dal copione approvato. L'automazione con API video e FFmpeg resta per la fase 2.

**Modelli video a confronto (720p, prezzi da [GenRates](https://www.genrates.com/), verificati ad agosto 2026).**

| Modello | Fornitore | USD al secondo | Da immagine | Audio nativo |
| --- | --- | --- | --- | --- |
| LTX-2 (Lightricks) | WaveSpeed | 0,016 | Sì | Sì |
| HunyuanVideo 1.5 (Tencent) | WaveSpeed | 0,040 (0,020 a 480p) | Sì | No |
| Hailuo 2.3 (MiniMax) | PiAPI | 0,027-0,038 | Sì | Non indicato |
| Veo 3.1 Lite (Google) | Vertex AI | 0,030 (0,050 con audio) | Non indicato | Opzionale |
| PixVerse V6 | fal.ai | 0,045 | Sì | Opzionale |
| Vidu Q3 | Vidu | 0,055 | Sì | Sì |
| Kling 3.0 | fal.ai | 0,084 | Sì | Opzionale |
| Seedance 2.0 (il modello di CapCut) | WaveSpeed | 0,10 | Sì | Sì |

I prezzi cambiano spesso: li riverifico prima di scegliere. L'audio nativo dei modelli non ci serve, perché genererebbe voci sempre diverse. Usiamo clip mute e sovrapponiamo le voci fisse di ElevenLabs.

**Il vero risparmio è nell'approccio, non nel modello.** Il volume mensile previsto è di circa 1.380 secondi di video (30 reel da 30 s più 4 puntate da 120 s).

- Generare tutto ogni volta, con un tentativo scartato ogni due: da circa 45 USD al mese (LTX-2) a 275 USD (Seedance 2.0).
- Libreria riusabile: una volta sola si generano circa 80 clip da 5 secondi per gatto e inquadratura (parla, ride, sbuffa, ascolta, piano largo della taverna), costo una tantum di 15-80 USD. Poi ogni puntata usa la libreria più circa 10 secondi di scene nuove (una gag, un oggetto legato alla notizia). Costo mensile stimato 15-45 USD con modelli economici.

La libreria garantisce anche la coerenza visiva. Le scene nuove a ogni puntata servono contro il rischio "template" di YouTube.

**Un'immagine dedicata per ogni notizia (decisione del 25/11/2026).** Oltre alla libreria, ogni puntata ha almeno un'immagine creata apposta per la notizia con Fotor. In fase 1 il software scrive il prompt e Marco crea l'immagine a mano. Serve contro la ripetitività e rende ogni puntata riconoscibile. Tre modi per metterla in scena, usati a rotazione: due video consecutivi non usano mai lo stesso modo (la regola vale tra reel e puntata settimanale, in ordine di pubblicazione). La scheda della puntata registra il modo usato e il software sceglie il successivo.

1. **La TV della taverna:** sopra il camino c'è un vecchio televisore a tubo che mostra l'immagine della notizia; i gatti si girano a guardarla e uno la commenta. È un elemento fisso del set, quindi coerente, ma il contenuto cambia sempre.
2. **Lo stacco a tutto schermo:** l'immagine occupa lo schermo per 2-3 secondi con un leggero zoom, mentre si sente la battuta di un gatto fuori campo.
3. **L'oggetto in scena:** un gatto tiene in mano un giornale o una foto con l'immagine, o la immagina in un fumetto sopra la testa.

Regole per i prompt: stile coerente con la taverna, nessun volto realistico di persone reali, nessun logo o marchio, nessuna foto ripresa dalle testate.

**Labiale.** Con clip mute il gatto che parla muove la bocca in modo generico, non sincronizzato. Per Podcat in stile cartoon lo considero accettabile. Un labiale vero richiede modelli guidati dall'audio, più costosi: lo lascerei come miglioramento futuro.

## Coerenza di personaggi, taverna e voci

La coerenza nasce da una "bibbia di produzione" versionata nel repo e da asset di riferimento creati una volta e mai rigenerati.

**Personaggi.** Ogni gatto ha un file `bible/characters/<nome>.md` con:

- aspetto fisso: razza, colore del manto, occhi, abiti grunge (camicia di flanella, jeans strappati, anfibi, beanie...), poltrona assegnata;
- descrizione testuale standard, la stessa riusata in ogni prompt di immagine e video;
- personalità, tic verbali, temi preferiti, rapporti con gli altri tre;
- voce: ID della voce ElevenLabs e parametri fissi (stabilità, velocità);
- registro dell'evoluzione: cosa è successo nelle puntate (un tormentone nato, una rivalità), che l'autore dei testi rilegge prima di scrivere.

**Immagini di riferimento con Fotor.** Per ogni gatto un "model sheet": fronte, tre quarti, profilo, e 4-6 espressioni. Per la taverna: piano largo con le quattro poltrone, più un'inquadratura per poltrona. L'API Fotor accetta immagini di riferimento proprio per mantenere lo stesso personaggio. Una volta approvate da te, queste immagini diventano la prima immagine di ogni clip video (generazione da immagine), così il modello parte sempre dallo stesso gatto nello stesso posto.

**Voci.** Quattro voci create con il Voice Design di ElevenLabs e salvate: stesso ID e stessi parametri per sempre. Non si usano le voci native dei modelli video.

**Asset riusabili.** Sigla iniziale e finale, stacchetti tra una notizia e l'altra, cartello "breaking news", musica di sottofondo con licenza libera, la libreria di clip per gatto. Sono registrati nel tracciamento e salvati fuori dal repo.

**Sottotitoli sempre presenti.** Impressi nel video, con colore diverso per ogni gatto, massimo due righe, posizionati sopra la zona coperta dall'interfaccia di Shorts. In più si carica il file SRT su YouTube per l'accessibilità e la ricerca.

Deciso il 25/11/2026: stile visivo cartoon 3D morbido, tipo film d'animazione. È più coerente tra una generazione e l'altra del fotorealismo, ed è esente dall'obbligo di etichetta AI.

## Pipeline di produzione

Ogni passo è un comando della CLI e aggiorna la scheda della puntata in `tracking/`. Tu intervieni in due punti: approvi il copione e approvi il video finale.

*[Diagramma: pipeline di una puntata, 8 passi, 1 approvazione — vedi il Claude Doc originale]*

Voci e clip si preparano in parallelo; il montaggio unisce tutto e imprime i sottotitoli. Un copione bocciato torna all'autore con le tue note, prima di spendere un centesimo in video.

In fase 1 la pipeline automatica si ferma al copione approvato: voci, clip, montaggio e sottotitoli si fanno a mano in CapCut, e la scheda della puntata registra il video scaricato.

## Tracciamento in Markdown e asset fuori da git

Niente database: ogni oggetto è un file Markdown con intestazione YAML, leggibile da te e dal codice. Gli asset vivono in una cartella esterna indicata dalla variabile `PODCAT_ASSETS_DIR`.

```
podcat/                      # repository git
  .specify/memory/constitution.md
  specs/                     # specifiche Spec Kit
  bible/                     # personaggi, taverna, stile, linee editoriali
  tracking/
    episodes/2026-12-01-daily.md
    assets/sigla-v1.md
    news/2026-12-01.md
    INDEX.md                 # generato dalla CLI
  src/podcat/

$PODCAT_ASSETS_DIR/          # fuori da git
  reference/  library/  episodes/2026-12-01-daily/  music/  intro/
```

**Scheda puntata** (`tracking/episodes/`): tipo (giornaliera o settimanale), data, stato (bozza, testo approvato, montato, pubblicato), notizie usate con link alla fonte, testo finale, elenco scene con durata, clip di libreria o nuova, modello e prompt usati, costi per voce, link YouTube.

**Scheda asset** (`tracking/assets/`): tipo, percorso relativo dentro `PODCAT_ASSETS_DIR`, impronta SHA-256 per riconoscere file spostati o modificati, origine (Fotor, modello video, manuale), prompt, licenza, puntate in cui è stato usato.

**Registro notizie** (`tracking/news/`): le notizie raccolte ogni giorno, quelle scelte e quelle scartate, per non ripetere lo stesso argomento.

Il file `INDEX.md` riassume puntate e costi del mese ed è rigenerato dalla CLI. Se un giorno i file diventassero troppi, si potrà passare a SQLite senza cambiare il formato delle schede.

Ipotesi: la cartella asset sta sul tuo disco, con un backup su un cloud a tua scelta (Google Drive, Dropbox o simili).

## Bozza della costituzione

Questo testo diventerà `.specify/memory/constitution.md`, scritto in inglese come il resto del repo. Qui lo riassumo in italiano per la tua approvazione.

**Identità del progetto**

1. Nome: Podcat. Sottotitolo: "Chiacchiere tra quattro gatti".
2. Formato: quattro gatti grunge in una taverna dalle luci calde, su quattro poltrone di pelle marrone, commentano notizie di attualità, sport, cultura e spettacolo con ironia, sarcasmo e spirito.
3. Uscite: un reel giornaliero di circa 30 secondi e una puntata settimanale di circa 2 minuti, sempre in formato verticale 9:16.
4. Voce autoriale: i testi si scrivono come un autore esperto di spettacolo e comicità. L'intrattenimento viene prima della spettacolarità visiva.

**Lingua**

5. Tutto il codice, i nomi, i commenti, i messaggi di commit e la documentazione tecnica sono in inglese.
6. In chat con Marco si parla sempre in italiano.
7. Il canale è solo in italiano: voci, sottotitoli, titoli, descrizioni e testi a schermo.

**Principi editoriali**

8. Ogni puntata ha battute, angolo e arco narrativo originali, e almeno un'immagine creata apposta per la notizia, messa in scena in un modo diverso da quello del video precedente; niente puntate fotocopia.
9. Si commentano i fatti, mai si copiano testi, immagini o video delle testate. Ogni notizia ha la fonte registrata.
10. Nessuna immagine o voce realistica di persone reali. Niente consigli su salute, finanza o legge presentati come da esperti.
11. La satira colpisce i fatti e i potenti, non categorie deboli. Niente contenuti violenti o angoscianti per fare visualizzazioni.
12. Nessuna pubblicazione senza approvazione umana del testo e del video finale.

**Coerenza**

13. Personaggi, taverna, stile e voci sono definiti nella bibbia di produzione e cambiano solo con una modifica approvata.
14. Ogni clip parte dalle immagini di riferimento approvate; le voci usano ID e parametri fissi.
15. La personalità dei gatti evolve solo tramite il registro dell'evoluzione.

**Produzione**

16. I sottotitoli sono sempre presenti, impressi nel video.
17. Il costo viene prima della qualità: si sceglie il modello più economico accettabile, si riusa la libreria prima di generare. Ogni puntata registra il proprio costo; il tetto mensile è di 50 USD per tutti i servizi.
18. Ogni fornitore esterno (testi, voci, immagini, video) è dietro un'interfaccia sostituibile.
19. Solo API ufficiali e conformi ai termini d'uso: niente automazioni di account personali.

**Dati e repository**

20. Nessun database: il tracciamento è in file Markdown con intestazione YAML in `tracking/`.
21. Gli asset binari stanno fuori dal repo, in `PODCAT_ASSETS_DIR`. Le chiavi API stanno in `.env`, mai versionato.
22. Ogni decisione di progetto è tracciata con Spec Kit (costituzione, spec, research).

**Sviluppo**

23. Python 3.12 con uv, CLI Typer, test con pytest. Ogni passo della pipeline è un comando ripetibile e idempotente.
24. Si parte dal minimo che funziona; niente infrastruttura prima che serva.

## Bozza dei requisiti

I requisiti sono numerati per poterli citare nelle specifiche. Quelli marcati "(v2)" li proporrei dopo la prima versione.

**Come si tracciano i requisiti futuri.** Tutto ciò che è marcato "(v2)" o "(fase 2)" va in un file `BACKLOG.md` alla radice del repo: una riga per voce con ID, titolo, fase, stato (idea, pronta, in spec, fatta) e il link alla spec quando esiste. Quando una voce viene scelta, diventa una spec Spec Kit (`/speckit-specify`) e la riga punta alla sua cartella `specs/NNN-nome/`. Così il backlog resta in Markdown, versionato con il codice, senza strumenti esterni. Se un giorno servisse una bacheca, le stesse voci si possono trasformare in issue GitHub.

Voci già previste nel backlog: voci automatiche (RF-06), clip automatiche (RF-07), montaggio FFmpeg con sottotitoli colorati (RF-08, RF-09), caricamento su YouTube (RF-14), esecuzione pianificata (RF-15), labiale vero sincronizzato all'audio.

**Requisiti funzionali**

| ID | Requisito |
| --- | --- |
| RF-01 | Raccogliere ogni giorno le notizie da un elenco configurabile di feed RSS, per categoria (attualità, sport, cultura, spettacolo). |
| RF-02 | Proporre 3-5 notizie candidate con un punteggio di "potenziale comico" ed escludere argomenti già trattati o vietati dalla costituzione. |
| RF-03 | Scrivere il copione del reel (circa 30 s, 70-90 parole) e della puntata settimanale (circa 2 min, 280-320 parole) con battute assegnate ai gatti secondo personalità e registro dell'evoluzione. |
| RF-04 | Revisione automatica del copione (secondo passaggio da "capo autore"), poi pubblicazione del copione come documento commentabile: Marco commenta battute e scene, il copione si aggiorna finché non lo approva. |
| RF-05 | Dividere il copione in scene: chi parla, inquadratura, clip di libreria o nuova, durata. |
| RF-06 | (fase 2) Generare l'audio di ogni battuta con la voce fissa del gatto e i tempi parola per parola. |
| RF-07 | (fase 2) Generare solo le clip nuove richieste, partendo dalle immagini di riferimento, tramite il fornitore video configurato. |
| RF-08 | (fase 2) Montare con FFmpeg: sigla, scene, stacchetti, audio, musica, chiusura; formato 9:16 per tutti i video. |
| RF-09 | Sottotitoli sempre presenti: in fase 1 con i sottotitoli automatici di CapCut, in fase 2 impressi da FFmpeg con colore per gatto e file SRT. |
| RF-10 | Creare e aggiornare le schede di tracciamento di puntate, asset e notizie, con i costi. |
| RF-11 | Gestire la bibbia di produzione: profili dei gatti, registro dell'evoluzione, immagini di riferimento, voci. |
| RF-12 | Creare una tantum gli asset di base: immagini di riferimento (Fotor), libreria di clip, voci, sigla. |
| RF-13 | Proporre titolo, descrizione e hashtag per YouTube. In fase 1 produrre anche un "pacchetto CapCut" pronto da incollare: battute per gatto in ordine, indicazioni di scena, prompt visivi per ogni scena e il prompt Fotor dell'immagine dedicata alla notizia, con il punto del video in cui compare e la battuta che la commenta. |
| RF-14 (v2) | Caricare su YouTube via API come bozza privata, con l'etichetta "AI use" attiva. |
| RF-15 (v2) | Esecuzione pianificata giornaliera fino al punto di approvazione, con notifica. |

**Requisiti non funzionali**

| ID | Requisito |
| --- | --- |
| RNF-01 | Costo medio per reel sotto 1 USD e costo mensile sotto un tetto configurabile, fissato a 50 USD; il comando si ferma se il tetto viene superato. |
| RNF-02 | Dalla notizia scelta al video montato in meno di 15 minuti, esclusi i tempi di approvazione. |
| RNF-03 | Ogni passo è ripetibile: rilanciarlo non rigenera (e non ripaga) ciò che esiste già. |
| RNF-04 | Nessun asset binario nel repo; nessuna chiave API nel repo. |
| RNF-05 | Fornitori sostituibili cambiando solo la configurazione. |
| RNF-06 | Codice e documentazione tecnica in inglese; contenuti del canale solo in italiano. |
| RNF-07 | Conformità alle policy YouTube e ai termini d'uso di tutti i fornitori. |
| RNF-08 | Funziona su Linux (il tuo computer) con Python 3.12 e FFmpeg installati. |

## I quattro gatti

Tre gatti e una gatta con nomi presi dall'immaginario grunge, senza nomi di musicisti, band o marchi reali (costituzione, principio III). Approvati da Marco il 25/11/2026.

| Nome | Sesso | Da dove viene | Ruolo nella chiacchierata | Aspetto |
| --- | --- | --- | --- | --- |
| Flanella | F | La camicia a quadri, simbolo del grunge | Guida la conversazione; sembra calma, poi smonta i potenti con una frase. Sarcastica e tagliente, ha sempre l'ultima parola | Tigrata rossa, camicia di flanella a quadri, collare borchiato |
| Fuzz | M | Il pedale distorsore | La testa calda: si indigna per tutto e "distorce" la notizia fino all'assurdo | Nero, pelo arruffato, jeans strappati |
| Feedback | M | Il fischio dell'amplificatore | Lento e filosofico: sembra assente, poi piazza la battuta finale | Grigio e grosso, beanie, sempre mezzo addormentato |
| Vinile | M | I dischi in vinile | Il nostalgico brontolone: "ai miei tempi la musica era vera", paragona tutto agli anni '90; forte su cultura e spettacolo | Bianco a macchie scure, occhiali tondi, il più anziano |

Alternative: Riot (F, dal movimento riot grrrl, al posto di Flanella), Anfibio (M, gli scarponi), Larsen (M, il nome italiano dell'effetto feedback).

Ogni gatto ha la sua scheda in `bible/characters/` con carattere, aspetto, tic verbali, voce CapCut, colore dei sottotitoli e registro dell'evoluzione.

## Ipotesi e domande aperte

Le ipotesi qui sotto sono già nella bozza; se ne cambi una, aggiorno costituzione e requisiti.

**Domande per te**

- [x] **Lingua del canale:** deciso il 25/11: solo italiano.
- [x] **CapCut:** deciso il 25/11: fase 1 manuale in CapCut partendo dal copione approvato, automazione in fase 2.
- [x] **Stile visivo:** deciso il 25/11: cartoon 3D morbido.
- [x] **Labiale:** deciso il 25/11: labiale generico all'inizio, labiale vero nel backlog.
- [x] **Formato settimanale:** deciso il 25/11: sempre 9:16 verticale.
- [x] **Budget:** deciso il 25/11: tetto di 50 USD al mese per tutti i servizi.
- [x] **Repository:** repo GitHub privato `podcat` creato il 25/11 (marco-sindoni/podcat), con Spec Kit e costituzione su main, clonato in Projects/podcat.
- [x] **Dove gira:** deciso il 25/11: codice in `/home/marco/Projects/podcat`, asset in `/home/marco/Projects/podcat-assets`.
- [x] **Fotor:** Fotor Pro annuale, valido fino al 21/10/2027 (non si rinnova da solo). In fase 1 le immagini si fanno a mano; la chiave API della Developer Platform serve solo in fase 2 e usa token a parte.
- [x] **ElevenLabs:** deciso il 25/11: in fase 1 si usano quattro voci fisse di CapCut, una per gatto, registrate nella bibbia; ElevenLabs solo in fase 2 (piano Starter, 6 USD al mese: il piano gratuito non ha licenza commerciale).
- [x] **Nomi dei gatti:** deciso il 25/11: Flanella, Fuzz, Feedback e Vinile (sezione "I quattro gatti").
- [ ] **Fonti di news:** testate preferite o da evitare? Temi esclusi (per esempio politica o cronaca nera)?

**Ipotesi tecniche da verificare in fase di piano**

- I prezzi dei modelli video sono di agosto 2026 e vanno riverificati.
- Seedance 2.5 via BytePlus ModelArk: risultava "in arrivo" ad agosto 2026.
- La qualità dei modelli più economici (LTX-2, Hailuo) con personaggi cartoon va provata con un test su 3-4 clip prima di scegliere.
