from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_buy import SteamBuyModel
from src.db_manager.steam.steam_sell import SteamSellModel
from src.execution_db import Date_base
from datetime import datetime

steamMarketV1 = Blueprint('steamMarketV1', __name__)

@steamMarketV1.route('/insertNewData', methods=['POST'])
def insertNewData():
    """插入新的Steam市场交易数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的JSON数据'}), 400
        
        # 获取当前用户（这里需要根据实际认证机制获取）
        data_user = request.headers.get('User-ID', 'default_user')
        trade_type = data.get('trade_type')
        
        # 根据trade_type决定插入到steam_buy表还是steam_sell表
        if trade_type == '+':
            # 购买记录 - 插入steam_buy表
            buy_record = SteamBuyModel()
            buy_record.set_field('ID', data.get('ID'))
            buy_record.set_field('asset_id', data.get('asset_id'))
            buy_record.set_field('trade_type', '+')
            buy_record.set_field('price', data.get('price'))
            buy_record.set_field('price_original', data.get('price_original'))
            buy_record.set_field('trade_date', data.get('trade_date'))
            buy_record.set_field('listing_date', data.get('listing_date'))
            buy_record.set_field('game_name', data.get('game_name'))
            buy_record.set_field('weapon_type', data.get('weapon_type'))
            buy_record.set_field('weapon_name', data.get('weapon_name'))
            buy_record.set_field('item_name', data.get('item_name'))
            buy_record.set_field('exterior_wear', data.get('exterior_wear'))
            buy_record.set_field('inspect_link', data.get('inspect_link'))
            buy_record.set_field('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            buy_record.set_field('data_user', data_user)
            
            saved = buy_record.save()
            operation_type = '购买'
            
        elif trade_type == '-':
            # 销售记录 - 插入steam_sell表
            sell_record = SteamSellModel()
            sell_record.set_field('ID', data.get('ID'))
            sell_record.set_field('asset_id', data.get('asset_id'))
            sell_record.set_field('trade_type', '-')
            sell_record.set_field('price', data.get('price'))
            sell_record.set_field('price_original', data.get('price_original'))
            sell_record.set_field('trade_date', data.get('trade_date'))
            sell_record.set_field('listing_date', data.get('listing_date'))
            sell_record.set_field('game_name', data.get('game_name'))
            sell_record.set_field('weapon_type', data.get('weapon_type'))
            sell_record.set_field('weapon_name', data.get('weapon_name'))
            sell_record.set_field('item_name', data.get('item_name'))
            sell_record.set_field('exterior_wear', data.get('exterior_wear'))
            sell_record.set_field('inspect_link', data.get('inspect_link'))
            sell_record.set_field('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sell_record.set_field('data_user', data_user)
            
            saved = sell_record.save()
            operation_type = '销售'
        else:
            return jsonify({'success': False, 'error': '无效的交易类型'}), 400
        
        # 检查是否保存成功
        if saved:
            return jsonify({
                'success': True,
                'message': f'{operation_type}数据插入成功',
                'data': {
                    'id': data.get('ID'),
                    'trade_type': trade_type,
                    'operation_type': operation_type,
                    'weapon_name': data.get('weapon_name'),
                    'item_name': data.get('item_name'),
                    'price': data.get('price')
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': '数据插入失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

