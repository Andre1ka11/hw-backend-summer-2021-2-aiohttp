from dataclasses import dataclass


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    id: int | None
    title: str
    theme_id: int
    answers: list[Answer]