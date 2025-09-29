import os
from flask import Flask
from flask_cors import CORS
from src.config.config_v1 import configV1
from src.web_side.youpin898.buy.buy_v1 import youpin898BuyV1
from src.web_side.youpin898.lent.lent_v1 import youpin898LentV1
from src.web_side.youpin898.sell.sell_v1 import youpin898SellV1
from src.web_side.youpin898.message.message_v1 import youpin898MessageBoxV1
from src.web.index_page import indexPage
from src.web.buy_page import webBuyV1
from src.web.sell_page import webSellV1
from src.web.lent import webLentV1
from src.web.DataSource_page import dataSourcePage
from src.web_side.buff163.buy import buff163BuyV1
from src.web_side.buff163.sell import buff163SellV1
from src.web_side.steam.market import steamMarketV1
from src.db_manager import init_database

app = Flask(__name__)
CORS(app)

def blankEndApi():
    # print("Blank End API Start")
    # 只在主进程中初始化数据库，避免Flask debug模式重复初始化
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # 初始化数据库
        print("正在初始化数据库...")
        if init_database():
            print("✅ 数据库初始化成功")
        else:
            print("❌ 数据库初始化失败")
            return
    
    app.register_blueprint(configV1, url_prefix = '/configV1')
    app.register_blueprint(youpin898BuyV1, url_prefix = '/youpin898BuyV1')
    app.register_blueprint(youpin898SellV1, url_prefix = '/youpin898SellV1')
    app.register_blueprint(youpin898LentV1, url_prefix = '/youpin898LentV1')
    app.register_blueprint(youpin898MessageBoxV1, url_prefix = '/youpin898MessageBoxV1')
    app.register_blueprint(indexPage, url_prefix = '/indexPage')
    app.register_blueprint(webBuyV1, url_prefix = '/webBuyV1')
    app.register_blueprint(webSellV1, url_prefix = '/webSellV1')
    app.register_blueprint(webLentV1, url_prefix = '/webLentV1')
    app.register_blueprint(dataSourcePage, url_prefix='/dataSourcePageV1')
    app.register_blueprint(buff163BuyV1, url_prefix = '/buff163BuyV1')
    app.register_blueprint(buff163SellV1, url_prefix = '/buff163SellV1')
    app.register_blueprint(steamMarketV1, url_prefix = '/steamMarketV1')
    app.run(debug=True, port=9001, host='0.0.0.0')

if __name__ == '__main__':
    blankEndApi()

