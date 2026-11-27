"""Shared data models for the news feature (data-model.md)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Category = Literal[
    "current-affairs", "sport", "culture", "entertainment", "music", "lifestyle", "oddities", "good-news", "satire"
]
StoryCategory = Literal[
    "current-affairs", "sport", "culture", "entertainment", "music", "lifestyle", "oddities", "good-news"
]
# Light categories: one approved starting source is enough (spec 001 A1, FR-004).
LIGHT_CATEGORIES = frozenset({"entertainment", "music", "lifestyle", "oddities"})
# Flags that keep the two-groups rule even in light categories.
SENSITIVE_FLAGS = frozenset({"politics", "legal", "health", "finance"})
Tone = Literal["comico", "pungente"]
Role = Literal["starting", "confirmation-only", "inspiration-only"]
Excluded = Literal["crime", "tragedy", "harm", "clickbait", "rumour", "sponsored", "social-only"]
Flag = Literal["politics", "health", "legal", "finance"]
StoryStatus = Literal["candidate", "chosen", "rejected", "used", "follow-up"]

CATEGORY_IT = {
    "current-affairs": "attualità",
    "sport": "sport",
    "culture": "cultura",
    "entertainment": "spettacolo",
    "music": "musica",
    "lifestyle": "lifestyle",
    "oddities": "curiosità",
    "good-news": "buone notizie",
    "satire": "satira",
}


class Source(BaseModel):
    id: str
    name: str
    category: Category
    group: str
    role: Role = "starting"
    home: Optional[str] = None
    feeds: list[str] = Field(default_factory=list)
    manual: bool = False
    last_check: Optional[str] = None

    @property
    def effective_role(self) -> Role:
        return "inspiration-only" if self.category == "satire" else self.role


class FeedItem(BaseModel):
    item_id: str
    source_id: str
    title: str
    summary_snippet: str = ""
    url: str
    published_at: Optional[datetime] = None
    agency: Optional[str] = None


# Model outputs ---------------------------------------------------------------


class TriageGroup(BaseModel):
    item_ids: list[str]
    category: StoryCategory
    excluded: Optional[Excluded] = None
    excluded_reason: Optional[str] = None
    positive: bool = False


class TriageResult(BaseModel):
    groups: list[TriageGroup]


class EditorialStory(BaseModel):
    group_index: int
    title: str
    summary: str
    importance: int = Field(ge=1, le=5)
    importance_reason: str
    comic_potential: int = Field(ge=1, le=5)
    comic_reason: str
    clarity: int = Field(default=3, ge=1, le=5)
    clarity_reason: str = ""
    satirical_potential: int = Field(default=1, ge=1, le=5)
    satirical_reason: str = ""
    sensitive: bool = False
    flags: list[Flag] = Field(default_factory=list)
    follow_up_of: Optional[str] = None
    already_covered: bool = False


class EditorialResult(BaseModel):
    stories: list[EditorialStory]


class WeeklyPick(BaseModel):
    story_id: str
    weekly_importance: int = Field(ge=1, le=5)
    reason: str


class WeeklyResult(BaseModel):
    picks: list[WeeklyPick]
