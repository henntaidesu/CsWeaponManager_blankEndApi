# -*- coding: utf-8 -*-
"""
武器ClassID表模型
用于存储各平台武器的模板ID和相关信息（悠悠有品、BUFF、Steam）
"""

from typing import Dict, Any, List
from ..base_model import BaseModel


class YyypWeaponClassIDModel(BaseModel):
    """武器ClassID表模型（统一管理各平台武器ID）"""
    
    @classmethod
    def get_table_name(cls) -> str:
        return "weapon_classID"
    
    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
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
            'CommodityName': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'en_weapon_name': {
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
                'name': 'idx_en_weapon_name',
                'columns': ['en_weapon_name']
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
    def find_by_commodity_name(cls, commodity_name: str):
        """根据商品名称查询"""
        return cls.find_all(where="[CommodityName] = ?", params=(commodity_name,))
    
    @classmethod
    def find_by_en_weapon_name(cls, en_weapon_name: str):
        """根据英文武器名称查询"""
        return cls.find_all(where="[en_weapon_name] = ?", params=(en_weapon_name,))
    
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
        批量插入或更新武器数据
        :param weapon_list: 武器数据列表
        :param platform: 平台标识 ('yyyp', 'buff', 'steam')
        :return: 成功处理的数量
        """
        success_count = 0
        id_field_map = {
            'yyyp': 'yyyp_id',
            'buff': 'buff_id',
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

                if platform == 'buff':
                    # BUFF平台：优先通过en_weapon_name匹配已有记录，然后更新buff_id
                    en_weapon_name = weapon_data.get('en_weapon_name')
                    if en_weapon_name:
                        # 先通过en_weapon_name查找记录
                        existing_list = cls.find_by_en_weapon_name(en_weapon_name)
                        if not existing_list:
                            # 如果通过en_weapon_name找不到，再尝试通过buff_id查找
                            existing_list = cls.find_by_buff_id(platform_id)
                    else:
                        # 如果没有en_weapon_name，直接通过buff_id查找
                        existing_list = cls.find_by_buff_id(platform_id)
                elif platform == 'yyyp':
                    existing_list = cls.find_by_yyyp_id(platform_id)
                elif platform == 'steam':
                    existing_list = cls.find_by_steam_id(platform_id)

                existing = existing_list[0] if existing_list else None

                if existing:
                    # 更新现有记录
                    for key, value in weapon_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)

                    if existing.save():
                        success_count += 1
                        if platform == 'buff':
                            print(f"通过en_weapon_name匹配并更新buff_id: {platform_id}, en_weapon_name: {weapon_data.get('en_weapon_name')}")
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

