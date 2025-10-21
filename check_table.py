# -*- coding: utf-8 -*-
"""检查weapon_classID表结构"""
from src.db_manager.database import DatabaseManager
from src.db_manager.yyyp.yyyp_weapon_classID import YyypWeaponClassIDModel

db = DatabaseManager()
table_name = 'weapon_classID'

print(f"\n=== 检查表 {table_name} ===")
print(f"表是否存在: {db.table_exists(table_name)}")

if db.table_exists(table_name):
    print("\n现有字段:")
    cols = db.get_table_columns(table_name)
    for col in cols:
        print(f"  - {col['name']} ({col['type']})")
    
    print("\n模型定义的字段:")
    for field_name, field_def in YyypWeaponClassIDModel.get_fields().items():
        print(f"  - {field_name} ({field_def['type']})")
    
    print("\n缺失的字段:")
    existing_names = {col['name'] for col in cols}
    required_names = set(YyypWeaponClassIDModel.get_fields().keys())
    missing = required_names - existing_names
    if missing:
        for field in missing:
            print(f"  [MISSING] {field}")
    else:
        print("  [OK] 没有缺失字段")

print("\n=== 尝试修复表结构 ===")
if YyypWeaponClassIDModel.ensure_table_exists():
    print("[OK] 表结构检查/修复成功")
else:
    print("[ERROR] 表结构检查/修复失败")

print("\n=== 再次检查字段 ===")
if db.table_exists(table_name):
    cols = db.get_table_columns(table_name)
    print("当前字段:")
    for col in cols:
        print(f"  - {col['name']} ({col['type']})")

