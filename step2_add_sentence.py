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
    word = entry.get("词组", "")
    endings = ['', 'e', 'es', 'er', 'en', 'em', 'n', 's']
    patterns = [rf"\b{re.escape(word)}{end}\b" for end in endings]
    return re.compile('|'.join(patterns), flags=re.IGNORECASE) if word else None

def adj_key(entry):
    return entry.get("词组", "")

def build_steigerung_patterns(entry):
    stems = []
    for key in ["原型", "比较级", "最高级"]:
        v = entry.get(key)
        if v and v not in stems:
            stems.append(v)
    endings = ['', 'e', 'es', 'er', 'en', 'em', 'n', 's', 'ste', 'sten', 'ster', 'stes', 'stem', 'ere', 'eren', 'erem', 'eres']
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
def fill_examples(json_path, opensub_folder, key_func, pattern_func, new_example=False,
                  priority_file=None, upgrade_priority=False):
    """
    upgrade_priority=True：只用 priority_file 扫全部条目，
    匹配到则替换例句+清空翻译，匹配不到则原样不动，不碰 OpenSubtitles。
    """
    with open(json_path, "r", encoding="utf-8") as f:
        word_list = json.load(f)

    # 建立全量 entry_map / pattern_map（upgrade_priority 需要扫全部）
    need_fill = set()
    entry_map = {}
    pattern_map = {}

    if upgrade_priority:
        for entry in word_list:
            key = key_func(entry)
            if key:
                need_fill.add(key)
                entry_map[key] = entry
                pattern = pattern_func(entry)
                if pattern:
                    pattern_map[key] = pattern
        print(f"upgrade_priority 模式：扫全部条目，共 {len(need_fill)} 个")
    elif new_example:
        # 所有单词都需要新例句
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

    def assign(word, sent):
        """写入例句；若句子有变化，同时清空翻译。"""
        entry = entry_map[word]
        old = entry.get("例句", "")
        entry["例句"] = sent
        if sent != old:
            entry["翻译"] = ""
        need_fill.remove(word)
        print(f"找到例句: {word} → {sent}")

    # ── 第一轮：优先语料（手工例句）──────────────────────
    if priority_file and need_fill:
        with open(priority_file, "r", encoding="utf-8") as f:
            priority_sents = [line.strip().replace('\xa0', ' ') for line in f if line.strip()]
        print(f"优先语料共 {len(priority_sents)} 句，开始匹配…")
        for sent in priority_sents:
            if not need_fill:
                break
            for word in list(need_fill):
                if pattern_map[word].search(sent):
                    assign(word, sent)
                    break
        print(f"优先语料匹配后剩余: {len(need_fill)}")

    # ── 第二轮：OpenSubtitles fallback ──────────────────
    if need_fill:
        part_files = sorted(
            [f for f in os.listdir(opensub_folder) if f.startswith("part_") and f.endswith(".txt")],
            key=lambda x: int(x.split("_")[1].split(".")[0])
        )
        random.shuffle(part_files)

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
                            assign(word, sent)
                            break

    # upgrade_priority 模式：未匹配到的原样不动（不写入任何内容）
    if upgrade_priority:
        print(f"upgrade_priority 完成：替换了 {len(entry_map) - len(need_fill)} 条，"
              f"{len(need_fill)} 条未匹配（原例句保留）")
        # need_fill 里剩余的词原样不动，直接跳过

    # 如果 new_example=True 且还有没匹配到的单词，拷贝原有例句（如果有）
    elif new_example and need_fill:
        print(f"有 {len(need_fill)} 个单词未找到全新例句，保留原例句（如有）")
        for word in need_fill:
            entry = entry_map[word]
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
        {"json": "public/data/adv_phrasen.json", "key_func": adj_key, "pattern_func": build_adj_patterns},
        {"json": "public/data/adj_adv.json", "key_func": steigerung_key, "pattern_func": build_steigerung_patterns},
        {"json": "public/data/nomen_obj.json", "key_func": noun_key, "pattern_func": build_noun_pattern},
        {"json": "public/data/nomen_people.json", "key_func": person_key, "pattern_func": build_person_pattern},
        {"json": "public/data/verben_base.json", "key_func": verb_key, "pattern_func": build_verb_patterns},
        # verben phrasen 需要手动添加
    ]
    opensub_folder  = "resource/OpenSubtitles"
    priority_file   = "public/data/sentences.txt"

    # ── 普通模式：新词填空 + sentences.txt 优先，找不到再 fallback 到 corpus ──
    for cfg in configs:
        print(f"\n正在处理 {cfg['json']}")
        fill_examples(cfg["json"], opensub_folder, cfg["key_func"], cfg["pattern_func"],
                      priority_file=priority_file)

    # ── 全量更新模式：所有词重新从语料找例句，找不到保留原句 ──
    # sentences.txt 优先，找不到再 fallback 到 OpenSubtitles。
    # 例句有变化的条目会自动清空翻译，运行完后需要重新跑 step3.ipynb 补充翻译。
    # 用法：取消下面注释，运行一次，完成后再注释回来。
    #
    # for cfg in configs:
    #     print(f"\n[new_example] 正在处理 {cfg['json']}")
    #     fill_examples(cfg["json"], opensub_folder, cfg["key_func"], cfg["pattern_func"],
    #                   priority_file=priority_file, new_example=True)

    # ── 一次性升级模式：把现有 corpus 例句替换成 sentences.txt 的高质量版本 ──
    # 匹配到则替换+清翻译，匹配不到则原样不动，不碰 OpenSubtitles。
    # 运行完后需要重新跑 step3.ipynb 补充翻译。
    # 用法：取消下面注释，运行一次，完成后再注释回来。
    #
    # for cfg in configs:
    #     print(f"\n[upgrade] 正在处理 {cfg['json']}")
    #     fill_examples(cfg["json"], opensub_folder, cfg["key_func"], cfg["pattern_func"],
    #                   priority_file=priority_file, upgrade_priority=True)
