# experiment-gen

根据 AI 教材自动生成配套实验设计，并写入飞书多维表格。每本教材对应表格中的一个独立数据表，数据表名称为教材年级。

## 使用方式

### 方式一：Claude Code（推荐）

**环境准备**

1. 安装 [Claude Code](https://claude.ai/code)
2. 在项目根目录打开终端，执行：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动 Claude Code：
   ```bash
   claude
   ```

**常用提示词**

直接把下面的句子发给 Claude Code，它会自动完成操作：

| 想做什么 | 发送给 Claude Code 的内容 |
|---------|--------------------------|
| 查看有哪些教材 | `教材文件夹里有哪些教材？` |
| 查看飞书已有数据表 | `飞书表格里现在有哪些数据表？` |
| 为某本教材生成实验 | `用 API Key [你的Key] 为五年级上册生成 8 个实验` |
| 切换飞书表格 | `用 Base Token [新Token] 为二年级下册生成 6 个实验` |

> Claude Code 会读取项目中的 `CLAUDE.md`，自动了解项目结构和接口规范，无需任何额外配置。

### 方式二：命令行

```bash
pip install -r requirements.txt
python main.py <教材路径> <实验数量> [--base-token TOKEN] [--api-key KEY]
```

**示例**

```bash
python main.py 教材/AI教材二年级下册.docx 6 --api-key sk-ant-...
```

也可通过环境变量提供 API Key：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py 教材/AI教材五年级上册.docx 10
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `textbook` | 教材 .docx 文件路径 | 必填 |
| `n` | 生成实验总数，均匀分配到各课 | 必填 |
| `--base-token` | 飞书多维表格 Base Token | 内置默认值 |
| `--api-key` | Anthropic API Key | 读取环境变量 |

## 实验字段

每条实验记录包含以下字段：

- **实验名称**
- **实验概述**
- **技术栈**
- **原型**（UI/交互描述）
- **实验准备**
- **实验步骤**
- **实验成效（问题与作业）**
- **单元与课次**

## AI 接口

实验中涉及 AI 能力时使用公司内部接口：

- **对话**：`POST https://api.qa.bingotalk.cn/api/v2/comm/vt/aiChat`
- **绘图**：`POST https://api.qa.bingotalk.cn/api/v2/comm/vt/aigcImg`

## 项目结构

```
experiment-gen/
├── main.py          # 入口
├── textbook.py      # 解析教材结构（单元/课次）
├── generator.py     # 调用 Claude 生成实验内容
├── feishu.py        # 飞书表格操作（建表、写记录）
├── 教材/            # 各年级教材 docx 文件
└── requirements.txt
```
