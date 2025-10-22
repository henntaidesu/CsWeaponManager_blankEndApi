# -*- coding: utf-8 -*-
"""
武器ClassID表模型
用于存储各平台武器的模板ID和相关信息（悠悠有品、BUFF、Steam）
"""

from typing import Dict, Any, List
from ..base_model import BaseModel


class WeaponClassIDModel(BaseModel):
    """武器ClassID表模型（统一管理各平台武器ID）"""

    @classmethod
    def get_table_name(cls) -> str:
        return "weapon_classID"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'steam_hash_name': {
                'type': 'TEXT',
                'primary_key': True,
                'not_null': True,
                'default': None
            },
            'yyyp_id': {
                'type': 'INTEGER',
                'primary_key': False,
                'not_null': False,
                'default': None
            },
            'buff_id': {
                'type': 'INTEGER',
                'primary_key': False,
                'not_null': False,
                'default': None
            },
            'steam_id': {
                'type': 'INTEGER',
                'primary_key': False,
                'not_null': False,
                'default': None
            },
            'yyyp_class_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'buff_class_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'market_listing_item_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'item_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'float_range': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'Rarity': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            }
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        """定义索引"""
        return [
            {
                'name': 'idx_yyyp_id',
                'columns': ['yyyp_id']
            },
            {
                'name': 'idx_buff_id',
                'columns': ['buff_id']
            },
            {
                'name': 'idx_steam_id',
                'columns': ['steam_id']
            },
            {
                'name': 'idx_yyyp_class_name',
                'columns': ['yyyp_class_name']
            },
            {
                'name': 'idx_buff_class_name',
                'columns': ['buff_class_name']
            },
            {
                'name': 'idx_weapon_type',
                'columns': ['weapon_type']
            },
            {
                'name': 'idx_weapon_name',
                'columns': ['weapon_name']
            },
            {
                'name': 'idx_item_name',
                'columns': ['item_name']
            },
            {
                'name': 'idx_float_range',
                'columns': ['float_range']
            },
            {
                'name': 'idx_rarity',
                'columns': ['Rarity']
            }
        ]

    @classmethod
    def find_by_weapon_info(cls, weapon_type: str = None, weapon_name: str = None, item_name: str = None):
        """根据武器信息查询"""
        conditions = []
        params = []

        if weapon_type:
            conditions.append("[weapon_type] = ?")
            params.append(weapon_type)

        if weapon_name:
            conditions.append("[weapon_name] = ?")
            params.append(weapon_name)

        if item_name:
            conditions.append("[item_name] = ?")
            params.append(item_name)

        if not conditions:
            return cls.find_all()

        where_clause = " AND ".join(conditions)
        return cls.find_all(where=where_clause, params=tuple(params))

    @classmethod
    def find_by_market_listing_item_name(cls, market_listing_item_name: str):
        """根据Steam市场商品名称查询"""
        return cls.find_all(where="[market_listing_item_name] = ?", params=(market_listing_item_name,))


    @classmethod
    def find_by_yyyp_id(cls, yyyp_id: int):
        """根据悠悠有品ID查询"""
        return cls.find_all(where="[yyyp_id] = ?", params=(yyyp_id,))

    @classmethod
    def find_by_buff_id(cls, buff_id: int):
        """根据BUFF ID查询"""
        return cls.find_all(where="[buff_id] = ?", params=(buff_id,))

    @classmethod
    def find_by_steam_id(cls, steam_id: int):
        """根据Steam ID查询"""
        return cls.find_all(where="[steam_id] = ?", params=(steam_id,))

    @classmethod
    def find_by_steam_hash_name(cls, steam_hash_name: str):
        """根据Steam Hash Name查询"""
        return cls.find_all(where="[steam_hash_name] = ?", params=(steam_hash_name,))

    @classmethod
    def find_by_rarity(cls, rarity: str):
        """根据稀有度查询"""
        return cls.find_all(where="[Rarity] = ?", params=(rarity,))

    @classmethod
    def find_by_float_range(cls, float_range: str):
        """根据品质范围查询"""
        return cls.find_all(where="[float_range] = ?", params=(float_range,))


    @classmethod
    def batch_insert_or_update(cls, weapon_list: List[Dict[str, Any]], platform: str = 'yyyp') -> int:
        """
        批量插入或更新武器数据（yyyp和steam平台专用）
        :param weapon_list: 武器数据列表
        :param platform: 平台标识 ('yyyp', 'steam')
        :return: 成功处理的数量
        """
        success_count = 0
        id_field_map = {
            'yyyp': 'yyyp_id',
            'steam': 'steam_id'
        }
        id_field = id_field_map.get(platform, 'yyyp_id')

        for weapon_data in weapon_list:
            try:
                # 兼容旧数据：如果传入的是'Id'字段，根据平台映射到对应字段
                if 'Id' in weapon_data and id_field not in weapon_data:
                    weapon_data[id_field] = weapon_data.pop('Id')

                platform_id = weapon_data.get(id_field)
                if not platform_id:
                    print(f"武器数据缺少{id_field}字段，跳过")
                    continue

                # 根据平台查询是否已存在
                existing_list = None

                if platform == 'yyyp':
                    existing_list = cls.find_by_yyyp_id(platform_id)
                elif platform == 'steam':
                    existing_list = cls.find_by_steam_id(platform_id)

                existing = existing_list[0] if existing_list else None

                if existing:
                    # 更新现有记录（更新所有字段）
                    for key, value in weapon_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)

                    if existing.save():
                        success_count += 1
                else:
                    # 插入新记录
                    new_weapon = cls(**weapon_data)
                    if new_weapon.save():
                        success_count += 1

            except Exception as e:
                print(f"处理武器数据失败 ({id_field}: {weapon_data.get(id_field)}): {e}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
                continue

        return success_count

    @classmethod
    def batch_update_buff_id(cls, weapon_list: List[Dict[str, Any]]) -> int:
        """
        BUFF专用：批量更新或插入buff_id和buff_class_name（UPSERT操作）
        :param weapon_list: 武器数据列表，每项包含 buff_id, steam_hash_name, buff_class_name
        :return: 成功处理的数量
        """
        success_count = 0
        skip_count = 0
        insert_count = 0
        update_count = 0
        db = cls().db

        for weapon_data in weapon_list:
            try:
                buff_id = weapon_data.get('buff_id')
                steam_hash_name = weapon_data.get('steam_hash_name')
                buff_class_name = weapon_data.get('buff_class_name')

                if not buff_id:
                    print(f"BUFF数据缺少buff_id字段，跳过")
                    skip_count += 1
                    continue

                if not steam_hash_name:
                    print(f"BUFF数据缺少steam_hash_name字段，跳过: buff_id={buff_id}")
                    skip_count += 1
                    continue

                # 先尝试 UPDATE
                sql_update = f'UPDATE {cls.get_table_name()} SET [buff_id] = ?, [buff_class_name] = ? WHERE [steam_hash_name] = ?'
                affected_rows = db.execute_update(sql_update, (buff_id, buff_class_name, steam_hash_name))

                if affected_rows > 0:
                    # 更新成功
                    success_count += 1
                    update_count += 1
                    print(f"✅ 更新BUFF数据成功: buff_id={buff_id}, buff_class_name={buff_class_name}, steam_hash_name={steam_hash_name}")
                else:
                    # 未找到记录，执行 INSERT
                    sql_insert = f'INSERT INTO {cls.get_table_name()} ([steam_hash_name], [buff_id], [buff_class_name]) VALUES (?, ?, ?)'
                    db.execute_insert(sql_insert, (steam_hash_name, buff_id, buff_class_name))
                    success_count += 1
                    insert_count += 1
                    print(f"✅ 插入新BUFF数据: buff_id={buff_id}, buff_class_name={buff_class_name}, steam_hash_name={steam_hash_name}")

            except Exception as e:
                print(f"处理BUFF数据失败: buff_id={weapon_data.get('buff_id')}, 错误: {e}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
                continue

        print(f"BUFF更新完成: 总成功 {success_count} 条 (更新 {update_count} 条, 插入 {insert_count} 条), 跳过 {skip_count} 条")
        return success_count

    @classmethod
    def batch_update_steam_hash_name(cls, weapon_list: List[Dict[str, Any]]) -> int:
        """
        Steam专用：批量插入steam_hash_name
        :param weapon_list: 武器数据列表，每项包含 data_hash_name, market_listing_item_name, weapon_type, weapon_name, item_name
        :return: 成功处理的数量
        """
        success_count = 0
        skip_count = 0
        db = cls().db

        for weapon_data in weapon_list:
            try:
                data_hash_name = weapon_data.get('data_hash_name')
                market_listing_item_name = weapon_data.get('market_listing_item_name')
                weapon_type = weapon_data.get('weapon_type')
                weapon_name = weapon_data.get('weapon_name')
                item_name = weapon_data.get('item_name')

                if not data_hash_name:
                    skip_count += 1
                    continue

                # 使用 INSERT OR IGNORE 避免主键冲突
                sql_insert = f'''INSERT OR IGNORE INTO {cls.get_table_name()} 
                                ([steam_hash_name], [weapon_type], [weapon_name], [item_name], [market_listing_item_name]) 
                                VALUES (?, ?, ?, ?, ?)'''
                affected_rows = db.execute_insert(sql_insert, (data_hash_name, weapon_type, weapon_name, item_name, market_listing_item_name))
                
                if affected_rows > 0:
                    success_count += 1
                else:
                    # 数据已存在，被忽略
                    skip_count += 1

            except Exception as e:
                print(f"处理Steam数据失败: {e}")
                continue

        print(f"Steam插入完成: 总成功 {success_count} 条, 跳过 {skip_count} 条（重复）")
        return success_count
