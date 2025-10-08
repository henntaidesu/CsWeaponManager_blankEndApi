from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_inventory import SteamInventoryModel

steamInventoryV1 = Blueprint('steamInventoryV1', __name__)

@steamInventoryV1.route('/inventory', methods=['POST'])
def insert_inventory():
    """插入Steam库存数据"""
    try:
        data = request.get_json()
        if not data:
            print("错误：无效的JSON数据")
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        # 创建库存记录
        inventory_record = SteamInventoryModel()
        
        # 基本信息
        inventory_record.assetid = data.get('assetid')
        inventory_record.instanceid = data.get('instanceid')
        inventory_record.classid = data.get('classid')
        inventory_record.data_user = data.get('steamId')
        
        # 武器信息 - 从tags中的parsed_name获取
        tags = data.get('tags', {})
        parsed_name = tags.get('parsed_name', {})
        
        inventory_record.weapon_type = parsed_name.get('weapon_type')
        inventory_record.weapon_name = parsed_name.get('weapon_name')
        inventory_record.item_name = parsed_name.get('item_name') or data.get('name')
        
        # 外观信息 - 从tags中获取
        exterior = tags.get('Exterior', {})
        inventory_record.float_range = exterior.get('localized_tag_name')
        
        # 磨损值 - 从asset_properties中获取
        asset_properties = data.get('asset_properties', [])
        weapon_float = None
        for prop in asset_properties:
            if prop.get('propertyid') == 2:  # propertyid 2 是磨损率
                weapon_float = prop.get('float_value')
                break
        inventory_record.weapon_float = weapon_float
        
        # 交易相关
        # remark 存储交易保护信息，如果没有则为NULL
        trade_lock_info = data.get('trade_lock_info')
        inventory_record.remark = trade_lock_info if trade_lock_info else None
        
        # buy_price 字段
        inventory_record.buy_price = data.get('buy_price') # 默认从前端传入，或在Spider中设置
        
        # 保存到数据库
        saved = inventory_record.save()
        
        if saved:
            return jsonify({
                'success': True,
                'message': '库存数据插入成功',
                'data': {
                    'assetid': data.get('assetid'),
                    'weapon_name': inventory_record.weapon_name,
                    'item_name': inventory_record.item_name,
                    'weapon_float': weapon_float
                }
            }), 200
        else:
            print("数据插入失败")
            return jsonify({'success': False, 'error': '数据插入失败'}), 500
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@steamInventoryV1.route('/inventory/<data_user>', methods=['GET'])
def get_inventory_by_user(data_user):
    """根据Steam ID获取库存列表"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        records = SteamInventoryModel.find_by_user(data_user, limit, offset)
        
        # 转换为字典列表
        inventory_list = []
        for record in records:
            inventory_list.append({
                'assetid': record.assetid,
                'instanceid': record.instanceid,
                'classid': record.classid,
                'weapon_name': record.weapon_name,
                'item_name': record.item_name,
                'weapon_type': record.weapon_type,
                'weapon_float': record.weapon_float,
                'float_range': record.float_range,
                'remark': record.remark
            })
        
        return jsonify({
            'success': True,
            'data': inventory_list,
            'count': len(inventory_list)
        }), 200
        
    except Exception as e:
        print(f"查询库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@steamInventoryV1.route('/inventory/count/<data_user>', methods=['GET'])
def count_inventory(data_user):
    """统计用户库存数量"""
    try:
        records = SteamInventoryModel.find_by_user(data_user)
        count = len(records)
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': data_user,
                'count': count
            }
        }), 200
        
    except Exception as e:
        print(f"统计库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'统计失败: {str(e)}'
        }), 500


@steamInventoryV1.route('/inventory/user/<data_user>', methods=['DELETE'])
def delete_user_inventory(data_user):
    """删除指定用户的所有库存记录"""
    try:
        # 先统计有多少条记录
        count_before = SteamInventoryModel.count("data_user = ?", (data_user,))
        
        if count_before == 0:
            return jsonify({
                'success': True,
                'message': '没有需要删除的记录',
                'deleted_count': 0
            }), 200
        
        # 使用SQL直接删除
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        sql = f"DELETE FROM {SteamInventoryModel.get_table_name()} WHERE data_user = ?"
        deleted_count = db.execute_update(sql, (data_user,))
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 条库存记录',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        print(f"删除库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500


@steamInventoryV1.route('/inventory/buy_price/<steam_id>/<assetid>', methods=['PUT'])
def update_buy_price(steam_id, assetid):
    """更新库存物品的购入价格"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        buy_price = data.get('buy_price')
        
        # 使用直接SQL更新
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE steam_inventory SET buy_price = ? WHERE data_user = ? AND assetid = ?',
            (buy_price, steam_id, assetid)
        )
        
        conn.commit()
        affected = cursor.rowcount
        
        if affected > 0:
            return jsonify({
                'success': True,
                'message': '更新成功',
                'affected': affected
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '未找到匹配的记录'
            }), 404
            
    except Exception as e:
        print(f"更新buy_price时出错: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
