import json
import os
import re
import random
import tempfile

def strip_article(word):
    """去掉德语冠词"""
    return re.sub(r'^(der|die|das|Der|Die|Das)\s+', '', word).strip()

# 各类型 pattern & key 构造函数
def build_adj_patterns(entry):
    word = entry.get("单词", "")
    endings = ['', 'e', 'es', 'er', 'en', 'em', 'n', 's']
    patterns = [rf"\b{re.escape(word)}{end}\b" for end in endings]
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if word else None

def adj_key(entry):
    return entry.get("单词", "")

def build_steigerung_patterns(entry):
    stems = []
    for key in ["原型", "比较级", "最高级"]:
        v = entry.get(key)
        if v and v not in stems:
            stems.append(v)
    endings = ['', 'e', 'es', 'er', 'en', 'em', 'n', 's', 'ste', 'sten', 'ster', 'stes', 'ere', 'eren', 'erem', 'eres']
    patterns = []
    for stem in stems:
        patterns += [rf"\b{re.escape(stem)}{end}\b" for end in endings]
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if patterns else None

def steigerung_key(entry):
    return entry.get("原型", "")

def build_noun_pattern(entry):
    forms = []
    for key in ["单数", "复数"]:
        w = entry.get(key, '').strip()
        if w:
            w = strip_article(w)
            if w and w not in forms:
                forms.append(w)
    patterns = [rf"\b{re.escape(w)}\b" for w in forms]
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if patterns else None

def noun_key(entry):
    return strip_article(entry.get("单数", "")) or strip_article(entry.get("复数", ""))

def build_person_pattern(entry):
    fields = ["单数男", "复数男", "单数女", "复数女"]
    forms = []
    for key in fields:
        w = entry.get(key, '').strip()
        if w:
            w = strip_article(w)
            if w and w not in forms:
                forms.append(w)
    patterns = [rf"\b{re.escape(w)}\b" for w in forms]
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if patterns else None

def person_key(entry):
    for field in ["单数男", "复数男", "单数女", "复数女"]:
        candidate = strip_article(entry.get(field, ""))
        if candidate:
            return candidate
    return ""

def build_verb_patterns(entry):
    forms = set()
    if entry.get("原型"):
        forms.add(entry["原型"].strip())
    if entry.get("现在"):
        forms.add(entry["现在"].strip())
    if entry.get("过去"):
        forms.add(entry["过去"].strip())
    if entry.get("完成"):
        parts = entry["完成"].strip().split()
        if len(parts) >= 2:
            forms.add(parts[-1])
        else:
            forms.add(entry["完成"].strip())
    endings = ['', 'e', 'st', 't', 'en', 'te', 'test', 'tet', 'ten', 'et']
    patterns = []
    for f in forms:
        for end in endings:
            patterns.append(rf"\b{re.escape(f)}{end}\b")
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if patterns else None

def verb_key(entry):
    return entry.get("原型", "")

# 通用主流程
def fill_examples(json_path, opensub_folder, key_func, pattern_func, new_example=False):
    with open(json_path, "r", encoding="utf-8") as f:
        word_list = json.load(f)

    # 用于记录需要填充例句的 key
    if new_example:
        # 所有单词都需要新例句
        need_fill = set()
        entry_map = {}
        pattern_map = {}
        for entry in word_list:
            key = key_func(entry)
            if key:
                need_fill.add(key)
                entry_map[key] = entry
                pattern = pattern_func(entry)
                if pattern:
                    pattern_map[key] = pattern
        print(f"需要为所有单词寻找全新例句，总数: {len(need_fill)}")
    else:
        # 仅为空的需要例句
        need_fill = set()
        entry_map = {}
        pattern_map = {}
        for entry in word_list:
            if entry.get("例句", "") == "":
                key = key_func(entry)
                if key:
                    need_fill.add(key)
                    entry_map[key] = entry
                    pattern = pattern_func(entry)
                    if pattern:
                        pattern_map[key] = pattern
        print(f"需要填充例句数: {len(need_fill)}")

    # 遍历文献文件
    part_files = sorted(
        [f for f in os.listdir(opensub_folder) if f.startswith("part_") and f.endswith(".txt")],
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )
    random.shuffle(part_files)

    # 为所有需要的单词找例句
    for fname in part_files:
        if not need_fill:
            print("全部找到例句！")
            break
        fpath = os.path.join(opensub_folder, fname)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as fin:
            for line in fin:
                sent = line.strip()
                if not sent:
                    continue
                for word in list(need_fill):
                    if pattern_map[word].search(sent):
                        entry_map[word]["例句"] = sent
                        need_fill.remove(word)
                        print(f"找到例句: {word} → {sent}")
                        break

    # 如果 new_example=True 且还有没匹配到的单词，拷贝原有例句（如果有）
    if new_example and need_fill:
        print(f"有 {len(need_fill)} 个单词未找到全新例句，保留原例句（如有）")
        for word in need_fill:
            entry = entry_map[word]
            # 如果原来有例句，保留
            # 若没有则为空字符串
            entry["例句"] = entry.get("例句", "")

    print(f"剩余未匹配到的单词数: {len(need_fill)}")

    # out_json_path = json_path.replace(".json", "_with_examples.json")
    # with open(out_json_path, "w", encoding="utf-8") as fout:
    #     json.dump(word_list, fout, ensure_ascii=False, indent=2)
    # print(f"已完成，保存到 {out_json_path}")
    dir_name = os.path.dirname(json_path) or "."
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=dir_name, suffix=".tmp") as tmpf:
        json.dump(word_list, tmpf, ensure_ascii=False, indent=2)
        tmp_path = tmpf.name

    os.replace(tmp_path, json_path)
    print(f"已完成，覆盖保存到 {json_path}")

# 配置与批量调用
if __name__ == "__main__":
    configs = [
        {"json": "public/data/adj_base.json", "key_func": adj_key, "pattern_func": build_adj_patterns},
        {"json": "public/data/adj_steigerung.json", "key_func": steigerung_key, "pattern_func": build_steigerung_patterns},
        {"json": "public/data/nomen_obj.json", "key_func": noun_key, "pattern_func": build_noun_pattern},
        {"json": "public/data/nomen_people.json", "key_func": person_key, "pattern_func": build_person_pattern},
        {"json": "public/data/verben_base.json", "key_func": verb_key, "pattern_func": build_verb_patterns},
        # verben phrasen 需要手动添加
    ]
    opensub_folder = "resource/OpenSubtitles"
    for cfg in configs:
        print(f"\n正在处理 {cfg['json']}")
        fill_examples(cfg["json"], opensub_folder, cfg["key_func"], cfg["pattern_func"])
