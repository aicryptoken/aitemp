# 是否完全移除 api.py 还取决于以下几个因素：

# 未来的扩展计划：
# 如果您预计在将来可能需要为其他应用程序或用户提供数据访问接口，保留一个基本的 API 结构可能会有帮助。
# 数据访问模式：
# 如果有其他程序或用户需要以编程方式访问这些数据，而不仅仅是直接读取 Parquet 文件，那么 API 可能仍然有用。
# 安全性考虑：
# 如果数据需要受到访问控制，API 可以提供一个集中的身份验证和授权层。
# 数据整合需求：
# 如果将来需要将多个数据源整合在一起，API 可以作为一个统一的接入点。


from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)
db = Database()

@app.route('/api/v1/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    asset_type = request.args.get('asset_type', 'stocks')

    data = db.fetch_data(asset_type, symbol, start_date, end_date)
    return jsonify(data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)