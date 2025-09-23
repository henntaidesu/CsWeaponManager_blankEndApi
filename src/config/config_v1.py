from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.read_conf import read_conf
import requests


configV1 = Blueprint('configV1', __name__)

def get_database_name():
    conf = read_conf()
    return conf.get_database_name()


@configV1.route('/config_v1/<key1>/<key2>/<value>', methods=['post'])
def updata_config(key1, key2, value):
    database_name = get_database_name()
    sql = f"UPDATE config SET value = '{value}' WHERE key1 = '{key1}' AND key2 = '{key2}';"
    Date_base().update(sql)
    return '更新成功', 200

@configV1.route('/get_config/<key1>/<key2>', methods=['post'])
def get_yyyp_config(key1, key2):
    database_name = get_database_name()
    sql = f"SELECT value FROM config WHERE key1 = '{key1}' and key2 = '{key2}'"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200
