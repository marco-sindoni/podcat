# News sources

**Status: APPROVED by Marco on 2026-11-25; sources without a working feed replaced on 2026-11-26.** RSS availability is checked when the news-gathering
feature is planned; a source without a working feed gets a replacement or is read by hand.

## Verification rules

1. A story becomes a candidate only if at least **two approved sources from different publishing
   groups** report it. Outlets republishing the same agency wire count as one source.
2. Every story records all confirming sources with their URLs.
3. Automatically discarded: low-traffic portals, clickbait headlines ("non crederai...", "shock"),
   rumours, sponsored content, stories based only on social media posts.
4. `satire` sources are never a source of facts, never count for rule 1, and their jokes are never
   copied. They show what the internet is already laughing at, so the cats pick a different angle.
5. "Giovedì buone notizie" exception (decided 2026-11-26): on Thursdays the search covers the last
   7 days, and one approved, non-satire starting source is enough for a positive story. Rule 1
   still applies on every other day. Positive outcomes of mourning, deaths, violence or crimes
   against people are excluded on Thursdays, and candidates are ranked by importance plus comic
   potential.

## Topics

- Excluded: crime news (cronaca nera) and tragedies.
- Politics: only as public fact and satire of the powerful; the show never takes a party's side.

## Categories

| Category | Sources |
| --- | --- |
| `current-affairs` | ANSA, AGI, Adnkronos, Corriere della Sera, la Repubblica, La Stampa, Il Sole 24 Ore, Sky TG24, RaiNews, BBC News (world news), Euronews Italiano, Open; Il Post and Il Fatto Quotidiano for cross-checking only |
| `sport` | La Gazzetta dello Sport, Corriere dello Sport, Tuttosport, Sky Sport, Sport Mediaset, RaiSport, OA Sport, ANSA Sport, L'Ultimo Uomo, Sportface |
| `culture` | Corriere della Sera – Cultura (La Lettura), la Repubblica – Cultura (Robinson), Domenica (Il Sole 24 Ore), Internazionale, Il Libraio, Artribune, Finestre sull'Arte, Focus, Wired Italia, Doppiozero |
| `entertainment` | ANSA Cinema e Spettacolo, Comingsoon.it, Ciak, BadTaste.it, Movieplayer, TV Sorrisi e Canzoni, TvBlog, DavideMaggio.it, Variety, Deadline |
| `music` | Rolling Stone Italia, All Music Italia, OndaRock, Rumore, Soundsblog, SentireAscoltare, Rockon, Loudwire, Pitchfork, NME |
| `lifestyle` | Vanity Fair Italia, GQ Italia, Vogue Italia, Elle Italia, Grazia, Cosmopolitan Italia, Gambero Rosso, Dissapore, Dove Viaggi (Corriere), How to Spend It (Il Sole 24 Ore) |
| `good-news` ("Giovedì buone notizie") | Italia che Cambia, Vita.it, Good News Network, Reasons to be Cheerful, Fix the News, The Guardian – The Upside, Good Good Good, The Optimist Daily, YES! Magazine, Our World in Data (for checking numbers) |
| `satire` (inspiration only) | Lercio, Il Vernacoliere, The Onion, The Daily Mash, NewsThump, The Hard Times, The Beaverton, The Shovel, Le Gorafi, Reductress |

Notes:
- Only sources with a working RSS feed are used, so everything is read automatically (Marco,
  2026-11-26: no manual sources). `config/sources.yaml` holds the feeds and publishing groups;
  `podcat sources check` verifies them.
- Il Post and Il Fatto Quotidiano are used only to cross-check, never as starting sources.
- Italian satire lives mostly on social media; only Lercio and Il Vernacoliere have feeds, so the
  category is completed with English and French satire sites (inspiration only).

## Excluded sources

| Source | Reason |
| --- | --- |
| Le Frasi di Osho | Satire too politically aligned (Marco) |
| Fanpage, Reuters, Rockol, Billboard Italia, Positive News | Block automated readers from the cloud; not worked around |
| La Lettura, Robinson (own feeds), National Geographic Italia, MYmovies, Rockit, Eurosport Italia, Condé Nast Traveller, Buone Notizie (Corriere), FIMI | No working feed (section feeds used where available) |
| Spinoza.it, Il Milanese Imbruttito, Il Terzo Segreto di Satira, The Jackal, Kotiomkin | No feed or inactive feed; mostly on social media |
| The Babylon Bee | Satire too politically aligned |
