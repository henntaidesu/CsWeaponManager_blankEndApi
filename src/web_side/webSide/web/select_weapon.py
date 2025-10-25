from flask import jsonify, request, Blueprint
from src.db_manager.index.weapon_classID import WeaponClassIDModel

webSelectWeaponV1 = Blueprint('webSelectWeaponV1', __name__)

@webSelectWeaponV1.route('/searchWeapon', methods=['GET'])
def searchWeapon():
    """
    根据market_listing_item_name模糊搜索武器
    参数: keyword - 搜索关键词
    返回: 匹配的武器列表（完整的market_listing_item_name字段，限制20条，不去重）
    """
    try:
        keyword = request.args.get('keyword', '')
        
        if not keyword or len(keyword.strip()) == 0:
            return jsonify({
                "success": True,
                "data": []
            }), 200
        
        # 使用LIKE进行模糊查询
        where_clause = "[market_listing_item_name] LIKE ?"
        params = (f"%{keyword}%",)
        
        # 查询数据库，限制返回20条
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=params,
            limit=20
        )
        
        # 提取market_listing_item_name字段，不去重，返回所有匹配的数据
        results = []
        for record in records:
            name = record.market_listing_item_name
            if name:
                results.append(name)
        
        return jsonify({
            "success": True,
            "data": results
        }), 200
        
    except Exception as e:
        print(f"搜索武器失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500

