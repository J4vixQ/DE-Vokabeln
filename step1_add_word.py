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
    columns,
    parse,
    update_existing: bool = False
):
    """
    仅新增不覆盖的版本：
    - 若旧 JSON 存在：只为“新键”添加条目；默认不改旧条目（避免覆盖例句/翻译）。
      若 update_existing=True，则仅在旧条目字段为空时用 Excel 值补齐（不改已有非空）。
    - 若旧 JSON 不存在：从 Excel 全量创建，并为每条补空的 例句/翻译。
    columns: 要读的 Excel 列；parse: {列名: 值} → (json 条目, warning)，解析不了抛 ValueError。
    """
    json_path = Path(json_path)

    # 读 Excel
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")
    except ValueError as e:
        print(f"⚠️  跳过 {excel_path} / {sheet_name}：{e}")
        return
    missing = [c for c in columns if c not in df.columns]
    if missing:
        print(f"⚠️  跳过 {excel_path} / {sheet_name}：缺少列 {missing}（现有列 {list(df.columns)}）")
        return
    df = df[columns].copy()
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
    errors, warnings, duplicates = [], [], []
    seen_in_sheet = {}

    for idx, row in df.iterrows():
        excel_row = idx + 2   # Excel 行号（第 1 行是表头）
        try:
            candidate, warning = parse({c: _strip(row[c]) for c in columns})
        except ValueError as e:
            errors.append(f"第 {excel_row} 行：{e}")
            continue
        if warning:
            warnings.append(f"第 {excel_row} 行：{warning}")
        key_tuple = tuple(_strip(candidate.get(k, "")) for k in key_fields)

        if not any(key_tuple):  # 键全空，跳过
            continue

        # 同一张表里重名（如 etwas bilden / jemanden bilden 去掉宾语后撞名）：只导入第一条
        if key_tuple in seen_in_sheet:
            duplicates.append(f"第 {excel_row} 行和第 {seen_in_sheet[key_tuple]} 行重名：{' / '.join(k for k in key_tuple if k)}")
            continue
        seen_in_sheet[key_tuple] = excel_row

        if key_tuple in existing_index:
            # 已存在：默认不覆盖；如需仅填补空值，可开启 update_existing=True
            if update_existing:
                entry = existing_index[key_tuple]
                for jf, v in candidate.items():
                    if not _strip(entry.get(jf, "")) and v:
                        entry[jf] = v
                        updated_count += 1
            continue

        # 新增：从 Excel 创建条目，并补空例句/翻译
        new_entry = dict(candidate)
        new_entry.setdefault("例句", "")
        new_entry.setdefault("翻译", "")
        data.append(new_entry)
        existing_index[key_tuple] = new_entry
        new_count += 1

    # 保存
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as fout:
        json.dump(data, fout, ensure_ascii=False, indent=2)

    print(f"完成：{excel_path} / {sheet_name} → 总 {len(data)} 条，新增 {new_count} 条，"
          f"{'补齐 '+str(updated_count)+' 处空值，' if update_existing else ''}"
          f"保存到 {json_path}")
    for title, items in (("❌ 解析失败，已跳过", errors),
                         ("⚠️  重名，只导入第一条", duplicates),
                         ("⚠️  已导入，但请检查", warnings)):
        if items:
            print(f"  {title}（{len(items)}）：")
            for line in items:
                print(f"    {line}")


def mapping_parser(field_map):
    """A 级表：按 field_map（json字段 -> excel列）直接拷贝。"""
    return lambda row: ({jf: row[ef] for jf, ef in field_map.items()}, None)


def run(jobs, update_existing: bool = False):
    """按 build.py 展开的导入任务批量把 Excel 写入 JSON。"""
    for d in jobs:
        create_json_from_excel(
            json_path=d["json"],
            excel_path=d["excel"],
            sheet_name=d["sheet"],
            key_fields=d["key_fields"],
            columns=d["columns"],
            parse=d["parse"],
            update_existing=update_existing,
        )


if __name__ == "__main__":
    from build import _excel_jobs
    run(list(_excel_jobs()))
