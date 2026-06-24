"""
欧洲 Amazon 数据采集器
支持: Amazon.de (德国) / .pl (波兰) / .es (西班牙) / .it (意大利) / .fr (法国)
"""
import sqlite3
import json
import hashlib
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import get_conn


EU_SOURCES = {
    'de': {'domain': 'amazon.de', 'currency': 'EUR', 'name': '德国'},
    'pl': {'domain': 'amazon.pl', 'currency': 'PLN', 'name': '波兰'},
    'es': {'domain': 'amazon.es', 'currency': 'EUR', 'name': '西班牙'},
    'it': {'domain': 'amazon.it', 'currency': 'EUR', 'name': '意大利'},
    'fr': {'domain': 'amazon.fr', 'currency': 'EUR', 'name': '法国'},
}

CATEGORY_SEARCH_QUERIES = {
    'powerbank': [
        ('60044f3a-CSsr', 'amazon.de', '/s?k=power+bank+10000mAh+Qi2&rh=n%3A2811685031&s=review-rank'),
        ('60044f3a-CSpr', 'amazon.pl', '/s?k=power+bank+10000mAh+magsafe&s=review-rank'),
    ],
    'wireless_charger': [
        ('60044f3a-CSwc', 'amazon.de', '/s?k=qi2+wireless+charger+3-in-1&rh=n%3A2811692031&s=review-rank'),
    ],
    'adapter_cable': [
        ('60044f3a-CSac', 'amazon.de', '/s?k=usb+c+ladeger%C3%A4t+gan+65w&rh=n%3A2811676031&s=review-rank'),
    ],
    'car_charger': [
        ('60044f3a-CScc', 'amazon.de', '/s?k=auto+ladeger%C3%A4t+einziehbares+kabel&rh=n%3A2811688031&s=review-rank'),
    ],
    'desktop_charger': [
        ('60044f3a-CSdc', 'amazon.de', '/s?k=desktop+charging+station+100w+gan&rh=n%3A2811687031&s=review-rank'),
    ],
    'energy_storage': [
        ('60044f3a-CSes', 'amazon.de', '/s?k=powerstation+akku+1000w&rh=n%3A2811689031&s=review-rank'),
    ],
}


def get_region_id(cur, code):
    cur.execute("SELECT id FROM regions WHERE code='EU'")
    row = cur.fetchone()
    return row['id'] if row else 1


def get_category_id(cur, slug):
    cur.execute("SELECT id FROM categories WHERE slug=?", (slug,))
    row = cur.fetchone()
    return row['id'] if row else None


def upsert_brand(cur, brand_name):
    if not brand_name or len(brand_name.strip()) < 1:
        return None
    normalized = brand_name.strip().lower().replace(' ', '-')
    cur.execute(
        "INSERT OR IGNORE INTO brands (name, normalized_name, region) VALUES (?,?,'EU')",
        (brand_name.strip(), normalized)
    )
    cur.execute("SELECT id FROM brands WHERE normalized_name=?", (normalized,))
    return cur.fetchone()['id']


def make_fingerprint(brand, name, region_code):
    raw = f"{brand or 'unknown'}|{name}|{region_code}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def extract_numeric(text):
    """从文本中提取数字"""
    if not text:
        return None
    match = re.search(r'[\d,]+\.?\d*', str(text).replace(',', ''))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def extract_int(text):
    """提取整数"""
    if not text:
        return None
    match = re.search(r'[\d,]+', str(text).replace(',', ''))
    if match:
        try:
            return int(match.group().replace(',', ''))
        except ValueError:
            return None
    return None


def parse_product_raw(raw_data, source_domain, region_id, category_id, cur, region_code='EU'):
    """
    解析单条产品原始数据，返回标准化的 products 表字段 dict。
    raw_data: {"brand": "...", "name": "...", "price": 29.99, ...}
    """
    brand_name = raw_data.get('brand', '') or ''
    if not brand_name:
        brand_name = str(raw_data.get('name', 'Unbranded')).split()[0]

    name = raw_data.get('name', '') or raw_data.get('product_name', '') or 'Unknown'

    brand_id = upsert_brand(cur, brand_name)
    fingerprint = make_fingerprint(brand_name, name, region_code)

    price = None
    raw_price = raw_data.get('price')
    if raw_price is not None:
        price = extract_numeric(str(raw_price))

    rating = None
    raw_rating = raw_data.get('rating') or raw_data.get('stars')
    if raw_rating is not None:
        rating = extract_numeric(str(raw_rating))
        if rating and rating > 5:
            rating = rating / 10.0
        if rating and rating > 5:
            rating = 5.0

    review_count = extract_int(
        raw_data.get('review_count') or raw_data.get('reviews') or raw_data.get('reviewCount')
    )

    capacity_mah = extract_int(
        raw_data.get('capacity_mAh') or raw_data.get('capacity') or
        raw_data.get('battery_capacity')
    )
    if not capacity_mah:
        cap_text = str(raw_data.get('capacity', '') or raw_data.get('name', ''))
        match = re.search(r'(\d[\d,]*)\s*m[Aa][Hh]', cap_text)
        if match:
            capacity_mah = int(match.group(1).replace(',', ''))

    wattage = extract_numeric(
        raw_data.get('wattage') or raw_data.get('power_w') or raw_data.get('power')
    )

    port_count = extract_int(raw_data.get('port_count') or raw_data.get('ports'))

    has_qi2 = 1 if raw_data.get('qi2') or raw_data.get('has_qi2') else 0
    has_magsafe = 1 if raw_data.get('magsafe') or raw_data.get('has_magsafe') else 0
    has_wireless = 1 if raw_data.get('wireless') or raw_data.get('has_wireless') else 0
    has_gan = 1 if raw_data.get('gan') or raw_data.get('has_gan') or 'GaN' in str(raw_data) else 0
    has_retractable = 1 if raw_data.get('retractable_cable') or raw_data.get(
        'has_retractable') else 0
    has_pd = 1 if 'PD' in str(raw_data) or 'Power Delivery' in str(raw_data) else 0

    form_factor = raw_data.get('form_factor') or raw_data.get('form') or raw_data.get('type')

    # 推断形态
    if not form_factor:
        name_lower = name.lower()
        if any(w in name_lower for w in ['magnetic', 'magsafe', '磁吸', 'qi2']):
            form_factor = 'magnetic'
        elif any(w in name_lower for w in ['3-in-1', '3合1', '2-in-1', '2合1', 'stand']):
            form_factor = 'stand'
        elif 'desktop' in name_lower or 'station' in name_lower:
            form_factor = 'desktop'
        elif 'car' in name_lower or 'auto' in name_lower:
            form_factor = 'car'
        elif any(w in name_lower for w in ['power bank', 'powerbank', '移动电源']):
            form_factor = 'brick'
        elif any(w in name_lower for w in ['wall', 'charger', 'gan', 'adapter',
                                            'ladegerät']):
            form_factor = 'brick'
        else:
            form_factor = 'brick'

    source_url = raw_data.get('source_url', '')

    features = {}
    for fkey in ['protocol', 'color', 'weight', 'dimensions', 'warranty', 'cable_length',
                 'foldable_plug', 'display', 'passthrough']:
        if fkey in raw_data:
            features[fkey] = raw_data[fkey]

    data_quality = 0.0
    if brand_name:
        data_quality += 0.15
    if price:
        data_quality += 0.2
    if rating:
        data_quality += 0.15
    if name and len(name) > 5:
        data_quality += 0.15
    if capacity_mah or wattage:
        data_quality += 0.2
    if has_qi2 or has_gan or has_wireless:
        data_quality += 0.15

    now = datetime.datetime.now().isoformat()

    return {
        'name': name[:200],
        'brand_id': brand_id,
        'brand_name': brand_name[:100],
        'category_id': category_id,
        'region_id': region_id,
        'source': source_domain,
        'source_url': source_url[:500],
        'price': round(price, 2) if price else None,
        'price_currency': 'USD' if region_code == 'NA' else 'EUR',
        'rating': round(rating, 2) if rating else None,
        'review_count': review_count,
        'capacity_mah': capacity_mah,
        'wattage': round(wattage, 1) if wattage else None,
        'port_count': port_count,
        'has_qi2': has_qi2,
        'has_magsafe': has_magsafe,
        'has_wireless': has_wireless,
        'has_gan': has_gan,
        'has_pd': has_pd,
        'has_retractable_cable': has_retractable,
        'form_factor': form_factor,
        'features': json.dumps(features, ensure_ascii=False),
        'is_active': 1,
        'first_seen': now,
        'last_seen': now,
        'collected_at': now,
        'fingerprint': fingerprint,
        'data_quality_score': round(data_quality, 2),
    }


def save_products(products, region_id, category_slug, source, conn):
    """批量保存产品，处理去重和更新"""
    cur = conn.cursor()
    category_id = get_category_id(cur, category_slug)
    if not category_id:
        print(f"  ⚠️ 未知品类: {category_slug}")
        return 0, 0

    # 根据 region_id 确定 region_code
    cur.execute("SELECT code FROM regions WHERE id=?", (region_id,))
    row = cur.fetchone()
    region_code = row['code'] if row else 'EU'

    new_count = 0
    update_count = 0

    for raw in products:
        try:
            parsed = parse_product_raw(raw, source, region_id, category_id, cur, region_code)
        except Exception as e:
            print(f"  ⚠️ 解析产品失败: {e}")
            continue

        if parsed['data_quality_score'] < 0.2:
            continue

        cur.execute("SELECT id, last_seen FROM products WHERE fingerprint=?",
                    (parsed['fingerprint'],))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE products SET
                    price=?, rating=?, review_count=?, is_active=1,
                    last_seen=?, collected_at=?, data_quality_score=?
                WHERE fingerprint=?
            """, (
                parsed['price'], parsed['rating'], parsed['review_count'],
                parsed['last_seen'], parsed['collected_at'], parsed['data_quality_score'],
                parsed['fingerprint']
            ))
            update_count += 1
        else:
            cur.execute("""
                INSERT INTO products (
                    name, brand_id, brand_name, category_id, region_id, source, source_url,
                    price, price_currency, rating, review_count,
                    capacity_mah, wattage, port_count,
                    has_qi2, has_magsafe, has_wireless, has_gan, has_pd, has_retractable_cable,
                    form_factor, features,
                    is_active, first_seen, last_seen, collected_at,
                    fingerprint, data_quality_score
                ) VALUES (
                    :name, :brand_id, :brand_name, :category_id, :region_id, :source, :source_url,
                    :price, :price_currency, :rating, :review_count,
                    :capacity_mah, :wattage, :port_count,
                    :has_qi2, :has_magsafe, :has_wireless, :has_gan, :has_pd, :has_retractable_cable,
                    :form_factor, :features,
                    :is_active, :first_seen, :last_seen, :collected_at,
                    :fingerprint, :data_quality_score
                )
            """, parsed)
            new_count += 1

        if new_count % 10 == 0:
            conn.commit()

    conn.commit()
    return new_count, update_count


def get_collection_urls():
    """获取所有需要采集的URL列表"""
    urls = []
    for category_slug, queries in CATEGORY_SEARCH_QUERIES.items():
        for query_id, domain_short, path in queries:
            source_info = EU_SOURCES.get(domain_short.split('.')[-1], {})
            urls.append({
                'id': query_id,
                'category': category_slug,
                'source': domain_short,
                'domain': source_info.get('domain', domain_short),
                'currency': source_info.get('currency', 'EUR'),
                'country': source_info.get('name', ''),
                'url': f"https://www.{source_info.get('domain', domain_short)}{path}",
            })
    return urls


def log_collection_start(cur, region_id, category_id, source):
    now = datetime.datetime.now().isoformat()
    cur.execute("""
        INSERT INTO collection_logs (region_id, category_id, source, status, started_at)
        VALUES (?,?,?,'running',?)
    """, (region_id, category_id, source, now))
    return cur.lastrowid


def log_collection_finish(cur, log_id, status, sku_count, new_count, error_msg=None,
                          duration_ms=None):
    now = datetime.datetime.now().isoformat()
    cur.execute("""
        UPDATE collection_logs SET status=?, sku_count=?, new_sku_count=?,
        error_message=?, duration_ms=?, finished_at=?
        WHERE id=?
    """, (status, sku_count, new_count, error_msg, duration_ms, now, log_id))
