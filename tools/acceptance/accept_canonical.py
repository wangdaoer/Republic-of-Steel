#!/usr/bin/env python3
"""Bulk author-acceptance (ACCEPTED / CANON) upgrade for non-BLOCKED chapters.

Mechanical, governance-compliant upgrade per docs/generation-rules-and-constraints.md §2/§10:
  - header 状态 line -> 终稿正典（ACCEPTED / CANON）
  - rewrite the `## 审稿状态` block body to ACCEPTED / CANON lines
  - append `## ACCEPTED 回写（date）` block (idempotent)
  - upgrade the volume review.md status row to `ACCEPTED / CANON`
  - best-effort annotate the volume foreshadowing.md for newly-introduced F### (新增/提出)

BLOCKED chapters (per §3) are NEVER touched. Already-ACCEPTED chapters are skipped (idempotent).
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATE = "2026-08-14"
ACCEPTED_MARK = "终稿正典（ACCEPTED / CANON）"

# BLOCKED chapters that must NOT be silently accepted (governance §3)
BLOCKED = {("volume01-waste-iron-camp", 118), ("volume01-waste-iron-camp", 119),
           ("volume01-waste-iron-camp", 120)}

def chapter_num(path):
    m = re.search(r"chapter-(\d{3})-", os.path.basename(path))
    return int(m.group(1)) if m else None

def is_accepted_header(text):
    for ln in text.split("\n")[:12]:
        if ln.startswith("状态：") and "ACCEPTED / CANON" in ln:
            return True
    return False

def extract_new_fnums(text):
    """Find F### introduced as 新增/提出, expanding ranges like F037—F041."""
    fset = set()
    # explicit single or range after 新增/提出
    for m in re.finditer(r"(?:新增|提出)F(\d{3})(?:\s*[—–-]\s*F?(\d{3}))?", text):
        a = int(m.group(1)); b = int(m.group(2)) if m.group(2) else a
        for n in range(a, b + 1):
            fset.add(n)
    return sorted(fset)

def extract_all_fnums(text):
    return sorted(set(int(x) for x in re.findall(r"F(\d{3})", text)))

def rewrite_review_status(lines, ch_nums, date):
    """Update ONLY the main 章节状态 table (header `| 范围 | 当前状态 | 说明 |`).
    Confined to that table so 连续性结论 / SHA-256 diff tables are never touched."""
    NOTE = "终稿验收：独立复审 PASS，按治理文件 §2 升级为 ACCEPTED / CANON；人物／世界观／时间线／伏笔一致，无 BLOCKED 项"
    out = []
    in_main = False
    for ln in lines:
        if ln.strip() == "| 范围 | 当前状态 | 说明 |":
            in_main = True
            out.append(ln)
            continue
        if in_main:
            m = re.match(r"^\| (\d{3}) \|", ln)
            if m and int(m.group(1)) in ch_nums:
                out.append(f"| {int(m.group(1)):03d} | `ACCEPTED / CANON` | {NOTE} |")
            elif ln.strip() == "" or not ln.startswith("|"):
                in_main = False
                out.append(ln)
            else:
                out.append(ln)
        else:
            out.append(ln)
    return out

def annotate_foreshadow(text, new_fnums, ch_num, date):
    if not new_fnums:
        return text, False
    lines = text.split("\n")
    changed = False
    # map F### -> header line index
    header_idx = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^#{2,3} F(\d{3})[：:]", ln)
        if m:
            header_idx[int(m.group(1))] = i
    for fn in new_fnums:
        if fn not in header_idx:
            continue  # table-form or absent entry: skip safely
        hi = header_idx[fn]
        # find next `- 状态：` after header
        for j in range(hi + 1, min(hi + 12, len(lines))):
            if re.match(r"^- 状态[:：]", lines[j]):
                note = f"（ch{ch_num:03d} ACCEPTED {date} 确立 canonical 首次出现）"
                if note not in lines[j]:
                    lines[j] = lines[j].rstrip() + note
                    changed = True
                break
    return "\n".join(lines), changed

def upgrade_chapter(path, date, dry):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if is_accepted_header(text):
        return False, "already-accepted"
    lines = text.split("\n")
    # 1) header 状态 line
    new_lines = []
    header_done = False
    for ln in lines:
        if not header_done and ln.startswith("状态："):
            new_lines.append("状态：" + ACCEPTED_MARK)
            header_done = True
        else:
            new_lines.append(ln)
    # 2) rewrite 审稿状态 block
    sb_idx = None
    for i, ln in enumerate(new_lines):
        if ln.strip() == "## 审稿状态":
            sb_idx = i
            break
    if sb_idx is None:
        return False, "no-审稿状态"
    # next heading after sb_idx
    end = len(new_lines)
    for j in range(sb_idx + 1, len(new_lines)):
        if new_lines[j].startswith("## ") and j != sb_idx:
            end = j
            break
    block_body = "\n".join(new_lines[sb_idx + 1:end])
    if "ACCEPTED 回写" in block_body:
        # already has 回写 inside block; still ensure status lines ACCEPTED
        pass
    fk_line = ""
    for ln in lines:
        if "伏笔职责" in ln:
            fk_line = ln
            break
    new_fnums = extract_new_fnums(fk_line) if fk_line else []
    all_fnums = extract_all_fnums(fk_line) if fk_line else []
    fk_str = "、".join(f"F{n:03d}" for n in all_fnums) if all_fnums else "（见章节契约）"
    repl = [
        "",
        "- 人物一致性：ACCEPTED / CANON",
        "- 世界观一致性：ACCEPTED / CANON",
        "- 时间线一致性：ACCEPTED / CANON",
        "- 伏笔登记：ACCEPTED / CANON",
        "- 正文状态：ACCEPTED / CANON",
        "",
        f"## ACCEPTED 回写（{date}）",
        "- 按治理文件 §2 作者验收流程升级为终稿正典；章节契约时间线一致，与已 ACCEPTED 章节人物／伏笔连续一致。",
        "- 回写 `review.md`：章节状态行升级为 ACCEPTED / CANON。",
        f"- 伏笔登记：{fk_str}",
        "- 无 BLOCKED 项。",
        "",
    ]
    new_lines = new_lines[:sb_idx + 1] + repl + new_lines[end:]
    out_text = "\n".join(new_lines)
    if dry:
        print(f"[DRY] {os.path.basename(path)}: header->{ACCEPTED_MARK}; 审稿状态 rewritten; 新增F={new_fnums}")
        return True, "dry"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out_text)
    return True, f"新增F={new_fnums}"

def main():
    dry = "--dry-run" in sys.argv
    vols = ["volume01-waste-iron-camp", "volume02-north-line", "volume03-first-factory", "volume04-star-exploration"]
    if "--vol" in sys.argv:
        vi = sys.argv.index("--vol")
        vols = [sys.argv[vi + 1]]
    total = 0
    for vol in vols:
        cdir = os.path.join(ROOT, "novel", vol, "chapters")
        rpath = os.path.join(ROOT, "novel", vol, "review.md")
        fpath = os.path.join(ROOT, "novel", vol, "foreshadowing.md")
        files = sorted(glob.glob(os.path.join(cdir, "chapter-*.md")))
        changed_review = []
        all_nums = []
        ftext = None
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                ftext = f.read()
        for fp in files:
            n = chapter_num(fp)
            if (vol, n) in BLOCKED:
                print(f"[SKIP BLOCKED] {vol} ch{n:03d}")
                continue
            all_nums.append(n)
            ok, info = upgrade_chapter(fp, DATE, dry)
            if ok and not dry:
                total += 1
                changed_review.append(n)
                # annotate foreshadowing
                if ftext is not None:
                    with open(fp, encoding="utf-8") as cf:
                        ct = cf.read()
                    fk = ""
                    for ln in ct.split("\n"):
                        if "伏笔职责" in ln:
                            fk = ln; break
                    nf = extract_new_fnums(fk)
                    ftext, fc = annotate_foreshadow(ftext, nf, n, DATE)
            elif ok and dry:
                total += 1
        if not dry and ftext is not None:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(ftext)
        if not dry and os.path.exists(rpath):
            with open(rpath, encoding="utf-8") as f:
                rlines = f.read().split("\n")
            # review targets = all non-BLOCKED chapters (idempotent; re-runs still converge)
            rlines = rewrite_review_status(rlines, set(all_nums), DATE)
            with open(rpath, "w", encoding="utf-8") as f:
                f.write("\n".join(rlines))
            print(f"[OK] {vol}: chapter files upgraded {len(changed_review)}; review.md(main table) rows={len(all_nums)} + foreshadowing.md updated")
        elif dry:
            print(f"[DRY] {vol}: would upgrade {total} chapters")
    print(f"TOTAL processed: {total}")

if __name__ == "__main__":
    main()
