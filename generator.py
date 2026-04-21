import json
import math
import anthropic


SYSTEM_PROMPT = """你是一位AI教育课程设计专家，专门为中小学AI课程设计配套实验。
每个实验必须与所给课程内容紧密相关，适合对应年级学生操作，有明确的技术实现方案。
请严格按照JSON格式输出，不要添加任何额外说明。"""

EXPERIMENT_SCHEMA = {
    "实验名称": "简洁吸引人的名称（不超过15字）",
    "实验概述": "2-3句话描述实验目标和核心体验",
    "技术栈": "具体技术工具列表（逗号分隔）",
    "原型": "UI/交互原型描述，包含主要界面区域",
    "实验准备": "所需硬件、软件、数据等准备工作",
    "实验步骤": "分步骤描述，每步以数字开头",
    "实验成效（问题与作业）": "2-3个思考问题 + 1个课后作业，格式：问题：...；作业：...",
    "单元与课次": "第X单元 第X课 课程名称",
}


def _build_prompt(lesson: dict, grade: str, n: int) -> str:
    schema_str = json.dumps(EXPERIMENT_SCHEMA, ensure_ascii=False, indent=2)
    return f"""请为以下课程设计 {n} 个配套实验，每个实验输出一个JSON对象。

年级：{grade}
单元：{lesson['unit']}
课次：{lesson['lesson']}
课程内容摘要：
{lesson['content']}

每个实验的JSON字段：
{schema_str}

输出格式（{n}个实验组成的JSON数组）：
[
  {{ ... }},
  {{ ... }}
]"""


def generate_experiments(book: dict, total_n: int, api_key: str | None = None) -> list[dict]:
    client = anthropic.Anthropic(api_key=api_key)
    lessons = book["lessons"]
    grade = book["grade"]

    if not lessons:
        return []

    # Distribute n experiments across lessons
    per_lesson = max(1, math.ceil(total_n / len(lessons)))
    remaining = total_n
    results = []

    for lesson in lessons:
        if remaining <= 0:
            break
        count = min(per_lesson, remaining)
        print(f"  生成 {lesson['lesson']} × {count} 个实验...")

        prompt = _build_prompt(lesson, grade, count)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        # Extract JSON array from response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        experiments = json.loads(raw[start:end])
        results.extend(experiments[:count])
        remaining -= count

    return results[:total_n]
