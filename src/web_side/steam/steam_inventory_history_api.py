# -*- coding: utf-8 -*-
"""
Steam库存历史记录API接口
"""

from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_inventory_history import SteamInventoryHistoryModel
from datetime import datetime
import json

steamInventoryHistoryV1 = Blueprint('steamInventoryHistoryV1', __name__)


@steamInventoryHistoryV1.route('/insert', methods=['POST'])
def insert_inventory_history():
    """插入库存历史记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        # 提取数据
        trade_id = data.get('trade_id')
        steam_id = data.get('steamId')
        
        if not trade_id or not steam_id:
            return jsonify({'success': False, 'error': '缺少必要字段'}), 400
        
        # 生成主键ID
        record_id = f"{steam_id}_{trade_id}"
        
        # 检查是否已存在
        existing = SteamInventoryHistoryModel.find_by_id(ID=record_id)
        if existing:
            return jsonify({
                'success': True,
                'message': '记录已存在，跳过插入',
                'data': {'id': record_id}
            }), 200
        
        # 创建新记录
        record = SteamInventoryHistoryModel()
        record.ID = record_id
        record.trade_id = trade_id
        record.steam_id = steam_id
        record.trade_time = data.get('trade_time', '')
        record.trade_time_timestamp = data.get('trade_time_timestamp')
        record.trade_type = data.get('trade_type', 'other')
        record.trade_partner = data.get('trade_partner', '')
        record.items_gave_count = data.get('items_gave_count', 0)
        record.items_received_count = data.get('items_received_count', 0)
        
        # 将物品列表转为JSON字符串存储
        items_gave = data.get('items_gave', [])
        items_received = data.get('items_received', [])
        record.items_gave_json = json.dumps(items_gave, ensure_ascii=False) if items_gave else None
        record.items_received_json = json.dumps(items_received, ensure_ascii=False) if items_received else None
        
        record.data_user = data.get('data_user', 'default')
        record.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存到数据库
        saved = record.save()
        
        if saved:
            return jsonify({
                'success': True,
                'message': '库存历史记录插入成功',
                'data': {'id': record_id}
            }), 200
        else:
            return jsonify({'success': False, 'error': '数据库保存失败'}), 500
            
    except Exception as e:
        print(f"插入库存历史记录错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/getLatestData/<steam_id>', methods=['GET'])
def get_latest_data(steam_id):
    """获取指定Steam ID的最新一条记录"""
    try:
        record = SteamInventoryHistoryModel.get_latest_by_steam_id(steam_id)
        
        if record:
            return jsonify({
                'success': True,
                'trade_id': record.trade_id,
                'trade_time': record.trade_time_timestamp,
                'trade_type': record.trade_type,
                'trade_partner': record.trade_partner
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '没有找到记录'
            }), 404
            
    except Exception as e:
        print(f"获取最新记录错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/getHistory/<steam_id>/<int:min>/<int:max>', methods=['GET'])
def get_history(steam_id, min, max):
    """获取库存历史记录（分页）"""
    try:
        records = SteamInventoryHistoryModel.find_by_steam_id(
            steam_id,
            limit=max,
            offset=min
        )
        
        data = []
        for record in records:
            # 解析JSON物品列表
            items_gave = json.loads(record.items_gave_json) if record.items_gave_json else []
            items_received = json.loads(record.items_received_json) if record.items_received_json else []
            
            data.append({
                'id': record.ID,
                'trade_id': record.trade_id,
                'steam_id': record.steam_id,
                'trade_time': record.trade_time,
                'trade_time_timestamp': record.trade_time_timestamp,
                'trade_type': record.trade_type,
                'trade_partner': record.trade_partner,
                'items_gave_count': record.items_gave_count,
                'items_received_count': record.items_received_count,
                'items_gave': items_gave,
                'items_received': items_received
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
        
    except Exception as e:
        print(f"获取历史记录错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/getHistoryByType/<steam_id>/<trade_type>/<int:min>/<int:max>', methods=['GET'])
def get_history_by_type(steam_id, trade_type, min, max):
    """根据交易类型获取历史记录（分页）"""
    try:
        records = SteamInventoryHistoryModel.find_by_trade_type(
            steam_id,
            trade_type,
            limit=max,
            offset=min
        )
        
        data = []
        for record in records:
            items_gave = json.loads(record.items_gave_json) if record.items_gave_json else []
            items_received = json.loads(record.items_received_json) if record.items_received_json else []
            
            data.append({
                'id': record.ID,
                'trade_id': record.trade_id,
                'steam_id': record.steam_id,
                'trade_time': record.trade_time,
                'trade_time_timestamp': record.trade_time_timestamp,
                'trade_type': record.trade_type,
                'trade_partner': record.trade_partner,
                'items_gave_count': record.items_gave_count,
                'items_received_count': record.items_received_count,
                'items_gave': items_gave,
                'items_received': items_received
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
        
    except Exception as e:
        print(f"获取历史记录错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/getStatistics/<steam_id>', methods=['GET'])
def get_statistics(steam_id):
    """获取交易统计数据"""
    try:
        # 总记录数
        total_count = SteamInventoryHistoryModel.count_by_steam_id(steam_id)
        
        # 各类型统计
        type_stats = SteamInventoryHistoryModel.get_trade_type_statistics(steam_id)
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'market_buy': type_stats.get('market_buy', 0),
                'market_sell': type_stats.get('market_sell', 0),
                'trade': type_stats.get('trade', 0),
                'unpack': type_stats.get('unpack', 0),
                'receive': type_stats.get('receive', 0),
                'use': type_stats.get('use', 0),
                'remove': type_stats.get('remove', 0),
                'other': type_stats.get('other', 0)
            }
        }), 200
        
    except Exception as e:
        print(f"获取统计数据错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/getHistoryByTimeRange/<steam_id>/<start_date>/<end_date>/<int:min>/<int:max>', methods=['GET'])
def get_history_by_time_range(steam_id, start_date, end_date, min, max):
    """根据时间范围获取历史记录（分页）"""
    try:
        records = SteamInventoryHistoryModel.find_by_time_range(
            steam_id,
            start_date,
            end_date,
            limit=max,
            offset=min
        )
        
        data = []
        for record in records:
            items_gave = json.loads(record.items_gave_json) if record.items_gave_json else []
            items_received = json.loads(record.items_received_json) if record.items_received_json else []
            
            data.append({
                'id': record.ID,
                'trade_id': record.trade_id,
                'steam_id': record.steam_id,
                'trade_time': record.trade_time,
                'trade_time_timestamp': record.trade_time_timestamp,
                'trade_type': record.trade_type,
                'trade_partner': record.trade_partner,
                'items_gave_count': record.items_gave_count,
                'items_received_count': record.items_received_count,
                'items_gave': items_gave,
                'items_received': items_received
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
        
    except Exception as e:
        print(f"获取历史记录错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryHistoryV1.route('/count/<steam_id>', methods=['GET'])
def count_records(steam_id):
    """统计记录总数"""
    try:
        count = SteamInventoryHistoryModel.count_by_steam_id(steam_id)
        return jsonify({
            'success': True,
            'count': count
        }), 200
        
    except Exception as e:
        print(f"统计记录错误: {str(e)}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

