from flask import jsonify, request, Blueprint
from src.execution_db import Date_base

youpin898BuyV1 = Blueprint('youpin898BuyV1', __name__)

@youpin898BuyV1.route('/getWeaponNotEndStatusList/<data_user>', methods=['get'])
def getWeaponNotEndStatusList(data_user):
    sql = f"SELECT ID FROM yyyp_buy WHERE status not in ('已完成', '已取消') AND data_user = '{data_user}';"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@youpin898BuyV1.route('/selectApexTime/<data_user>', methods=['get'])
def selectApexTime(data_user):
    sql = f"SELECT order_time FROM yyyp_buy WHERE data_user = '{data_user}' ORDER BY order_time DESC LIMIT 1"
    flag, data = Date_base().select(sql)
    try:
        data = str(data[0][0])
    except TypeError:
        data = 0
    return jsonify(data), 200

@youpin898BuyV1.route('/selectNotEndID/<data_user>', methods=['get'])
def selectNotEndID(data_user):
    sql = f"SELECT ID FROM yyyp_buy WHERE status <> '已完成' and status <> '已取消' AND data_user = '{data_user}'"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@youpin898BuyV1.route('/getCount/<data_user>', methods=['get'])
def getCount(data_user):
    sql = f"SELECT COUNT(*) FROM yyyp_buy WHERE data_user = '{data_user}';"
    flag, data = Date_base().select(sql)
    try:
        data = str(data[0][0])
    except TypeError:
        data = 0
    return data, 200

@youpin898BuyV1.route('/updateBuyData', methods=['post'])
def updateBuyData():
    data = request.get_json()
    weapon_ID = data['ID']
    weapon_status = data['weapon_status']
    sql = (f"UPDATE yyyp_buy SET status = '{weapon_status}' WHERE ID = '{weapon_ID}';")
    a_status = Date_base().update(sql)
    sql = (f"UPDATE buy SET status = '{weapon_status}' WHERE ID LIKE '{weapon_ID}%' AND \"from\" = 'yyyp';")
    Date_base().update(sql)
    if a_status is True:
        update_status = "更新成功"
        return update_status, 200
    elif a_status == '重复数据':
        update_status = '重复数据'
        return update_status, 200
    else:
        update_status = '更新失败'
        return update_status, 500



@youpin898BuyV1.route('/insert_webside_buydata', methods=['post'])
def insert_webside_buydata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    seller_name = data['seller_name']
    status = data['status']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    data_user = data['data_user']
    try:
        buy_number = int(data['buy_number'])
    except TypeError:
        buy_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"
    price_all = data['price_all']
    payment = data['payment']
    tradeType = data['tradeType']

    sql = (f"INSERT INTO {data_from}_buy "
            f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,"
            f" seller_name, order_time, status, \"from\", steam_id,"
            f" buy_number, err_number, price_all, payment, trade_type, data_user)"
            f" VALUES "
            f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
            f" '{seller_name}', '{order_time}', '{status}', '{data_from}', '{steamid}',"
            f" '{buy_number}', '{err_number}', {price_all}, '{payment}' , '{tradeType}', '{data_user}');")
    a_status = Date_base().insert(sql)
    
    if buy_number == 1 :
        sql = (f"INSERT INTO buy "
        f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,"
        f" seller_name, status, \"from\", steam_id, order_time, payment, trade_type, data_user)"
        f" VALUES "
        f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
        f" '{seller_name}',  '{status}', '{data_from}', '{steamid}', '{order_time}', '{payment}' , '{tradeType}', '{data_user}');")
        Date_base().insert(sql)
        
    if a_status == '重复数据':
        insert_status = "重复数据"
    elif a_status:
        insert_status = '写入成功'
    else:
        insert_status = '写入失败'
    return insert_status, 200

@youpin898BuyV1.route('/insert_main_buydata', methods=['post'])
def insert_main_buydata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    seller_name = data['seller_name']
    status = data['status']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    payment = data['payment']
    tradeType = data['tradeType']
    data_user = data['data_user']
    try:
        buy_number = int(data['buy_number'])
    except TypeError:
        buy_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"

    price_all = data['price_all']

    sql = (f"INSERT INTO buy "
        f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,"
        f" seller_name, order_time, status, \"from\", steam_id, payment, trade_type, data_user)"
        f" VALUES "
        f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
        f" '{seller_name}', '{order_time}', '{status}', '{data_from}',  '{steamid}', '{payment}', '{tradeType}', '{data_user}');")
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    return insert_status, 200


