"""一键更新词库：Excel -> JSON -> 例句 -> 翻译。

日常用法：
    python build.py                 # 跑完整流程
    python build.py --only excel    # 只做某一步：excel / sentences / examples / translation
    python build.py --skip translation
    python build.py --sentence-mode upgrade   # 用 sentences.docx 升级已有例句

============================================================
升级到新阶段（B1、B2…）时，唯一要改的就是下面这一行：
把新笔记文件夹加进列表即可。文件夹内的 Excel 名 / sheet 名 /
sentences.docx 名都保持一致，其余不用动。
============================================================
"""
NOTES_DIRS = ["_A2"]

# Ollama 翻译模型
OLLAMA_MODEL = "qwen2.5:14b"

# 例句填充模式（也可用 --sentence-mode 临时覆盖）：
#   "normal"      只给「例句为空」的词找例句：sentences.txt 优先，找不到 fallback 到 OpenSubtitles
#   "new_example" 所有词都重新找一遍全新例句；没找到的 → 保留原有例句，不删除
#   "upgrade"     只把已有例句替换成 sentences.txt 里的高质量版本；匹配不到就原样不动，不碰 OpenSubtitles
# 例句有变化的条目会自动清空「翻译」，跑完 examples 后记得再跑 translation。
SENTENCE_MODE = "normal"

# ────────────────────────────────────────────────────────
# 以下为固定结构，除非笔记的表格结构变了，一般不用改。
# ────────────────────────────────────────────────────────
import argparse
import itertools
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

OLLAMA_URL = "http://localhost:11434/api/generate"
SENTENCES_TXT = "public/data/sentences.txt"
OPENSUB_FOLDER = "resource/OpenSubtitles"
UPDATE_EXISTING_FROM_EXCEL = False   # True: 用 Excel 补齐旧条目的空字段（不覆盖非空）

# 每个笔记文件夹里都有这些 docx（按优先级）
SENTENCE_DOCX_NAMES = [
    "sentences.docx",
    "sentences from the internet.docx",
]

# 词库表结构：excel 文件名 / sheet / 主键 / 字段映射(json字段 -> excel列) / 输出 json / step2 匹配器
# sentence_type=None 表示例句需手动填（phrasen）。
DECK_TEMPLATES = [
    {"out": "adj_adv",       "excel": "Adjektive.xlsx", "sheet": "AdjAdv",
     "key_fields": ["原型"],
     "field_map": {"原型": "原型", "比较级": "比较级", "最高级": "最高级", "意思": "意思"},
     "sentence_type": "steigerung"},
    {"out": "adv_phrasen",   "excel": "Adjektive.xlsx", "sheet": "AdvPhrasen",
     "key_fields": ["词组"],
     "field_map": {"词组": "单词", "意思": "意思"},
     "sentence_type": None},
    {"out": "nomen_obj",     "excel": "Nomen.xlsx", "sheet": "Obj",
     "key_fields": ["单数", "复数"],
     "field_map": {"单数": "单数", "复数": "复数", "意思": "意思"},
     "sentence_type": "noun"},
    {"out": "nomen_people",  "excel": "Nomen.xlsx", "sheet": "人",
     "key_fields": ["单数男", "复数男", "单数女", "复数女"],
     "field_map": {"单数男": "单数男", "复数男": "复数男", "意思男": "意思男",
                   "单数女": "单数女", "复数女": "复数女", "意思女": "意思女"},
     "sentence_type": "person"},
    {"out": "verben_base",   "excel": "Verben.xlsx", "sheet": "GrundVerben",
     "key_fields": ["原型"],
     "field_map": {"原型": "原型", "现在": "现在", "过去": "过去", "完成": "完成", "意思": "意思"},
     "sentence_type": "verb"},
    {"out": "verben_phrasen", "excel": "Verben.xlsx", "sheet": "VerbenPhrasen",
     "key_fields": ["词组"],
     "field_map": {"词组": "词组", "意思": "意思"},
     "sentence_type": None},
]

# json 层面的 deck 列表（step2 / step3 用），每个模板一条
DECKS = [
    {"json": f"public/data/{t['out']}.json", "sentence_type": t["sentence_type"]}
    for t in DECK_TEMPLATES
]


def _excel_jobs():
    """展开成 (每个笔记文件夹 × 每个词库表) 的导入任务。"""
    for notes_dir, t in itertools.product(NOTES_DIRS, DECK_TEMPLATES):
        yield {
            "json": f"public/data/{t['out']}.json",
            "excel": f"{notes_dir}/{t['excel']}",
            "sheet": t["sheet"],
            "key_fields": t["key_fields"],
            "field_map": t["field_map"],
        }


def _docx_sources():
    import os
    for notes_dir in NOTES_DIRS:
        for name in SENTENCE_DOCX_NAMES:
            p = os.path.join(notes_dir, name)
            if os.path.exists(p):
                yield p


# ── docx -> sentences.txt（合并去重，不覆盖）──────────────
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


def refresh_sentences_txt(docx_sources, out_path):
    import os
    import tempfile

    existing = []
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = [ln.strip() for ln in f if ln.strip()]

    seen = set(existing)
    merged = list(existing)
    added = 0
    for src in docx_sources:
        for line in _read_docx_paragraphs(src):
            line = line.replace("\xa0", " ").strip()
            if line and line not in seen:
                seen.add(line)
                merged.append(line)
                added += 1

    dir_name = os.path.dirname(out_path) or "."
    os.makedirs(dir_name, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False,
                                     dir=dir_name, suffix=".tmp") as tmp:
        tmp.write("\n".join(merged) + ("\n" if merged else ""))
        tmp_path = tmp.name
    os.replace(tmp_path, out_path)
    print(f"sentences.txt: 原 {len(existing)} 句，新增 {added} 句，共 {len(merged)} 句 → {out_path}")


# ── 主流程 ───────────────────────────────────────────────
STEPS = ["excel", "sentences", "examples", "translation"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=STEPS, help="只跑这一步")
    ap.add_argument("--skip", choices=STEPS, action="append", default=[], help="跳过某步（可多次）")
    ap.add_argument("--sentence-mode", choices=["normal", "new_example", "upgrade"],
                    default=SENTENCE_MODE, help="覆盖 build.py 里的 SENTENCE_MODE")
    args = ap.parse_args()

    todo = [args.only] if args.only else [s for s in STEPS if s not in args.skip]
    print(f"笔记文件夹: {NOTES_DIRS}")
    print(f"将执行: {todo}\n")

    if "excel" in todo:
        import step1_add_word
        step1_add_word.run(list(_excel_jobs()), update_existing=UPDATE_EXISTING_FROM_EXCEL)

    if "sentences" in todo:
        refresh_sentences_txt(list(_docx_sources()), SENTENCES_TXT)

    if "examples" in todo:
        import step2_add_sentence
        step2_add_sentence.run(DECKS, OPENSUB_FOLDER, SENTENCES_TXT, mode=args.sentence_mode)

    if "translation" in todo:
        import step3_add_translation
        step3_add_translation.run([d["json"] for d in DECKS], OLLAMA_MODEL, OLLAMA_URL)

    print("\n✅ 全部完成")


if __name__ == "__main__":
    main()
