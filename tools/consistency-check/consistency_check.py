#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《钢铁共和国》一致性检查器 (consistency-check)
状态：Canonical / IMPLEMENTED

实际章节 schema（## 章节契约）：
  - 版本 / 状态 / 时间 / 地点 / 视角（限知视角）
  - 主要人物：仅最早期 4 章使用，其余章以「视角」标定 POV，故为可选项

检查项：
  A. 章节必备元数据完整性（版本 / 状态 / 时间 / 地点 / 视角）
  B. 「视角」/「主要人物」是否解析到 canon 人物库（疑似笔误 -> 警告）
  C. 卷内章节编号完整性（重复 / 缺号）
  D. canon 人物在正文中的出现覆盖统计（信息性）

用法：
  python tools/consistency-check/consistency_check.py
报告同时写入 tools/consistency-check/last-run.json
"""
import json
import re
import sys
from difflib import get_close_matches
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CANON_CHARS_DIR = REPO / "canon" / "characters"
NOVEL_DIR = REPO / "novel"

# 已知 canon 人物（显示名 -> 别名/可接受写法）。
CANON: dict[str, list[str]] = {
    "周衡": ["周衡"],
    "404号机甲": ["404号机甲", "404", "404号"],
    "S-00": ["S-00", "S00"],
    "韩朔": ["韩朔"],
    "顾言": ["顾言"],
    "苏烈": ["苏烈"],
    "林川": ["林川"],
    "陈默": ["陈默"],
}

# 自动发现 canon 人物（H1 形如 "# 《钢铁共和国》Character Bible：XXX"）
for md in sorted(CANON_CHARS_DIR.glob("*.md")):
    if md.name.lower() == "readme.md":
        continue
    for line in md.read_text(encoding="utf-8", errors="ignore").splitlines()[:5]:
        m = re.match(r"^#\s*.*[：:]\s*(.+)$", line)
        if m:
            CANON.setdefault(m.group(1).strip(), [])
            break

TOKEN2CANON: dict[str, str] = {}
for canon_name, aliases in CANON.items():
    TOKEN2CANON[canon_name] = canon_name
    for a in aliases:
        TOKEN2CANON[a] = canon_name
ALL_TOKENS = list(TOKEN2CANON.keys())

# 必备元数据（按实际 schema：以「视角」标定 POV）
REQUIRED_META = ["版本", "状态", "时间", "地点", "视角"]
META_RE = {k: re.compile(rf"^(?:[-*]\s*)?{k}\s*[:：]\s*(.+)$") for k in REQUIRED_META}
PEOPLE_RE = re.compile(r"^(?:[-*]\s*)?主要人物\s*[:：]\s*(.+)$")
BODY_RE = re.compile(r"^##\s*正文\s*$")


def split_people(raw: str) -> list[str]:
    return [p.strip() for p in re.split(r"[、，,\s/；;]+", raw.strip()) if p.strip()]


def resolve_person(token: str):
    if token in TOKEN2CANON:
        return ("ok", TOKEN2CANON[token], None)
    near = get_close_matches(token, ALL_TOKENS, n=1, cutoff=0.6)
    if near:
        return ("warn", None, TOKEN2CANON.get(near[0], near[0]))
    return ("info", None, None)


def parse_chapter(path: Path):
    meta = {}
    body_lines = []
    in_body = False
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if in_body:
            body_lines.append(line)
            continue
        for k, rx in META_RE.items():
            m = rx.match(line.strip())
            if m:
                meta[k] = m.group(1).strip()
                break
        else:
            mp = PEOPLE_RE.match(line.strip())
            if mp:
                meta.setdefault("主要人物", mp.group(1).strip())
            elif BODY_RE.match(line.strip()):
                in_body = True
    return meta, "\n".join(body_lines)


def main():
    report = {
        "errors": [], "warnings": [], "infos": [],
        "missing_meta": [], "unknown_people": [], "alias_usage": {},
        "pov_unresolved": [], "numbering": {}, "summary": {},
    }
    chapters_total = 0
    volumes = {}

    for vol_dir in sorted(NOVEL_DIR.glob("volume*")):
        vol_name = vol_dir.name
        ch_files = sorted(vol_dir.glob("chapters/chapter-*.md"))
        nums = []
        for ch in ch_files:
            chapters_total += 1
            m = re.match(r"chapter-(\d+)-", ch.name)
            if m:
                nums.append(int(m.group(1)))
            meta, body = parse_chapter(ch)
            label = f"{vol_name}/{ch.name}"

            for k in REQUIRED_META:
                if not meta.get(k):
                    report["missing_meta"].append({"chapter": label, "field": k})
                    report["errors"].append(f"[元数据缺失] {label} 缺少「{k}」")

            # B. 视角 / 主要人物 解析
            for field in ("视角", "主要人物"):
                raw = meta.get(field)
                if not raw:
                    continue
                if field == "视角":
                    # 视角值如「周衡限知视角」，扫描是否含 canon token
                    hit = any(tok in raw for tok in ALL_TOKENS)
                    if not hit:
                        report["pov_unresolved"].append(label)
                        report["infos"].append(f"[视角非核心] {label} 视角「{raw}」未命中 canon 人物（可能为群像/多视角）")
                else:
                    for p in split_people(raw):
                        st, _, sugg = resolve_person(p)
                        if st == "ok":
                            pass
                        elif st == "warn":
                            report["warnings"].append(f"[疑似笔误] {label} 主要人物「{p}」最近匹配「{sugg}」")
                        else:
                            report["unknown_people"].append({"chapter": label, "person": p})
                            report["infos"].append(f"[非核心人物] {label} 主要人物「{p}」不在 canon 库（配角，待登记）")

            # D. 正文 canon 人物覆盖
            for canon_name, aliases in CANON.items():
                if any(tok in body for tok in aliases):
                    report["alias_usage"].setdefault(canon_name, set()).add(label)

        if nums:
            lo, hi = min(nums), max(nums)
            dup = sorted({n for n in nums if nums.count(n) > 1})
            missing = [n for n in range(lo, hi + 1) if n not in nums]
            report["numbering"][vol_name] = {
                "count": len(nums), "min": lo, "max": hi,
                "duplicates": dup, "missing": missing,
            }
            if dup:
                report["errors"].append(f"[编号重复] {vol_name}: {dup}")
            if missing:
                report["warnings"].append(f"[编号缺号] {vol_name}: 预期 {lo}..{hi}，缺失 {missing}")
        volumes[vol_name] = len(ch_files)

    report["alias_usage"] = {k: sorted(v) for k, v in report["alias_usage"].items()}
    report["summary"] = {
        "chapters_total": chapters_total,
        "volumes": volumes,
        "canon_people": list(CANON.keys()),
        "character_coverage": {k: len(v) for k, v in report["alias_usage"].items()},
        "errors": len(report["errors"]),
        "warnings": len(report["warnings"]),
        "infos": len(report["infos"]),
    }

    s = report["summary"]
    print("=" * 60)
    print("一致性检查报告 / Consistency Check")
    print("=" * 60)
    print(f"章节总数: {s['chapters_total']}  | 卷: {volumes}")
    print(f"canon 人物: {', '.join(s['canon_people'])}")
    print("canon 人物正文覆盖（出现章节数）:")
    for name, cov in s["character_coverage"].items():
        print(f"  - {name}: {cov} 章")
    print(f"错误: {s['errors']}  警告: {s['warnings']}  信息: {s['infos']}")
    print("-" * 60)
    if report["errors"]:
        print("【错误 ERROR】")
        for e in report["errors"][:50]:
            print("  -", e)
    if report["warnings"]:
        print("【警告 WARNING】")
        for w in report["warnings"][:50]:
            print("  -", w)
    if report["infos"]:
        print(f"【信息 INFO】前 30 / 共 {len(report['infos'])} 条")
        for i in report["infos"][:30]:
            print("  -", i)
    print("=" * 60)

    out = Path(__file__).with_name("last-run.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON 报告已写入: {out}")
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
