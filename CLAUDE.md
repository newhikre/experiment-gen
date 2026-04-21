# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目目标

根据教材 docx 文件，用 Claude API 自动生成配套实验设计，并写入飞书多维表格。每本教材在飞书 Base 中对应一个独立数据表，表名为教材年级（如"二年级下册"）。

## 交互式使用方式（Claude Code）

用户可以直接用自然语言描述需求，例如：

- "为五年级上册生成 8 个实验"
- "看看教材文件夹里有哪些教材"
- "飞书表格里现在有哪些数据表"

遇到此类请求时，直接调用相应模块完成任务，无需用户手动运行脚本：

```python
from textbook import parse_textbook
from generator import generate_experiments
from feishu import FeishuBase

book = parse_textbook("教材/AI教材五年级上册.docx")
experiments = generate_experiments(book, 8, api_key="sk-ant-...")
feishu = FeishuBase("T5WXb4Hx2aRmoUs1fpJcbkFrn8g")
table_id = feishu.get_or_create_table(book["grade"])
feishu.write_experiments(table_id, experiments)
```

## 脚本启动方式

```bash
pip install -r requirements.txt
python main.py 教材/AI教材二年级下册.docx 6 --api-key sk-ant-...
# 或设置环境变量后省略 --api-key
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py 教材/AI教材五年级上册.docx 10
```

## 架构

- **textbook.py**：解析 docx，按正则识别"第X单元"/"第X课"标题，返回 `{grade, lessons: [{unit, lesson, content}]}`
- **generator.py**：将课程内容发给 Claude (`claude-sonnet-4-6`)，按 JSON schema 生成实验，n 个实验均匀分配到各课
- **feishu.py**：封装 `lark-cli base` 子命令（`+table-list/create`, `+field-list/create`, `+record-upsert`），注意必须用 `LARK_CLI_NO_PROXY=1` 且不能在路径前加 `/open-apis/`（Windows 路径解析问题）
- **main.py**：CLI 入口，串联以上三个模块

## 飞书操作

飞书 Base Token：`T5WXb4Hx2aRmoUs1fpJcbkFrn8g`（即 https://my.feishu.cn/base/T5WXb4Hx2aRmoUs1fpJcbkFrn8g）

查看当前所有数据表：
```python
from feishu import FeishuBase
print(FeishuBase("T5WXb4Hx2aRmoUs1fpJcbkFrn8g").list_tables())
```

## 实验中的 AI 接口

生成的实验设计中，凡涉及 AI 能力必须使用公司内部接口：
- **对话**：`POST https://api.qa.bingotalk.cn/api/v2/comm/vt/aiChat`，body 为消息数组，响应为流式 JSON，取 `data.result` 拼接
- **绘图**：`POST https://api.qa.bingotalk.cn/api/v2/comm/vt/aigcImg?question=<提示词>`，body 为 `{"username": "student", "score": 100}`

参考实现见 `../公司接口/对话.py` 和 `../公司接口/绘图.py`。
