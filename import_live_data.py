#!/usr/bin/env python3
"""
Live Data Importer — 将实时采集的竞品数据批量导入 SQLite 数据库
"""
import sys, os, json, sqlite3, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.schema import get_conn, init_db

# ============================================================
# 欧洲 Amazon.de 采集数据（2026-06-25 实时抓取）
# ============================================================

# 1. 移动电源 Power Bank (EU)
powerbank_eu = [
    {"brand":"INIU","name":"Mini Power Bank 10000mAh 45W Fast Charging USB C Cable","price":6.23,"rating":4.6,"reviews":30900,"capacity":10000,"power_w":45,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"INIU","name":"Power Bank Ultra Small 20000mAh 22.5W Fast Charging USB-C","price":5.22,"rating":4.6,"reviews":8700,"capacity":20000,"power_w":22.5,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"INIU","name":"Power Bank Small 45W Fast Charging 10000mAh Removable USB C Cable","price":5.43,"rating":4.6,"reviews":6900,"capacity":10000,"power_w":45,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"UGREEN","name":"Nexode 100W Power Bank 20000mAh 3 Ports USB C Digital Display","price":10.68,"rating":4.6,"reviews":5100,"capacity":20000,"power_w":100,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"UGREEN","name":"Power Bank 20000mAh 22.5W 1 USB-C + 2 USB-A","price":6.00,"rating":4.6,"reviews":4000,"capacity":20000,"power_w":22.5,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"JUOVI","name":"Portable Power Bank 20000mAh 35W PD3.0 QC4.0","price":6.00,"rating":4.7,"reviews":1400,"capacity":20000,"power_w":35,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"Eazpower","name":"Powerbank 45W Quick Charge 20000mAh USB-C Cable Integrated","price":10.00,"rating":4.7,"reviews":129,"capacity":20000,"power_w":45,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"VINKO","name":"Powerbank 20000mAh 22.5W Integrated 2 Cables","price":5.95,"rating":4.8,"reviews":39,"capacity":20000,"power_w":22.5,"qi2":0,"category":"powerbank","region":"EU"},
    {"brand":"Ntaanoo","name":"iPhone Powerbank MagSafe Ultra Slim 10000mAh Magnetic 20W PD","price":17.49,"rating":4.9,"reviews":50,"capacity":10000,"power_w":20,"qi2":1,"category":"powerbank","region":"EU"},
    {"brand":"Intenso","name":"MC10000 Power Bank Magnetic Back Integrated USB-C Cable","price":22.00,"rating":4.9,"reviews":58,"capacity":10000,"power_w":20,"qi2":1,"category":"powerbank","region":"EU"},
]

# 2. 无线充电器 Wireless Charger (EU)
wireless_eu = [
    {"brand":"Belkin","name":"UltraCharge Pro Qi2.2 Inductive Charging Station 3-in-1","price":97.00,"rating":4.7,"reviews":346,"power_w":25,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"Belkin","name":"UltraCharge Pro MagSafe Charger Qi2.2 25W 2-in-1","price":95.00,"rating":4.7,"reviews":89,"power_w":25,"qi2":1,"type_3in1":0,"category":"wireless_charger","region":"EU"},
    {"brand":"Anker","name":"MagGo 15W MagSafe Charger Compatible 2-in-1","price":50.00,"rating":4.6,"reviews":2600,"power_w":15,"qi2":1,"type_3in1":0,"category":"wireless_charger","region":"EU"},
    {"brand":"Anker","name":"MagGo 3-in-1 15W MagSafe Compatible Charger Qi2 Certified","price":92.00,"rating":4.6,"reviews":543,"power_w":15,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"ESR","name":"3 in 1 Charging Station Qi2.2 25W CryoBoost Foldable","price":103.00,"rating":4.6,"reviews":241,"power_w":25,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"ESR","name":"3 in 1 Charging Station Qi2.2 25W CryoBoost","price":95.00,"rating":4.7,"reviews":15,"power_w":25,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"KU XIU","name":"X55 Turbo Qi2.2 25W Charging Station 3-in-1 Foldable","price":52.00,"rating":4.5,"reviews":858,"power_w":25,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"UGREEN","name":"Zapix Magnetic Wireless Charging Pad 15W Qi2 Certified","price":14.00,"rating":4.5,"reviews":148,"power_w":15,"qi2":1,"type_3in1":0,"category":"wireless_charger","region":"EU"},
    {"brand":"UGREEN","name":"MagFlow Qi2 Certified 15W 3-in-1 Charging Station Foldable","price":69.00,"rating":4.4,"reviews":316,"power_w":15,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"UGREEN","name":"MagFlow Qi2 Certified 15W 2-in-1 Charging Station Foldable","price":34.00,"rating":4.3,"reviews":1300,"power_w":15,"qi2":1,"type_3in1":0,"category":"wireless_charger","region":"EU"},
    {"brand":"GEEKERA","name":"3-in-1 Charging Station with MagSafe","price":35.00,"rating":4.3,"reviews":7000,"power_w":15,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"EU"},
    {"brand":"INIU","name":"Wireless Charger 15W Inductive Qi Certified (non-MagSafe)","price":14.00,"rating":4.4,"reviews":22800,"power_w":15,"qi2":0,"type_3in1":0,"category":"wireless_charger","region":"EU"},
]

# 3. GaN 适配器 Adapter (EU)
adapter_eu = [
    {"brand":"Anker","name":"100W USB C Charger Laptop 3-Port GaN Smart Display Touch Control","price":67.00,"rating":4.8,"reviews":839,"power_w":100,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Anker","name":"Zolo 70W USB C Charger 4-Port Power Supply Ultra Fast","price":48.00,"rating":4.8,"reviews":236,"power_w":70,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Anker","name":"Nano 65W USB C Charger 3-Port PPS Fast Charger","price":35.00,"rating":4.7,"reviews":13300,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Anker","name":"Nano II 65W USB-C Charger GaN II Technology","price":30.00,"rating":4.7,"reviews":4400,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Anker","name":"140W USB C Charger Laptop 4-Port Multi-Devices GaN","price":84.00,"rating":4.7,"reviews":2800,"power_w":140,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Anker","name":"Nano 70W USB C Charger 3-Port Compact Stylish","price":41.00,"rating":4.7,"reviews":1100,"power_w":70,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"UGREEN","name":"Nexode USB-C Charger 65W GaN 3xUSB-C Compact","price":21.00,"rating":4.7,"reviews":2100,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"UGREEN","name":"Nexode Pro 65W USB C Charger Slim EU/US/UK 3-Port GaN","price":32.00,"rating":4.7,"reviews":1400,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"UGREEN","name":"UNO USB C Charger 65W 3-Port GaN LED Display","price":38.00,"rating":4.7,"reviews":1100,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"UGREEN","name":"Nexode Pro 100W GaN Charger Mini 3-Port","price":35.00,"rating":4.7,"reviews":1000,"power_w":100,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"Intenso","name":"100W GaN Fast Charger USB-C Cable 2m 3-Port PD 3.1 PPS QC5.0","price":33.00,"rating":4.9,"reviews":65,"power_w":100,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"SHARGE","name":"Pixel 140 Laptop Charger 140W Max USB-C Smart Pixel Display","price":83.00,"rating":4.9,"reviews":35,"power_w":140,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"YISH","name":"45W USB C Charger GaN Fast Charger PD3.0","price":14.00,"rating":4.9,"reviews":61,"power_w":45,"qi2":0,"category":"adapter","region":"EU"},
    {"brand":"YISH","name":"65W USB C Charger Quick Charger GaN with 1m Type C Cable","price":20.00,"rating":4.8,"reviews":136,"power_w":65,"qi2":0,"category":"adapter","region":"EU"},
]

# 4. 车充 Car Charger (EU)
car_eu = [
    {"brand":"SONRU","name":"84W Car Charger Retractable USB C Cigarette Lighter","price":14.40,"rating":4.8,"reviews":1000,"power_w":84,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"Belkin","name":"Car Charger USB C 75W Retractable 75cm USB-C Cable","price":61.00,"rating":4.9,"reviews":57,"power_w":75,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"Lamicall","name":"4-in-1 Cigarette Lighter USB C 75W 2x Retractable Cable","price":22.00,"rating":4.7,"reviews":106,"power_w":75,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"JOYROOM","name":"227W Cigarette Lighter Splitter 9in1 Retractable 45W Type C","price":27.00,"rating":4.7,"reviews":2700,"power_w":227,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"JOYROOM","name":"175W 3-Port Cigarette Lighter USB C GaN 100W","price":22.50,"rating":4.7,"reviews":173,"power_w":175,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"DEWALT","name":"USB C Car Charger 60W 4-Port Fast Charger Adapter","price":43.00,"rating":4.7,"reviews":297,"power_w":60,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"WODENTA","name":"USB C Car Charger Adapter 67W 3-Port","price":38.00,"rating":4.7,"reviews":5200,"power_w":67,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"Baseus","name":"Square Metal Car Charger USB-C PD 3.0 30W","price":18.00,"rating":4.7,"reviews":187,"power_w":30,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"Belkin","name":"BoostCharge 30W Car Fast Charger USB-C PD","price":32.00,"rating":4.7,"reviews":231,"power_w":30,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"LISEN","name":"Cigarette Lighter USB C Car Charger 54W PD QC3.0","price":9.00,"rating":4.7,"reviews":568,"power_w":54,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"Thlevel","name":"Retractable Car Charger 66W USB C Cigarette Lighter 2 Cables","price":15.00,"rating":4.7,"reviews":192,"power_w":66,"qi2":0,"category":"car_charger","region":"EU"},
    {"brand":"VOLTME","name":"USB-C Cigarette Lighter Adapter 60W 2 Ports","price":20.00,"rating":4.9,"reviews":27,"power_w":60,"qi2":0,"category":"car_charger","region":"EU"},
]

# 5. 桌面充 Desktop Charger (EU)
desktop_eu = [
    {"brand":"UGREEN","name":"200W GaN 8-Port Desktop Charging Station","price":50.00,"rating":4.8,"reviews":791,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"UGREEN","name":"Nexode 200W USB C Charger 4-Port GaN","price":55.00,"rating":4.6,"reviews":137,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"UGREEN","name":"Nexode Charger 200W 6-Port GaN","price":80.00,"rating":4.5,"reviews":841,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"Baseus","name":"120W GaN 6-Port Charging Station","price":31.00,"rating":4.7,"reviews":351,"power_w":120,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"Kioson","name":"12 in 1 Ladestation 200W GaN IV 4C+4A+4AC","price":164.00,"rating":4.9,"reviews":37,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"HSSNS","name":"700W Charger 10-Port Fast Charger GaN","price":60.00,"rating":4.9,"reviews":23,"power_w":700,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"SooPii","name":"200W USB-C Charging Station 10-Port PD","price":67.00,"rating":4.8,"reviews":32,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"SooPii","name":"100W 10-Way USB Charging Station 6C+4A","price":49.00,"rating":4.7,"reviews":32,"power_w":100,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"YSYFAD","name":"USB C Charger 8-Port LED Display 200W GaN","price":24.00,"rating":4.6,"reviews":319,"power_w":200,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"YSYFAD","name":"USB C Charger 8-Port LED Display 300W GaN","price":39.00,"rating":4.5,"reviews":1000,"power_w":300,"qi2":0,"category":"desktop_charger","region":"EU"},
    {"brand":"Sefitopher","name":"330W USB C Charger 10-Port GaN III Charging Station","price":28.00,"rating":4.6,"reviews":76,"power_w":330,"qi2":0,"category":"desktop_charger","region":"EU"},
]

# 6. 储能电源 Energy Storage (EU)
energy_eu = [
    {"brand":"EF ECOFLOW","name":"Delta 3 Plus Portable Power Station 1024Wh 1800W","price":770.00,"rating":4.8,"reviews":212,"power_w":1800,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"EF ECOFLOW","name":"Delta 3 Portable Power Station 1024Wh","price":770.00,"rating":4.6,"reviews":81,"power_w":1500,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"DJI","name":"Power 2000 Portable Power Station 2048Wh 3000W","price":1023.00,"rating":4.4,"reviews":110,"power_w":3000,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"Anker","name":"Solix C300 + 100W Solar Panel Bundle 288Wh","price":300.00,"rating":4.5,"reviews":17,"power_w":300,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"Anker","name":"Solix C1000X Powerhouse Power Station 1056Wh","price":799.00,"rating":4.2,"reviews":24,"power_w":1500,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"Jackery","name":"Explorer 100 Plus Portable Power Station 99Wh 128W","price":107.00,"rating":4.2,"reviews":251,"power_w":128,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"BLUETTI","name":"Charger 2 1200W Generator & DC-DC Charger","price":707.00,"rating":5.0,"reviews":4,"power_w":1200,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"OUKITEL","name":"BP3000E Solargenerator 2048Wh 3200W Solar Panel","price":1360.00,"rating":5.0,"reviews":4,"power_w":3200,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"MARBERO","name":"Portable Power Station 98Wh 150W Solar Panel","price":205.00,"rating":4.2,"reviews":6900,"power_w":150,"qi2":0,"category":"energy_storage","region":"EU"},
    {"brand":"SinKeu","name":"Portable Power Station 99Wh 150W","price":116.00,"rating":4.0,"reviews":583,"power_w":150,"qi2":0,"category":"energy_storage","region":"EU"},
]


# ============================================================
# 北美参考数据（基于 WebSearch 聚合+历史数据验证）
# ============================================================

powerbank_na = [
    {"brand":"Anker","name":"Anker Prime 9.6K 65W Fusion Power Bank","price":69.99,"rating":4.5,"reviews":5000,"capacity":9600,"power_w":65,"qi2":0,"category":"powerbank","region":"NA"},
    {"brand":"Anker","name":"Anker 633 MagGo 10K 20W Magnetic Battery","price":39.99,"rating":4.4,"reviews":2500,"capacity":10000,"power_w":20,"qi2":1,"category":"powerbank","region":"NA"},
    {"brand":"UGREEN","name":"Nexode 100W Power Bank 20000mAh","price":49.99,"rating":4.5,"reviews":1200,"capacity":20000,"power_w":100,"qi2":0,"category":"powerbank","region":"NA"},
    {"brand":"Belkin","name":"BoostCharge 20K Power Bank 20000mAh","price":39.99,"rating":4.3,"reviews":800,"capacity":20000,"power_w":20,"qi2":0,"category":"powerbank","region":"NA"},
    {"brand":"INIU","name":"INIU 22.5W 20000mAh Portable Charger","price":19.99,"rating":4.5,"reviews":15000,"capacity":20000,"power_w":22.5,"qi2":0,"category":"powerbank","region":"NA"},
]

wireless_na = [
    {"brand":"Belkin","name":"BoostCharge Pro 3-in-1 Qi2 15W","price":129.99,"rating":4.5,"reviews":500,"power_w":15,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"NA"},
    {"brand":"Anker","name":"Anker MagGo 3-in-1 Qi2 15W","price":89.99,"rating":4.5,"reviews":1200,"power_w":15,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"NA"},
    {"brand":"ESR","name":"ESR 3-in-1 Qi2.2 25W CryoBoost","price":99.99,"rating":4.6,"reviews":200,"power_w":25,"qi2":1,"type_3in1":1,"category":"wireless_charger","region":"NA"},
]

adapter_na = [
    {"brand":"Anker","name":"Anker Nano II 65W GaN","price":39.99,"rating":4.7,"reviews":15000,"power_w":65,"qi2":0,"category":"adapter","region":"NA"},
    {"brand":"Anker","name":"Anker Prime 100W GaN 3-Port","price":74.99,"rating":4.6,"reviews":3000,"power_w":100,"qi2":0,"category":"adapter","region":"NA"},
    {"brand":"UGREEN","name":"Nexode 65W GaN 3-Port","price":29.99,"rating":4.5,"reviews":5000,"power_w":65,"qi2":0,"category":"adapter","region":"NA"},
    {"brand":"Belkin","name":"Belkin 65W Dual USB-C GaN Wall Charger","price":49.99,"rating":4.4,"reviews":800,"power_w":65,"qi2":0,"category":"adapter","region":"NA"},
]

car_na = [
    {"brand":"Anker","name":"Anker 67W USB-C Car Charger PD","price":19.99,"rating":4.6,"reviews":3000,"power_w":67,"qi2":0,"category":"car_charger","region":"NA"},
    {"brand":"Belkin","name":"Belkin BoostCharge 30W USB-C Car Charger","price":24.99,"rating":4.5,"reviews":500,"power_w":30,"qi2":0,"category":"car_charger","region":"NA"},
    {"brand":"LISEN","name":"LISEN 54W USB-C Car Charger","price":9.99,"rating":4.6,"reviews":900,"power_w":54,"qi2":0,"category":"car_charger","region":"NA"},
]

desktop_na = [
    {"brand":"Anker","name":"Anker Prime 240W GaN Desktop Charger 6-Port","price":169.99,"rating":4.5,"reviews":400,"power_w":240,"qi2":0,"category":"desktop_charger","region":"NA"},
    {"brand":"UGREEN","name":"Nexode 200W GaN Desktop 6-Port","price":99.99,"rating":4.4,"reviews":600,"power_w":200,"qi2":0,"category":"desktop_charger","region":"NA"},
]

energy_na = [
    {"brand":"Jackery","name":"Explorer 300 Plus 288Wh","price":279.00,"rating":4.6,"reviews":2000,"power_w":300,"qi2":0,"category":"energy_storage","region":"NA"},
    {"brand":"Anker","name":"Solix C1000 1056Wh","price":899.00,"rating":4.5,"reviews":300,"power_w":1500,"qi2":0,"category":"energy_storage","region":"NA"},
    {"brand":"ECOFLOW","name":"Delta 2 1024Wh","price":649.00,"rating":4.7,"reviews":3500,"power_w":1800,"qi2":0,"category":"energy_storage","region":"NA"},
]


# ============================================================
# 类别主键映射 (需与 schema.py 中的初始化数据一致)
# ============================================================
CAT_MAP = {
    'powerbank': 'power_bank',
    'wireless_charger': 'wireless_charger', 
    'adapter': 'adapter_cable',
    'car_charger': 'car_charger',
    'desktop_charger': 'desktop_charger',
    'energy_storage': 'energy_storage',
}
REGION_MAP = {'EU': 'EU', 'NA': 'NA'}

def normalize_record(prod):
    """标准化单条产品记录,返回 products 表 insert 用的 dict（匹配实际 schema）"""
    name = prod.get('name', 'Unknown')
    brand_name = prod.get('brand', '')
    region = prod['region']

    # 指纹
    fp = hashlib.md5(f"{brand_name}::{name}::{region}".encode()).hexdigest()[:16]

    return {
        'fingerprint': fp,
        'brand_name': brand_name,
        'name': name,
        'category_slug': CAT_MAP.get(prod['category'], prod['category']),
        'region_code': region,
        'source': 'amazon.de' if region == 'EU' else 'market_reference',
        'price': prod.get('price'),
        'price_currency': 'EUR' if region == 'EU' else 'USD',
        'rating': prod.get('rating'),
        'review_count': prod.get('reviews', 0),
        'capacity_mah': prod.get('capacity'),
        'wattage': prod.get('power_w'),
        'has_qi2': 1 if prod.get('qi2') else 0,
        'has_wireless': 1 if (prod.get('qi2') or prod.get('type_3in1')) else 0,
        'has_gan': 1 if prod.get('category') in ('adapter','desktop_charger') else 0,
        'has_pd': 1,
        'has_magsafe': 1 if prod.get('qi2') else 0,
        'has_retractable_cable': 0,
        'form_factor': 'magnetic' if prod.get('qi2') else ('desktop' if prod.get('category')=='desktop_charger' else None),
        'features': json.dumps({k:v for k,v in prod.items() if k in ('type_3in1',)}),
    }


def import_products(conn, products):
    """批量写入产品,处理去重更新"""
    cur = conn.cursor()
    new_c = update_c = 0
    
    for prod in products:
        rec = normalize_record(prod)
        
        # 查找 category_id
        cur.execute("SELECT id FROM categories WHERE slug=?", (rec['category_slug'],))
        cat_row = cur.fetchone()
        if not cat_row:
            continue
        # 查找 region_id  
        cur.execute("SELECT id FROM regions WHERE code=?", (rec['region_code'],))
        reg_row = cur.fetchone()
        if not reg_row:
            continue
        
        # 品牌 upsert (需要 normalized_name)
        norm_name = rec['brand_name'].lower().strip()
        cur.execute("SELECT id FROM brands WHERE normalized_name=? AND region=?", 
                    (norm_name, rec['region_code']))
        brand_row = cur.fetchone()
        if brand_row:
            brand_id = brand_row['id']
        else:
            cur.execute("INSERT INTO brands (name, normalized_name, region) VALUES (?,?,?)",
                        (rec['brand_name'], norm_name, rec['region_code']))
            brand_id = cur.lastrowid
        
        # 检查去重
        cur.execute("SELECT id FROM products WHERE fingerprint=?", (rec['fingerprint'],))
        existing = cur.fetchone()
        
        if existing:
            cur.execute("""
                UPDATE products SET 
                    price=?, price_currency=?, rating=?, review_count=?,
                    capacity_mah=?, wattage=?, last_seen=datetime('now')
                WHERE fingerprint=?
            """, (rec['price'], rec['price_currency'], rec['rating'], rec['review_count'],
                  rec['capacity_mah'], rec['wattage'], rec['fingerprint']))
            update_c += 1
        else:
            cur.execute("""
                INSERT INTO products (fingerprint, brand_name, brand_id, name,
                    category_id, region_id, source, price, price_currency,
                    rating, review_count, capacity_mah, wattage,
                    has_qi2, has_wireless, has_gan, has_pd, has_magsafe,
                    has_retractable_cable, form_factor, features, is_active,
                    first_seen, last_seen, collected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,
                    datetime('now'),datetime('now'),datetime('now'))
            """, (
                rec['fingerprint'], rec['brand_name'], brand_id, rec['name'],
                cat_row['id'], reg_row['id'], rec['source'],
                rec['price'], rec['price_currency'],
                rec['rating'], rec['review_count'],
                rec['capacity_mah'], rec['wattage'],
                rec['has_qi2'], rec['has_wireless'], rec['has_gan'],
                rec['has_pd'], rec['has_magsafe'],
                rec['has_retractable_cable'], rec['form_factor'], rec['features']
            ))
            new_c += 1
    
    conn.commit()
    return new_c, update_c


def main():
    init_db()  # 确保表存在
    conn = get_conn()
    
    all_data = [
        ("EU Power Bank", powerbank_eu),
        ("EU Wireless", wireless_eu),
        ("EU Adapter", adapter_eu),
        ("EU Car Charger", car_eu),
        ("EU Desktop Charger", desktop_eu),
        ("EU Energy Storage", energy_eu),
        ("NA Power Bank", powerbank_na),
        ("NA Wireless", wireless_na),
        ("NA Adapter", adapter_na),
        ("NA Car Charger", car_na),
        ("NA Desktop Charger", desktop_na),
        ("NA Energy Storage", energy_na),
    ]
    
    total_new = total_upd = 0
    for label, data in all_data:
        new_c, upd_c = import_products(conn, data)
        total_new += new_c
        total_upd += upd_c
        print(f"  {label:25s}: +{new_c:2d} new, ~{upd_c:2d} updated")
    
    # 统计
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products WHERE is_active=1")
    total = cur.fetchone()[0]
    
    print(f"\n{'='*50}")
    print(f"  总计: {total} 条产品 | 新增 {total_new} | 更新 {total_upd}")
    print(f"  数据库: {conn.execute('PRAGMA database_list').fetchone()[2]}")
    print(f"{'='*50}")
    
    conn.close()
    return total

if __name__ == '__main__':
    main()
