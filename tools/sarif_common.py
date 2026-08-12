#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《钢铁共和国》SARIF 生成共享模块
供 consistency_check.py / timeline_check.py 复用，输出 SARIF 2.1.0 供 GitHub 代码扫描。

finding 结构：
  {
    "rule_id":   "missing-metadata",
    "severity":  "error" | "warning" | "info",
    "message":   "人类可读说明",
    "rel_path":  "novel/volume01-waste-iron-camp/chapters/chapter-005-xxx.md",
    "line":      12,
    "rule_short": "缺失必备元数据",   # 可选
  }
"""
import json
from pathlib import Path

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def _sarif_level(severity: str) -> str:
    return {"error": "error", "warning": "warning"}.get(severity, "note")


def build_sarif(tool_name: str, info_uri: str, findings: list[dict]) -> dict:
    rules = {}
    results = []
    for f in findings:
        rid = f["rule_id"]
        if rid not in rules:
            short = f.get("rule_short", rid)
            rules[rid] = {
                "id": rid,
                "shortDescription": {"text": short},
                "fullDescription": {"text": f.get("rule_full", short)},
                "defaultConfiguration": {"level": _sarif_level(f["severity"])},
            }
        uri = f.get("rel_path", "README.md")
        line = max(1, int(f.get("line", 1)))
        results.append({
            "ruleId": rid,
            "level": _sarif_level(f["severity"]),
            "message": {"text": f["message"]},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": uri},
                        "region": {"startLine": line},
                    }
                }
            ],
        })
    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": "1.0.0",
                        "informationUri": info_uri,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def write_sarif(tool_name: str, info_uri: str, findings: list[dict], out_path) -> dict:
    sarif = build_sarif(tool_name, info_uri, findings)
    Path(out_path).write_text(json.dumps(sarif, ensure_ascii=False, indent=2), encoding="utf-8")
    return sarif
