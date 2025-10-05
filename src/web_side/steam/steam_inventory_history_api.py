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
    try:
        data = request.get_json()
        if not data or 'history_list' not in data:
            return jsonify({'success': False, 'message': '缺少history_list参数'}), 400

        history_list = data['history_list']
        inserted_count = 0
        failed_count = 0
        errors = []

        for history_item in history_list:
            try:
                # 提取历史记录基本信息
                history_id = history_item.get('ID', '')  # 新格式：这里的ID就是history_id
                order_time = history_item.get('order_time', '')
                trade_title = history_item.get('trade_title', '')
                trade_type = history_item.get('trade_type', '')

                # 遍历每个物品，创建独立记录
                items = history_item.get('items', [])

                if not items:
                    # 如果没有物品，也插入一条记录（只有交易信息）
                    record_id = history_id
                    record = {
                        'ID': record_id,
                        'order_time': order_time,
                        'trade_title': trade_title,
                        'appid': '',
                        'item_name': '',
                        'weapon_name': '',
                        'weapon_type': '',
                        'float_range': '',
                        'trade_type': trade_type
                    }

                    # 检查是否已存在
                    existing = SteamInventoryHistoryModel.find_by_id(record_id)
                    if not existing:
                        SteamInventoryHistoryModel.create(record)
                        inserted_count += 1
                elif len(items) == 1:
                    # 只有一个物品时，直接使用 history_id
                    item = items[0]
                    record_id = history_id

                    record = {
                        'ID': record_id,
                        'order_time': order_time,
                        'trade_title': trade_title,
                        'appid': item.get('appid', ''),
                        'item_name': item.get('item_name', ''),
                        'weapon_name': item.get('weapon_name', ''),
                        'weapon_type': item.get('weapon_type', ''),
                        'float_range': item.get('float_range', ''),
                        'trade_type': trade_type
                    }

                    # 检查是否已存在
                    existing = SteamInventoryHistoryModel.find_by_id(record_id)
                    if not existing:
                        SteamInventoryHistoryModel.create(record)
                        inserted_count += 1
                else:
                    # 多个物品时，ID格式：{history_id}-{classid}
                    for item in items:
                        classid = item.get('classid', '')
                        record_id = f"{history_id}-{classid}" if classid else f"{history_id}-unknown"

                        record = {
                            'ID': record_id,
                            'order_time': order_time,
                            'trade_title': trade_title,
                            'appid': item.get('appid', ''),
                            'item_name': item.get('item_name', ''),
                            'weapon_name': item.get('weapon_name', ''),
                            'weapon_type': item.get('weapon_type', ''),
                            'float_range': item.get('float_range', ''),
                            'trade_type': trade_type
                        }

                        # 检查是否已存在
                        existing = SteamInventoryHistoryModel.find_by_id(record_id)
                        if not existing:
                            SteamInventoryHistoryModel.create(record)
                            inserted_count += 1

            except Exception as e:
                failed_count += 1
                errors.append(f"处理记录失败: {str(e)}")
                continue

        return jsonify({
            'success': True,
            'message': f'成功插入 {inserted_count} 条记录',
            'inserted_count': inserted_count,
            'failed_count': failed_count,
            'errors': errors if errors else None
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'插入失败: {str(e)}'
        }), 500


@steamInventoryHistoryV1.route('/query', methods=['GET'])
def query_inventory_history():
    """查询库存历史记录

    查询参数:
    - trade_type: 交易类型 (+ 或 -)
    - weapon_type: 武器类型
    - appid: 应用ID
    - start_time: 开始时间
    - end_time: 结束时间
    - limit: 返回数量限制
    - offset: 偏移量
    """
    try:
        trade_type = request.args.get('trade_type')
        weapon_type = request.args.get('weapon_type')
        appid = request.args.get('appid')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)

        records = []

        if start_time and end_time:
            records = SteamInventoryHistoryModel.find_by_time_range(start_time, end_time, limit, offset)
        elif trade_type:
            records = SteamInventoryHistoryModel.find_by_trade_type(trade_type, limit, offset)
        elif weapon_type:
            records = SteamInventoryHistoryModel.find_by_weapon_type(weapon_type, limit, offset)
        elif appid:
            records = SteamInventoryHistoryModel.find_by_appid(appid, limit, offset)
        else:
            records = SteamInventoryHistoryModel.get_latest_records(limit or 10)

        return jsonify({
            'success': True,
            'count': len(records),
            'data': records
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500
