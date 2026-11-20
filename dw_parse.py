"""DW 格式（B1 起）的 Excel 行 → json 条目。

每个 parse_* 接收一行 {excel 列名: 字符串}，返回 (entry, warning)：
    entry    json 条目（字段和 A 级 json 一致，前端不用区分来源）
    warning  需要人工看一眼但仍会导入的问题，没有则为 None
解析不了时抛 ValueError，build 会列出来并跳过这一行。
"""
import re

ARTICLES = {"m": "der", "f": "die", "n": "das"}
_DEUMLAUT = str.maketrans("äöüÄÖÜ", "aouAOU")
# 直接接在单数后面的复数词尾：Gegenteil, -e → Gegenteile
_PLAIN_ENDINGS = {"e", "n", "en", "nen", "s", "er", "se"}

# 只表示格的宾语占位词，从动词原型里去掉
_OBJECT_WORDS = {"jemand", "jemanden", "jemandem", "jemandes", "etwas", "etw.", "jmd.", "jmdn.", "jmdm."}


def _expand_plural(singular, plural):
    """DW 的复数写法 → 完整复数；展开不了返回 None。"""
    if plural in ("-", "–"):
        return singular
    if not plural.startswith(("-", "–")):
        return plural                       # Gymnasium, Gymnasien：已是完整形式
    suffix = plural[1:]
    if suffix in _PLAIN_ENDINGS:
        return singular + suffix
    # Arbeitsmarkt, -märkte：替换复合词的最后一段（允许变音）
    target = suffix.translate(_DEUMLAUT).lower()
    for i in range(len(singular)):
        tail = singular[i:].translate(_DEUMLAUT).lower()
        if len(tail) >= 3 and target.startswith(tail):
            return singular[:i] + suffix
    return None


def parse_noun_cell(cell):
    """'Gegenteil, -e (n.)' → ('das Gegenteil', 'die Gegenteile', warning)。只看第一行。"""
    line = cell.strip().splitlines()[0].strip() if cell.strip() else ""
    if not line:
        return "", "", None

    m = re.match(r"^(.+?)\s*\(Pl\.\)$", line)
    if m:                                   # Eltern (Pl.)：只有复数
        return "", f"die {m[1]}", None

    m = re.match(r"^([^,(]+?)\s*,\s*([^(]+?)\s*\(([mfn])\.\s*(?:,\s*([^)]*))?\)", line)
    if not m:
        raise ValueError(f"认不出名词格式：{line}")
    singular, plural, gender, note = m.groups()
    full = _expand_plural(singular, plural)
    warning = None
    if full is None:
        plural_text = plural                # 展开不了就原样保留 -xyz
        warning = f"复数没能展开，原样保留：{line}"
    else:
        plural_text = f"die {full}"
    if note:
        plural_text += f" ({note})"
    return f"{ARTICLES[gender]} {singular}", plural_text, warning


def parse_noun(row):
    singular, plural, warning = parse_noun_cell(row["名词"])
    if not singular and not plural:
        raise ValueError("名词为空")
    return {"单数": singular, "复数": plural, "意思": row["意思"]}, warning


def parse_person(row):
    sm, pm, wm = parse_noun_cell(row["男"])
    sf, pf, wf = parse_noun_cell(row["女"])
    if not (sm or pm or sf or pf):
        raise ValueError("男 / 女 都为空")
    # 意思只有一份：有男性形式就挂在男性上，否则挂在女性上
    has_male = bool(sm or pm)
    entry = {
        "单数男": sm, "复数男": pm, "意思男": row["意思"] if has_male else "",
        "单数女": sf, "复数女": pf, "意思女": "" if has_male else row["意思"],
    }
    return entry, "；".join(w for w in (wm, wf) if w) or None


def clean_verb(raw):
    """'jemanden aus|bilden' → 'bilden aus'；'sich aus|ruhen' → 'ruhen sich aus'。
    去掉只表示格的 jemand/etwas；和 A 级一样动词在前，其余（sich、前缀）跟在后面。"""
    words = [w for w in raw.split() if w.lower() not in _OBJECT_WORDS]
    if not words:
        raise ValueError(f"动词为空：{raw}")
    *rest, verb = words
    prefix = ""
    if "|" in verb:
        prefix, verb = verb.split("|", 1)
    return " ".join([verb] + rest + ([prefix] if prefix else []))


def parse_verb(row):
    entry = {
        "原型": clean_verb(row["原型"]),
        "现在": row["现在"], "过去": row["过去"], "完成": row["完成"],
        "意思": row["意思"],
    }
    return entry, None


def parse_adj(row):
    if not row["形容词"]:
        raise ValueError("形容词为空")
    # 比较级 / 最高级 可留空（副词、规则变化的不必写）
    return {"原型": row["形容词"], "比较级": row["比较级"], "最高级": row["最高级"], "意思": row["意思"]}, None


def parse_phrase(row):
    if not row["词组"]:
        raise ValueError("词组为空")
    return {"词组": row["词组"], "意思": row["意思"]}, None


PARSERS = {
    "noun":   parse_noun,
    "person": parse_person,
    "verb":   parse_verb,
    "adj":    parse_adj,
    "phrase": parse_phrase,
}
