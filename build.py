"""一键更新词库：例句库 -> Excel -> 例句 -> 翻译。

日常用法：
    python build.py                 # 跑完整流程
    python build.py --only excel    # 只做某一步：sentences / excel / examples / translation
    python build.py --skip translation
    python build.py --sentence-mode upgrade   # 用 sentences.json 升级已有例句

流程：
    1. sentences    sentences.docx 的新句子 → sentences.json，并翻译新句子
    2. excel        Excel 新单词 → 各词库 json
    3. examples     给没有例句的词配例句：先 sentences.json（连同翻译一起拷），再 OpenSubtitles
    4. translation  翻译还没有译文的例句（sentences.json 里有的直接拷，不再调用模型）

一次性初始化 sentences.json（从旧笔记导入）：
    python build.py --only sentences --docx "_A2/sentences.docx" "_A2/sentences from the internet.docx"

============================================================
升级到新阶段（B1、B2…）时，唯一要改的就是下面这一行：
把新笔记文件夹加进列表即可。B1 起每个文件夹放一个 Vokabeln.xlsx
（DW 格式，sheet：Nomen / Personen / Verben / Adjektive / Phrasen）
和 sentences.docx，名字保持一致，其余不用动。
没有 Vokabeln.xlsx 的文件夹按 A 级的三个 Excel 读。
============================================================
"""
NOTES_DIRS = ["_B1"]

# Ollama 翻译模型
OLLAMA_MODEL = "qwen2.5:14b"

# 例句填充模式（也可用 --sentence-mode 临时覆盖）：
#   "normal"      只给「例句为空」的词找例句：sentences.json 优先，找不到 fallback 到 OpenSubtitles
#   "new_example" 所有词都重新找一遍全新例句；没找到的 → 保留原有例句，不删除
#   "upgrade"     只把已有例句替换成 sentences.json 里的版本；匹配不到就原样不动，不碰 OpenSubtitles
# 例句来自 sentences.json 时翻译一起拷过去；来自 OpenSubtitles 时清空「翻译」，由 translation 步骤补上。
SENTENCE_MODE = "normal"

# ────────────────────────────────────────────────────────
# 以下为固定结构，除非笔记的表格结构变了，一般不用改。
# ────────────────────────────────────────────────────────
import argparse
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

OLLAMA_URL = "http://localhost:11434/api/generate"
SENTENCES_JSON = "public/data/sentences.json"
OPENSUB_FOLDER = "resource/OpenSubtitles"
UPDATE_EXISTING_FROM_EXCEL = False   # True: 用 Excel 补齐旧条目的空字段（不覆盖非空）

# 每个笔记文件夹里读这个 docx 进 sentences.json
SENTENCE_DOCX_NAME = "sentences.docx"

# 输出 json → 主键 / step2 例句匹配器（None 表示例句需手动填，如 phrasen）
DECKS_META = {
    "nomen_obj":    {"key_fields": ["单数", "复数"], "sentence_type": "noun"},
    "nomen_people": {"key_fields": ["单数男", "复数男", "单数女", "复数女"], "sentence_type": "person"},
    "verben_base":  {"key_fields": ["原型"], "sentence_type": "verb"},
    "adj_adv":      {"key_fields": ["原型"], "sentence_type": "steigerung"},
    "phrasen":      {"key_fields": ["词组"], "sentence_type": None},
}

# 笔记文件夹里有 DW_EXCEL 就按 DW 格式读，否则按 A 级的三个 Excel 读。
# ── DW 格式（B1 起）：一个 Excel，每个 sheet 对应一个 json；单元格由 dw_parse 解析 ──
DW_EXCEL = "Vokabeln.xlsx"
DW_TEMPLATES = [
    {"out": "nomen_obj",    "sheet": "Nomen",     "columns": ["名词", "意思"],                       "parse": "noun"},
    {"out": "nomen_people", "sheet": "Personen",  "columns": ["男", "女", "意思"],                   "parse": "person"},
    {"out": "verben_base",  "sheet": "Verben",    "columns": ["原型", "现在", "过去", "完成", "意思"], "parse": "verb"},
    {"out": "adj_adv",      "sheet": "Adjektive", "columns": ["形容词", "意思"],                     "parse": "adj"},
    {"out": "phrasen",      "sheet": "Phrasen",   "columns": ["词组", "意思"],                       "parse": "phrase"},
]

# ── A 级格式（A1 / A2）：excel 文件名 / sheet / 字段映射(json字段 -> excel列) ──
A_TEMPLATES = [
    {"out": "adj_adv",      "excel": "Adjektive.xlsx", "sheet": "AdjAdv",
     "field_map": {"原型": "原型", "比较级": "比较级", "最高级": "最高级", "意思": "意思"}},
    {"out": "phrasen",      "excel": "Adjektive.xlsx", "sheet": "AdvPhrasen",
     "field_map": {"词组": "单词", "意思": "意思"}},
    {"out": "nomen_obj",    "excel": "Nomen.xlsx", "sheet": "Obj",
     "field_map": {"单数": "单数", "复数": "复数", "意思": "意思"}},
    {"out": "nomen_people", "excel": "Nomen.xlsx", "sheet": "人",
     "field_map": {"单数男": "单数男", "复数男": "复数男", "意思男": "意思男",
                   "单数女": "单数女", "复数女": "复数女", "意思女": "意思女"}},
    {"out": "verben_base",  "excel": "Verben.xlsx", "sheet": "GrundVerben",
     "field_map": {"原型": "原型", "现在": "现在", "过去": "过去", "完成": "完成", "意思": "意思"}},
    {"out": "phrasen",      "excel": "Verben.xlsx", "sheet": "VerbenPhrasen",
     "field_map": {"词组": "词组", "意思": "意思"}},
]

# json 层面的 deck 列表（step2 / step3 用）
DECKS = [
    {"json": f"public/data/{out}.json", "sentence_type": m["sentence_type"]}
    for out, m in DECKS_META.items()
]


def _excel_jobs():
    """展开成 (每个笔记文件夹 × 每张表) 的导入任务，按文件夹自动选 DW / A 级格式。"""
    import os
    import dw_parse
    from step1_add_word import mapping_parser
    for notes_dir in NOTES_DIRS:
        dw_path = os.path.join(notes_dir, DW_EXCEL)
        if os.path.exists(dw_path):
            for t in DW_TEMPLATES:
                yield {
                    "json": f"public/data/{t['out']}.json",
                    "excel": dw_path,
                    "sheet": t["sheet"],
                    "key_fields": DECKS_META[t["out"]]["key_fields"],
                    "columns": t["columns"],
                    "parse": dw_parse.PARSERS[t["parse"]],
                }
        else:
            for t in A_TEMPLATES:
                yield {
                    "json": f"public/data/{t['out']}.json",
                    "excel": os.path.join(notes_dir, t["excel"]),
                    "sheet": t["sheet"],
                    "key_fields": DECKS_META[t["out"]]["key_fields"],
                    "columns": list(t["field_map"].values()),
                    "parse": mapping_parser(t["field_map"]),
                }


def _docx_sources():
    import os
    for notes_dir in NOTES_DIRS:
        p = os.path.join(notes_dir, SENTENCE_DOCX_NAME)
        if os.path.exists(p):
            yield p


# ── docx -> sentences.json（合并去重，不覆盖）─────────────
# sentences.json: [{ "例句": "...", "翻译": "..." }]，按加入顺序
def _read_docx_paragraphs(path):
    import xml.etree.ElementTree as ET
    import zipfile
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    lines = []
    for p in root.iter(ns + "p"):
        text = "".join(t.text for t in p.iter(ns + "t") if t.text).strip()
        if text:
            lines.append(text)
    return lines


def refresh_sentences_json(docx_sources, out_path):
    import json
    import os
    from step3_add_translation import save_json

    existing = []
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    seen = {e["例句"] for e in existing}
    merged = list(existing)
    added = 0
    for src in docx_sources:
        for line in _read_docx_paragraphs(src):
            line = line.replace("\xa0", " ").strip()
            if line and line not in seen:
                seen.add(line)
                merged.append({"例句": line, "翻译": ""})
                added += 1

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    save_json(out_path, merged)
    print(f"sentences.json: 原 {len(existing)} 句，新增 {added} 句，共 {len(merged)} 句 → {out_path}")


# ── 主流程 ───────────────────────────────────────────────
STEPS = ["sentences", "excel", "examples", "translation"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=STEPS, help="只跑这一步")
    ap.add_argument("--skip", choices=STEPS, action="append", default=[], help="跳过某步（可多次）")
    ap.add_argument("--sentence-mode", choices=["normal", "new_example", "upgrade"],
                    default=SENTENCE_MODE, help="覆盖 build.py 里的 SENTENCE_MODE")
    ap.add_argument("--docx", nargs="+", metavar="PATH",
                    help="sentences 步骤改读这些 docx（初始化用），代替 NOTES_DIRS 里的 sentences.docx")
    args = ap.parse_args()

    todo = [args.only] if args.only else [s for s in STEPS if s not in args.skip]
    print(f"笔记文件夹: {NOTES_DIRS}")
    print(f"将执行: {todo}\n")

    word_jsons = [d["json"] for d in DECKS]

    if "sentences" in todo:
        import step3_add_translation
        refresh_sentences_json(args.docx or list(_docx_sources()), SENTENCES_JSON)
        # 词库里已经翻过的同一句直接复用
        known = step3_add_translation.collect_translations(word_jsons)
        step3_add_translation.run([SENTENCES_JSON], OLLAMA_MODEL, OLLAMA_URL, known=known)

    if "excel" in todo:
        import step1_add_word
        step1_add_word.run(list(_excel_jobs()), update_existing=UPDATE_EXISTING_FROM_EXCEL)

    if "examples" in todo:
        import step2_add_sentence
        step2_add_sentence.run(DECKS, OPENSUB_FOLDER, SENTENCES_JSON, mode=args.sentence_mode)

    if "translation" in todo:
        import step3_add_translation
        known = step3_add_translation.collect_translations([SENTENCES_JSON])
        step3_add_translation.run(word_jsons, OLLAMA_MODEL, OLLAMA_URL, known=known)

    print("\n✅ 全部完成")


if __name__ == "__main__":
    main()
