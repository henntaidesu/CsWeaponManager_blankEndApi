from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_inventory import SteamInventoryModel
from datetime import datetime

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
        
        # 时间信息
        inventory_record.order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 交易相关
        inventory_record.trade_type = 'inventory'  # 标记为库存数据
        inventory_record.trade_title = data.get('market_name') or data.get('name')
        
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
                'trade_title': record.trade_title,
                'order_time': record.order_time
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

