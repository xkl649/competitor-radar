"""
批量导入脚本：将所有采集的竞品数据导入SQLite数据库
包含：北美(NA) 和 欧洲(EU) 6个品类的产品
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import get_conn, init_db
from collectors.eu_amazon import save_products, get_region_id, get_category_id, upsert_brand


# ============================================================
# 北美 (NA) 产品数据 — 从 WIRED, ZDNET, DeskForged, DriveTechGear 等评测站采集
# ============================================================

NA_POWERBANK = [
    # === WIRED Best MagSafe Power Banks 2026 ===
    {"brand": "Anker", "name": "Anker MagGo Power Bank 10K Qi2", "price": 65.00, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 27, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 3500, "source_url": "https://www.amazon.com/dp/B0CF56RPPQ"},
    {"brand": "Anker", "name": "Anker MagGo Ultra-Slim Qi2 Power Bank", "price": 80.00, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 27, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "source_url": "https://www.amazon.com/dp/B0D8J2R7QM"},
    {"brand": "Mophie", "name": "Mophie Powerstation Wireless Stand Qi2 10K", "price": 90.00, "rating": 4.2,
     "capacity_mAh": 10000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "source_url": "https://www.amazon.com/dp/B0CSKGWMGQ"},
    {"brand": "Sharge", "name": "Sharge Icemag 3 Qi2 25W Power Bank 10000mAh", "price": 64.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 35, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 200, "source_url": "https://www.amazon.com/dp/B0DP8HGLXT"},
    {"brand": "Baseus", "name": "Baseus Picogo Qi2 25W MagSafe Power Bank 10000mAh", "price": 57.00, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 45, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "retractable_cable": True, "source_url": "https://www.amazon.com/dp/B0DY7J8HPQ"},
    {"brand": "Infinacore", "name": "Infinacore M3 Qi2 MagSafe Power Bank 5200mAh", "price": 30.00, "rating": 4.0,
     "capacity_mAh": 5200, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "source_url": "https://www.amazon.com/dp/B0DM5LN6HX"},
    {"brand": "Anker", "name": "Anker 622 MagGo Portable Charger A1614 5000mAh", "price": 33.00, "rating": 4.3,
     "capacity_mAh": 5000, "wattage": 12, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 12000},
    {"brand": "Torras", "name": "Torras MiniMag Magnetic Power Bank 5000mAh", "price": 34.00, "rating": 4.2,
     "capacity_mAh": 5000, "wattage": 18, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 800},
    {"brand": "Native Union", "name": "Native Union (Re)Classic MagSafe Power Bank 5000mAh", "price": 66.00, "rating": 4.1,
     "capacity_mAh": 5000, "wattage": 18, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "Pitaka", "name": "Pitaka Aramid Fiber Qi2 Magnetic Power Bank 5000mAh", "price": 70.00, "rating": 4.3,
     "capacity_mAh": 5000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "PopSockets", "name": "PopSockets MagSafe PowerPack 5000mAh", "price": 40.00, "rating": 4.0,
     "capacity_mAh": 5000, "wattage": 20, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 2500},
    {"brand": "Baseus", "name": "Baseus PicoGo Qi2 MagSafe Power Bank 5000mAh", "price": 50.00, "rating": 4.2,
     "capacity_mAh": 5000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "Kuxiu", "name": "Kuxiu S2 Magnetic Solid State Qi2 Power Bank 5000mAh", "price": 46.00, "rating": 4.3,
     "capacity_mAh": 5000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "UAG", "name": "UAG Rugged Wireless Power Bank and Stand 10000mAh", "price": 100.00, "rating": 4.0,
     "capacity_mAh": 10000, "wattage": 20, "wireless": True,
     "form_factor": "magnetic"},
    {"brand": "EcoFlow", "name": "EcoFlow Rapid Qi2 Power Bank", "price": 90.00, "rating": 4.1,
     "wattage": 36, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "Anker", "name": "Anker Nano Qi2 Power Bank 5000mAh", "price": 55.00, "rating": 4.4,
     "wattage": 22.5, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic"},
    {"brand": "Belkin", "name": "Belkin BoostCharge Wireless Power Bank 5000mAh", "price": 33.00, "rating": 3.9,
     "capacity_mAh": 5000, "wattage": 12, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 900},

    # === whoismcafee Best 10000mAh ===
    {"brand": "INIU", "name": "INIU 45W Fast Charging Power Bank 10000mAh", "price": 25.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 45, "has_pd": True,
     "form_factor": "brick", "review_count": 8500},
    {"brand": "Anker", "name": "Anker 30W Power Bank with Built-in USB-C Cable 10000mAh", "price": 35.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 30, "has_pd": True,
     "form_factor": "brick", "review_count": 4200},
    {"brand": "Anker", "name": "Anker Nano 45W Retractable Power Bank 10000mAh", "price": 45.00, "rating": 4.6,
     "capacity_mAh": 10000, "wattage": 45, "has_pd": True,
     "form_factor": "brick", "review_count": 3100},
    {"brand": "Anker", "name": "Anker PowerCore 10K Slim Power Bank 10000mAh", "price": 22.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 15, "has_pd": True,
     "form_factor": "brick", "review_count": 25000},
    {"brand": "Anker", "name": "Anker MagGo Qi2 15W MagSafe Power Bank 10000mAh", "price": 70.00, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 30, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 1800},
    {"brand": "LISEN", "name": "LISEN Ultra-Slim 22.5W Power Bank 10000mAh", "price": 28.00, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "review_count": 5600},
    {"brand": "Orfeika", "name": "Orfeika 22.5W 4 Built-in Cables Power Bank 10000mAh", "price": 20.00, "rating": 4.6,
     "capacity_mAh": 10000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "retractable_cable": True, "review_count": 2800},
    {"brand": "Aobbow", "name": "Aobbow Magnetic 5-in-1 Power Bank 10000mAh", "price": 30.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 20, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 1200},
    {"brand": "VRURC", "name": "VRURC Slim 10000mAh Power Bank with 4 Built-in Cables", "price": 18.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 12,
     "form_factor": "brick", "review_count": 4200},
    {"brand": "VEEKTOMX", "name": "VEEKTOMX 10000mAh Power Bank with 4 Built-in Cables", "price": 22.00, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 12,
     "form_factor": "brick", "review_count": 3500},
    {"brand": "TORRAS", "name": "TORRAS MiniMag Wireless Magnetic Power Bank 10000mAh", "price": 40.00, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 22.5, "wireless": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 2200},
]

NA_WIRELESS_CHARGER = [
    # === WIRED Best 3-in-1 2026 ===
    {"brand": "Belkin", "name": "Belkin 3-in-1 Qi2 Charging Stand", "price": 63.00, "rating": 4.3,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 4500},
    {"brand": "Nomad", "name": "Nomad Stand One Max Qi2 25W 3-in-1 Charger", "price": 165.00, "rating": 4.4,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 120},
    {"brand": "ESR", "name": "ESR Qi2 3-in-1 Wireless Charging Station", "price": 24.00, "rating": 4.2,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 3200},
    {"brand": "Belkin", "name": "Belkin UltraCharge Pro Qi2.2 25W 3-in-1 Wireless Charging Station", "price": 130.00, "rating": 4.4,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 335},
    {"brand": "Mophie", "name": "Mophie MagSafe 3-in-1 Extendable Wireless Charging Stand", "price": 83.00, "rating": 4.2,
     "wattage": 15, "wireless": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 2100},
    {"brand": "Noco", "name": "Noco X Grid XDS3 Qi2 Wireless Charger", "price": 130.00, "rating": 4.0,
     "wattage": 15, "wireless": True, "qi2": True,
     "form_factor": "stand"},
    {"brand": "Twelve South", "name": "Twelve South HiRise 3 Deluxe Wireless Charging Stand", "price": 100.00, "rating": 4.2,
     "wattage": 15, "wireless": True,
     "form_factor": "stand", "review_count": 800},
    {"brand": "Anker", "name": "Anker Prime 3-in-1 Qi2 25W Charging Station", "price": 150.00, "rating": 4.5,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 600},
    {"brand": "Anker", "name": "Anker MagGo Qi2 Wireless Charging Station Stand", "price": 90.00, "rating": 4.3,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 3500},
    {"brand": "Anker", "name": "Anker 3-in-1 Cube with MagSafe", "price": 90.00, "rating": 4.4,
     "wattage": 15, "wireless": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 8000},
    {"brand": "Zens", "name": "Zens Office Charger Pro 3 Qi2 3-in-1", "price": 85.00, "rating": 4.1,
     "wattage": 15, "wireless": True, "qi2": True,
     "form_factor": "stand", "review_count": 400},
    {"brand": "Lululook", "name": "Lululook 3-in-1 Qi2 Charging Station", "price": 60.00, "rating": 4.0,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand"},
    {"brand": "Satechi", "name": "Satechi 3-in-1 Magnetic Wireless Charging Stand", "price": 130.00, "rating": 4.1,
     "wattage": 15, "wireless": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 600},
    {"brand": "Case-Mate", "name": "Case-Mate Fuel 3-in-1 Foldable Wireless Charger", "price": 50.00, "rating": 3.8,
     "wattage": 15, "wireless": True,
     "form_factor": "stand"},
    {"brand": "Belkin", "name": "Belkin UltraCharge 2-in-1 Foldable Qi2 25W Charger", "price": 45.00, "rating": 4.2,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 800},
    {"brand": "Zens", "name": "Zens Nightstand Charger Pro 2 Qi2", "price": 80.00, "rating": 4.0,
     "wattage": 15, "wireless": True, "qi2": True,
     "form_factor": "stand"},
]

NA_ADAPTER_CABLE = [
    # === SmartGadgetKit Best GaN 2026 ===
    {"brand": "UGREEN", "name": "UGREEN Nexode Pro 65W GaN Charger 3-Port", "price": 35.00, "rating": 4.0,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 4200},
    {"brand": "Anker", "name": "Anker Prime 100W GaN Charger 3-Port", "price": 60.00, "rating": 4.1,
     "wattage": 100, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 2800},
    {"brand": "UGREEN", "name": "UGREEN Nexode 200W GaN Charger 4-Port 3C1A", "price": 85.00, "rating": 4.2,
     "wattage": 200, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 1500},
    {"brand": "Anker", "name": "Anker 140W GaN Charger 4-Port USB-C", "price": 90.00, "rating": 4.3,
     "wattage": 140, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 1800},
    {"brand": "Baseus", "name": "Baseus 65W GaN5 3-Port Charger", "price": 28.00, "rating": 4.2,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 94},
    {"brand": "Anker", "name": "Anker 511 Nano 4 GaN 30W Charger", "price": 20.00, "rating": 4.4,
     "wattage": 30, "port_count": 1, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 15000},

    # === ZDNET Best GaN 2026 ===
    {"brand": "UGREEN", "name": "UGREEN Nexode 500W GaN 6-Port Desktop Charging Station", "price": 220.00, "rating": 4.0,
     "wattage": 500, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop"},
    {"brand": "UGREEN", "name": "UGREEN Nexode 300W GaN 5-Port Desktop Charging Station", "price": 150.00, "rating": 3.7,
     "wattage": 300, "port_count": 5, "has_gan": True, "has_pd": True,
     "form_factor": "desktop"},
    {"brand": "StarTech", "name": "StarTech 4-Port 240W Multi-Device USB-C Charger", "price": 179.00, "rating": 4.0,
     "wattage": 240, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "desktop"},
    {"brand": "Tessan", "name": "Tessan 65W GaN Universal Travel Adapter 4-Port", "price": 38.00, "rating": 4.1,
     "wattage": 65, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "brick"},
    {"brand": "Anker", "name": "Anker Prime 200W GaN 6-Port Desktop Charger", "price": 56.00, "rating": 3.1,
     "wattage": 200, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop"},
    {"brand": "UGREEN", "name": "UGREEN Nexode 65W GaN Charger with MagSafe 4-Port", "price": 80.00, "rating": 3.0,
     "wattage": 65, "port_count": 4, "has_gan": True, "has_pd": True, "wireless": True,
     "form_factor": "desktop"},
    {"brand": "Amazon Basics", "name": "Amazon Basics 68W GaN 2-Port Wall Charger", "price": 25.00, "rating": 4.2,
     "wattage": 68, "port_count": 2, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 3200},
]

NA_CAR_CHARGER = [
    # === DriveTechGear Best Retractable Car Chargers 2026 ===
    {"brand": "Baseus", "name": "Baseus 163W Retractable Car Charger 4-Port", "price": 35.00, "rating": 4.3,
     "wattage": 163, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 1800},
    {"brand": "Anker", "name": "Anker 75W Retractable Car Charger USB-C", "price": 30.00, "rating": 4.4,
     "wattage": 75, "port_count": 2, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 3200},
    {"brand": "LISEN", "name": "LISEN 75W Dual Retractable USB-C Car Charger 4-Port", "price": 25.00, "rating": 4.3,
     "wattage": 75, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 4500},
    {"brand": "SUPERONE", "name": "SUPERONE 99W Retractable Car Charger 6-Port", "price": 28.00, "rating": 4.1,
     "wattage": 99, "port_count": 6, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 600},
    {"brand": "BERTHALESS", "name": "BERTHALESS 4-in-1 Retractable Car Charger", "price": 15.00, "rating": 4.0,
     "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 900},
    {"brand": "LISEN", "name": "LISEN 69W Compact Retractable Car Charger 4-Port", "price": 22.00, "rating": 4.2,
     "wattage": 69, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 2200},
]

NA_DESKTOP_CHARGER = [
    # === DeskForged Best Desktop Charging Stations 2026 ===
    {"brand": "UGREEN", "name": "UGREEN 140W Magic Box GaN Desktop Charging Station", "price": 6.00, "rating": 4.2,
     "wattage": 140, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 1200},
    {"brand": "UGREEN", "name": "UGREEN 200W GaN 6-Port Desktop Charging Station", "price": 42.00, "rating": 4.3,
     "wattage": 200, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 2500},
    {"brand": "CukTech", "name": "CukTech 15 Desktop Charging Station 140W with Display", "price": 55.00, "rating": 4.1,
     "wattage": 140, "port_count": 4, "has_gan": True, "has_pd": True, "wireless": True,
     "form_factor": "desktop", "review_count": 400},
    {"brand": "Baseus", "name": "Baseus 100W 7-in-1 Ultra-Thin Desktop Charging Station", "price": 37.00, "rating": 4.2,
     "wattage": 100, "port_count": 7, "has_gan": True, "has_pd": True, "wireless": True,
     "form_factor": "desktop", "review_count": 1500},
    {"brand": "UGREEN", "name": "UGREEN S6 Magic Box 65W Desktop Charger with AC Outlets", "price": 14.00, "rating": 4.0,
     "wattage": 65, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 900},
    {"brand": "Aohi", "name": "Aohi 140W GaN PD3.1 UFCS Desktop Charger", "price": 39.00, "rating": 3.9,
     "wattage": 140, "port_count": 2, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 300},
    {"brand": "Anker", "name": "Anker Prime 240W GaN 6-Port Desktop Charger with Display", "price": 180.00, "rating": 4.5,
     "wattage": 240, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 2200},
]

NA_ENERGY_STORAGE = [
    # === OutdoorTechLab Best Portable Power Stations 2026 ===
    {"brand": "Anker", "name": "Anker Solix C1000 Gen 2 Portable Power Station 1024Wh", "price": 398.00, "rating": 4.5,
     "wattage": 2000, "capacity_mAh": None, "features": {"capacity_wh": 1024, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 1800,
     "source_url": "https://www.amazon.com/dp/B0CK2SGYNW"},
    {"brand": "Jackery", "name": "Jackery Explorer 1000 v2 Portable Power Station 1070Wh", "price": 469.00, "rating": 4.4,
     "wattage": 1500, "features": {"capacity_wh": 1070, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 3500},
    {"brand": "EcoFlow", "name": "EcoFlow Delta 2 Portable Power Station 1024Wh", "price": 499.00, "rating": 4.5,
     "wattage": 1800, "features": {"capacity_wh": 1024, "battery": "LiFePO4", "solar": True, "expandable": True},
     "form_factor": "station", "review_count": 4200,
     "source_url": "https://www.amazon.com/dp/B0B8MXPRXB"},
    # === Additional from reviews ===
    {"brand": "EcoFlow", "name": "EcoFlow Delta Pro Portable Power Station 3600Wh", "price": 2799.00, "rating": 4.3,
     "wattage": 3600, "features": {"capacity_wh": 3600, "battery": "LFP", "solar": True, "solar_w": 1600},
     "form_factor": "station", "review_count": 1500},
    {"brand": "Jackery", "name": "Jackery Explorer 2000 Plus Portable Power Station 2048Wh", "price": 1599.00, "rating": 4.3,
     "wattage": 3000, "features": {"capacity_wh": 2048, "battery": "LiFePO4", "solar": True, "solar_w": 1000},
     "form_factor": "station", "review_count": 1200},
    {"brand": "Bluetti", "name": "Bluetti AC180 Portable Power Station 1152Wh", "price": 599.00, "rating": 4.4,
     "wattage": 1800, "features": {"capacity_wh": 1152, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 2800},
    {"brand": "Bluetti", "name": "Bluetti AC200P Portable Power Station 2000Wh", "price": 1199.00, "rating": 4.3,
     "wattage": 2000, "features": {"capacity_wh": 2000, "battery": "LiFePO4", "solar": True, "solar_w": 700},
     "form_factor": "station", "review_count": 1800},
    {"brand": "Bluetti", "name": "Bluetti AC300 Portable Power Station 3072Wh Modular", "price": 1899.00, "rating": 4.2,
     "wattage": 3000, "features": {"capacity_wh": 3072, "battery": "LiFePO4", "solar": True, "expandable": True},
     "form_factor": "station", "review_count": 900},
]


# ============================================================
# 欧洲 (EU) 产品数据 — 从 Amazon.de 采集
# ============================================================

EU_POWERBANK = [
    {"brand": "Anker", "name": "Anker MagGo Qi2 Power Bank 10000mAh 15W Wireless", "price": 39.99, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 30, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 2800},
    {"brand": "Anker", "name": "Anker PowerCore 10000mAh Power Bank 22.5W", "price": 19.99, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "review_count": 12000},
    {"brand": "INIU", "name": "INIU 45W Power Bank 10000mAh PD Fast Charging", "price": 22.99, "rating": 4.5,
     "capacity_mAh": 10000, "wattage": 45, "has_pd": True,
     "form_factor": "brick", "review_count": 6500},
    {"brand": "INIU", "name": "INIU 22.5W Power Bank 20000mAh", "price": 24.99, "rating": 4.4,
     "capacity_mAh": 20000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "review_count": 4800},
    {"brand": "INIU", "name": "INIU 45W Power Bank with Removable Cable 10000mAh", "price": 29.99, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 45, "has_pd": True,
     "form_factor": "brick", "review_count": 2200},
    {"brand": "Baseus", "name": "Baseus Qi2 MagSafe Power Bank 10000mAh 30W", "price": 36.99, "rating": 4.2,
     "capacity_mAh": 10000, "wattage": 30, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 1500},
    {"brand": "ESR", "name": "ESR Qi2 MagSafe Power Bank 10000mAh with Kickstand", "price": 34.99, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 900},
    {"brand": "UGREEN", "name": "UGREEN 10000mAh Power Bank 22.5W PD", "price": 17.99, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "review_count": 3800},
    {"brand": "Belkin", "name": "Belkin BoostCharge Qi2 Power Bank 10000mAh", "price": 49.99, "rating": 4.1,
     "capacity_mAh": 10000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 400},
    {"brand": "Kuxiu", "name": "Kuxiu Qi2 Magnetic Wireless Power Bank 5000mAh", "price": 29.99, "rating": 4.2,
     "capacity_mAh": 5000, "wattage": 20, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "magnetic", "review_count": 200},
    {"brand": "Samsung", "name": "Samsung 10000mAh Power Bank 25W Super Fast Charging", "price": 29.90, "rating": 4.4,
     "capacity_mAh": 10000, "wattage": 25, "has_pd": True,
     "form_factor": "brick", "review_count": 5500},
    {"brand": "VEGER", "name": "VEGER 10000mAh Mini Power Bank 22.5W with Built-in Cable", "price": 15.99, "rating": 4.3,
     "capacity_mAh": 10000, "wattage": 22.5, "has_pd": True,
     "form_factor": "brick", "review_count": 2800},
]

EU_WIRELESS_CHARGER = [
    {"brand": "Belkin", "name": "Belkin Qi2 3-in-1 Wireless Charging Station 15W", "price": 89.99, "rating": 4.3,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 1500},
    {"brand": "Belkin", "name": "Belkin BoostCharge Pro Qi2.2 25W 3-in-1 Charger", "price": 119.99, "rating": 4.4,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 250},
    {"brand": "Anker", "name": "Anker MagGo Qi2 3-in-1 Wireless Charging Station", "price": 79.99, "rating": 4.4,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 1800},
    {"brand": "Anker", "name": "Anker 3-in-1 Cube with MagSafe Wireless Charger", "price": 89.99, "rating": 4.5,
     "wattage": 15, "wireless": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 3200},
    {"brand": "ESR", "name": "ESR Qi2 3-in-1 Wireless Charging Station with CryoBoost", "price": 49.99, "rating": 4.2,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 2100},
    {"brand": "ESR", "name": "ESR Qi2 2-in-1 MagSafe Charger with Phone Stand", "price": 29.99, "rating": 4.3,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 1600},
    {"brand": "UGREEN", "name": "UGREEN Qi2 3-in-1 Wireless Charging Station 15W", "price": 44.99, "rating": 4.1,
     "wattage": 15, "wireless": True, "qi2": True,
     "form_factor": "stand", "review_count": 900},
    {"brand": "LISEN", "name": "LISEN Qi2 25W 3-in-1 Wireless Charging Station", "price": 42.99, "rating": 4.2,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 600},
    {"brand": "KU XIU", "name": "KU XIU Qi2 25W Magnetic Wireless Charger Stand", "price": 36.99, "rating": 4.3,
     "wattage": 25, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 350},
    {"brand": "Satechi", "name": "Satechi Trio Qi2 3-in-1 Wireless Charging Stand", "price": 119.99, "rating": 4.0,
     "wattage": 15, "wireless": True, "qi2": True,
     "form_factor": "stand", "review_count": 200},
    {"brand": "Cellularline", "name": "Cellularline FreePWR Qi2 MagSafe Wireless Charger", "price": 34.99, "rating": 3.9,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "stand", "review_count": 150},
    {"brand": "Anker", "name": "Anker PowerWave Qi2 Magnetic Pad 15W", "price": 24.99, "rating": 4.3,
     "wattage": 15, "wireless": True, "qi2": True, "has_magsafe": True,
     "form_factor": "pad", "review_count": 1200},
]

EU_ADAPTER_CABLE = [
    {"brand": "Anker", "name": "Anker 735 GaNPrime 65W 3-Port Charger", "price": 44.99, "rating": 4.6,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 8500},
    {"brand": "Anker", "name": "Anker 735 Prime 100W GaN 3-Port Charger", "price": 59.99, "rating": 4.5,
     "wattage": 100, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 4200},
    {"brand": "UGREEN", "name": "UGREEN Nexode Pro 65W GaN Charger 3-Port", "price": 32.99, "rating": 4.5,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 6800},
    {"brand": "UGREEN", "name": "UGREEN Nexode 100W GaN Charger 4-Port", "price": 49.99, "rating": 4.5,
     "wattage": 100, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 3200},
    {"brand": "Baseus", "name": "Baseus GaN5 Pro 65W 3-Port Charger", "price": 25.99, "rating": 4.4,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 4500},
    {"brand": "Baseus", "name": "Baseus GaN5 100W 4-Port Charger", "price": 35.99, "rating": 4.3,
     "wattage": 100, "port_count": 4, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 2200},
    {"brand": "Samsung", "name": "Samsung 45W Super Fast Charger USB-C PD", "price": 34.90, "rating": 4.6,
     "wattage": 45, "port_count": 1, "has_pd": True,
     "form_factor": "brick", "review_count": 12000},
    {"brand": "Apple", "name": "Apple 20W USB-C Power Adapter", "price": 19.99, "rating": 4.7,
     "wattage": 20, "port_count": 1, "has_pd": True,
     "form_factor": "brick", "review_count": 35000},
    {"brand": "Anker", "name": "Anker 511 Nano 3 30W GaN Charger", "price": 17.99, "rating": 4.7,
     "wattage": 30, "port_count": 1, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 18000},
    {"brand": "Belkin", "name": "Belkin BoostCharge 65W GaN Dual USB-C Charger", "price": 39.99, "rating": 4.3,
     "wattage": 65, "port_count": 2, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 2200},
    {"brand": "INIU", "name": "INIU 67W GaN Charger 3-Port USB-C PD", "price": 21.99, "rating": 4.5,
     "wattage": 67, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 3600},
    {"brand": "AOHI", "name": "AOHI 65W GaN+ Charger 2-Port PD3.0", "price": 29.99, "rating": 4.4,
     "wattage": 65, "port_count": 2, "has_gan": True, "has_pd": True,
     "form_factor": "brick", "review_count": 1800},
]

EU_CAR_CHARGER = [
    {"brand": "Baseus", "name": "Baseus 65W Retractable Car Charger 4-Port", "price": 22.99, "rating": 4.3,
     "wattage": 65, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 3200},
    {"brand": "LISEN", "name": "LISEN 75W Retractable Car Charger 4-Port USB-C", "price": 24.99, "rating": 4.4,
     "wattage": 75, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 4100},
    {"brand": "Anker", "name": "Anker PowerDrive 67W Car Charger USB-C PD", "price": 29.99, "rating": 4.5,
     "wattage": 67, "port_count": 2, "has_pd": True,
     "form_factor": "car", "review_count": 6800},
    {"brand": "Ainope", "name": "Ainope 90W Retractable Car Charger 5-Port", "price": 19.99, "rating": 4.2,
     "wattage": 90, "port_count": 5, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 2200},
    {"brand": "UGREEN", "name": "UGREEN 65W Car Charger PD USB-C", "price": 19.99, "rating": 4.4,
     "wattage": 65, "port_count": 2, "has_pd": True,
     "form_factor": "car", "review_count": 4500},
    {"brand": "Spigen", "name": "Spigen 65W Car Charger USB-C PD GaN", "price": 24.99, "rating": 4.3,
     "wattage": 65, "port_count": 2, "has_gan": True, "has_pd": True,
     "form_factor": "car", "review_count": 1600},
    {"brand": "JOYROOM", "name": "JOYROOM 66W Retractable Car Charger 4-in-1", "price": 18.99, "rating": 4.3,
     "wattage": 66, "port_count": 4, "has_pd": True, "retractable_cable": True,
     "form_factor": "car", "review_count": 2800},
    {"brand": "LISEN", "name": "LISEN 90W Retractable Car Charger with MagSafe", "price": 32.99, "rating": 4.2,
     "wattage": 90, "port_count": 4, "has_pd": True, "retractable_cable": True, "wireless": True,
     "form_factor": "car", "review_count": 1800},
    {"brand": "Scosche", "name": "Scosche PowerVolt 60W Car Charger USB-C PD", "price": 24.99, "rating": 4.1,
     "wattage": 60, "port_count": 2, "has_pd": True,
     "form_factor": "car", "review_count": 900},
    {"brand": "Belkin", "name": "Belkin BoostCharge 68W USB-C Car Charger", "price": 32.99, "rating": 4.3,
     "wattage": 68, "port_count": 2, "has_pd": True,
     "form_factor": "car", "review_count": 1200},
]

EU_DESKTOP_CHARGER = [
    {"brand": "UGREEN", "name": "UGREEN Nexode 200W GaN Desktop Charger 6-Port", "price": 89.99, "rating": 4.5,
     "wattage": 200, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 1800},
    {"brand": "Baseus", "name": "Baseus PowerCombo 100W GaN Desktop Charging Station", "price": 49.99, "rating": 4.2,
     "wattage": 100, "port_count": 6, "has_gan": True, "has_pd": True, "wireless": True,
     "form_factor": "desktop", "review_count": 1200},
    {"brand": "YSYFAD", "name": "YSYFAD 200W GaN Desktop Charger 8-Port", "price": 45.99, "rating": 4.0,
     "wattage": 200, "port_count": 8, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 300},
    {"brand": "Anker", "name": "Anker Prime 200W GaN 6-Port Desktop Charger", "price": 119.99, "rating": 4.4,
     "wattage": 200, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 1500},
    {"brand": "Anker", "name": "Anker 637 MagGo Magnetic Desktop Charging Station", "price": 69.99, "rating": 4.2,
     "wattage": 67, "port_count": 4, "wireless": True, "has_magsafe": True,
     "form_factor": "desktop", "review_count": 800},
    {"brand": "Cellularline", "name": "Cellularline DeskPWR 3 GaN Desktop Charger 65W", "price": 40.99, "rating": 3.8,
     "wattage": 65, "port_count": 3, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 100},
    {"brand": "PISEN", "name": "PISEN 100W GaN 5-Port Desktop Charging Station", "price": 34.99, "rating": 4.1,
     "wattage": 100, "port_count": 5, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 600},
    {"brand": "Tecknet", "name": "Tecknet 65W GaN Desktop Charger 5-Port", "price": 29.99, "rating": 4.2,
     "wattage": 65, "port_count": 5, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 450},
    {"brand": "Anker", "name": "Anker Prime 250W GaN 6-Port Desktop Charging Station", "price": 169.99, "rating": 4.5,
     "wattage": 250, "port_count": 6, "has_gan": True, "has_pd": True,
     "form_factor": "desktop", "review_count": 900},
]

EU_ENERGY_STORAGE = [
    {"brand": "EcoFlow", "name": "EcoFlow Delta 3 Plus Portable Power Station 1024Wh", "price": 699.00, "rating": 4.8,
     "wattage": 1800, "features": {"capacity_wh": 1024, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 212},
    {"brand": "DJI", "name": "DJI Power 2000 Portable Power Station 2048Wh 3000W", "price": 1499.00, "rating": 4.5,
     "wattage": 3000, "features": {"capacity_wh": 2048, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 80},
    {"brand": "Anker", "name": "Anker Solix C1000X Portable Power Station 1056Wh", "price": 649.00, "rating": 4.4,
     "wattage": 1800, "features": {"capacity_wh": 1056, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 350},
    {"brand": "Jackery", "name": "Jackery Explorer 1000 Pro Portable Power Station 1002Wh", "price": 649.00, "rating": 4.4,
     "wattage": 1000, "features": {"capacity_wh": 1002, "battery": "Li-Ion", "solar": True},
     "form_factor": "station", "review_count": 450},
    {"brand": "Bluetti", "name": "Bluetti EB3A Portable Power Station 268Wh", "price": 199.99, "rating": 4.3,
     "wattage": 600, "features": {"capacity_wh": 268, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 1200},
    {"brand": "Bluetti", "name": "Bluetti AC70 Portable Power Station 768Wh", "price": 449.00, "rating": 4.4,
     "wattage": 1000, "features": {"capacity_wh": 768, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 680},
    {"brand": "Allpowers", "name": "Allpowers S2000 Pro Portable Power Station 1500Wh", "price": 599.00, "rating": 4.2,
     "wattage": 2000, "features": {"capacity_wh": 1500, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 320},
    {"brand": "Goal Zero", "name": "Goal Zero Yeti 500X Portable Power Station 505Wh", "price": 499.00, "rating": 4.1,
     "wattage": 300, "features": {"capacity_wh": 505, "battery": "Li-Ion", "solar": True},
     "form_factor": "station", "review_count": 250},
    {"brand": "Bluetti", "name": "Bluetti AC180T Portable Power Station 1440Wh", "price": 699.00, "rating": 4.5,
     "wattage": 1800, "features": {"capacity_wh": 1440, "battery": "LiFePO4", "solar": True, "expandable": True},
     "form_factor": "station", "review_count": 180},
    {"brand": "Anker", "name": "Anker Solix F2000 Portable Power Station 2048Wh", "price": 1399.00, "rating": 4.4,
     "wattage": 2400, "features": {"capacity_wh": 2048, "battery": "LiFePO4", "solar": True},
     "form_factor": "station", "review_count": 400},
]


# ============================================================
# 主导入逻辑
# ============================================================

ALL_DATA = {
    # (region_code, category_slug): product_list
    ('NA', 'powerbank'): NA_POWERBANK,
    ('NA', 'wireless_charger'): NA_WIRELESS_CHARGER,
    ('NA', 'adapter_cable'): NA_ADAPTER_CABLE,
    ('NA', 'car_charger'): NA_CAR_CHARGER,
    ('NA', 'desktop_charger'): NA_DESKTOP_CHARGER,
    ('NA', 'energy_storage'): NA_ENERGY_STORAGE,
    ('EU', 'powerbank'): EU_POWERBANK,
    ('EU', 'wireless_charger'): EU_WIRELESS_CHARGER,
    ('EU', 'adapter_cable'): EU_ADAPTER_CABLE,
    ('EU', 'car_charger'): EU_CAR_CHARGER,
    ('EU', 'desktop_charger'): EU_DESKTOP_CHARGER,
    ('EU', 'energy_storage'): EU_ENERGY_STORAGE,
}


def import_all():
    init_db()
    conn = get_conn()
    
    total_new = 0
    total_updated = 0
    
    for (region_code, cat_slug), products in ALL_DATA.items():
        cur = conn.cursor()
        
        # Get region_id
        cur.execute("SELECT id FROM regions WHERE code=?", (region_code,))
        row = cur.fetchone()
        if not row:
            print(f"  ⚠️ 未找到区域: {region_code}")
            continue
        region_id = row['id']
        
        source = 'amazon.de' if region_code == 'EU' else 'aggregator'
        
        print(f"\n📦 导入 {region_code} / {cat_slug} ({len(products)} 产品)...")
        new_count, update_count = save_products(products, region_id, cat_slug, source, conn)
        
        total_new += new_count
        total_updated += update_count
        print(f"   新增: {new_count}, 更新: {update_count}")
    
    conn.close()
    
    print(f"\n✅ 导入完成！")
    print(f"   总计新增: {total_new}")
    print(f"   总计更新: {total_updated}")
    print(f"   总计处理: {total_new + total_updated}")


if __name__ == '__main__':
    import_all()
