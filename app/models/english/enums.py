from __future__ import annotations

from enum import Enum


class EnglishSystem(str, Enum):
    grammar = "grammar"
    lexis = "lexis"
    phonology = "phonology"


class CefrLevel(str, Enum):
    a1 = "a1"
    a2 = "a2"
    b1 = "b1"
    b2 = "b2"
    c1 = "c1"
    c2 = "c2"


class Skill(str, Enum):
    reading = "reading"
    writing = "writing"
    listening = "listening"
    speaking = "speaking"


class GradeTag(str, Enum):
    grade_10 = "grade_10"
    grade_11 = "grade_11"
    grade_12 = "grade_12"
    adult = "adult"


class SessionType(str, Enum):
    regular = "regular"
    exam_prep = "exam_prep"


class RecallSource(str, Enum):
    recall = "recall"
    direct = "direct"


class ExamType(str, Enum):
    midterm = "midterm"
    final = "final"
    suneung_mock = "suneung_mock"
    suneung = "suneung"


class QuestionType(str, Enum):
    main_idea = "main_idea"
    title = "title"
    detail = "detail"
    inference = "inference"
    vocabulary = "vocabulary"
    grammar = "grammar"
    ordering = "ordering"
    insertion = "insertion"
    summary = "summary"
    blank_filling = "blank_filling"
    long_answer = "long_answer"


class RecallEventType(str, Enum):
    chat_recall = "chat_recall"
    quiz_response = "quiz_response"
    manual = "manual"
