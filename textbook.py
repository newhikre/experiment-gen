import re
from pathlib import Path
from docx import Document


UNIT_RE = re.compile(r'^第[一二三四五六七八九十百]+单元')
LESSON_RE = re.compile(r'^第[一二三四五六七八九十百]+课')
GRADE_RE = re.compile(r'([一二三四五六七八]年级[上下]册)')


def parse_grade(filepath: str) -> str:
    m = GRADE_RE.search(Path(filepath).name)
    return m.group(1) if m else Path(filepath).stem


def parse_textbook(filepath: str) -> dict:
    doc = Document(filepath)
    grade = parse_grade(filepath)

    lessons = []
    current_unit = ""
    current_lesson = ""
    current_content: list[str] = []

    def flush():
        if current_lesson:
            lessons.append({
                "unit": current_unit,
                "lesson": current_lesson,
                "content": "\n".join(current_content[:60]),  # cap context length
            })

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if UNIT_RE.match(text) and len(text) < 30:
            flush()
            current_unit = text
            current_lesson = ""
            current_content = []
        elif LESSON_RE.match(text) and len(text) < 30:
            flush()
            current_lesson = text
            current_content = []
        elif current_lesson:
            current_content.append(text)

    flush()
    return {"grade": grade, "lessons": lessons}
