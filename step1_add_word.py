import json
import pandas as pd
from pathlib import Path

def update_json_from_excel(json_path, excel_path, sheet_name, key_fields, field_map):
    # key_fields 可以是 ['单数男', '复数男']
    json_path = Path(json_path)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    # 1. 构建主键 -> entry 映射。允许多个 key 指向同一个 entry
    db = {}
    for entry in data:
        for kf in key_fields:
            key = entry.get(kf, "").strip()
            if key:
                db[key] = entry

    df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")
    new_items = 0

    for i, row in df.iterrows():
        matched_entry = None
        for kf in key_fields:
            key = row[field_map[kf]].strip()
            if key and key in db:
                matched_entry = db[key]
                break

        if matched_entry:
            # 已有 entry，更新字段（可根据需求只覆盖意思类字段）
            for field in field_map:
                val = row[field_map[field]].strip()
                if val:
                    matched_entry[field] = val
            # 例句/翻译保持不动
        else:
            # 新增 entry，主键为所有非空 key_fields 字段
            entry = {field: row[field_map[field]].strip() for field in field_map}
            entry.setdefault("例句", "")
            entry.setdefault("翻译", "")
            data.append(entry)
            for kf in key_fields:
                key = entry.get(kf, "").strip()
                if key:
                    db[key] = entry
            new_items += 1

    # 4. 保存
    out_path = json_path
    with open(out_path, "w", encoding="utf-8") as fout:
        json.dump(data, fout, ensure_ascii=False, indent=2)

    print(f"完成：共 {len(data)} 条，新增 {new_items} 条，保存到 {out_path}")




update_json_from_excel(
    json_path="public/data/adj_base.json",
    excel_path="_A1/Adjektive.xlsx",
    sheet_name="Adj",
    key_fields=["单词"],
    field_map={
        "单词": "单词",
        "意思": "意思"
    }
)

update_json_from_excel(
    json_path="public/data/adj_steigerung.json",
    excel_path="_A1/Adjektive.xlsx",
    sheet_name="Gut",
    key_fields=["原型"],
    field_map={
        "原型": "原型",
        "比较级": "比较级",
        "最高级": "最高级",
        "意思": "意思"
    }
)

update_json_from_excel(
    json_path="public/data/nomen_obj.json",
    excel_path="_A1/Nomen.xlsx",
    sheet_name="Obj",
    key_fields=["单数", "复数"],
    field_map={
        "单数": "单数",
        "复数": "复数",
        "意思": "意思"
    }
)

update_json_from_excel(
    json_path="public/data/nomen_people.json",
    excel_path="_A1/Nomen.xlsx",
    sheet_name="人",
    key_fields=["单数男", "复数男"],
    field_map={
        "单数男": "单数男",
        "复数男": "复数男",
        "意思男": "意思男",
        "单数女": "单数女",
        "复数女": "复数女",
        "意思女": "意思女"
    }
)

update_json_from_excel(
    json_path="public/data/verben_base.json",
    excel_path="_A1/Verben.xlsx",
    sheet_name="Grund Verben",
    key_fields=["原型"],
    field_map={
        "原型": "原型",
        "现在": "现在(第三人称单数)",
        "过去": "过去(第三人称单数)",
        "完成": "完成(第三人称单数)",
        "意思": "意思"
    }
)

update_json_from_excel(
    json_path="public/data/verben_phrasen.json",
    excel_path="_A1/Verben.xlsx",
    sheet_name="Verben Phrasen",
    key_fields=["词组"],
    field_map={
        "词组": "词组",
        "意思": "意思"
    }
)