"""Step 3: 用本地 Ollama 批量补充中文翻译。

遍历 JSON 文件，找到 `翻译` 为空的条目，把 `例句` 发给 Ollama 翻译成中文写回。
前提：Ollama 已在本地运行，且已 pull 对应模型。
"""
import json
import os
import tempfile
import time
from pathlib import Path

import requests


def translate(sentence: str, model: str, ollama_url: str) -> str:
    """调用本地 Ollama 翻译一条德语例句为中文，只返回译文本身。"""
    prompt = (
        "请将以下德语句子翻译成中文。"
        "只输出中文译文，不要任何解释、标注或多余文字。\n\n"
        f"{sentence}"
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    resp = requests.post(ollama_url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["response"].strip()


def save_json(path: str, data: list):
    """原子写入，避免中途崩溃损坏文件。"""
    dir_name = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False,
                                     dir=dir_name, suffix=".tmp") as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name
    os.replace(tmp_path, path)


def check_online(ollama_url: str) -> bool:
    base = ollama_url.split("/api/")[0]
    try:
        requests.get(base, timeout=3)
        print("✅ Ollama 在线")
        return True
    except Exception as e:
        print(f"❌ 无法连接 Ollama：{e}\n请先运行 `ollama serve`")
        return False


def run(json_files, model, ollama_url, save_every: int = 20,
        skip_empty_sentence: bool = True):
    if not check_online(ollama_url):
        return

    for path in json_files:
        if not Path(path).exists():
            print(f"\n⚠️  跳过（文件不存在）: {path}")
            continue

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        pending = [e for e in data if e.get("翻译", "") == ""]
        if not pending:
            print(f"\n✅ {Path(path).name}：无需翻译，跳过")
            continue

        print(f"\n📄 {Path(path).name}  （{len(pending)} 条待翻译）")
        print("-" * 60)
        done = errors = 0

        for entry in pending:
            sentence = entry.get("例句", "").strip()
            if skip_empty_sentence and not sentence:
                continue
            try:
                entry["翻译"] = translate(sentence, model, ollama_url)
                done += 1
                word_key = (entry.get("原型") or entry.get("单数") or
                            entry.get("单数男") or entry.get("单词") or
                            entry.get("词组") or "?")
                print(f"  [{done:4d}] {word_key:20s}  →  {entry['翻译'][:40]}")
            except Exception as e:
                errors += 1
                print(f"  ❌ 翻译失败（{entry.get('原型', '?')}）: {e}")
                time.sleep(2)
                continue
            if done % save_every == 0:
                save_json(path, data)
                print(f"  💾 已保存进度（{done} 条）")

        save_json(path, data)
        print(f"  ✅ 完成：{done} 条翻译，{errors} 条失败 → 已保存 {path}")

    print("\n=== 最终统计 ===")
    for path in json_files:
        if not Path(path).exists():
            continue
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        empty = sum(1 for e in data if e.get("翻译", "") == "")
        print(f"  {Path(path).name:30s}  {'✅' if empty == 0 else f'⚠️  还剩 {empty} 条'}")


if __name__ == "__main__":
    from build import DECKS, OLLAMA_MODEL, OLLAMA_URL
    run([d["json"] for d in DECKS], OLLAMA_MODEL, OLLAMA_URL)
