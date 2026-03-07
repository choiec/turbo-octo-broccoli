from __future__ import annotations

from enum import Enum


class EnglishSystem(str, Enum):
    grammar = "grammar"
    lexis = "lexis"
    phonology = "phonology"


class CefrLevel(str, Enum):
    a1 = "A1"
    a2 = "A2"
    b1 = "B1"
    b2 = "B2"
    c1 = "C1"
    c2 = "C2"


class Skill(str, Enum):
    reading = "reading"
    writing = "writing"
    listening = "listening"
    speaking = "speaking"
