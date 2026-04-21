---
description: 列出飞书 Base 中现有的所有数据表
---

立即执行，不要询问用户：

```bash
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from feishu import FeishuBase; t = FeishuBase('T5WXb4Hx2aRmoUs1fpJcbkFrn8g').list_tables(); [print(f'{n}: {i}') for n, i in t.items()]"
```

以表格形式展示结果给用户。
