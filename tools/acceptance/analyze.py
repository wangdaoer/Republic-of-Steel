#!/usr/bin/env python3
"""Analysis-only: dump header status, 审稿状态 block, and 伏笔职责 per chapter."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOL = "novel/volume01-waste-iron-camp"

def parse(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    # header status
    status = None
    version = None
    for i, ln in enumerate(lines[:12]):
        if ln.startswith("版本："):
            version = ln.strip()
        if ln.startswith("状态："):
            status = ln.strip()
    # 审稿状态 block
    sb = []
    in_sb = False
    for ln in lines:
        if ln.strip().startswith("## 审稿状态"):
            in_sb = True
            sb.append(ln.strip())
            continue
        if in_sb:
            if ln.strip().startswith("## ") and not ln.strip().startswith("## 审稿状态"):
                break
            sb.append(ln.strip())
    # 伏笔职责
    fk = [ln.strip() for ln in lines if "伏笔职责" in ln or "推进F" in ln or "新增F" in ln]
    return version, status, sb, fk[:3]

for ch in sorted(glob.glob(os.path.join(ROOT, VOL, "chapters", "chapter-*.md"))):
    base = os.path.basename(ch)
    v, s, sb, fk = parse(ch)
    print("="*70)
    print(base, "|", v, "|", s)
    for ln in sb:
        print("   SB:", ln)
    for ln in fk:
        print("   FK:", ln)
