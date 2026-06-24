"""
竞品雷达 v1.0 — Flask 主应用
API 端点：品类列表 / 产品查询 / 统计面板 / 采集触发 / 品牌对比 / 趋势分析
"""
import os
import sys
import json
import datetime
import time

# 确保项目根路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db.schema import get_conn, init_db
from collectors.eu_amazon import (
    get_collection_urls, save_products, get_region_id as get_eu_region,
    get_category_id, log_collection_start, log_collection_finish
)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ============================================================================
# 初始化
# ============================================================================
init_db()

# ============================================================================
# 页面路由
# ============================================================================
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# ============================================================================
# 品类 API
# ============================================================================
@app.route('/api/categories')
def api_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id=c.id AND p.is_active=1
        GROUP BY c.id
        ORDER BY c.id
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


# ============================================================================
# 区域 API
# ============================================================================
@app.route('/api/regions')
def api_regions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, COUNT(p.id) as product_count
        FROM regions r
        LEFT JOIN products p ON p.region_id=r.id AND p.is_active=1
        GROUP BY r.id
        ORDER BY r.id
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


# ============================================================================
# 产品查询 API (支持多维度过滤)
# ============================================================================
@app.route('/api/products')
def api_products():
    conn = get_conn()
    cur = conn.cursor()

    category = request.args.get('category')
    region = request.args.get('region')           # 'EU' or 'NA'
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    has_qi2 = request.args.get('qi2', type=int)
    has_gan = request.args.get('gan', type=int)
    has_wireless = request.args.get('wireless', type=int)
    form_factor = request.args.get('form')
    sort_by = request.args.get('sort', 'rating')
    order = request.args.get('order', 'desc')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = """
        SELECT p.*, c.name_zh as category_name, c.slug as category_slug,
               r.code as region_code, r.name as region_name
        FROM products p
        JOIN categories c ON c.id=p.category_id
        JOIN regions r ON r.id=p.region_id
        WHERE p.is_active=1
    """
    params = []

    if category:
        query += " AND (c.slug=? OR c.name_zh=? OR c.name_en=?)"
        params.extend([category, category, category])
    if region:
        query += " AND r.code=?"
        params.append(region)
    if brand:
        query += " AND (p.brand_name LIKE ? OR p.brand_name=?)"
        like = f"%{brand}%"
        params.extend([like, brand])
    if min_price is not None:
        query += " AND p.price>=?"
        params.append(min_price)
    if max_price is not None:
        query += " AND p.price<=?"
        params.append(max_price)
    if min_rating is not None:
        query += " AND p.rating>=?"
        params.append(min_rating)
    if has_qi2 is not None:
        query += " AND p.has_qi2=?"
        params.append(has_qi2)
    if has_gan is not None:
        query += " AND p.has_gan=?"
        params.append(has_gan)
    if has_wireless is not None:
        query += " AND p.has_wireless=?"
        params.append(has_wireless)
    if form_factor:
        query += " AND p.form_factor=?"
        params.append(form_factor)

    valid_sorts = ['rating', 'price', 'review_count', 'collected_at', 'wattage', 'capacity_mah']
    if sort_by not in valid_sorts:
        sort_by = 'rating'

    order_clause = 'DESC' if order.lower() == 'desc' else 'ASC'
    query += f" ORDER BY p.{sort_by} {order_clause} NULLS LAST"
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        if d.get('features'):
            try:
                d['features'] = json.loads(d['features'])
            except json.JSONDecodeError:
                d['features'] = {}
        rows.append(d)

    # 获取总数
    count_query = """
        SELECT COUNT(*) as total FROM products p
        JOIN categories c ON c.id=p.category_id
        JOIN regions r ON r.id=p.region_id
        WHERE p.is_active=1
    """
    count_params = []
    if category:
        count_query += " AND (c.slug=? OR c.name_zh=? OR c.name_en=?)"
        count_params.extend([category, category, category])
    if region:
        count_query += " AND r.code=?"
        count_params.append(region)

    cur.execute(count_query, count_params)
    total = cur.fetchone()['total']
    conn.close()

    return jsonify({'total': total, 'products': rows, 'limit': limit, 'offset': offset})


# ============================================================================
# 统计面板 API
# ============================================================================
@app.route('/api/stats/overview')
def api_stats_overview():
    conn = get_conn()
    cur = conn.cursor()

    # 总量统计
    cur.execute("""
        SELECT
            COUNT(*) as total_products,
            COUNT(DISTINCT brand_name) as total_brands,
            COUNT(DISTINCT source) as total_sources,
            AVG(price) as avg_price,
            AVG(rating) as avg_rating,
            SUM(CASE WHEN has_qi2=1 THEN 1 ELSE 0 END) as qi2_count,
            SUM(CASE WHEN has_gan=1 THEN 1 ELSE 0 END) as gan_count,
            SUM(CASE WHEN has_wireless=1 THEN 1 ELSE 0 END) as wireless_count
        FROM products WHERE is_active=1
    """)
    overview = dict(cur.fetchone())

    # 按区域统计
    cur.execute("""
        SELECT r.code, r.name, COUNT(*) as count, AVG(p.price) as avg_price, AVG(p.rating) as avg_rating
        FROM products p JOIN regions r ON r.id=p.region_id
        WHERE p.is_active=1
        GROUP BY r.id
    """)
    by_region = [dict(r) for r in cur.fetchall()]

    # 按品类统计
    cur.execute("""
        SELECT c.slug, c.name_zh, c.name_en, COUNT(*) as count,
               AVG(p.price) as avg_price, AVG(p.rating) as avg_rating,
               SUM(CASE WHEN p.has_qi2=1 THEN 1 ELSE 0 END) as qi2_count,
               SUM(CASE WHEN p.has_gan=1 THEN 1 ELSE 0 END) as gan_count
        FROM products p JOIN categories c ON c.id=p.category_id
        WHERE p.is_active=1
        GROUP BY c.id
    """)
    by_category = [dict(r) for r in cur.fetchall()]

    # 品牌 Top 10
    cur.execute("""
        SELECT brand_name, COUNT(*) as count, AVG(rating) as avg_rating,
               AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price
        FROM products WHERE is_active=1 AND brand_name IS NOT NULL
        GROUP BY brand_name ORDER BY count DESC LIMIT 10
    """)
    top_brands = [dict(r) for r in cur.fetchall()]

    # 最近采集时间
    cur.execute("""
        SELECT MAX(collected_at) as last_collected,
               COUNT(*) as products_24h,
               SUM(CASE WHEN collected_at >= datetime('now','-7 days') THEN 1 ELSE 0 END) as products_7d
        FROM products WHERE is_active=1
    """)
    freshness = dict(cur.fetchone())

    conn.close()

    return jsonify({
        'overview': overview,
        'by_region': by_region,
        'by_category': by_category,
        'top_brands': top_brands,
        'freshness': freshness,
    })


# ============================================================================
# 品牌对比 API
# ============================================================================
@app.route('/api/brands/compare')
def api_brands_compare():
    category = request.args.get('category')
    region = request.args.get('region')

    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT brand_name,
               COUNT(*) as product_count,
               AVG(rating) as avg_rating,
               AVG(price) as avg_price,
               MIN(price) as min_price,
               MAX(price) as max_price,
               SUM(CASE WHEN has_qi2=1 THEN 1 ELSE 0 END) as qi2_count,
               SUM(CASE WHEN has_gan=1 THEN 1 ELSE 0 END) as gan_count,
               SUM(CASE WHEN has_wireless=1 THEN 1 ELSE 0 END) as wireless_count,
               AVG(wattage) as avg_wattage,
               AVG(capacity_mah) as avg_capacity
        FROM products p
        JOIN categories c ON c.id=p.category_id
        JOIN regions r ON r.id=p.region_id
        WHERE p.is_active=1 AND p.brand_name IS NOT NULL
    """
    params = []

    if category:
        query += " AND c.slug=?"
        params.append(category)
    if region:
        query += " AND r.code=?"
        params.append(region)

    query += " GROUP BY brand_name HAVING product_count >= 1 ORDER BY product_count DESC LIMIT 20"

    cur.execute(query, params)
    brands = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(brands)


# ============================================================================
# 趋势 API
# ============================================================================
@app.route('/api/trends')
def api_trends():
    conn = get_conn()
    cur = conn.cursor()

    # Qi2 采用率趋势（按周聚合）
    cur.execute("""
        SELECT DATE(collected_at) as dt,
               COUNT(*) as total,
               SUM(CASE WHEN has_qi2=1 THEN 1 ELSE 0 END) as qi2_count
        FROM products WHERE is_active=1
        GROUP BY dt ORDER BY dt DESC LIMIT 30
    """)
    qi2_trend = [dict(r) for r in cur.fetchall()]

    # 价格趋势
    cur.execute("""
        SELECT DATE(collected_at) as dt,
               AVG(price) as avg_price,
               MIN(price) as min_price,
               MAX(price) as max_price
        FROM products WHERE is_active=1 AND price IS NOT NULL
        GROUP BY dt ORDER BY dt DESC LIMIT 30
    """)
    price_trend = [dict(r) for r in cur.fetchall()]

    # 品类增长
    cur.execute("""
        SELECT c.name_zh, COUNT(*) as count
        FROM products p JOIN categories c ON c.id=p.category_id
        WHERE p.is_active=1
        GROUP BY c.id ORDER BY count DESC
    """)
    category_growth = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        'qi2_trend': list(reversed(qi2_trend)),
        'price_trend': list(reversed(price_trend)),
        'category_growth': category_growth,
    })


# ============================================================================
# 采集管理 API
# ============================================================================
@app.route('/api/collection/urls')
def api_collection_urls():
    """获取 EU Amazon 采集 URL 列表"""
    urls = get_collection_urls()
    return jsonify({'sources': urls, 'total': len(urls)})


@app.route('/api/collection/logs')
def api_collection_logs():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT cl.*, r.name as region_name, c.name_zh as category_name
        FROM collection_logs cl
        LEFT JOIN regions r ON r.id=cl.region_id
        LEFT JOIN categories c ON c.id=cl.category_id
        ORDER BY cl.created_at DESC LIMIT 50
    """)
    logs = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(logs)


@app.route('/api/collection/trigger', methods=['POST'])
def api_collection_trigger():
    """触发一次采集任务 (需要 AI Agent 执行实际的 WebFetch)
    这里返回需要采集的 URL 列表，前端可以显示采集状态
    """
    data = request.get_json() or {}
    category = data.get('category', 'all')
    region = data.get('region', 'EU')

    urls = get_collection_urls()
    if category != 'all':
        urls = [u for u in urls if u['category'] == category]

    conn = get_conn()
    cur = conn.cursor()
    for u in urls:
        region_id = get_eu_region(cur, 'EU')
        cat_id = get_category_id(cur, u['category'])
        log_collection_start(cur, region_id, cat_id, u['source'])
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'triggered',
        'task_count': len(urls),
        'urls': urls,
        'message': f'已创建 {len(urls)} 个采集任务，请在 AI Agent 中执行 WebFetch 采集',
    })


# ============================================================================
# 产品导入 API (供 AI Agent 采集后调用)
# ============================================================================
@app.route('/api/products/import', methods=['POST'])
def api_products_import():
    """导入采集到的产品数据"""
    data = request.get_json() or {}
    products = data.get('products', [])
    category = data.get('category', 'powerbank')
    region = data.get('region', 'EU')
    source = data.get('source', 'manual')

    if not products:
        return jsonify({'status': 'error', 'message': 'No products provided'}), 400

    conn = get_conn()
    cur = conn.cursor()
    region_id = get_eu_region(cur, region) if region == 'EU' else 2

    new_count, update_count = save_products(products, region_id, category, source, conn)
    conn.close()

    return jsonify({
        'status': 'ok',
        'new': new_count,
        'updated': update_count,
        'total_received': len(products),
    })


# ============================================================================
# 健康检查
# ============================================================================
@app.route('/api/health')
def api_health():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM products")
    count = cur.fetchone()['count']
    cur.execute("SELECT MAX(collected_at) as last_update FROM products")
    last = cur.fetchone()
    conn.close()
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'total_products': count,
        'last_update': last['last_update'] if last else None,
    })


# ============================================================================
# 启动
# ============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8765))
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   竞品雷达 v1.0 — Competitor Radar      ║
    ║   端口: {port}                           ║
    ║   地址: http://localhost:{port}           ║
    ╚══════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
