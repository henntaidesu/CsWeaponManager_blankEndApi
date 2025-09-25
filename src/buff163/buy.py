from flask import jsonify, request, Blueprint
from src.execution_db import Date_base

buff163BuyV1 = Blueprint('buff163BuyV1', __name__)

@buff163BuyV1.route('/insert_db', methods=['post'])
def insert_db():
    data = request.get_json()
    item_id = data['item_id']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weaponitem_name = data['weaponitem_name']
    float_range = data['float_range']
    price = data['price']
    state_sub = data['state_text']
    created_at = data['created_at']
    pay_method_text = data['pay_method_text']
    steam_price_cny = data['steam_price_cny']
    seller_id = data['seller_id']
    weapon_float = data['weapon_float']

    if state_sub == "已下架":
        state_text = "已下架"
        

    sql = f'''INSERT INTO "main"."buff_buy" ("ID", "weapon_name", "weapon_type", "item_name", "weapon_float", "float_range", 
    "price", "seller_name", "status", "from", "order_time", "sell_of", "payment", "trade_type", "data_user") VALUES 
    ('{item_id}', '{weaponitem_name}', '{weapon_type}', '{item_name}', {weapon_float}, '{float_range}', {price}, '{seller_id}', 
    '{state_text}', 'buff', '{created_at}', NULL, '{pay_method_text}', NULL, NULL);
    '''
    Date_base().insert(sql)
    sql = f'''INSERT INTO "main"."buy" ("ID", "weapon_name", "weapon_type", "item_name", "weapon_float", "float_range", 
    "price", "seller_name", "status", "from", "order_time", "sell_of", "payment", "trade_type", "data_user") VALUES 
    ('{item_id}', '{weaponitem_name}', '{weapon_type}', '{item_name}', {weapon_float}, '{float_range}', {price}, '{seller_id}', 
    '{state_text}', 'buff', '{created_at}', NULL, '{pay_method_text}', NULL, NULL);
    '''
    Date_base().insert(sql)
    return "写入成功", 200

@buff163BuyV1.route('/countData', methods=['get'])
def countData():
    sql = '''SELECT COUNT(*) FROM "main"."buff_buy";'''
    flag, result = Date_base().select(sql)
    print(result[0][0])
    return jsonify({"count": result[0][0]}), 200
    
