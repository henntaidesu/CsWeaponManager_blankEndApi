# -*- coding: utf-8 -*-
"""
Steam库存历史记录表模型
"""

from typing import Dict, Any, List
from ..base_model import BaseModel


class SteamInventoryHistoryModel(BaseModel):
    """Steam库存历史记录表模型"""
    
    @classmethod
    def get_table_name(cls) -> str:
        return "steam_inventory_history"
    
    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'ID': {
                'type': 'TEXT',
                'primary_key': True,
                'not_null': True,
                'comment': '记录ID，格式：{steamId}_{trade_id}'
            },
            'trade_id': {
                'type': 'TEXT',
                'not_null': True,
                'default': None,
                'comment': '交易ID'
            },
            'steam_id': {
                'type': 'TEXT',
                'not_null': True,
                'default': None,
                'comment': 'Steam64 ID'
            },
            'trade_time': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '交易时间（原始格式）'
            },
            'trade_time_timestamp': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None,
                'comment': '交易时间戳（标准格式）'
            },
            'trade_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '交易类型：market_buy/market_sell/trade/receive/unpack/use/remove/other'
            },
            'trade_partner': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '交易对象'
            },
            'items_gave_count': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0,
                'comment': '给出物品数量'
            },
            'items_received_count': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0,
                'comment': '收到物品数量'
            },
            'items_gave_json': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '给出物品列表（JSON格式）'
            },
            'items_received_json': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '收到物品列表（JSON格式）'
            },
            'data_user': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '数据所属用户'
            },
            'created_at': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None,
                'comment': '记录创建时间'
            }
        }
    
    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'steam_inventory_history_idx_steam_id',
                'columns': ['steam_id']
            },
            {
                'name': 'steam_inventory_history_idx_trade_type',
                'columns': ['trade_type']
            },
            {
                'name': 'steam_inventory_history_idx_trade_time',
                'columns': ['trade_time_timestamp']
            },
            {
                'name': 'steam_inventory_history_idx_user',
                'columns': ['data_user']
            },
            {
                'name': 'steam_inventory_history_idx_trade_id',
                'columns': ['trade_id']
            }
        ]
    
    @classmethod
    def find_by_steam_id(cls, steam_id: str, limit: int = None, offset: int = None):
        """根据Steam ID查找历史记录"""
        return cls.find_all(
            "steam_id = ? ORDER BY trade_time_timestamp DESC", 
            (steam_id,), 
            limit, 
            offset
        )
    
    @classmethod
    def find_by_trade_type(cls, steam_id: str, trade_type: str, limit: int = None, offset: int = None):
        """根据Steam ID和交易类型查找历史记录"""
        return cls.find_all(
            "steam_id = ? AND trade_type = ? ORDER BY trade_time_timestamp DESC",
            (steam_id, trade_type),
            limit,
            offset
        )
    
    @classmethod
    def find_by_time_range(cls, steam_id: str, start_time: str, end_time: str, limit: int = None, offset: int = None):
        """根据时间范围查找历史记录"""
        return cls.find_all(
            "steam_id = ? AND DATE(trade_time_timestamp) BETWEEN ? AND ? ORDER BY trade_time_timestamp DESC",
            (steam_id, start_time, end_time),
            limit,
            offset
        )
    
    @classmethod
    def get_latest_by_steam_id(cls, steam_id: str):
        """获取指定Steam ID的最新一条记录"""
        records = cls.find_all(
            "steam_id = ? ORDER BY trade_time_timestamp DESC",
            (steam_id,),
            limit=1
        )
        return records[0] if records else None
    
    @classmethod
    def count_by_steam_id(cls, steam_id: str) -> int:
        """统计指定Steam ID的记录数"""
        return cls.count("steam_id = ?", (steam_id,))
    
    @classmethod
    def count_by_trade_type(cls, steam_id: str, trade_type: str) -> int:
        """统计指定Steam ID和交易类型的记录数"""
        return cls.count("steam_id = ? AND trade_type = ?", (steam_id, trade_type))
    
    @classmethod
    def get_trade_type_statistics(cls, steam_id: str) -> Dict[str, int]:
        """获取各类型交易的统计数据"""
        db = cls().db
        sql = """
        SELECT trade_type, COUNT(*) as count 
        FROM steam_inventory_history 
        WHERE steam_id = ?
        GROUP BY trade_type
        """
        
        try:
            result = db.execute_query(sql, (steam_id,))
            stats = {}
            for row in result:
                stats[row[0]] = row[1]
            return stats
        except Exception as e:
            print(f"获取交易类型统计失败: {e}")
            return {}

