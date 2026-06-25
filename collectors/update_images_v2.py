"""
批量更新产品图片 v2 — 整合 Amazon.com + Best Buy 抓取数据
"""
import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.schema import DB_PATH

# ============================================================
# Amazon.com 搜索结果 — ASIN → (图片URL, 品牌, 产品关键词)
# ============================================================
AMAZON_COM = [
    # === Car Chargers (amazon.com search: USB C car charger Anker Belkin Baseus Samsung) ===
    ("B0FKB8LCKZ", "https://m.media-amazon.com/images/I/51RYa9ti7cL._AC_SL1500_.jpg", "Belkin", "USB C Car Charger 75W Retractable"),
    ("B0CS4RTC64", "https://m.media-amazon.com/images/I/51-Y6FfowfL._AC_SL1500_.jpg", "Belkin", "BoostCharge 42W Dual Port Fast Car Charger"),
    ("B0FY3ZGZH9", "https://m.media-amazon.com/images/I/71vEfru0gUL._AC_SL1500_.jpg", "Belkin", "Wireless Car Charger Magnetic Qi2"),
    ("B0F8T4RH9Y", "https://m.media-amazon.com/images/I/71WeDednX4L._AC_SL1500_.jpg", "Baseus", "163W Retractable Car Charger"),
    ("B0B3D9XW8X", "https://m.media-amazon.com/images/I/61UCFe0Tv3L._AC_SL1500_.jpg", "UGREEN", "130W USB C Car Charger"),
    ("B0DB6Z8Y5K", "https://m.media-amazon.com/images/I/71tODuq4nFL._AC_SL1500_.jpg", "Anker", "Car Carplay Cable USB A to USB C"),
    ("B0CX1W5W41", "https://m.media-amazon.com/images/I/71BUzSq3WgL._AC_SL1500_.jpg", "LISEN", "200W Car Charger GaN"),
    ("B0B3CSLPZR", "https://m.media-amazon.com/images/I/61ZPtxtTTuL._AC_SL1500_.jpg", "UGREEN", "130W Car Charger PD 100W"),
    ("B0B9G3M7V4", "https://m.media-amazon.com/images/I/51Io6VM2sIL._AC_SL1500_.jpg", "Belkin", "37W Dual Port Fast Car Charger"),
    ("B0BPH6S4DN", "https://m.media-amazon.com/images/I/51iMQX7Gm0L._AC_SL1500_.jpg", "Anker", "323 Car Charger 52.5W"),
    ("B0C1MB7MSX", "https://m.media-amazon.com/images/I/61DkAtgoFtL._AC_SL1500_.jpg", "Belkin", "BoostCharge 30W Compact Car Charger"),
    ("B086H4BG51", "https://m.media-amazon.com/images/I/71nt8kfpgDL._AC_SL1500_.jpg", "Belkin", "36W Dual USB Car Charger"),
    ("B09H6PJDWB", "https://m.media-amazon.com/images/I/51b48hzeuXL._AC_SL1500_.jpg", "Belkin", "37W Dual USB Car Charger"),
    ("B09WCSNLCB", "https://m.media-amazon.com/images/I/41SZeIuxnbL._AC_SL1500_.jpg", "Belkin", "37W Dual USB Car Charger Lightning"),
    ("B08558BTD2", "https://m.media-amazon.com/images/I/41BH99eQJWL._AC_SL1500_.jpg", "Belkin", "24W Dual USB Car Charger"),
    ("B0FHBNSXV6", "https://m.media-amazon.com/images/I/61KYQmxgn4L._AC_SL1500_.jpg", "Baseus", "240W Retractable Car Charger VR2 Max"),
    ("B0CYQ9JM3L", "https://m.media-amazon.com/images/I/71gO7u2eSrL._AC_SL1500_.jpg", "Generic", "200W USB C Car Charger"),
    ("B0F8QWX55C", "https://m.media-amazon.com/images/I/71yjJ9kiqyL._AC_SL1500_.jpg", "Generic", "140W USB C Car Charger"),
    ("B0DNYTBNHN", "https://m.media-amazon.com/images/I/71gWeI+1uWL._AC_SL1500_.jpg", "ROADRESS", "200W Super Fast Car Charger"),

    # === Power Banks (amazon.com search: power bank Anker Belkin INIU RAVPower ESR Mophie) ===
    ("B0D9BC6FCJ", "https://m.media-amazon.com/images/I/41+RtwA01pL._AC_SL1500_.jpg", "Anker", "MagGo Qi2 10K 15W Magnetic"),
    ("B0GGLQGZ53", "https://m.media-amazon.com/images/I/61zbd3nlluL._AC_SL1500_.jpg", "Anker", "633 Magnetic 10K Wireless"),
    ("B0DP9FQ1VW", "https://m.media-amazon.com/images/I/4159Zajr5oL._AC_SL1500_.jpg", "Anker", "621 Magnetic 5K MagGo"),
    ("B0FKHCKZXX", "https://m.media-amazon.com/images/I/51BTsHsc9VL._AC_SL1500_.jpg", "Anker", "Nano Ultra-Slim Qi2 15W Magnetic"),
    ("B0FWRMBXVP", "https://m.media-amazon.com/images/I/41iqZH8sseL._AC_SL1500_.jpg", "Anker", "Zolo 45W 20K Dual Built-in Cables"),
    ("B0DQ8F7544", "https://m.media-amazon.com/images/I/61hkWuhMgBL._AC_SL1500_.jpg", "Anker", "Nano 3-in-1 Prime Bundle"),
    ("B0D83QJ2N6", "https://m.media-amazon.com/images/I/51uk0-7Tw5L._AC_SL1500_.jpg", "Anker", "Nano 5K Built-in Foldable USB-C"),
    ("B0FKBF5MB7", "https://m.media-amazon.com/images/I/21tyiMZovRL._AC_SL1500_.jpg", "Anker", "Nano Ultra-Slim 5K Qi2 Magnetic"),
    ("B0D5QRT1K9", "https://m.media-amazon.com/images/I/41ywQSpKmIL._AC_SL1500_.jpg", "Anker", "3-in-1 Power Bank 10K Built-in Cable AC Plug"),
    ("B0DCBR91R7", "https://m.media-amazon.com/images/I/21T0-z6Xl4L._AC_SL1500_.jpg", "Anker", "Prime 9.6K 65W Fusion"),
    ("B0D9BBXMKQ", "https://m.media-amazon.com/images/I/21LvW7ELQsL._AC_SL1500_.jpg", "Anker", "20K Built-in USB-C Cable"),
    ("B0DFQ2MRJZ", "https://m.media-amazon.com/images/I/31Waz08-bqL._AC_SL1500_.jpg", "Anker", "Prime 9.6K 65W"),
    ("B0CT628KVH", "https://m.media-amazon.com/images/I/51etAI0gAJL._AC_SL1500_.jpg", "Anker", "2 Pack Nano 5K Built-in USB-C"),
    ("B0FH4LHS71", "https://m.media-amazon.com/images/I/2173X5A83BL._AC_SL1500_.jpg", "Anker", "633 Magnetic 10K Wireless Foldable"),

    # === INIU Power Banks (amazon.com search: INIU power bank) ===
    ("B07YPY31FL", "https://m.media-amazon.com/images/I/511wKuw0OaL._AC_SL1500_.jpg", "INIU", "20K PD 3.0 QC 4.0 LED Display"),
    ("B0FPVZFX74", "https://m.media-amazon.com/images/I/71IbpUvg1sL._AC_SL1500_.jpg", "INIU", "5K 20W PD + Wall Charger Combo"),
    ("B0FPLZQ1DB", "https://m.media-amazon.com/images/I/61OeIb98VIL._AC_SL1500_.jpg", "INIU", "Smallest 45W 20K Built-in Cable + Wireless"),
    ("B0FN7GYJ4S", "https://m.media-amazon.com/images/I/519q21g0yJL._AC_SL1500_.jpg", "INIU", "Ultra Slim 10K 45W + 65W Charger"),
    ("B0G7ZJTFML", "https://m.media-amazon.com/images/I/51LlnY49NnL._AC_SL1500_.jpg", "INIU", "45W Mini + Built-in Cable"),
    ("B0DQSMJ67P", "https://m.media-amazon.com/images/I/614zOPpamHL._AC_SL1500_.jpg", "INIU", "Ultra Slim 10K 45W + 240W Cable"),
    ("B0FPLTQZKB", "https://m.media-amazon.com/images/I/71ZPS74cvLL._AC_SL1500_.jpg", "INIU", "Slimmest 10K 45W x2 Combo"),
    ("B0FPLFQM22", "https://m.media-amazon.com/images/I/61lA4+ewu2L._AC_SL1500_.jpg", "INIU", "Ultra Small 10K 45W + 240W Cable"),
    ("B0FQJJD528", "https://m.media-amazon.com/images/I/71wJQLKbpZL._AC_SL1500_.jpg", "INIU", "Ultra Slim 10K 45W + Qi2 Wireless Station"),
    ("B0FP521DH3", "https://m.media-amazon.com/images/I/81rEVyO2W3L._AC_SL1500_.jpg", "INIU", "Smallest 22.5W 10K + 240W Cable"),
    ("B0FPLJGTSL", "https://m.media-amazon.com/images/I/51mkNhUsjBL._AC_SL1500_.jpg", "INIU", "Smallest 45W 20K Built-in Cable + Ultra Slim"),

    # === Qi2 Wireless Chargers (amazon.com search: Qi2 wireless charger Belkin ESR Anker Mophie) ===
    ("B0FHWK3W1S", "https://m.media-amazon.com/images/I/61wk-mE6-PL._AC_SL1500_.jpg", "Anker", "Prime Foldable MagSafe 25W Qi2.2 3-in-1"),
    ("B0FMBTB5Y7", "https://m.media-amazon.com/images/I/61ne4lTsfdL._AC_SL1500_.jpg", "Belkin", "MagSafe 2-in-1 Qi2.2 25W Foldable"),
    ("B0FVTJN9Y2", "https://m.media-amazon.com/images/I/71u9S68ovGL._AC_SL1500_.jpg", "Mophie", "2-in-1 Wireless Charging Stand Qi2"),
    ("B0FHQDKX7G", "https://m.media-amazon.com/images/I/71EU9BxcZaL._AC_SL1500_.jpg", "ESR", "3-in-1 Qi2.2 25W CryoBoost"),
    ("B0DL86NC5Z", "https://m.media-amazon.com/images/I/61bzhlJcO8L._AC_SL1500_.jpg", "Belkin", "MagSafe 3-in-1 Qi2 15W Wireless"),
    ("B0FQS1T3SK", "https://m.media-amazon.com/images/I/61rVDRlc-YL._AC_SL1500_.jpg", "Belkin", "2-in-1 Qi2 Wireless Charging Dock 15W"),
    ("B0FMB7M8JB", "https://m.media-amazon.com/images/I/71bNeyqSP2L._AC_SL1500_.jpg", "Belkin", "MagSafe 3-in-1 Qi2.2 25W Foldable"),
    ("B0GMTRTMSQ", "https://m.media-amazon.com/images/I/61rBOSOkruL._AC_SL1500_.jpg", "Belkin", "3-in-1 Qi2.2 25W Samsung Galaxy"),
    ("B0FBQXV7HN", "https://m.media-amazon.com/images/I/61o8b5jwjZL._AC_SL1500_.jpg", "Belkin", "MagSafe 2-in-1 Qi2 Convertible"),
    ("B0F1RQ48GG", "https://m.media-amazon.com/images/I/61YsIOKVKOL._AC_SL1500_.jpg", "Belkin", "Magnetic Wireless Charging Pad Qi2 15W Kickstand"),
    ("B0GFWF75Y7", "https://m.media-amazon.com/images/I/61GHK3qlyrL._AC_SL1500_.jpg", "Belkin", "MagSafe Qi2 25W Kickstand"),
    ("B0FMC3PW5W", "https://m.media-amazon.com/images/I/61HYLqCnpGL._AC_SL1500_.jpg", "Belkin", "MagSafe 3-in-1 Qi2.2 25W Cooling Fan"),
    ("B0D9WXYJF8", "https://m.media-amazon.com/images/I/61dzCygXLXL._AC_SL1500_.jpg", "Belkin", "MagSafe 2-in-1 Foldable Qi2 15W"),
    ("B0FHQFBQSM", "https://m.media-amazon.com/images/I/711dl1Gfq9L._AC_SL1500_.jpg", "ESR", "3-in-1 Qi2.2 25W CryoBoost Stand"),
    ("B0D6RZT4HH", "https://m.media-amazon.com/images/I/61xZiF10SLL._AC_SL1500_.jpg", "Belkin", "3-in-1 MagSafe Qi2 Foldable"),
    ("B0GH31CT4C", "https://m.media-amazon.com/images/I/61Cpj4gd+SL._AC_SL1500_.jpg", "Belkin", "MagSafe 2-in-1 Qi2.2 25W Convertible"),
    ("B0F8LMHB64", "https://m.media-amazon.com/images/I/6176xQ+tyeL._AC_SL1500_.jpg", "Belkin", "Magnetic Wireless Charging Pad Qi2 15W PSU"),

    # === Desktop Chargers (amazon.com search: GaN desktop charger UGREEN Satechi Belkin) ===
    ("B0DBZY57ZF", "https://m.media-amazon.com/images/I/51-qg6pm0+L._AC_SL1500_.jpg", "UGREEN", "Nexode 300W GaN 5-Port Desktop"),
    ("B0GP57G1FN", "https://m.media-amazon.com/images/I/61LKwNKO2kL._AC_SL1500_.jpg", "Satechi", "ChargeView 140W Desktop 4-Port"),
    ("B0DL5L1ZLH", "https://m.media-amazon.com/images/I/713u9WoQenL._AC_SL1500_.jpg", "UGREEN", "Nexode 500W GaN 6-Port Desktop"),
    ("B0DNSRXRFT", "https://m.media-amazon.com/images/I/51cCM6WEJKL._AC_SL1500_.jpg", "UGREEN", "100W 6-Port GaN Desktop"),
    ("B0DL5F8223", "https://m.media-amazon.com/images/I/51b3-TDgFkL._AC_SL1500_.jpg", "UGREEN", "Nexode 200W GaN 8-Port Desktop"),
    ("B0FYFDD1WW", "https://m.media-amazon.com/images/I/51NMLU5nJBL._AC_SL1500_.jpg", "UGREEN", "Nexode Pro 160W GaN 5-Port Display"),
    ("B0CYZ52VPX", "https://m.media-amazon.com/images/I/51nKMY3u+hL._AC_SL1500_.jpg", "UGREEN", "Nexode 65W GaN 4-Port"),
    ("B091Z6JNX4", "https://m.media-amazon.com/images/I/516szWmX2ZL._AC_SL1500_.jpg", "UGREEN", "Nexode 100W GaN 4-Port"),
    ("B0CRD4NHY9", "https://m.media-amazon.com/images/I/71JKxvk9Z9L._AC_SL1500_.jpg", "Satechi", "145W GaN Travel 4-Port"),
    ("B0BXBQL713", "https://m.media-amazon.com/images/I/711lvwpozEL._AC_SL1500_.jpg", "Satechi", "200W GaN 6-Port Charging Station"),
    ("B0FNBNFBP7", "https://m.media-amazon.com/images/I/61VAOpYG0vL._AC_SL1500_.jpg", "Belkin", "GaN 70W 7-in-1 Charging Station"),
    ("B0FZYBK851", "https://m.media-amazon.com/images/I/61cuv+DZAcL._AC_SL1500_.jpg", "Belkin", "140W GaN 2-Outlet Charging Station"),
    ("B0C2YZL9XC", "https://m.media-amazon.com/images/I/61MEG0uRi6L._AC_SL1500_.jpg", "Belkin", "108W GaN 4-Port Desktop"),
    ("B0DQVHMJNC", "https://m.media-amazon.com/images/I/41gOst3AmwL._AC_SL1500_.jpg", "Belkin", "112W 4-Port GaN Charger"),
    ("B0F9FHXPDF", "https://m.media-amazon.com/images/I/51OIowhP8GL._AC_SL1500_.jpg", "UGREEN", "Nexode Pro 100W GaN 5-Port Display"),
    ("B0DBZTQRMF", "https://m.media-amazon.com/images/I/51KyN6BQP-L._AC_SL1500_.jpg", "UGREEN", "Nexode 65W GaN 3-Port Qi2 Wireless Stand"),

    # === Power Stations (amazon.com search: power station Jackery EcoFlow Bluetti Goal Zero) ===
    ("B0C5C9HMQ2", "https://m.media-amazon.com/images/I/61RROVy8tKL._AC_SL1500_.jpg", "Anker", "SOLIX F3800 3840Wh"),
    ("B0FVFKMMG6", "https://m.media-amazon.com/images/I/71LwP1pwdNL._AC_SL1500_.jpg", "Anker", "SOLIX C2000 Gen 2 2048Wh"),
    ("B0753TW31T", "https://m.media-amazon.com/images/I/71PPjNP2UyL._AC_SL1500_.jpg", "Goal Zero", "Boulder 200 Solar Panel"),
    ("B0D8377KV3", "https://m.media-amazon.com/images/I/71UcwVR1HzL._AC_SL1500_.jpg", "Jackery", "SolarSaga 200W Solar Panel"),
    ("B0GC5689MQ", "https://m.media-amazon.com/images/I/71hom5IRwwL._AC_SL1500_.jpg", "EBL", "100W Solar Panel for Jackery Ecoflow Bluetti"),
]

# ============================================================
# Best Buy 搜索结果 — SKU → (图片URL, 品牌, 产品关键词)
# ============================================================
BESTBUY = [
    # Power Banks (bestbuy.com: anker power bank)
    ("6553396", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6553/6553396_sd.jpg", "Anker", "Power Bank 20K 200W 3-Port"),
    ("8b0d670f", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/8b0d670f-ec12-4909-8d34-1d7c36882152.png", "Anker", "Power Bank 10K 22.5W"),
    ("8b70f2db", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/8b70f2db-26e5-4df3-ba99-86a8b085ebaa.jpg", "Anker", "Laptop Power Bank 25K 165W Retractable"),
    ("8c179ce7", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/8c179ce7-af0a-4669-acb4-8ce9a06ce815.jpg", "Anker", "MagGo Ultra-Slim 10K Qi2 15W Magnetic"),
    ("f0ba9541", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/f0ba9541-436b-4dbe-86aa-0d7ae6f0d757.jpg", "Anker", "Power Bank 20K 87W Built-in USB-C Cable"),
    ("f0438c7d", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/f0438c7d-edc0-43e6-a95a-feaadd7d0021.jpg", "Anker", "Prime 9.6K 65W Fusion"),
    ("6553401", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6553/6553401_sd.jpg", "Anker", "Nano 5K 22.5W Built-in Foldable USB-C"),
    ("f94075ea", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/f94075ea-053d-43dd-99db-20da670d2053.jpg", "Anker", "Prime 26K 300W 3-Port"),
    ("87cb3860", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/87cb3860-8c93-438f-b3f6-497f4f4dced7.jpg", "Anker", "Laptop Power Bank 25K Triple 100W"),
    ("ea126ba7", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/ea126ba7-0237-44ce-a160-2da9fa24adce.jpg", "Anker", "Power Bank 20K 30W"),
    ("3a41461a", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/3a41461a-a858-4c8b-bcc8-9a83b88db2eb.jpg", "Anker", "633 Magnetic 10K Wireless Foldable"),

    # Wireless Chargers (bestbuy.com: anker belkin mophie wireless charger)
    ("6432663", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6432/6432663_sd.jpg", "Mophie", "15W Wireless Charging Pad"),
    ("6241206", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6241/6241206_sd.jpg", "Mophie", "Charge Stream 5W Qi Wireless Charging Pad"),
    ("a2542476", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/a2542476-982b-4cdd-8c63-9d5672117c4d.jpg", "Mophie", "Wireless Charging Hub USB-A USB-C"),
    ("7b1199d7", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/7b1199d7-ab91-42be-9e4d-e3a3209c58a0.jpg", "Anker", "313 Wireless Charger Pad Qi 10W"),

    # Car Chargers (bestbuy.com: anker car charger belkin)
    ("b277e8c5", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/b277e8c5-b0d2-4b46-a4a4-6d35c67e6af8.jpg", "Anker", "Car Charger 30W 2-Port Type-C"),
    ("a49f1a60", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/a49f1a60-1e01-407d-a52f-47017b7bd5fd.jpg", "Anker", "320 Car Charger 24W Dual USB"),
    ("6402748", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6402/6402748_sd.jpg", "Belkin", "BoostCharge Dual USB-A Car Charger 24W"),
    ("6d296ae9", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6d296ae9-c4f0-42c8-8a5c-e60a3258451d.jpg", "Anker", "Prime MagSafe Car Mount Qi2 25W"),

    # Power Stations (bestbuy.com: jackery ecoflow bluetti power station)
    ("f81a3d89", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/f81a3d89-427f-4273-ac30-da23cde6c9eb.jpg", "Jackery", "Explorer 2000 Plus 2042Wh"),
    ("b5e96dcb", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/b5e96dcb-a83e-495d-882c-7e8e08febf92.jpg", "Jackery", "Explorer 5000 Plus 5040Wh"),
    ("522a0881", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/522a0881-c67a-475f-92c4-d81ab4f25f1a.jpg", "Jackery", "Explorer 2000 V2 2042Wh"),
    ("6972e259", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6972e259-1a9f-4813-b861-450dd6bc10cd.jpg", "Jackery", "HomePower 3600 Plus 3584Wh"),
]

# Also add some Walmart product image data from previous session
WALMART = [
    # (image_url, brand, keywords)
    # Walmart images we may have collected; add placeholder structure
]


def match_product(db_name, db_brand, candidates):
    """Match a DB product to the best candidate by brand + keyword score"""
    db_name_l = (db_name or '').lower()
    db_brand_l = (db_brand or '').lower()

    best_score = 0
    best_match = None

    for item in candidates:
        if len(item) == 3:
            # Walmart format: (image_url, brand, keywords)
            img_url, brand, keywords = item
            source_url = None
        elif len(item) == 4:
            # Amazon/Best Buy format
            if item[0].startswith('B0'):
                # Amazon: (asin, img_url, brand, keywords)
                asin, img_url, brand, keywords = item
                source_url = f"https://www.amazon.com/dp/{asin}"
            else:
                # Best Buy: (sku, img_url, brand, keywords) — no source_url
                sku, img_url, brand, keywords = item
                source_url = None
        else:
            continue

        if brand.lower() != db_brand_l:
            continue

        score = 0
        kw_list = keywords.lower().split()
        for kw in kw_list:
            kw_clean = kw.strip('()+')
            if kw_clean in db_name_l and len(kw_clean) > 2:
                score += 2
            elif kw_clean in db_name_l:
                score += 1

        # Bonus for capacity/wattage match
        for kw in ['10k', '20k', '5k', '25k', '27k', '45w', '65w', '100w', '140w', '200w',
                    'qi2', 'magsafe', 'gan', 'wireless', 'car', 'desktop', 'retractable']:
            if kw in keywords.lower() and kw in db_name_l:
                score += 1

        if score > best_score:
            best_score = score
            best_match = (img_url, source_url, score)

    return best_match


def update_images():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all products without images
    cur.execute("""
        SELECT p.id, p.name, p.brand_name, p.source, p.region_id, p.category_id,
               p.source_url, c.slug as cat_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE (p.image_url IS NULL OR p.image_url = '')
        ORDER BY p.source, p.brand_name
    """)
    db_products = cur.fetchall()
    print(f"Products without images: {len(db_products)}")

    stats = {'amazon_com_matched': 0, 'bestbuy_matched': 0, 'updated': 0}

    for prod in db_products:
        prod_id = prod['id']
        prod_name = prod['name'] or ''
        prod_brand = prod['brand_name'] or ''
        prod_source = prod['source'] or ''
        matched = None

        # Try Amazon.com data for amazon.com, aggregator, market_reference products
        if prod_source in ('amazon.com', 'aggregator', 'market_reference'):
            matched = match_product(prod_name, prod_brand, AMAZON_COM)
            if matched:
                stats['amazon_com_matched'] += 1

        # Try Best Buy data for bestbuy.com products
        elif prod_source == 'bestbuy.com':
            matched = match_product(prod_name, prod_brand, BESTBUY)
            if matched:
                stats['bestbuy_matched'] += 1

        # For amazon.de products without image, also try Amazon.com data
        elif prod_source == 'amazon.de':
            # Try amazon.de existing data first (from update_images.py)
            # Then try amazon.com as fallback
            matched = match_product(prod_name, prod_brand, AMAZON_COM)
            if matched:
                stats['amazon_com_matched'] += 1

        # For walmart.com, try both
        elif prod_source == 'walmart.com':
            matched = match_product(prod_name, prod_brand, AMAZON_COM)
            if matched:
                stats['amazon_com_matched'] += 1
            if not matched:
                matched = match_product(prod_name, prod_brand, BESTBUY)
                if matched:
                    stats['bestbuy_matched'] += 1

        # For target.com
        elif prod_source == 'target.com':
            matched = match_product(prod_name, prod_brand, AMAZON_COM)
            if matched:
                stats['amazon_com_matched'] += 1

        if matched:
            img_url, source_url, score = matched
            if img_url:
                update_source = source_url if source_url else prod['source_url']
                if update_source:
                    cur.execute("""
                        UPDATE products SET image_url=?, source_url=?
                        WHERE id=?
                    """, (img_url, update_source, prod_id))
                else:
                    cur.execute("""
                        UPDATE products SET image_url=? WHERE id=?
                    """, (img_url, prod_id))
                stats['updated'] += 1
                if prod_source == 'amazon.de':
                    print(f"  [amazon.com fallback] {prod_brand} | {prod_name[:50]} [score={score}]")

    conn.commit()

    # Stats
    cur.execute("SELECT COUNT(*) as cnt FROM products WHERE image_url IS NOT NULL AND image_url != ''")
    with_image = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM products")
    total = cur.fetchone()['cnt']
    cur.execute("""
        SELECT source, COUNT(*) as cnt,
        SUM(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 ELSE 0 END) as with_img
        FROM products GROUP BY source ORDER BY cnt DESC
    """)
    by_source = cur.fetchall()

    print(f"\n=== Results ===")
    print(f"Amazon.com matches: {stats['amazon_com_matched']}")
    print(f"Best Buy matches: {stats['bestbuy_matched']}")
    print(f"Total updated: {stats['updated']}")
    print(f"Products with image: {with_image} / {total} ({with_image*100//total}%)")
    print(f"\nBy source:")
    for r in by_source:
        pct = r['with_img']*100//r['cnt'] if r['cnt'] else 0
        print(f"  {r['source']:20s}: {r['cnt']:3d} total, {r['with_img']:3d} with images ({pct}%)")

    conn.close()


if __name__ == '__main__':
    update_images()
