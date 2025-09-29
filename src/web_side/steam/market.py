from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_buy import SteamBuyModel
from src.db_manager.steam.steam_sell import SteamSellModel
from src.execution_db import Date_base
from datetime import datetime

steamMarketV1 = Blueprint('steamMarketV1', __name__)

@steamMarketV1.route('/countData/<data_user>', methods=['get'])
def countData(data_user):
    pass

@steamMarketV1.route('/insertNewData', methods=['POST'])
def insertNewData():
    """插入新的Steam市场交易数据"""
    try:
        data = request.get_json()

        
        if not data:
            print("错误：无效的JSON数据")
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        # 获取当前用户（这里需要根据实际认证机制获取）
        trade_type = data.get('trade_type')
        
        # 根据trade_type决定插入到steam_buy表还是steam_sell表
        print(f"交易类型: {trade_type}")
        
        if trade_type == '+':
            # 购买记录 - 插入steam_buy表
            print("插入购买记录到steam_buy表")
            buy_record = SteamBuyModel()
            buy_record.ID = data.get('ID')
            buy_record.asset_id = data.get('asset_id')
            buy_record.price = data.get('price')
            buy_record.trade_date = data.get('trade_date')
            buy_record.listing_date = data.get('listing_date')
            buy_record.game_name = data.get('game_name')
            buy_record.weapon_type = data.get('weapon_type')
            buy_record.weapon_name = data.get('weapon_name')
            buy_record.item_name = data.get('item_name')
            buy_record.float_range = data.get('exterior_wear')
            buy_record.inspect_link = data.get('inspect_link')
            buy_record.data_user = data.get('steamId')
            saved = buy_record.save()
            operation_type = '购买'
            
        elif trade_type == '-':
            # 销售记录 - 插入steam_sell表
            print("插入销售记录到steam_sell表")
            sell_record = SteamSellModel()
            sell_record.ID = data.get('ID')
            sell_record.asset_id = data.get('asset_id')
            sell_record.price = data.get('price')
            sell_record.price_original = data.get('price_original')
            sell_record.trade_date = data.get('trade_date')
            sell_record.listing_date = data.get('listing_date')
            sell_record.game_name = data.get('game_name')
            sell_record.weapon_type = data.get('weapon_type')
            sell_record.weapon_name = data.get('weapon_name')
            sell_record.item_name = data.get('item_name')
            buy_record.float_range = data.get('exterior_wear')
            sell_record.inspect_link = data.get('inspect_link')
            sell_record.data_user = data.get('steamId')
            
            print("开始保存销售记录...")
            saved = sell_record.save()
            print(f"销售记录保存结果: {saved}")
            operation_type = '销售'
        else:
            return jsonify({'success': False, 'error': '无效的交易类型'}), 400
        
        # 检查是否保存成功
        print(f"最终保存结果: {saved}")
        if saved:
            print(f"{operation_type}数据插入成功")
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
            print("数据插入失败")
            return jsonify({'success': False, 'error': '数据插入失败'}), 500
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

