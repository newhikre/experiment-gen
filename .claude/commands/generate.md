---
description: 为指定教材生成配套实验并写入飞书表格
argument-hint: <年级> <数量>
---

用户请求：$ARGUMENTS

立即按以下流程执行，**不要询问用户任何细节**：

1. 从用户请求中解析出「年级」和「数量」
2. 匹配教材文件：`教材/AI教材<年级>.docx`（若文件不存在，用 Glob 在 `教材/` 下查找最接近的一本）
3. 检查 `ANTHROPIC_API_KEY` 环境变量是否存在，若不存在则告知用户设置后重试
4. 运行以下 Python 代码（通过 Bash 工具执行 `python -c`）：

```python
import sys; sys.stdout.reconfigure(encoding='utf-8')
from textbook import parse_textbook
from generator import generate_experiments
from feishu import FeishuBase

book = parse_textbook("<教材路径>")
print(f"年级: {book['grade']}, 课数: {len(book['lessons'])}")
experiments = generate_experiments(book, <数量>)
feishu = FeishuBase("T5WXb4Hx2aRmoUs1fpJcbkFrn8g")
table_id = feishu.get_or_create_table(book["grade"])
feishu.write_experiments(table_id, experiments)
print(f"完成: {len(experiments)} 个实验已写入数据表「{book['grade']}」")
```

5. 运行完毕后，用一句话汇报结果：写入了多少个实验、对应的年级/数据表名称。
