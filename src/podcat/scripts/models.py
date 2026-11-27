"""Script data shapes (data-model.md: Script version, Model outputs)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Cat = Literal["flanella", "fuzz", "vinile", "feedback"]
Mode = Literal["A", "B", "C"]
CATS: tuple[str, ...] = ("fuzz", "flanella", "vinile", "feedback")  # seat order, left to right
CAT_NAMES = {"flanella": "Flanella", "fuzz": "Fuzz", "vinile": "Vinile", "feedback": "Feedback"}
MODE_IT = {
    "A": "modo A (vecchio televisore sopra il camino)",
    "B": "modo B (stacco a tutto schermo)",
    "C": "modo C (gatto con giornale o foto)",
}


class Line(BaseModel):
    n: int = Field(description="Numero della battuta, da 1 in ordine")
    cat: Cat
    text: str
    manual: bool = Field(default=False, description="Corretta a mano da Marco: non toccarla")


class Reaction(BaseModel):
    cat: Cat
    direction: str = Field(description="Faccia o gesto, in italiano, breve")


class Scene(BaseModel):
    n: int
    shot: str = Field(description="Id di inquadratura dalla lista fissa")
    lines: list[int] = Field(description="Numeri delle battute dette in questa scena")
    reactions: list[Reaction] = Field(default_factory=list)
    duration_s: Optional[float] = None


class NewsImage(BaseModel):
    mode: Mode
    scene: int
    comment_line: int
    held_by: Optional[Cat] = None
    subject: str = Field(description="Una frase in italiano sul soggetto dell'immagine")


class Ending(BaseModel):
    feedback: str
    flanella: str


class Draft(BaseModel):
    angle: str
    lines: list[Line]
    scenes: list[Scene]
    news_image: NewsImage


class RoomResult(BaseModel):
    drafts: list[Draft]


class HeadWriterResult(BaseModel):
    chosen_angle: str
    lines: list[Line]
    scenes: list[Scene]
    news_image: NewsImage
    endings: list[Ending] = Field(description="Esattamente 2 finali alternativi")
    notes: list[str]


class FixResult(HeadWriterResult):
    pass


class LineChange(BaseModel):
    n: int = Field(description="Battuta da cambiare; per una battuta nuova, quella dopo cui inserirla")
    cat: Cat
    text: str
    insert_after: bool = False


class Answer(BaseModel):
    comment: str
    answer: str
    changed_lines: list[int] = Field(default_factory=list)


class RevisionResult(BaseModel):
    changes: list[LineChange]
    coherence_changes: list[int] = Field(default_factory=list)
    scenes: Optional[list[Scene]] = None
    news_image: Optional[NewsImage] = None
    endings: Optional[list[Ending]] = None
    answers: list[Answer]
    tone: Optional[Literal["comico", "pungente"]] = None
    notes: list[str] = Field(default_factory=list)


class Version(BaseModel):
    """One saved version (tracking/scripts/<id>/v<N>.md front matter)."""

    version: int
    lines: list[Line]
    scenes: list[Scene]
    news_image: NewsImage
    endings: list[Ending]
    words: int = 0
    duration_s: float = 0.0
    head_writer_notes: list[str] = Field(default_factory=list)
    answers: list[Answer] = Field(default_factory=list)
    coherence_changes: list[int] = Field(default_factory=list)
    chosen_angle: Optional[str] = None
