# Chinese Classics Catalog · 古文书斋古籍目录

A metadata catalog of **20,628 Chinese classical texts** — title, author, dynasty,
traditional four-branch category, and chapter count.

> **This repository contains metadata only. No full text is included.**

Chinese documentation is below the English section.

---

## What's inside

| File | Format | Size | Records |
|---|---|---|---|
| [`data/books.json`](data/books.json) | JSON (UTF-8) | 2.8 MB | 20,628 |
| [`data/books.csv`](data/books.csv) | CSV (UTF-8) | 0.9 MB | 20,628 |

`books.json` also carries a `meta` block with generation date, corpus statistics,
dynasty distribution and category distribution, so you can profile the dataset
without parsing every record.

## Fields

| Field | Type | Description |
|---|---|---|
| `title` | string | Book title in Chinese, e.g. `老子`, `資治通鑑` |
| `author` | string | Author name. Empty string when unknown |
| `dynasty` | string | Dynasty, normalized to the `X代` form, e.g. `先秦`, `唐代`, `宋代`. Empty when unknown |
| `category` | string | Traditional four-branch classification, e.g. `子部道家类` |
| `chapters` | int | Number of chapters in the text |

## Quick start

```python
import json

data = json.load(open("data/books.json", encoding="utf-8"))
print(data["meta"]["count"], "books")

# Longest works in the corpus
longest = sorted(data["books"], key=lambda b: -b["chapters"])[:10]
for b in longest:
    print(b["title"], b["chapters"])

# Traditional Chinese medicine
tcm = [b for b in data["books"] if b["category"] == "子部医家类"]
print(len(tcm), "titles in 子部医家类")

# Everything attributed to a Tang author
tang = [b for b in data["books"] if b["dynasty"] == "唐代" and b["author"]]
```

```sql
-- If you load books.csv into SQLite
CREATE TABLE books (title TEXT, author TEXT, dynasty TEXT, category TEXT, chapters INT);
.mode csv
.import data/books.csv books
SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY 2 DESC LIMIT 10;
```

## Data profile

- **20,628** books, **369,163** chapters in total
- **89%** have no dynasty recorded. Most of these are Buddhist canon entries
  (`子部释家类`, 4,687 titles) and large Ming/Qing collectanea, which historically
  were catalogued without a dynasty attribution. The field is left empty rather
  than guessed.
- **1,273** have no author recorded
- Largest category: `子部释家类` (4,687) · then `子部杂家类` (2,264),
  `史部传记类` (1,806), `子部医家类` (1,729), `集部词曲类` (1,634)

The `meta.top_dynasties` and `meta.top_categories` arrays in `books.json` carry the
full distribution.

## Classification

`category` follows the traditional **四部** (four-branch) system used by the
*Siku Quanshu* and most Chinese library catalogues:

| Branch | Meaning | Example classes |
|---|---|---|
| `经部` | Classics / Confucian canon | 易类, 四书类, 小学类 |
| `史部` | Histories | 正史类, 编年类, 传记类 |
| `子部` | Masters / technical arts | 道家类, 释家类, 医家类, 术数类 |
| `集部` | Belles-lettres | 别集类, 总集类, 词曲类, 诗文评类 |

Two classes are site-specific extensions rather than strict Siku categories:
`集部小说类` (vernacular fiction) and `子部武术类` (martial arts manuals and archery).

## Provenance

The catalog was assembled from public-domain digitizations and open text
collections, then de-duplicated and reclassified. Titles, authors and dynasties
were normalized for consistency, which means the values here may differ slightly
from any single upstream source.

Full texts are readable at **<https://book.jzzn.cloud>** — 20,000+ works with
chapter-level navigation, searchable poetry, and a classical Chinese dictionary.

## License

The metadata in this repository is released under **CC0 1.0 Universal** — see
[LICENSE](LICENSE). Use it for anything, no attribution required.

This covers the *metadata only*. Copyright status of the underlying texts varies
by work; nothing here grants rights to any full text. If you are a rights holder
and believe an entry should be removed, open an issue and it will be handled.

## Regenerating

`scripts/export.py` converts the raw TSV export into the two files above:

```bash
python scripts/export.py books.tsv .
```

---

# 中文说明

## 这是什么

**20,628 部中国古籍的目录数据**——书名、作者、朝代、四部分类、章节数。

> **本仓库只包含元数据，不包含任何正文。**

## 文件

| 文件 | 格式 | 大小 | 条数 |
|---|---|---|---|
| `data/books.json` | JSON（UTF-8） | 2.8 MB | 20,628 |
| `data/books.csv` | CSV（UTF-8） | 0.9 MB | 20,628 |

## 字段

| 字段 | 说明 |
|---|---|
| `title` | 书名，如 `老子`、`資治通鑑` |
| `author` | 作者，未知为空串 |
| `dynasty` | 朝代，统一成 `X代` 形式，如 `先秦`、`唐代`；未知为空串 |
| `category` | 四部分类，如 `子部道家类` |
| `chapters` | 章节数 |

## 数据概况

- 20,628 部，合计 369,163 章
- **89% 没有朝代信息**——绝大多数是佛典（`子部释家类` 4,687 部）和明清大型丛书，
  历代书目本就不标朝代。这里选择留空，不做猜测。
- 1,273 部没有作者
- 最大分类：`子部释家类` 4,687，其次 `子部杂家类` 2,264、`史部传记类` 1,806

## 分类说明

`category` 沿用传统四部分类法。`集部小说类`（通俗小说）和 `子部武术类`（拳谱射艺）
是本站在四部之外补的两个类目，方便检索。

## 来源

目录由公版影印本与开放文本集整理而成，经过去重与重新分类。书名、作者、朝代做过
统一化处理，可能与任何单一上游数据源存在差异。

全文可在 **<https://book.jzzn.cloud>** 在线阅读。

## 许可

元数据以 **CC0 1.0** 发布，随便用，不用署名。

**只覆盖元数据**。各书正文的版权状态不一，本仓库不授予任何正文权利。
如权利人认为某条目不妥，提 issue 即处理。
