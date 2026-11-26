# Tracking file contract

Paths and front matter fields are defined in [data-model.md](../data-model.md). Rules every writer
follows:

- Files are UTF-8 Markdown with a YAML front matter block between `---` lines.
- Writers preserve unknown front matter keys and the body below the table they own, so Marco can add
  notes by hand.
- Marco may edit `picked` or a story `status` by hand; the CLI re-reads files on every command and
  validates them, reporting the file and field on error.
- Example shortlist:

```markdown
---
date: 2026-11-27
kind: daily
good_news_thursday: false
status: proposed
candidates: [2026-11-27-sciopero-treni, 2026-11-27-festival-sanremo-cast, 2026-11-27-record-maratona]
backups: []
picked: null
warning: null
doc_url: null
run_log: tracking/news/runs/2026-11-27-daily.md
cost_usd: 0.011
---

# Notizie candidate – venerdì 27 novembre 2026

| # | Notizia | Categoria | Importanza | Potenziale comico | Fonti |
| --- | --- | --- | --- | --- | --- |
| 1 | ... | attualità | 5 | 3 | ANSA, Corriere, Sky TG24 |
```
