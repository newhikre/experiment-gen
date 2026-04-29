#!/usr/bin/env python3
"""
Usage:
    python main.py <textbook.docx> <n> [--base-token TOKEN] [--api-key KEY]

Example:
    python main.py ../教材/AI教材二年级下册.docx 6
"""
import argparse
import os
import sys
from textbook import parse_textbook
from generator import generate_experiments
from feishu import FeishuBase

DEFAULT_BASE_TOKEN = "T5WXb4Hx2aRmoUs1fpJcbkFrn8g"


def main():
    parser = argparse.ArgumentParser(description="为AI教材生成配套实验并写入飞书多维表格")
    parser.add_argument("textbook", help="教材 .docx 文件路径")
    parser.add_argument("n", type=int, help="生成实验总数")
    parser.add_argument("--base-token", default=DEFAULT_BASE_TOKEN, help="飞书多维表格 Base Token")
    parser.add_argument("--api-key", default=os.getenv("ANTHROPIC_API_KEY"), help="Anthropic API Key")
    args = parser.parse_args()

    if not args.api_key:
        sys.exit("错误：请通过 --api-key 或环境变量 ANTHROPIC_API_KEY 提供 API Key")

    print(f"📖 解析教材: {args.textbook}")
    book = parse_textbook(args.textbook)
    print(f"   年级: {book['grade']}，共 {len(book['lessons'])} 课")

    if not book["lessons"]:
        sys.exit("错误：未能从教材中解析出课程结构")

    print(f"\n🤖 生成 {args.n} 个实验...")
    experiments = generate_experiments(book, args.n, api_key=args.api_key)
    print(f"   生成完成，共 {len(experiments)} 个实验")

    print(f"\n📊 写入飞书表格 (Base: {args.base_token})")
    feishu = FeishuBase(args.base_token)
    table_id = feishu.get_or_create_table(book["grade"])
    feishu.write_experiments(table_id, experiments)

    print(f"\n✅ 完成！{len(experiments)} 个实验已写入数据表「{book['grade']}」")


if __name__ == "__main__":
    main()