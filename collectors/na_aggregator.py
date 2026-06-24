"""
北美竞品数据采集器
策略：通过 WebSearch + 聚合站 (Consumerecho, Chargetechlab 等) 获取数据
配合 Keepa / Amazon PA-API 做后续价格追踪
"""
import hashlib
import json
import datetime


NA_SOURCES = {
    'consumerecho': {'domain': 'consumerecho.com', 'name': 'ConsumerEcho', 'type': 'review'},
    'chargetechlab': {'domain': 'chargetechlab.com', 'name': 'ChargeTechLab', 'type': 'review'},
    'gsmgotech': {'domain': 'gsmgotech.com', 'name': 'GSMGotech', 'type': 'blog'},
    'google_shopping': {'domain': 'shopping.google.com', 'name': 'Google Shopping', 'type': 'aggregator'},
}

CATEGORY_SEARCH_CONFIG = {
    'powerbank': {
        'keywords': [
            'best power bank 10000mAh Qi2 MagSafe 2026 review price',
            'Anker Belkin Baseus power bank portable charger top rated 2026',
            'power bank magnetic wireless charger best sellers Amazon',
        ],
        'aggregator_urls': [
            'https://products.consumerecho.com/product/qi2-powerbank/',
        ],
    },
    'wireless_charger': {
        'keywords': [
            'best Qi2 wireless charger 3-in-1 2026 Belkin Anker review',
            'wireless charger stand pad MagSafe top rated 2026 price',
        ],
        'aggregator_urls': [],
    },
    'adapter_cable': {
        'keywords': [
            'best USB-C GaN charger 65W 100W 2026 compact review',
            'Anker Ugreen GaN wall charger price specs 2026',
        ],
        'aggregator_urls': [],
    },
    'car_charger': {
        'keywords': [
            'best car charger USB-C PD retractable cable 2026',
        ],
        'aggregator_urls': [],
    },
    'desktop_charger': {
        'keywords': [
            'best desktop charging station multi port 100W 200W 2026',
            'Anker Ugreen desktop charger GaN review 2026',
        ],
        'aggregator_urls': [],
    },
    'energy_storage': {
        'keywords': [
            'best portable power station 1000Wh solar 2026 review',
            'Jackery EcoFlow Bluetti power station price specs 2026',
        ],
        'aggregator_urls': [],
    },
}


def make_fingerprint(brand, name):
    raw = f"{brand or 'unknown'}|{name}|NA".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def get_search_configs():
    """获取所有北美搜索配置"""
    configs = []
    for slug, conf in CATEGORY_SEARCH_CONFIG.items():
        for kw in conf['keywords']:
            configs.append({
                'category': slug,
                'type': 'websearch',
                'query': kw,
                'source': 'google',
            })
        for url in conf['aggregator_urls']:
            configs.append({
                'category': slug,
                'type': 'webfetch',
                'url': url,
                'source': url.split('/')[2],
            })
    return configs


def parse_na_product(raw_data, source_name):
    """解析北美产品数据为标准化格式"""
    brand = raw_data.get('brand', '') or raw_data.get('Brand', '')
    if not brand:
        name = raw_data.get('name', '') or raw_data.get('product', '')
        if name:
            brand = name.split()[0]

    name = raw_data.get('name', '') or raw_data.get('product', '') or raw_data.get('title', '')
    price = None
    try:
        p = raw_data.get('price') or raw_data.get('Price')
        if p and isinstance(p, str):
            p = p.replace('$', '').replace(',', '')
            price = float(p)
        elif p:
            price = float(p)
    except (ValueError, TypeError):
        pass

    rating = None
    try:
        r = raw_data.get('rating') or raw_data.get('Rating') or raw_data.get('stars')
        if r:
            rating = float(r)
            if rating > 5:
                rating = rating / 10.0
    except (ValueError, TypeError):
        pass

    capacity_mah = None
    wattage = None
    has_qi2 = 0
    has_gan = 0

    name_lower = str(name).lower()
    raw_str = str(raw_data).lower()

    if 'qi2' in name_lower or 'qi2' in raw_str:
        has_qi2 = 1
    if 'magsafe' in name_lower:
        has_qi2 = 1
    if 'gan' in name_lower or 'gan' in raw_str:
        has_gan = 1

    return {
        'name': name[:200],
        'brand_name': brand[:100],
        'price': price,
        'price_currency': 'USD',
        'rating': round(rating, 2) if rating else None,
        'review_count': None,
        'capacity_mah': capacity_mah,
        'wattage': wattage,
        'has_qi2': has_qi2,
        'has_gan': has_gan,
        'source': source_name,
        'region': 'NA',
    }
