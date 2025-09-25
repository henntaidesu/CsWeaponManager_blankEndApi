from flask import jsonify, request, Blueprint
from src.execution_db import Date_base

buff163SellV1 = Blueprint('buff163SellV1', __name__)

@buff163SellV1.route('/selectNotEnd/<user_id>', methods=['get'])
def selectNotEnd(user_id):
    sql = f'''  SELECT ID FROM buff_sell WHERE status NOT IN ('已完成', '已取消') and data_user = {user_id};'''
    flag, result = Date_base().select(sql)
    return jsonify({"not_end_orders": [row[0] for row in result]}), 200


@buff163SellV1.route('/ApexTimeUrl/<user_id>', methods=['get'])
def ApexTimeUrl(user_id):
    sql = f'''SELECT order_time FROM "main"."buff_sell" WHERE "data_user" = "{user_id}" ORDER BY "order_time" DESC LIMIT 1;'''
    flag, result = Date_base().select(sql)
    return jsonify({"last_order_time": result[0][0] if result else None}), 200

@buff163SellV1.route('/updateOrderStatus', methods=['post'])
def updateOrderStatus():
    data = request.get_json()
    item_id = data['item_id']
    status = data['state']
    status_sub = data.get('state_sub')
    sql = f'''UPDATE "main"."buff_sell" SET "status" = '{status}', "status_sub" = '{status_sub}' WHERE "ID" = '{item_id}';'''
    Date_base().update(sql)
    sql = f'''UPDATE "main"."sell" SET "status" = '{status}', "status_sub" = '{status_sub}' WHERE "ID" = '{item_id}';'''
    # Date_base().update(sql)
    return "更新成功", 200  

@buff163SellV1.route('/insert_db', methods=['post'])
def insert_db():
    data = request.get_json()
    item_id = data['item_id']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weaponitem_name = data['weaponitem_name']
    float_range = data['float_range']
    price = data['price']
    state = data['state']
    state_sub = data['state_sub']
    created_at = data['created_at']
    price_original = data.get('price_original')
    seller_id = data['seller_id']
    weapon_float = data['weapon_float']
    data_user = data['data_user']

    sql = f'''INSERT INTO "main"."buff_sell" ("ID", "weapon_name", "weapon_type", "item_name", "weapon_float", "float_range",
    "price", "buyer_name", "status", "from", "order_time", "data_user", "status_sub", "price_original") VALUES
    ('{item_id}', '{weaponitem_name}', '{weapon_type}', '{item_name}', {weapon_float}, '{float_range}', {price}, '{seller_id}',
    '{state}', 'buff', '{created_at}', '{data_user}', '{state_sub}', {price_original});
    '''
    Date_base().insert(sql)
    sql = f'''INSERT INTO "main"."sell" ("ID", "weapon_name", "weapon_type", "item_name", "weapon_float", "float_range",
    "price", "buyer_name", "status", "from", "order_time", "data_user", "status_sub","price_original") VALUES
    ('{item_id}', '{weaponitem_name}', '{weapon_type}', '{item_name}', {weapon_float}, '{float_range}', {price}, '{seller_id}',
    '{state}', 'buff', '{created_at}', '{data_user}', '{state_sub}', {price_original});
    '''
    # Date_base().insert(sql)
    return "写入成功", 200

@buff163SellV1.route('/countData/<user_id>', methods=['get'])
def countData(user_id):
    sql = f'''SELECT COUNT(*) FROM "main"."buff_sell" where "data_user" = "{user_id}";'''
    flag, result = Date_base().select(sql)
    print(result[0][0])
    return jsonify({"count": result[0][0]}), 200
    
