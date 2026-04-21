import json
import shutil
import subprocess
import os

FIELDS = [
    "实验名称",
    "实验概述",
    "技术栈",
    "原型",
    "实验准备",
    "实验步骤",
    "实验成效（问题与作业）",
    "单元与课次",
]

# lark-cli uses base/v3 API internally; avoid /open-apis/ prefix (Windows path issue)
ENV = {**os.environ, "LARK_CLI_NO_PROXY": "1"}
LARK_CLI = shutil.which("lark-cli") or r"C:\Program Files\nodejs\lark-cli.cmd"


def _cli(*args) -> dict:
    result = subprocess.run(
        [LARK_CLI, *args],
        capture_output=True, text=True, encoding="utf-8", env=ENV,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(result.stdout + result.stderr)


class FeishuBase:
    def __init__(self, base_token: str):
        self.token = base_token

    def list_tables(self) -> dict[str, str]:
        """Returns {name: table_id}"""
        data = _cli("base", "+table-list", "--base-token", self.token)
        tables = data.get("data", {}).get("tables") or data.get("data", {}).get("items", [])
        return {t.get("name"): t.get("id") or t.get("table_id") for t in tables}

    def get_or_create_table(self, grade: str) -> str:
        tables = self.list_tables()
        if grade in tables:
            print(f"  数据表已存在: {grade}")
            table_id = tables[grade]
            self._ensure_fields(table_id)
            return table_id

        print(f"  创建数据表: {grade}")
        # Build fields spec for table creation
        fields_spec = [{"name": f, "type": "text"} for f in FIELDS]
        data = _cli(
            "base", "+table-create",
            "--base-token", self.token,
            "--json", json.dumps({"name": grade, "fields": fields_spec}, ensure_ascii=False),
        )
        table_id = data["data"]["table_id"]
        return table_id

    def _ensure_fields(self, table_id: str):
        """Add any missing fields to an existing table."""
        data = _cli(
            "base", "+field-list",
            "--base-token", self.token,
            "--table-id", table_id,
        )
        existing = {f["name"] for f in data.get("data", {}).get("items", [])}
        for field in FIELDS:
            if field not in existing:
                _cli(
                    "base", "+field-create",
                    "--base-token", self.token,
                    "--table-id", table_id,
                    "--json", json.dumps({"name": field, "type": "text"}, ensure_ascii=False),
                )

    def write_experiments(self, table_id: str, experiments: list[dict]):
        for i, exp in enumerate(experiments, 1):
            fields = {k: str(v) for k, v in exp.items() if k in FIELDS and v}
            _cli(
                "base", "+record-upsert",
                "--base-token", self.token,
                "--table-id", table_id,
                "--json", json.dumps(fields, ensure_ascii=False),
            )
            print(f"  [{i}/{len(experiments)}] 写入: {exp.get('实验名称', '—')}")
