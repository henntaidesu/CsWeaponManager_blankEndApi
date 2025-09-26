from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
import requests

youpin898SellV1 = Blueprint('youpin898SellV1/', __name__)

@youpin898SellV1.route('/getWeaponNotEndStatusList/<data_user>', methods=['get'])
def getWeaponNotEndStatusList(data_user):
    sql = f"SELECT ID FROM yyyp_sell WHERE status not in ('已完成', '已取消') AND data_user = '{data_user}';"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@youpin898SellV1.route('/updateSellData', methods=['post'])
def updateSellData():
    data = request.get_json()
    weapon_ID = data['ID']
    weapon_status = data['weapon_status']
    sql = (f"UPDATE yyyp_sell SET status = '{weapon_status}' WHERE ID = '{weapon_ID}';")
    a_status = Date_base().update(sql)
    sql = (f"UPDATE sell SET status = '{weapon_status}' WHERE ID LIKE '{weapon_ID}%' AND \"from\" = 'yyyp';")
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


@youpin898SellV1.route('/selectApexTime/<data_user>', methods=['get'])
def selectApexTime(data_user):
    sql = f"SELECT order_time FROM yyyp_sell WHERE data_user = '{data_user}' ORDER BY order_time DESC LIMIT 1"
    print(sql)
    flag, data = Date_base().select(sql)
    data = str(data[0][0])
    return jsonify(data), 200

@youpin898SellV1.route('/getCount/<data_user>', methods=['get'])
def getCount(data_user):
    sql = f"SELECT COUNT(*) FROM yyyp_sell WHERE data_user = '{data_user}';"
    flag, data = Date_base().select(sql)
    try:
        data = str(data[0][0])
    except TypeError:
        data = 0
    return data, 200
    

@youpin898SellV1.route('/insert_webside_selldata', methods=['post'])
def insert_webside_selldata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    price_original = data['price_original']
    buyer_user_name = data['buyer_user_name']
    status = data['status']
    status_sub = data['status_sub']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    data_user = data['data_user']
    try:
        sell_number = int(data['sell_number'])
    except TypeError:
        sell_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"

    price_all = data['price_all']


    sql =  (f"INSERT INTO {data_from}_sell "
            f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price, price_original,"
            f" buyer_name, status,  status_sub, \"from\", order_time, steam_id, sell_number, err_number, price_all, data_user)"
            f" VALUES "
            f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},{price_original},"
            f" '{buyer_user_name}', '{status}', '{status_sub}', '{data_from}', '{order_time}', '{steamid}',"
            f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
    a_status = Date_base().insert(sql)

    if sell_number == 1:
        sql =  (f"INSERT INTO sell "
                f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price, price_original,"
                f" buyer_name, status, status_sub, \"from\", order_time, steam_id,"
                f" sell_number, err_number, price_all, data_user)"
                f" VALUES "
                f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price}, {price_original},"
                f" '{buyer_user_name}',  '{status}', '{status_sub}', '{data_from}', '{order_time}', '{steamid}',"
                f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
        Date_base().insert(sql)
        
    if a_status == '重复数据':
        insert_status = "重复数据"
    elif a_status:
        insert_status = '写入成功'
    else:
        insert_status = '写入失败'
    return insert_status, 200

@youpin898SellV1.route('/insert_main_selldata', methods=['post'])
def insert_main_selldata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    price_original = data['price_original']
    buyer_user_name = data['buyer_user_name']
    status = data['status']
    status_sub = data['status_sub']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    data_user = data['data_user']
    try:
        sell_number = int(data['sell_number'])
    except TypeError:
        sell_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"
    price_all = data['price_all']

    sql =  (f"INSERT INTO sell "
        f"(ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price, price_original,"
        f" buyer_name, status, status_sub, \"from\", order_time, steam_id,"
        f" sell_number, err_number, price_all, data_user)"
        f" VALUES "
        f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price}, {price_original},"
        f" '{buyer_user_name}', '{status}', '{status_sub}', '{data_from}', '{order_time}', '{steamid}',"
        f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    return insert_status, 200

@youpin898SellV1.route('/countSellNumber', methods=['get'])
def countSellNumber():
    sql = "SELECT COUNT(*) FROM sell"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify({"count": data[0][0]}), 200
    return "查询失败", 500

@youpin898SellV1.route('/getSellData/<int:min>/<int:max>', methods=['get'])
def getSellData(min, max):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status FROM sell ORDER BY order_time DESC LIMIT {max} OFFSET {min};"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@youpin898SellV1.route('/selectSellWeaponName/<itemName>', methods=['get'])
def selectSellWeaponName(itemName):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status FROM sell WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%';"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@youpin898SellV1.route('/getSellDataByStatus/<status>/<int:min>/<int:max>', methods=['get'])
def getSellDataByStatus(status, min, max):
    if status == 'all':
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status FROM sell ORDER BY order_time DESC LIMIT {max} OFFSET {min};"
    else:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status FROM sell WHERE status = '{status}' ORDER BY order_time DESC LIMIT {max} OFFSET {min};"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

