# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目目标

根据教材 docx 文件，用 Claude API 自动生成配套实验设计，并写入飞书多维表格。每本教材在飞书 Base 中对应一个独立数据表，表名为教材年级（如"二年级下册"）。

## 交互式使用方式（Claude Code）

### 自动触发规则（重要）

当用户的请求属于下表中任一**意图类型**时，**立即执行**对应的操作，不要追问年级/数量/路径等细节（已能从自然语言中推断），不要请求用户确认，不要给出"我可以帮你做..."之类的准备性回复——直接开跑。

| 意图类型 | 触发词示例 | 执行方式 |
|---------|-----------|---------|
| 生成实验 | "生成/创建/写... X个... 实验"、"为X年级... 做实验" | 按下方代码模板运行 |
| 查看表格 | "有哪些数据表"、"飞书里有什么" | 调用 `FeishuBase.list_tables()` |
| 查看教材 | "有哪些教材"、"教材文件夹" | Glob `教材/*.docx` |

### 生成实验的执行模板

```bash
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from textbook import parse_textbook
from generator import generate_experiments
from feishu import FeishuBase
book = parse_textbook('教材/AI教材<年级>.docx')
experiments = generate_experiments(book, <数量>)
feishu = FeishuBase('T5WXb4Hx2aRmoUs1fpJcbkFrn8g')
table_id = feishu.get_or_create_table(book['grade'])
feishu.write_experiments(table_id, experiments)
print(f'done: {len(experiments)} experiments in table {book[\"grade\"]}')
"
```

### 预制斜杠命令

`.claude/commands/` 下已预制：
- `/generate <年级> <数量>` — 生成实验
- `/list-tables` — 查看飞书数据表
- `/list-textbooks` — 查看本地教材

### 前置检查

运行前仅需确认 `ANTHROPIC_API_KEY` 环境变量存在。不存在则一次性告知用户设置，不要反复询问。

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
