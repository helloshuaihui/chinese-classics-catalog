#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把服务器导出的 books.tsv 转成 JSON / CSV。

MySQL `--batch --raw` 的转义规则：
    字段分隔符   \\t
    字段内换行   \\n
    字段内制表   \\t
    反斜杠本身   \\\\
    空值         \\N

    python scripts/export.py books.tsv .
"""
import csv
import json
import os
import sys
from collections import Counter
from datetime import date

SRC = sys.argv[1] if len(sys.argv) > 1 else "books.tsv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

# 库里「清」「明」「宋」和「清代」「明代」「宋代」混着存，统一成带「代」的形式。
# 不加「代」的：本身已经是完整朝代的，加了反而错（先秦代、魏晋代）。
FIXED_DYNASTY = {
    "先秦", "两汉", "魏晋", "南北朝", "五代", "近现代", "民国",
}
SINGLE_DYNASTY = {
    "清": "清代", "明": "明代", "宋": "宋代", "唐": "唐代", "元": "元代",
    "汉": "汉代", "秦": "秦代", "晋": "晋代", "隋": "隋代", "金": "金代",
    "辽": "辽代", "周": "周代", "商": "商代", "夏": "夏代",
    "魏": "曹魏", "蜀": "蜀汉", "吴": "东吴",
}


def unescape(s: str) -> str:
    """还原 MySQL --raw 的转义。\\N 是 NULL，这里当空串处理。"""
    if s == "\\N":
        return ""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "n":
                out.append("\n")
                i += 2
                continue
            if nxt == "t":
                out.append("\t")
                i += 2
                continue
            if nxt == "0":
                out.append("\0")
                i += 2
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
            out.append(c)
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def norm_dynasty(s: str) -> str:
    s = s.strip()
    if not s:
        return ""
    if s in FIXED_DYNASTY:
        return s
    if s in SINGLE_DYNASTY:
        return SINGLE_DYNASTY[s]
    if s.endswith("代") or s.endswith("朝"):
        return s
    # 「春秋战国」「三国」这类保持原样，其余单字/双字朝代补「代」
    if len(s) <= 2:
        return s + "代"
    return s


def main():
    rows = []
    with open(SRC, "r", encoding="utf-8", newline="") as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < len(header):
                continue

            def col(name):
                return unescape(parts[idx[name]])

            title = col("title").strip()
            if not title:
                continue
            rows.append({
                "title": title,
                "author": col("author").strip(),
                "dynasty": norm_dynasty(col("dynasty")),
                "category": col("category").strip(),
                "chapters": int(parts[idx["chapter_count"]] or 0),
            })

    rows.sort(key=lambda r: (-r["chapters"], r["title"]))
    print(f"读到 {len(rows)} 条")

    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)

    # 空朝代单独统计成「未标注」，别混进作者字段用的「佚名」
    dynasties = Counter(r["dynasty"] if r["dynasty"] else "未标注" for r in rows)
    cats = Counter(r["category"] if r["category"] else "未分类" for r in rows)
    unknown_author = sum(1 for r in rows if not r["author"])

    payload = {
        "meta": {
            "name": "Chinese Classics Catalog / 古文书斋古籍目录",
            "description": "A metadata catalog of Chinese classical texts: title, author, "
                           "dynasty, category and chapter count. Text content is NOT included.",
            "count": len(rows),
            "total_chapters": sum(r["chapters"] for r in rows),
            "generated_at": date.today().isoformat(),
            "source": "https://book.jzzn.cloud",
            "license": "CC0-1.0",
            "fields": {
                "title": "书名 (book title)",
                "author": "作者 (author, empty if unknown)",
                "dynasty": "朝代 (dynasty, empty if unknown)",
                "category": "四部分类 (traditional four-branch classification)",
                "chapters": "章节数 (number of chapters)",
            },
            "stats": {
                "books_without_author": unknown_author,
                "books_without_dynasty": dynasties.get("未标注", 0),
            },
            "top_dynasties": [{"name": k, "count": v} for k, v in dynasties.most_common(20)],
            "top_categories": [{"name": k, "count": v} for k, v in cats.most_common(25)],
        },
        "books": rows,
    }
    jpath = os.path.join(OUT, "data", "books.json")
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"写出 {jpath}  {os.path.getsize(jpath) / 1048576:.1f} MB")

    cpath = os.path.join(OUT, "data", "books.csv")
    with open(cpath, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["title", "author", "dynasty", "category", "chapters"])
        for r in rows:
            w.writerow([r["title"], r["author"], r["dynasty"], r["category"], r["chapters"]])
    print(f"写出 {cpath}  {os.path.getsize(cpath) / 1048576:.1f} MB")

    print(f"\n无作者 {unknown_author} 条，无朝代 {dynasties.get('未标注', 0)} 条")
    print("\n朝代 Top10:")
    for k, v in dynasties.most_common(10):
        print(f"  {k}: {v}")
    print("\n分类 Top10:")
    for k, v in cats.most_common(10):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
