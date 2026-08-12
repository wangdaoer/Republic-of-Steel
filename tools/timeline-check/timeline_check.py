#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《钢铁共和国》时间线检查器 (timeline-check)
状态：Canonical / IMPLEMENTED

检查项：
  A. 解析每章「时间」字段中的钢铁纪元 SE 编号
  B. 将 SE 映射到 master-timeline.md 的纪元（epoch）
  C. 卷内章节按编号顺序是否为非递减 SE（回退 -> 警告，可能是闪回）
  D. 无法解析「时间」的章节 -> 警告（需补全）
  E. 各卷 SE 区间与全局卷序（V1<V2<V3<V4）校验

用法：
  python tools/timeline-check/timeline_check.py
报告同时写入 tools/timeline-check/last-run.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NOVEL_DIR = REPO / "novel"

# 纪元区间（与 canon/timeline/master-timeline.md 对齐）。
# (名称, 起点SE, 终点SE|None 表示开放)
EPOCHS = [
    ("工业觉醒时代", -200, 0),
    ("废铁营时代", 0, 30),
    ("拓荒者时代", 30, 120),
    ("北境战争时代", 120, 160),
    ("第一工业时代", 160, 350),
    ("智能文明时代", 350, 1000),
    ("星海拓荒时代", 1000, 5000),
    ("文明修复时代", 5000, 100000),
    ("第五文明时代", 100000, 500000),
    ("回声时代", 500000, None),
]

# 卷 -> 期望纪元（用于异常提示，闪回除外）
VOLUME_EPOCH = {
    "volume01-waste-iron-camp": "废铁营时代",
    "volume02-north-line": "北境战争时代",
    "volume03-first-factory": "第一工业时代",
    "volume04-star-exploration": "星海拓荒时代",
}

SE_RE = re.compile(r"SE\s*(-?\d+)")


def epoch_of(se: int) -> str:
    for name, lo, hi in EPOCHS:
        if hi is None:
            if se >= lo:
                return name
        elif lo <= se < hi:
            return name
    return "未知纪元"


def parse_se(raw: str):
    m = SE_RE.search(raw or "")
    return int(m.group(1)) if m else None


def main():
    report = {
        "errors": [],
        "warnings": [],
        "infos": [],
        "unparsed": [],
        "regressions": [],
        "epoch_mismatch": [],
        "per_volume": {},
        "summary": {},
    }
    volumes_order = []

    for vol_dir in sorted(NOVEL_DIR.glob("volume*")):
        vol_name = vol_dir.name
        ch_files = sorted(vol_dir.glob("chapters/chapter-*.md"))
        rows = []  # (num, se, epoch, name)
        for ch in ch_files:
            m = re.match(r"chapter-(\d+)-", ch.name)
            num = int(m.group(1)) if m else 0
            text = ch.read_text(encoding="utf-8", errors="ignore")
            time_raw = ""
            for line in text.splitlines():
                mm = re.match(r"^(?:[-*]\s*)?时间\s*[:：]\s*(.+)$", line.strip())
                if mm:
                    time_raw = mm.group(1).strip()
                    break
            se = parse_se(time_raw)
            if se is None:
                report["unparsed"].append(f"{vol_name}/{ch.name} (时间={time_raw or '空'})")
                report["warnings"].append(f"[时间缺失/未解析] {vol_name}/{ch.name}: 时间={time_raw or '空'}")
                rows.append((num, None, None, ch.name))
            else:
                ep = epoch_of(se)
                rows.append((num, se, ep, ch.name))
                exp = VOLUME_EPOCH.get(vol_name)
                if exp and ep != exp:
                    report["epoch_mismatch"].append(
                        f"{vol_name}/{ch.name}: SE {se} -> {ep}（卷预期纪元：{exp}）"
                    )
                    report["infos"].append(
                        f"[纪元偏移] {vol_name}/{ch.name}: SE {se} 落入「{ep}」，卷预期「{exp}」（可能为闪回/前史）"
                    )

        rows.sort(key=lambda r: (r[0] if r[0] is not None else 0))
        # C. 卷内非递减校验
        prev = None
        for num, se, ep, name in rows:
            if se is None:
                prev = se if prev is None else prev
                continue
            if prev is not None and se < prev:
                report["regressions"].append(
                    f"{vol_name}/chapter-{num:03d}: SE {se} < 前章 SE {prev}"
                )
                report["warnings"].append(
                    f"[时间回退] {vol_name}/chapter-{num:03d}: SE {se} 早于前一章 SE {prev}（确认是否为闪回）"
                )
            prev = se if prev is None else max(prev, se)

        ses = [r[1] for r in rows if r[1] is not None]
        epochs_dist = {}
        for r in rows:
            if r[2]:
                epochs_dist[r[2]] = epochs_dist.get(r[2], 0) + 1
        report["per_volume"][vol_name] = {
            "chapters": len(rows),
            "se_min": min(ses) if ses else None,
            "se_max": max(ses) if ses else None,
            "unparsed": len([r for r in rows if r[1] is None]),
            "epoch_distribution": epochs_dist,
        }
        volumes_order.append((vol_name, min(ses) if ses else None, max(ses) if ses else None))

    # E. 全局卷序
    valid = [(v, lo, hi) for v, lo, hi in volumes_order if lo is not None]
    for i in range(1, len(valid)):
        if valid[i][1] < valid[i - 1][2]:
            report["warnings"].append(
                f"[卷序交叉] {valid[i-1][0]} (SE {valid[i-1][1]}..{valid[i-1][2]}) 与 "
                f"{valid[i][0]} (SE {valid[i][1]}..{valid[i][2]}) 时间区间重叠/倒挂"
            )

    report["summary"] = {
        "volumes": {v: report["per_volume"][v] for v, _, _ in volumes_order},
        "errors": len(report["errors"]),
        "warnings": len(report["warnings"]),
        "infos": len(report["infos"]),
        "unparsed": len(report["unparsed"]),
        "regressions": len(report["regressions"]),
    }

    print("=" * 60)
    print("时间线检查报告 / Timeline Check")
    print("=" * 60)
    for v, lo, hi in volumes_order:
        pv = report["per_volume"][v]
        print(f"{v}: 章节 {pv['chapters']} | SE {pv['se_min']}..{pv['se_max']} | "
              f"未解析 {pv['unparsed']} | 纪元 {pv['epoch_distribution']}")
    s = report["summary"]
    print(f"错误: {s['errors']}  警告: {s['warnings']}  信息: {s['infos']}  "
          f"未解析: {s['unparsed']}  时间回退: {s['regressions']}")
    print("-" * 60)
    if report["regressions"]:
        print("【时间回退 REGRESSION】")
        for r in report["regressions"][:40]:
            print("  -", r)
    if report["unparsed"]:
        print("【未解析 UNPARSED】前 30")
        for u in report["unparsed"][:30]:
            print("  -", u)
    if report["epoch_mismatch"]:
        print(f"【纪元偏移 MISMATCH】前 20 / 共 {len(report['epoch_mismatch'])}")
        for e in report["epoch_mismatch"][:20]:
            print("  -", e)
    print("=" * 60)

    out = Path(__file__).with_name("last-run.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON 报告已写入: {out}")
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
