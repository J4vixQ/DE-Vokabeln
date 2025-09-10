import json
import pandas as pd
from pathlib import Path

def _strip(s: str) -> str:
    return s.strip() if isinstance(s, str) else ""

def create_json_from_excel(
    json_path,
    excel_path,
    sheet_name,
    key_fields,
    field_map,
    update_existing: bool = False
):
    """
    仅新增不覆盖的版本：
    - 若旧 JSON 存在：只为“新键”添加条目；默认不改旧条目（避免覆盖例句/翻译）。
      若 update_existing=True，则仅在旧条目字段为空时用 Excel 值补齐（不改已有非空）。
    - 若旧 JSON 不存在：从 Excel 全量创建，并为每条补空的 例句/翻译。
    """
    json_path = Path(json_path)

    # 读 Excel
    df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")
    df = df[[field_map[f] for f in field_map]].copy()
    df = df[~df.apply(lambda r: all(_strip(v) == "" for v in r), axis=1)]

    # 读旧 JSON（若有）
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 旧数据建索引
        existing_index = {}
        for entry in data:
            key_tuple = tuple(_strip(entry.get(k, "")) for k in key_fields)
            if any(key_tuple):  # 至少有一个键非空
                existing_index[key_tuple] = entry
    else:
        data = []
        existing_index = {}

    new_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        # 构造本行条目的键与字段
        candidate = {json_field: _strip(row[excel_col])
                     for json_field, excel_col in field_map.items()}
        key_tuple = tuple(candidate.get(k, "") for k in key_fields)

        if not any(key_tuple):  # 键全空，跳过
            continue

        if key_tuple in existing_index:
            # 已存在：默认不覆盖；如需仅填补空值，可开启 update_existing=True
            if update_existing:
                entry = existing_index[key_tuple]
                for jf, ef in field_map.items():
                    if not _strip(entry.get(jf, "")) and _strip(row[ef]):
                        entry[jf] = _strip(row[ef])
                        updated_count += 1
            continue

        # 新增：从 Excel 创建条目，并补空例句/翻译
        new_entry = {jf: _strip(row[ef]) for jf, ef in field_map.items()}
        new_entry.setdefault("例句", "")
        new_entry.setdefault("翻译", "")
        data.append(new_entry)
        existing_index[key_tuple] = new_entry
        new_count += 1

    # 保存
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as fout:
        json.dump(data, fout, ensure_ascii=False, indent=2)

    print(f"完成：总 {len(data)} 条，新增 {new_count} 条，"
          f"{'补齐 '+str(updated_count)+' 处空值，' if update_existing else ''}"
          f"保存到 {json_path}")




# Adjektive
create_json_from_excel(
    json_path="public/data/adj_adv.json",
    excel_path="_A1/Adjektive.xlsx",
    sheet_name="AdjAdv",
    key_fields=["原型"],
    field_map={
        "原型": "原型",
        "比较级": "比较级",
        "最高级": "最高级",
        "意思": "意思"
    }
)

create_json_from_excel(
    json_path="public/data/adv_phrasen.json",
    excel_path="_A1/Adjektive.xlsx",
    sheet_name="AdvPhrasen",
    key_fields=["单词"],
    field_map={
        "单词": "单词",
        "意思": "意思"
    }
)

# Nomen
create_json_from_excel(
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

create_json_from_excel(
    json_path="public/data/nomen_people.json",
    excel_path="_A1/Nomen.xlsx",
    sheet_name="人",
    key_fields=["单数男", "复数男", "单数女", "复数女"],
    field_map={
        "单数男": "单数男",
        "复数男": "复数男",
        "意思男": "意思男",
        "单数女": "单数女",
        "复数女": "复数女",
        "意思女": "意思女"
    }
)


# Verben
create_json_from_excel(
    json_path="public/data/verben_base.json",
    excel_path="_A1/Verben.xlsx",
    sheet_name="GrundVerben",
    key_fields=["原型"],
    field_map={
        "原型": "原型",
        "现在": "现在",
        "过去": "过去",
        "完成": "完成",
        "意思": "意思"
    }
)

create_json_from_excel(
    json_path="public/data/verben_phrasen.json",
    excel_path="_A1/Verben.xlsx",
    sheet_name="VerbenPhrasen",
    key_fields=["词组"],
    field_map={
        "词组": "词组",
        "意思": "意思"
    }
)

