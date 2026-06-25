"""
批量更新产品图片和真实产品页链接
- 从 WebFetch 抓取的 Amazon.de 搜索结果匹配到数据库产品
- 更新 source_url → 真实 ASIN 链接, image_url → 产品图片
"""

import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.schema import DB_PATH

# ============================================================
# 从 Amazon.de 搜索结果中提取的 ASIN → (image_url, 品牌, 产品名)
# ============================================================
AMAZON_PRODUCTS = [
    # Anker 品类
    ("B0CFDPQXN4", "https://m.media-amazon.com/images/I/61nB5ITlheL._AC_UY218_.jpg", "Anker", "MagGo Qi2 10K"),
    ("B0CFDSMNT7", "https://m.media-amazon.com/images/I/61exLw6fM4L._AC_UY218_.jpg", "Anker", "MagGo Qi2 10K"),
    ("B0CFDQ9QH5", "https://m.media-amazon.com/images/I/51tLiKYI4DL._AC_UY218_.jpg", "Anker", "MagGo Qi2 10K"),
    ("B0CZDFL2BY", "https://m.media-amazon.com/images/I/61k4xGsWAnL._AC_UY218_.jpg", "Anker", "MagGo Apple Watch 10K"),
    ("B09P8CX1X7", "https://m.media-amazon.com/images/I/51VJQ1lfAaL._AC_UY218_.jpg", "Anker", "633 Magnetic 10K"),
    ("B0FKMG4WPN", "https://m.media-amazon.com/images/I/61xFVOUcwjL._AC_UY218_.jpg", "Anker", "Prime 3-in-1 Qi2 25W"),
    ("B0CFPHZZYT", "https://m.media-amazon.com/images/I/516SYoZrerL._AC_UY218_.jpg", "Anker", "MagGo 3-in-1 Qi2"),
    ("B0D8SV392D", "https://m.media-amazon.com/images/I/61Icx1aPA6L._AC_UY218_.jpg", "Anker", "MagGo 3-in-1 Travel"),
    ("B0D8PN1GBP", "https://m.media-amazon.com/images/I/61tsPe-PZaL._AC_UY218_.jpg", "Anker", "MagGo Wireless Stand"),

    # Belkin 品类
    ("B0GPY1GYP5", "https://m.media-amazon.com/images/I/51P-MO0GwdL._AC_UY218_.jpg", "Belkin", "BoostCharge Magnetic 5K Qi2"),
    ("B0GPXS51KD", "https://m.media-amazon.com/images/I/51EcjyqpAJL._AC_UY218_.jpg", "Belkin", "BoostCharge Magnetic 5K Sand"),
    ("B0G5QYQZTW", "https://m.media-amazon.com/images/I/5140LK39JZL._AC_UY218_.jpg", "Belkin", "BoostCharge Pro 10K Apple Watch"),
    ("B0CTJBXBBN", "https://m.media-amazon.com/images/I/512Wic2cMfL._AC_UY218_.jpg", "Belkin", "BoostCharge Pro Qi2 5K"),
    ("B0GKP5G1T2", "https://m.media-amazon.com/images/I/51TlpfNZV8L._AC_UY218_.jpg", "Belkin", "BoostCharge Qi2 5K Slim"),
    ("B0GKP1B1SP", "https://m.media-amazon.com/images/I/51O3-n+T4hL._AC_UY218_.jpg", "Belkin", "BoostCharge Qi2 5K White"),
    ("B0GYT2RYB7", "https://m.media-amazon.com/images/I/51V7r4z6fJL._AC_UY218_.jpg", "Belkin", "BoostCharge Magnetic 5K Black"),
    ("B0GYSXSN4W", "https://m.media-amazon.com/images/I/518+jNhtbcL._AC_UY218_.jpg", "Belkin", "BoostCharge Magnetic 5K Sand"),
    ("B0DCDWTTSG", "https://m.media-amazon.com/images/I/51B1Adm7osL._AC_UY218_.jpg", "Belkin", "BoostCharge 3-Port 20K"),
    ("B0GY331C26", "https://m.media-amazon.com/images/I/61TEtbfOXKL._AC_UY218_.jpg", "AC Island", "5-in-1 Qi2 Charging Station"),

    # UGREEN 品类
    ("B0DJXN3N3L", "https://m.media-amazon.com/images/I/61KYNMzRbXL._AC_UY218_.jpg", "UGREEN", "Zapix Qi2 10K"),
    ("B0DPQP8L9S", "https://m.media-amazon.com/images/I/61xOiaDsUDL._AC_UY218_.jpg", "UGREEN", "Zapix Qi2 20K"),
    ("B0F6NC41DZ", "https://m.media-amazon.com/images/I/516ZMALSZbL._AC_UY218_.jpg", "UGREEN", "MagFlow Air 10K"),
    ("B0DSPW29HV", "https://m.media-amazon.com/images/I/51IJCL5OfwL._AC_UY218_.jpg", "UGREEN", "Zapix Qi2 10K Stand"),
    ("B0F6NFHB31", "https://m.media-amazon.com/images/I/51P-ylI1GpL._AC_UY218_.jpg", "UGREEN", "MagFlow Air 5K"),
    ("B0BJQ7F16T", "https://m.media-amazon.com/images/I/612WlRQDgtL._AC_UY218_.jpg", "UGREEN", "Nexode 145W 25K"),
    ("B0G2SDQQMF", "https://m.media-amazon.com/images/I/51fSrRCK2zL._AC_UY218_.jpg", "UGREEN", "MagFlow 25W Qi2 10K White"),
    ("B0FJR63WW4", "https://m.media-amazon.com/images/I/51vJzOl2iHL._AC_UY218_.jpg", "UGREEN", "Nexode Pro 200W 25K"),
    ("B0G2S9LVS4", "https://m.media-amazon.com/images/I/51Hv0WGVbsL._AC_UY218_.jpg", "UGREEN", "MagFlow 25W Qi2 10K Grey"),
    ("B0CH33F5P2", "https://m.media-amazon.com/images/I/51zFgm2MTHL._AC_UY218_.jpg", "UGREEN", "Zapix Magnetic 10K"),
    ("B0CMXFVB71", "https://m.media-amazon.com/images/I/51axzgXHQLL._AC_UY218_.jpg", "UGREEN", "Nexode X 160W GaN"),
    ("B0DL59GWWK", "https://m.media-amazon.com/images/I/51XAoD5UyxL._AC_UY218_.jpg", "UGREEN", "Nexode 200W 8-Port Desktop"),

    # Baseus 品类
    ("B0FNRDRDTQ", "https://m.media-amazon.com/images/I/51ZSmwYOViL._AC_UY218_.jpg", "Baseus", "USB MagSafe 160W"),
    ("B0F23N4HNH", "https://m.media-amazon.com/images/I/51JArPv4BkL._AC_UY218_.jpg", "Baseus", "Enerfill 100W GaN"),
    ("B0DX6SVQ7P", "https://m.media-amazon.com/images/I/61kFXxMvT0L._AC_UY218_.jpg", "Baseus", "QPow3 45W 20K"),
    ("B0GGN4P3FM", "https://m.media-amazon.com/images/I/51fsvuCAdGL._AC_UY218_.jpg", "Baseus", "Enerfill MagSafe 10K 30W"),
    ("B0F1XRYGKZ", "https://m.media-amazon.com/images/I/71giszY1qcL._AC_UY218_.jpg", "Baseus", "Picogo AM41 Titanium"),
    ("B0CM93KQSC", "https://m.media-amazon.com/images/I/71VzYv2CL5L._AC_UY218_.jpg", "Baseus", "Power Bank 20K 20W"),
    ("B0FN86KVLV", "https://m.media-amazon.com/images/I/71mEn22Jd7L._AC_UY218_.jpg", "Baseus", "Picogo AM41 Black"),
    ("B0G4CHTD53", "https://m.media-amazon.com/images/I/61NhmZHsNBL._AC_UY218_.jpg", "Baseus", "PicoGo AM52 Qi2.2 10K"),
    ("B0F5QBG5M8", "https://m.media-amazon.com/images/I/71eMEGnWdEL._AC_UY218_.jpg", "Baseus", "Mini MagSafe 5K Qi2"),
    ("B0FXGNDKZM", "https://m.media-amazon.com/images/I/51ghmeQ6GYL._AC_UY218_.jpg", "Baseus", "Enerfill MagSafe 10K v2"),
    ("B0F434TYST", "https://m.media-amazon.com/images/I/513+1Bc8cpL._AC_UY218_.jpg", "Baseus", "Power Bank 20K 45W Purple"),
    ("B0F4C8PFNB", "https://m.media-amazon.com/images/I/512rg8IESoL._AC_UY218_.jpg", "Baseus", "Power Bank 20K 45W Blue"),
    ("B0DKFS24X8", "https://m.media-amazon.com/images/I/61bT862AmtL._AC_UY218_.jpg", "Baseus", "Picogo 10K 45W"),
    ("B0FNRKQTZ9", "https://m.media-amazon.com/images/I/61KaD38c+kL._AC_UY218_.jpg", "Baseus", "USB C 120W GaN 6-Port"),
    ("B0DK2SZZ8L", "https://m.media-amazon.com/images/I/61T-cbWe6BL._AC_UY218_.jpg", "Baseus", "Nomos Qi2 10K"),

    # INIU 品类
    ("B0DCYR5VNR", "https://m.media-amazon.com/images/I/71vl4HvUaxL._AC_UY218_.jpg", "INIU", "45W 20K Built-in Cable"),
    ("B0DCZ82MGG", "https://m.media-amazon.com/images/I/71GCJKW+zEL._AC_UY218_.jpg", "INIU", "Smallest 22.5W 20K"),
    ("B0FW45F3ZJ", "https://m.media-amazon.com/images/I/71vZsgkBmvL._AC_UY218_.jpg", "INIU", "Ultra Thin 10K 45W"),
    ("B0CB19RKZ1", "https://m.media-amazon.com/images/I/61YRH5u8wAL._AC_UY218_.jpg", "INIU", "140W Laptop 27K"),
    ("B09MK7PQBV", "https://m.media-amazon.com/images/I/61-EpK1mPnS._AC_UY218_.jpg", "INIU", "65W LED 20K"),
    ("B0DC93Z911", "https://m.media-amazon.com/images/I/7194KeugdyL._AC_UY218_.jpg", "INIU", "Mini 10K 45W"),
    ("B0B7438Q2Z", "https://m.media-amazon.com/images/I/61P0pp12VGL._AC_UY218_.jpg", "INIU", "100W Laptop 25K"),
    ("B0GLZ3YSW8", "https://m.media-amazon.com/images/I/61cKQE7vNOL._AC_UY218_.jpg", "INIU", "45W 20K + 30W Charger Bundle"),
    ("B0DS5VS6TT", "https://m.media-amazon.com/images/I/61m1PyD9RXL._AC_UY218_.jpg", "INIU", "Apple Watch 5K Pink"),
    ("B0CB1DF4JQ", "https://m.media-amazon.com/images/I/71NHdNB748L._AC_UY218_.jpg", "INIU", "65W Laptop 20K"),
    ("B0DKN3VMF1", "https://m.media-amazon.com/images/I/71Mrbn4vuUL._AC_UY218_.jpg", "INIU", "Mini 22.5W 5.5K Foldable"),
    ("B0FC6D44MT", "https://m.media-amazon.com/images/I/71Y8al653mL._AC_UY218_.jpg", "INIU", "Mini 45W 10K White"),
    ("B0DNZ8LC4B", "https://m.media-amazon.com/images/I/61Fnyr-gKAL._AC_UY218_.jpg", "INIU", "30W Magnetic Qi2 10K Blue"),
    ("B0DS5TFF2V", "https://m.media-amazon.com/images/I/6156ej5lBmL._AC_UY218_.jpg", "INIU", "Apple Watch 5K Purple"),
    ("B0DD3P1GKT", "https://m.media-amazon.com/images/I/71hw1u4b28L._AC_UL640_QL65_.jpg", "INIU", "Ultra Thin 45W 10K"),
    ("B0DMT6FMT7", "https://m.media-amazon.com/images/I/71hR0tdjwfL._AC_UY218_.jpg", "INIU", "Ultra Slim Qi2 10K 45W"),
    ("B0DMP9YJTP", "https://m.media-amazon.com/images/I/710zuoBGqiL._AC_UY218_.jpg", "INIU", "Ultra Slim Qi2 10K White"),
    ("B0GT65MCKK", "https://m.media-amazon.com/images/I/71DHwJquU-L._AC_UY218_.jpg", "INIU", "Kompakt MagSafe 25W+45W"),

    # 其他品牌 (ESR/EcoFlow/TORRAS/iWALK)
    ("B0GD7CX1F7", "https://m.media-amazon.com/images/I/51VzDy7Z+iL._AC_UY218_.jpg", "EcoFlow", "Qi2.2 MagSafe 10K 25W"),
    ("B0F8VLH5QN", "https://m.media-amazon.com/images/I/51nd0Upo+OL._AC_UY218_.jpg", "EcoFlow", "MagSafe 5K"),
    ("B0FNWHDTM5", "https://m.media-amazon.com/images/I/71J-Zw5LHwL._AC_UY218_.jpg", "ESR", "OmniLock Qi2.2 Car Mount"),
    ("B0D8JFJ5W4", "https://m.media-amazon.com/images/I/615YIcC7DlL._AC_UL320_.jpg", "TORRAS", "MiniMag Qi2 10K 22.5W"),
    ("B0DLNR6ZKN", "https://m.media-amazon.com/images/I/61oSelM-UOL._AC_UY218_.jpg", "TORRAS", "MiniMag Desert Ti"),
    ("B0DJ3528LG", "https://m.media-amazon.com/images/I/61N+5-gZJuL._AC_UY218_.jpg", "TORRAS", "MiniMag Qi2 10K 30W"),
    ("B0D91ZBH3P", "https://m.media-amazon.com/images/I/519zw7fbfVL._AC_UY218_.jpg", "iWALK", "MagSafe Qi2 10K 30W"),
    ("B0DYV89XD6", "https://m.media-amazon.com/images/I/61soC5uOb5L._AC_UL320_.jpg", "Movespeed", "MagSafe Qi2 10K Slim"),
    ("B0F2HN19JM", "https://m.media-amazon.com/images/I/71oDvlEhnLL._AC_UY218_.jpg", "KU XIU", "K1ULTRA 10K Apple Watch Qi2.2"),

    # GaN 适配器 (Amazon.de search: Anker GaN USB-C charger 65W 100W)
    ("B0FG745LNB", "https://m.media-amazon.com/images/I/61vURARLAJL._AC_UY218_.jpg", "Anker", "100W GaN 3-Port Smart Display"),
    ("B0FG77P8RR", "https://m.media-amazon.com/images/I/71MqkMflRBL._AC_UY218_.jpg", "Anker", "100W GaN 3-Port Smart Display"),
    ("B0DSVZ993Y", "https://m.media-amazon.com/images/I/61XqdeGtCiL._AC_UY218_.jpg", "Anker", "Prime 100W GaN 3-Port"),
    ("B0DK5FTVPK", "https://m.media-amazon.com/images/I/71wVHkK4G0L._AC_UY218_.jpg", "Anker", "140W GaN 4-Port Touch"),
    ("B0DK5F58HW", "https://m.media-amazon.com/images/I/61k+d19bUkL._AC_UY218_.jpg", "Anker", "140W GaN 4-Port Touch"),
    ("B0C4YDS6CF", "https://m.media-amazon.com/images/I/51xr1Ii90oL._AC_UY218_.jpg", "Anker", "Prime 67W GaN 3-Port"),
    ("B0FG6ZTWPH", "https://m.media-amazon.com/images/I/610g2u62UtL._AC_UY218_.jpg", "Anker", "Prime 160W GaN 3-Port"),
    ("B09LLRNGSD", "https://m.media-amazon.com/images/I/61HyQWXH2UL._AC_UY218_.jpg", "Anker", "Nano 65W 3-Port"),
    ("B0D1RB1L66", "https://m.media-amazon.com/images/I/51QxTpLA5vL._AC_UY218_.jpg", "Anker", "Nano 65W 3-Port White"),
    ("B0F9K5Z3JL", "https://m.media-amazon.com/images/I/51vvMCvmIGL._AC_UL320_.jpg", "UGREEN", "Nexode Pro 100W 5-Port Display"),
    ("B0CQN1MC42", "https://m.media-amazon.com/images/I/51vTslonsTL._AC_UL320_.jpg", "UGREEN", "Nexode X 100W Mini 3-Port"),
    ("B091TV6LWN", "https://m.media-amazon.com/images/I/61BxooRLmlL._AC_UY218_.jpg", "UGREEN", "Nexode 100W 4-Port"),
    ("B0DP1ZCWXK", "https://m.media-amazon.com/images/I/51RpTc1KsmL._AC_UY218_.jpg", "UGREEN", "100W 6-Port Charging Station"),
    ("B0G1MQVDY2", "https://m.media-amazon.com/images/I/51D-lxo-BhL._AC_UL320_.jpg", "Generic", "730W 10-Port GaN III"),

    # 储能电源 (占位 — 后续补充)
    ("B0CDWKJ25T", "https://m.media-amazon.com/images/I/71PbrjEWhSL._AC_SL1500_.jpg", "ECOFLOW", "DELTA 3 Plus"),
    ("B0CCPDVJ9X", "https://m.media-amazon.com/images/I/71KHZvf-RhL._AC_SL1500_.jpg", "Jackery", "Explorer 2000 Pro"),
    ("B0CK2WM99B", "https://m.media-amazon.com/images/I/71Y2KGf-3IL._AC_SL1500_.jpg", "BLUETTI", "AC180"),
    ("B0CJY1R5KJ", "https://m.media-amazon.com/images/I/712UaPD5hHL._AC_SL1500_.jpg", "Anker", "SOLIX C1000X"),
    ("B0CN3WZM4C", "https://m.media-amazon.com/images/I/71CN0qK8Y3L._AC_SL1500_.jpg", "DJI", "Power 2000"),

    # 车充 (Amazon.de search: USB C car charger PD)
    ("B09DSV9G78", "https://m.media-amazon.com/images/I/61GA5C97SXL._AC_UY218_.jpg", "UGREEN", "Car Charger 30W PD"),
    ("B0B3D9XW8X", "https://m.media-amazon.com/images/I/61UCFe0Tv3L._AC_UY218_.jpg", "UGREEN", "130W 3-Port Car Charger"),
    ("B0DG8SMD4Y", "https://m.media-amazon.com/images/I/51WKD1T6KZL._AC_UY218_.jpg", "UGREEN", "75W Retractable Car Charger"),
    ("B0B3D184XK", "https://m.media-amazon.com/images/I/61u-N57OgqL._AC_UY218_.jpg", "UGREEN", "63W Dual Car Charger"),
    ("B0DSBNYRKS", "https://m.media-amazon.com/images/I/51JtC5mifTL._AC_UY218_.jpg", "UGREEN", "Nexode 145W Car Charger"),
    ("B0DDBVBQ7R", "https://m.media-amazon.com/images/I/61Q66xDEiQL._AC_UY218_.jpg", "UGREEN", "3-Port PD30W Car Charger"),
    ("B0DMNQS7L6", "https://m.media-amazon.com/images/I/41tZV5Mo3ZL._AC_UY218_.jpg", "UGREEN", "45W 3-Port GaN Charger"),
    ("B08VJ2VH2J", "https://m.media-amazon.com/images/I/71MJZ5+btfL._AC_UY218_.jpg", "INIU", "30W+30W Dual Car Charger"),
    ("B0CB1D68V4", "https://m.media-amazon.com/images/I/71W4j7dosVL._AC_UY218_.jpg", "INIU", "66W Car Charger 36W PD"),
    ("B0CS4RTC64", "https://m.media-amazon.com/images/I/51-Y6FfowfL._AC_UY218_.jpg", "Belkin", "BoostCharge 42W 2-Port Car"),
    ("B0GF7RD8QG", "https://m.media-amazon.com/images/I/81XJq9PycKL._AC_UY218_.jpg", "JOYROOM", "125W Mini Car Charger"),
    ("B09D3NXCBL", "https://m.media-amazon.com/images/I/71CwBWGc26L._AC_UY218_.jpg", "Syncwire", "60W Car Charger Mini Metal"),
    ("B0CKKYNJMF", "https://m.media-amazon.com/images/I/71qCWjGm7KL._AC_UY218_.jpg", "LISEN", "90W Car Charger PD3.0"),
    ("B0CZL4Z26H", "https://m.media-amazon.com/images/I/81LiMbyonZL._AC_UY218_.jpg", "MRGLAS", "125W Car Charger Mini"),
    ("B0CBVGZJPD", "https://m.media-amazon.com/images/I/61s0Hflco4L._AC_UY218_.jpg", "LISEN", "54W Car Charger PD QC3.0"),

    # 桌面充 (Amazon.de search: desktop charging station)
    ("B0DL5BKJKH", "https://m.media-amazon.com/images/I/71cgvLXRj5L._AC_UY218_.jpg", "UGREEN", "Nexode 500W 6-Port Desktop"),
    ("B0DP213JFW", "https://m.media-amazon.com/images/I/51qRNxqSL9L._AC_UY218_.jpg", "UGREEN", "65W 5-Port Desktop Station"),
    ("B0CCXTZHHF", "https://m.media-amazon.com/images/I/51gF3PRk0mL._AC_UY218_.jpg", "UGREEN", "Nexode Pro 160W 4-Port"),
    ("B0CYT277T6", "https://m.media-amazon.com/images/I/51wlq8YjNNL._AC_UY218_.jpg", "UGREEN", "Nexode 100W 5-Port"),
    ("B0D3X2KSXW", "https://m.media-amazon.com/images/I/516NKynBN1L._AC_UY218_.jpg", "UGREEN", "Nexode 300W 5-Port"),
    ("B0FQBXG5PG", "https://m.media-amazon.com/images/I/51aisNV6AwL._AC_UY218_.jpg", "UGREEN", "Nexode 200W 4-Port"),
    ("B0DMW32V6B", "https://m.media-amazon.com/images/I/71ent6LAHdL._AC_UL320_.jpg", "INIU", "65W GaN 3-in-1 Charger"),
    ("B0B5Z9TGGW", "https://m.media-amazon.com/images/I/51ttbqvUgrL._AC_UL320_.jpg", "NANAMI", "100W GaN 4-Port"),
    ("B0GDFFWFRT", "https://m.media-amazon.com/images/I/61o7J2K48LL._AC_UY218_.jpg", "Sefitopher", "330W 10-Port GaN III"),
    ("B0FKH847Q8", "https://m.media-amazon.com/images/I/71EJ0TdZy-L._AC_UY218_.jpg", "Generic", "765W 10-Port GaN III"),
]


def update_images():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all products that need image update (EU products from amazon.de)
    cur.execute("""
        SELECT p.id, p.name, p.brand_name, p.source
        FROM products p
        WHERE p.source = 'amazon.de' AND (p.image_url IS NULL OR p.image_url = '')
        ORDER BY p.brand_name, p.rating DESC
    """)
    db_products = cur.fetchall()
    print(f"EU Amazon products without image: {len(db_products)}")

    matched = 0
    updated = 0

    for prod in db_products:
        db_name = (prod['name'] or '').lower()
        db_brand = (prod['brand_name'] or '').lower()

        best_asin = None
        best_image = None
        best_score = 0

        for asin, img_url, brand, name_hint in AMAZON_PRODUCTS:
            if brand.lower() != db_brand:
                continue
            hint_lower = name_hint.lower()
            # Score: count matching keywords
            score = 0
            keywords = hint_lower.split()
            for kw in keywords:
                if kw in db_name and len(kw) > 2:
                    score += 2
                elif kw in db_name:
                    score += 1
            # Bonus for capacity/power match
            for kw in ['10k', '20k', '5k', '25k', '27k', '45w', '65w', '100w', '140w', 'qi2', 'magsafe']:
                if kw in hint_lower and kw in db_name:
                    score += 1

            if score > best_score:
                best_score = score
                best_asin = asin
                best_image = img_url

        if best_score >= 2 and best_asin:
            product_url = f"https://www.amazon.de/dp/{best_asin}"
            # Replace small thumbnail URL with larger version
            image_url = best_image.replace('_AC_UY218_', '_AC_SL1500_').replace('_AC_UL320_', '_AC_SL1500_').replace('_AC_UL640_QL65_', '_AC_SL1500_')
            cur.execute("""
                UPDATE products SET source_url=?, image_url=? WHERE id=?
            """, (product_url, image_url, prod['id']))
            matched += 1
            updated += 1
            if best_score >= 5:
                print(f"  ✓ {prod['brand_name']} | {prod['name'][:50]}  [score={best_score}] → {product_url}")

    conn.commit()
    print(f"\nMatched: {matched}, Updated: {updated}")

    # Stats
    cur.execute("SELECT COUNT(*) as cnt FROM products WHERE image_url IS NOT NULL AND image_url != ''")
    with_image = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM products")
    total = cur.fetchone()['cnt']
    print(f"Products with image: {with_image} / {total}")

    conn.close()


if __name__ == '__main__':
    update_images()
