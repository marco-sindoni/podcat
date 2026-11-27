"""Deterministic verification: the two-groups rule (research R4, FR-004) and the Thursday rule (FR-009).

On Thursdays ("Giovedì buone notizie") one approved, non-satire starting source is enough,
because the story only has to be a real positive fact, not breaking news. The same holds every day
for light categories (spec 001 A1, research R15); a light story flagged politics, legal, health or
finance is sent back to the two-groups rule after the editorial pass (pipeline).
"""

from __future__ import annotations

from dataclasses import dataclass

from podcat.news.models import LIGHT_CATEGORIES, FeedItem, Source, TriageGroup


@dataclass
class Verdict:
    group: TriageGroup
    items: list[FeedItem]
    effective_groups: list[str]
    verified: bool
    reason: str | None = None  # Italian reason when not verified


def effective_group(item: FeedItem, source: Source) -> str:
    """An item crediting an agency counts as that agency, whatever outlet published it.

    Agency ids in config/agencies.yaml match the `group` of the agencies' own sources
    (ansa, agi, adnkronos, reuters), so an ANSA item and an ANSA wire count once.
    """
    return item.agency or source.group


def verify_group(
    group: TriageGroup,
    items: dict[str, FeedItem],
    sources: dict[str, Source],
    thursday: bool = False,
) -> Verdict:
    members = [items[i] for i in group.item_ids if i in items]
    counted = [m for m in members if sources[m.source_id].effective_role != "inspiration-only"]
    groups = sorted({effective_group(m, sources[m.source_id]) for m in counted})

    def fail(reason: str) -> Verdict:
        return Verdict(group, members, groups, False, reason)

    if group.excluded:
        return fail(f"argomento escluso ({group.excluded}): {group.excluded_reason or ''}".strip())
    if not counted:
        return fail("solo fonti satiriche")
    if thursday and not group.positive:
        return fail("giovedì: non è una buona notizia")
    one_source_ok = thursday or group.category in LIGHT_CATEGORIES
    if len(groups) < 2 and not one_source_ok:
        return fail("una sola fonte (o la stessa agenzia ripresa da più testate)")
    if not any(sources[m.source_id].effective_role == "starting" for m in counted):
        return fail("solo fonti di conferma, nessuna fonte di partenza")
    return Verdict(group, members, groups, True)


def verify_all(
    groups: list[TriageGroup],
    items: dict[str, FeedItem],
    sources: dict[str, Source],
    thursday: bool = False,
) -> list[Verdict]:
    return [verify_group(g, items, sources, thursday) for g in groups]
