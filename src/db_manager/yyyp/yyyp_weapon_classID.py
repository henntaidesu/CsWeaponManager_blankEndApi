# -*- coding: utf-8 -*-
"""
YYYP武器ClassID表模型
用于存储悠悠有品武器的模板ID和相关信息
"""

from typing import Dict, Any, List
from ..base_model import BaseModel


class YyypWeaponClassIDModel(BaseModel):
    """YYYP武器ClassID表模型"""
    
    @classmethod
    def get_table_name(cls) -> str:
        return "yyyp_weapon_classID"
    
    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'Id': {
                'type': 'INTEGER',
                'primary_key': True,
                'not_null': True
            },
            'CommodityName': {
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
            'created_at': {
                'type': 'DATETIME',
                'not_null': False,
                'default': 'CURRENT_TIMESTAMP'
            },
            'updated_at': {
                'type': 'DATETIME',
                'not_null': False,
                'default': 'CURRENT_TIMESTAMP'
            }
        }
    
    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        """定义索引"""
        return [
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
    def batch_insert_or_update(cls, weapon_list: List[Dict[str, Any]]) -> int:
        """批量插入或更新武器数据"""
        success_count = 0
        
        for weapon_data in weapon_list:
            try:
                # 检查是否已存在
                existing = cls.find_by_id(Id=weapon_data.get('Id'))
                
                if existing:
                    # 更新现有记录
                    for key, value in weapon_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    
                    # 更新时间戳
                    from datetime import datetime
                    existing.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if existing.save():
                        success_count += 1
                else:
                    # 插入新记录
                    from datetime import datetime
                    weapon_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    weapon_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    new_weapon = cls(**weapon_data)
                    if new_weapon.save():
                        success_count += 1
            
            except Exception as e:
                print(f"处理武器数据失败 (Id: {weapon_data.get('Id')}): {e}")
                continue
        
        return success_count

