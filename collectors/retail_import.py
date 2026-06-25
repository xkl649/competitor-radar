"""
零售渠道竞品数据批量导入脚本
数据来源: Best Buy, Walmart, Target (北美) + 部分欧洲零售
区域: NA (北美零售)
"""
import sys
sys.path.insert(0, '.')
from db.schema import get_conn, init_db
import hashlib
import json

# ============== BEST BUY 数据 ==============

# 1. BB 移动电源 (best-selling) - 25 products
bb_powerbank = [
    {"brand":"INIU","name":"Portable Charger, Market's Smallest 10000mAh PD 45W Power Bank with Layout USB-C Cable","price":29.97,"capacity":10000,"power_w":45,"rating":4.9,"reviews":20,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Nano Power Bank w/ Built-in Foldable USB-C Connector","price":10.00,"capacity":5000,"power_w":22.5,"rating":4.4,"reviews":872,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"Qi2 Certified 15W Magnetic Power Bank","price":37.99,"capacity":10000,"power_w":30,"rating":4.6,"reviews":86,"source":"bestbuy.com","qi2":True},
    {"brand":"Energizer","name":"Ultimate Lithium 20,000 mAh 20W USB-C PD & 15W Qi Wireless 4-Port Power Bank with LCD Display","price":39.99,"capacity":20000,"power_w":20,"rating":4.4,"reviews":187,"source":"bestbuy.com","wireless":True},
    {"brand":"INIU","name":"Compact 10000mAh PD 22.5W Power Bank","price":16.34,"capacity":10000,"power_w":22.5,"rating":4.7,"reviews":462,"source":"bestbuy.com"},
    {"brand":"INIU","name":"22.5W Fast Charging 20000 mAh Power Bank, USB C in & out with LED Display","price":24.99,"capacity":20000,"power_w":22.5,"rating":4.7,"reviews":149,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Prime Power Bank (20K, 220W)","price":179.99,"capacity":20000,"power_w":220,"rating":4.9,"reviews":18,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"Nexode 200W 25,000mAh Power Bank with Smart TFT Display, PD 3.1","price":90.99,"capacity":25000,"power_w":200,"rating":4.8,"reviews":93,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"Nexode 130W 20,000mAh Power Bank with Smart TFT Display, 3-Port","price":56.92,"capacity":20000,"power_w":130,"rating":4.8,"reviews":325,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"MagFlow Qi2.2 25W Magnetic Power Bank for MagSafe with 30W Built-in Cable","price":69.99,"capacity":10000,"power_w":30,"rating":4.5,"reviews":67,"source":"bestbuy.com","qi2":True},
    {"brand":"Energizer","name":"5,000mAh SLIM METAL 20W Magnetic Wireless Qi/Qi2.0/MagSafe PowerBank","price":12.99,"capacity":5000,"power_w":20,"rating":4.3,"reviews":549,"source":"bestbuy.com","qi2":True},
    {"brand":"Energizer","name":"Ultimate Lithium 30,000 mAh 30W Power Delivery 3-Port USB-C Power Bank w/ LCD Display","price":29.99,"capacity":30000,"power_w":30,"rating":4.6,"reviews":170,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"Ultimate Lithium 50,000 mAh 30W Power Delivery 3-Port USB-C Power Bank w/ LCD Display","price":59.99,"capacity":50000,"power_w":30,"rating":4.6,"reviews":101,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"MAX 20,000mAh 15W USB-C 3-Port Power Bank w/ LCD screen","price":24.99,"capacity":20000,"power_w":15,"rating":4.7,"reviews":439,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"MAX 30,000mAh 15W USB-C 3-Port Power Bank w/ LCD screen","price":34.99,"capacity":30000,"power_w":15,"rating":4.6,"reviews":335,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"MAX 10,000mAh 15W USB-C 3-Port Power Bank w/ LCD screen","price":14.99,"capacity":10000,"power_w":15,"rating":4.6,"reviews":559,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"10,000mAh SLIM METAL 20W Magnetic Wireless Qi/Qi2.0/MagSafe PowerBank","price":16.99,"capacity":10000,"power_w":20,"rating":4.4,"reviews":811,"source":"bestbuy.com","qi2":True},
    {"brand":"Anker","name":"Laptop Power Bank (25K, 165W, Built-In and Retractable Cables)","price":119.99,"capacity":25000,"power_w":165,"rating":4.8,"reviews":220,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Power Bank (20K, 87W, Built-In USB-C Cable)","price":47.49,"capacity":20000,"power_w":87,"rating":4.7,"reviews":126,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Zolo Power Bank (20K, 22.5W, Built-In USB-C Cable)","price":39.99,"capacity":20000,"power_w":22.5,"rating":4.8,"reviews":84,"source":"bestbuy.com"},
    {"brand":"INIU","name":"Compact 20000mAh PD Power Bank with Built-in Cable & Digital Display","price":31.35,"capacity":20000,"rating":4.7,"reviews":30,"source":"bestbuy.com"},
    {"brand":"INIU","name":"Compact 10000mAh PD 45W Power Bank with Lanyard USB-C Cable","price":21.99,"capacity":10000,"power_w":45,"rating":5.0,"reviews":12,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"Nexode 165W 20,000mAh Power Bank with Retractable Cable, 3-Port","price":66.47,"capacity":20000,"power_w":165,"rating":5.0,"reviews":1,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Power Bank (20,000mAh, 30W)","price":49.99,"capacity":20000,"power_w":30,"rating":4.6,"reviews":754,"source":"bestbuy.com"},
    {"brand":"Energizer","name":"10,000mAh 22.5W Magnetic Wireless Qi/Qi2.0/MagSafe PowerBank, OLED Display, Apple Watch Charger, 2 Built-in USB-C Cables","price":29.99,"capacity":10000,"power_w":22.5,"rating":4.5,"reviews":223,"source":"bestbuy.com","qi2":True},
]

# 1b. BB 移动电源 (top-rated) - additional unique products
bb_powerbank_top = [
    {"brand":"Belkin","name":"2-in-1 MagSafe Wireless Charging Dock 15W","price":126.99,"rating":4.6,"reviews":110,"source":"bestbuy.com","qi2":True},
    {"brand":"UGREEN","name":"Qi2 Certified 15W Magnetic Power Bank, 30W USB-C Fast Charging","price":37.99,"capacity":10000,"power_w":30,"rating":4.6,"reviews":86,"source":"bestbuy.com","qi2":True},
    {"brand":"Anker","name":"MagGo Power Bank, Ultra-Slim Magnetic Battery Pack, Qi2 Certified 15W","price":79.99,"capacity":10000,"power_w":15,"rating":4.7,"reviews":15,"source":"bestbuy.com","qi2":True},
    {"brand":"Belkin","name":"BOOST↑CHARGE USB-C Portable Charger 10K Power Bank","price":34.99,"capacity":10000,"rating":4.6,"reviews":77,"source":"bestbuy.com"},
    {"brand":"mophie","name":"Universe Powerstation Portable Charger","price":64.99,"capacity":2500,"rating":4.6,"reviews":20,"source":"bestbuy.com"},
    {"brand":"Belkin","name":"BOOST↑CHARGE Pro 3-Port Laptop Power Bank 20k, 65W","price":89.99,"capacity":20000,"power_w":65,"rating":4.6,"reviews":25,"source":"bestbuy.com"},
]

# 2. BB Qi2/MagSafe 无线充电器
bb_wireless = [
    {"brand":"Belkin","name":"Convertible Magnetic Charging Stand 15W Qi2","price":59.99,"power_w":15,"rating":4.0,"reviews":104,"source":"bestbuy.com","qi2":True,"type":"stand"},
    {"brand":"Belkin","name":"15W Qi2 Car Vent Mount Pro","price":71.99,"power_w":15,"rating":4.0,"reviews":58,"source":"bestbuy.com","qi2":True,"type":"car_mount"},
    {"brand":"Anker","name":"MagGo 15W Wireless Stand Charger","price":38.73,"power_w":15,"rating":5.0,"reviews":48,"source":"bestbuy.com","qi2":True,"type":"stand"},
    {"brand":"Belkin","name":"3-in-1 Foldable Magnetic Charging Stand, 25W Qi2","price":89.99,"power_w":25,"rating":5.0,"reviews":48,"source":"bestbuy.com","qi2":True,"type":"3in1"},
    {"brand":"Belkin","name":"2-in-1 Magnetic Foldable Wireless Charger with Qi2 15W","price":32.99,"power_w":15,"rating":5.0,"reviews":35,"source":"bestbuy.com","qi2":True,"type":"2in1"},
    {"brand":"Anker","name":"Prime MagSafe Car Mount Charger, Qi2 25W with TEC Cooling","price":89.99,"power_w":25,"rating":5.0,"reviews":2,"source":"bestbuy.com","qi2":True,"type":"car_mount"},
    {"brand":"Anker","name":"MagGo Charger Stand, Qi2 Certified 15W","price":39.78,"power_w":15,"source":"bestbuy.com","qi2":True,"type":"stand"},
    {"brand":"Anker","name":"MagSafe Charger Pad, Qi2 Certified 15W Wireless","price":21.99,"power_w":15,"source":"bestbuy.com","qi2":True,"type":"pad"},
    {"brand":"Anker","name":"MagGo Charger Stand, Qi2 Certified 15W (Black)","price":53.99,"power_w":15,"source":"bestbuy.com","qi2":True,"type":"2in1"},
    {"brand":"Anker","name":"Prime 3-in-1 Charging Station, AirCool Qi2 25W Foldable","price":149.99,"power_w":25,"source":"bestbuy.com","qi2":True,"type":"3in1"},
    {"brand":"Energizer","name":"3-in-1 15W Magnetic MagSafe/Qi2 Compatible Fast Charger","price":19.99,"power_w":15,"rating":5.0,"reviews":558,"source":"bestbuy.com","qi2":True,"type":"3in1"},
]

# 3. BB 壁充/GaN
bb_wallcharger = [
    {"brand":"Samsung","name":"25W Super Fast Charging Wall Charger","price":12.99,"power_w":25,"ports":1,"rating":4.9,"reviews":2221,"source":"bestbuy.com"},
    {"brand":"Insignia","name":"47W 4-Port Wall Charger (1 USB-C & 3 USB)","price":17.99,"power_w":47,"ports":4,"rating":4.8,"reviews":127,"source":"bestbuy.com"},
    {"brand":"INIU","name":"100W USB C/A Wall Charger, GaN Fast Charge","price":27.99,"power_w":100,"ports":2,"rating":4.9,"reviews":43,"source":"bestbuy.com"},
    {"brand":"Anker","name":"PowerPort PD 60W GaN Fast Charger","price":34.99,"power_w":60,"ports":1,"rating":4.7,"reviews":1066,"source":"bestbuy.com"},
    {"brand":"INIU","name":"65W Fast GaN Charger with USB-A/C Ports","price":29.99,"power_w":65,"ports":2,"rating":4.8,"reviews":270,"source":"bestbuy.com"},
    {"brand":"Google","name":"45W USB-C Power Charger","price":24.99,"power_w":45,"ports":1,"rating":4.8,"reviews":159,"source":"bestbuy.com"},
    {"brand":"UGREEN","name":"Nexode 30W USB-C Charger, Compact Foldable GaN","price":6.99,"power_w":30,"ports":1,"rating":4.9,"reviews":102,"source":"bestbuy.com"},
    {"brand":"Baseus","name":"Enercore with Single Retractable USB-C Cable Charger 45W","price":12.99,"power_w":45,"ports":1,"rating":4.7,"reviews":37,"source":"bestbuy.com"},
    {"brand":"Apple","name":"35W Dual USB-C Port Compact Power Adapter","price":59.00,"power_w":35,"ports":2,"rating":4.9,"reviews":957,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Nano II 45W PPS USB-C Fast Wall Charger with GaN","price":26.99,"power_w":45,"ports":1,"rating":4.9,"reviews":955,"source":"bestbuy.com"},
    {"brand":"Anker","name":"32W Wall Charger","price":12.98,"power_w":32,"rating":4.8,"reviews":408,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Nano Charger (45W, Smart Display, 180° Foldable)","price":29.99,"power_w":45,"ports":1,"source":"bestbuy.com"},
    {"brand":"Anker","name":"523 Charger (Nano 3 47W)","price":18.52,"power_w":47,"rating":4.8,"reviews":39,"source":"bestbuy.com"},
    {"brand":"Anker","name":"PPS 3-Port Fast Compact Foldable Wall Charger (Nano II 65W)","price":26.31,"power_w":65,"ports":3,"rating":4.8,"reviews":4,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Wall Charger (32W, 2-Port)","price":12.99,"power_w":32,"ports":2,"rating":4.6,"reviews":438,"source":"bestbuy.com"},
    {"brand":"Samsung","name":"60W Power Adapter","price":46.74,"power_w":60,"rating":4.9,"reviews":78,"source":"bestbuy.com"},
    {"brand":"Samsung","name":"45W Power Adapter","price":25.76,"power_w":45,"rating":4.8,"reviews":677,"source":"bestbuy.com"},
    {"brand":"Insignia","name":"65W 3-Port USB-C/USB Wall Charger","price":19.99,"power_w":65,"ports":3,"rating":4.7,"reviews":808,"source":"bestbuy.com"},
    {"brand":"Best Buy essentials","name":"20W Dual-Port Wall Charging Kit (2 Pack)","price":10.89,"power_w":20,"ports":2,"rating":4.8,"reviews":1368,"source":"bestbuy.com"},
    {"brand":"Insignia","name":"65W Wall Charger with 6 ft. USB-C Cable","price":26.99,"power_w":65,"ports":1,"rating":5.0,"reviews":29,"source":"bestbuy.com"},
    {"brand":"Apple","name":"40W Dynamic Power Adapter with 60W Max","price":34.99,"power_w":40,"rating":4.9,"reviews":253,"source":"bestbuy.com"},
    {"brand":"Apple","name":"20W USB-C Power Adapter","price":14.99,"power_w":20,"ports":1,"rating":4.8,"reviews":24803,"source":"bestbuy.com"},
    {"brand":"Best Buy essentials","name":"12W Dual-Port Wall Charger (2-pack)","price":8.99,"power_w":12,"ports":2,"rating":4.9,"reviews":10,"source":"bestbuy.com"},
    # Anker brand zone - desktop-class products
    {"brand":"Anker","name":"Laptop Charger (140W, 4-Port, PD 3.1)","price":79.99,"power_w":140,"ports":4,"rating":4.7,"reviews":164,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Prime Charger (100W, 3 Ports, GaN)","price":69.99,"power_w":100,"ports":3,"rating":4.9,"reviews":36,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Prime Desktop Charger (200W, 6 Ports, GaN)","price":79.99,"power_w":200,"ports":6,"rating":4.8,"reviews":168,"source":"bestbuy.com"},
    {"brand":"Anker","name":"Prime Charger (250W, 6 Ports, GaNPrime)","price":149.99,"power_w":250,"ports":6,"rating":5.0,"reviews":24,"source":"bestbuy.com"},
]

# ============== WALMART 数据 ==============

# 4. WM INIU 移动电源
wm_iniu = [
    {"brand":"INIU","name":"45W Fast Charging Portable Charger, Slimmest 10000mAh","price":23.99,"capacity":10000,"power_w":45,"rating":4.6,"reviews":426,"source":"walmart.com"},
    {"brand":"INIU","name":"20,000 mAh Portable Power Bank with Built-in Cables, 45W","price":29.99,"capacity":20000,"power_w":45,"rating":4.7,"reviews":410,"source":"walmart.com"},
    {"brand":"INIU","name":"10,000 mAh Portable Power Bank with Built-in Cables, 45W","price":24.29,"capacity":10000,"power_w":45,"rating":4.6,"reviews":47,"source":"walmart.com"},
    {"brand":"INIU","name":"Portable Charger, Ultra Mini 10000mAh 45W Fast Charging","price":29.69,"capacity":10000,"power_w":45,"rating":4.4,"reviews":83,"source":"walmart.com"},
    {"brand":"INIU","name":"SnapGo Mini Portable Charger, Power Bank for Apple Watch and iPhone","price":21.23,"capacity":5000,"power_w":20,"rating":4.4,"reviews":24,"source":"walmart.com","wireless":True},
    {"brand":"INIU","name":"10000mAh Power Bank, Slimmest 15W Portable Charger","price":18.39,"capacity":10000,"power_w":15,"rating":4.6,"reviews":986,"source":"walmart.com"},
    {"brand":"INIU","name":"Portable Charger, 20000mAh Power Bank with 22.5W Fast Charging","price":24.99,"capacity":20000,"power_w":22.5,"rating":5.0,"reviews":1,"source":"walmart.com"},
]

# 5. WM UGREEN 移动电源
wm_ugreen = [
    {"brand":"UGREEN","name":"67W 20000mAh Power Bank with Built-in USB-C Cable","price":36.79,"capacity":20000,"power_w":67,"rating":4.6,"reviews":94,"source":"walmart.com"},
    {"brand":"UGREEN","name":"10000mAh Magsafe Power Bank, Wireless Portable Charger","price":26.39,"capacity":10000,"power_w":20,"rating":4.7,"reviews":42,"source":"walmart.com","qi2":True},
    {"brand":"UGREEN","name":"Nexode 45W Power Bank, 20,000mAh with Built-in USB-C Cable, 3-Port","price":28.48,"capacity":20000,"power_w":45,"rating":4.6,"reviews":94,"source":"walmart.com"},
    {"brand":"UGREEN","name":"Magnetic Wireless Power Bank, 5000mAh 20W PD + 15W Wireless","price":37.99,"capacity":5000,"power_w":20,"source":"walmart.com","qi2":True},
    {"brand":"UGREEN","name":"10000mAh Magnetic Power Bank (Pink)","price":29.99,"capacity":10000,"rating":3.0,"reviews":3,"source":"walmart.com","qi2":True},
]

# 6. WM Belkin 移动电源
wm_belkin = [
    {"brand":"Belkin","name":"Portable Charger, 10000 mAh, 23W w/Integrated Lightning & USB-C Cable","price":35.00,"capacity":10000,"power_w":23,"rating":4.4,"reviews":178,"source":"walmart.com"},
    {"brand":"Belkin","name":"USB-C Power Bank 20,000mAh w/ 2 USB-A Ports, 15W","price":26.00,"capacity":20000,"power_w":15,"rating":4.2,"reviews":120,"source":"walmart.com"},
    {"brand":"Belkin","name":"BoostCharge USB-C Portable Charger 10K Power Bank","price":18.00,"capacity":10000,"rating":4.2,"reviews":403,"source":"walmart.com"},
    {"brand":"Belkin","name":"USB-C Power Bank 10,000mAh w/ 1xUSB-C and 2xUSB-A Ports, 15W (Pink)","price":15.00,"capacity":10000,"power_w":15,"rating":3.6,"reviews":85,"source":"walmart.com"},
    {"brand":"Belkin","name":"Power Bank 10,000mAh with Integrated Cable - 20W USB-C PD","price":18.00,"capacity":10000,"power_w":20,"rating":4.6,"reviews":145,"source":"walmart.com"},
    {"brand":"Belkin","name":"BoostCharge Power Bank 10K","price":21.24,"capacity":10000,"rating":4.2,"reviews":198,"source":"walmart.com"},
]

# 7. WM Qi2/MagSafe 无线充电器
wm_qi2 = [
    {"brand":"ETEPEHI","name":"3 in 1 Magnetic Charging Station - Foldable Wireless Charger","price":13.39,"power_w":15,"rating":4.5,"reviews":1848,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"ETEPEHI","name":"36W Wireless Charger: 5 in 1 Fast Charging Station","price":22.69,"power_w":36,"rating":4.6,"reviews":1291,"source":"walmart.com","qi2":True,"type":"5in1"},
    {"brand":"ETEPEHI","name":"Travel Magnetic Wireless Charger: 3 in 1 Foldable Charging Pad","price":17.69,"power_w":15,"rating":4.8,"reviews":284,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"ETEPEHI","name":"18W Wireless Charger for iPhone - 3 in 1 Charging Station","price":15.99,"power_w":18,"rating":4.5,"reviews":3648,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"Monster","name":"10-in-1 Charging Sphere Desktop Charging Station, 100W, Qi2","price":44.88,"power_w":100,"rating":4.5,"reviews":122,"source":"walmart.com","qi2":True,"type":"10in1_desktop"},
    {"brand":"Monster","name":"3-in-1 Wireless Charger Stand, Qi2, Motorized Rotating, 22.5W","price":34.99,"power_w":22.5,"rating":4.4,"reviews":87,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"Anker","name":"Zolo Magnetic Wireless Charger, 2-Pack, Qi2 Certified 15W","price":39.99,"power_w":15,"rating":4.5,"reviews":4,"source":"walmart.com","qi2":True,"type":"pad"},
    {"brand":"Belkin","name":"MagSafe Charger Compatible 3-in-1 Wireless Charging Stand 15W Qi2","price":99.99,"power_w":15,"rating":4.2,"reviews":945,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"Swayvoo","name":"25W Qi2.2 Fast Wireless Charging Pad","price":20.70,"power_w":25,"rating":3.7,"reviews":3,"source":"walmart.com","qi2":True,"type":"pad"},
    {"brand":"Anker","name":"MagGo Qi2 Ultra-Slim Magnetic Power Bank, 15W, 10000mAh","price":55.00,"capacity":10000,"power_w":15,"rating":4.6,"reviews":200,"source":"walmart.com","qi2":True},
    {"brand":"Anker","name":"MagGo Qi2 3-in-1 Foldable Charging Station, 15W","price":49.00,"power_w":15,"rating":4.5,"reviews":42,"source":"walmart.com","qi2":True,"type":"3in1"},
    {"brand":"Belkin","name":"Magnetic Wireless Charging Pad 15W w/Pop-Up Stand, Qi2","price":19.98,"power_w":15,"rating":4.2,"reviews":342,"source":"walmart.com","qi2":True,"type":"pad"},
]

# 8. WM GaN 充电器
wm_gan = [
    {"brand":"Greenworks","name":"POWERALL 140W GaN II Charger, 4-Port","price":53.60,"power_w":140,"ports":4,"rating":4.8,"reviews":6,"source":"walmart.com"},
    {"brand":"onn","name":"67W Laptop Charger, GaN","price":35.86,"power_w":67,"ports":1,"rating":4.5,"reviews":170,"source":"walmart.com"},
    {"brand":"j5create","name":"140W GaN PD 3.1 USB-C Charger (JUP17140)","price":69.97,"power_w":140,"rating":4.5,"reviews":65,"source":"walmart.com"},
    {"brand":"onn","name":"65W + 12W Laptop Charger, GaN","price":37.94,"power_w":65,"rating":4.3,"reviews":372,"source":"walmart.com"},
    {"brand":"Ankereame","name":"120W GaN Charger 2-in-1 Retractable Cable","price":14.14,"power_w":120,"ports":2,"source":"walmart.com"},
    {"brand":"Generic","name":"100W GaN Fast Charger, 4-Port (3 USB-C + 1 USB-A)","price":39.90,"power_w":100,"ports":4,"source":"walmart.com"},
    {"brand":"Generic","name":"500W GaN 10-Port USB Type C Charging Station","price":39.31,"power_w":100,"ports":10,"rating":4.0,"reviews":10,"source":"walmart.com"},
]

# ============== TARGET 数据 ==============

target_products = [
    {"brand":"Anker","name":"Qi2 10000mAh Magnetic Power Bank","price":49.99,"capacity":10000,"power_w":15,"rating":4.6,"reviews":84,"source":"target.com","qi2":True},
    {"brand":"Belkin","name":"25W Qi2 Wireless 3-in-1 Stand - Charcoal Gray","price":69.99,"power_w":25,"rating":4.7,"reviews":139,"source":"target.com","qi2":True,"type":"3in1"},
    {"brand":"Monster","name":"10-in-1 Charging Sphere Desktop Charging Station with Qi2, 3 AC, 2 USB-C, 2 USB-A","price":59.99,"power_w":65,"ports":10,"rating":4.7,"reviews":64,"source":"target.com","qi2":True,"type":"desktop"},
]

# ============== MAPPING & IMPORT ==============

def fingerprint(brand, name, source):
    return hashlib.md5(f"{brand}::{name}::{source}".encode()).hexdigest()[:16]

def classify_category(prod):
    """根据产品特征判断品类 (匹配数据库实际 slug)"""
    ptype = prod.get('type','')
    has_cap = prod.get('capacity') and prod.get('capacity',0) >= 1000
    has_power = prod.get('power_w') and prod.get('power_w',0) >= 10
    
    # 桌面充电站: 10in1 类型 或 大功率多口
    if 'desktop' in ptype or '10in1' in ptype:
        return 'desktop_charger'
    # 车载
    if 'car' in ptype:
        return 'car_charger'
    # Qi2 无线充电器 (不带电池容量)
    if (prod.get('qi2') or prod.get('wireless')) and not has_cap:
        return 'wireless_charger'
    # Qi2 磁吸充电宝 (带电池)
    if prod.get('qi2') and has_cap:
        return 'powerbank'
    # 有容量 → 充电宝
    if has_cap:
        return 'powerbank'
    # 大功率多口 → 桌面充
    if has_power and prod.get('power_w',0) >= 100 and prod.get('ports',0) >= 4:
        return 'desktop_charger'
    # 有功率 → 适配器
    if has_power:
        return 'adapter_cable'
    # 无线类型默认
    if prod.get('wireless') or ptype in ('pad','stand','2in1','3in1','5in1'):
        return 'wireless_charger'
    return 'powerbank'

def import_products(conn, products, region='NA'):
    cur = conn.cursor()
    new_c = update_c = skip_c = 0
    
    for prod in products:
        cat_slug = classify_category(prod)
        fp = fingerprint(prod['brand'], prod['name'], prod['source'])
        
        # Find category
        cur.execute("SELECT id FROM categories WHERE slug=?", (cat_slug,))
        cat = cur.fetchone()
        if not cat:
            skip_c += 1
            continue
        
        # Find region
        cur.execute("SELECT id FROM regions WHERE code=?", (region,))
        reg = cur.fetchone()
        if not reg:
            skip_c += 1
            continue
        
        # Brand upsert
        norm = prod['brand'].lower().strip()
        cur.execute("SELECT id FROM brands WHERE normalized_name=? AND region=?", (norm, region))
        brand = cur.fetchone()
        if brand:
            brand_id = brand['id']
        else:
            cur.execute("INSERT INTO brands (name, normalized_name, region) VALUES (?,?,?)",
                       (prod['brand'], norm, region))
            brand_id = cur.lastrowid
        
        # Check existing
        cur.execute("SELECT id FROM products WHERE fingerprint=?", (fp,))
        exist = cur.fetchone()
        
        has_qi2 = 1 if prod.get('qi2') else 0
        has_wireless = 1 if (prod.get('qi2') or prod.get('wireless')) else 0
        has_gan = 1 if cat_slug in ('adapter_cable','desktop_charger') else 0
        has_magsafe = 1 if prod.get('qi2') else 0
        
        if exist:
            cur.execute("""UPDATE products SET 
                price=?, price_currency='USD', rating=?, review_count=?,
                capacity_mah=?, wattage=?, last_seen=datetime('now')
                WHERE fingerprint=?""",
                (prod.get('price'), prod.get('rating'), prod.get('reviews',0),
                 prod.get('capacity'), prod.get('power_w'), fp))
            update_c += 1
        else:
            cur.execute("""INSERT INTO products 
                (fingerprint, brand_name, brand_id, name, category_id, region_id,
                 source, price, price_currency, rating, review_count,
                 capacity_mah, wattage, has_qi2, has_wireless, has_gan,
                 has_pd, has_magsafe, has_retractable_cable, form_factor,
                 features, is_active, first_seen, last_seen, collected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,0,?,?,1,
                    datetime('now'),datetime('now'),datetime('now'))""",
                (fp, prod['brand'], brand_id, prod['name'],
                 cat['id'], reg['id'], prod['source'],
                 prod.get('price'), 'USD', prod.get('rating'), prod.get('reviews',0),
                 prod.get('capacity'), prod.get('power_w'),
                 has_qi2, has_wireless, has_gan,
                 has_magsafe,
                 prod.get('type',''),
                 json.dumps({'retail_source': prod['source']})))
            new_c += 1
    
    conn.commit()
    return new_c, update_c, skip_c

def main():
    init_db()
    conn = get_conn()
    
    all_batches = [
        ("BB PowerBank", bb_powerbank),
        ("BB PowerBank Top", bb_powerbank_top),
        ("BB Wireless", bb_wireless),
        ("BB Wall Charger", bb_wallcharger),
        ("WM INIU", wm_iniu),
        ("WM UGREEN", wm_ugreen),
        ("WM Belkin", wm_belkin),
        ("WM Qi2", wm_qi2),
        ("WM GaN", wm_gan),
        ("Target", target_products),
    ]
    
    total_new = total_upd = total_skip = 0
    for label, data in all_batches:
        n, u, s = import_products(conn, data)
        total_new += n; total_upd += u; total_skip += s
        print(f"  {label:25s}: +{n:2d} new, ~{u:2d} upd, -{s:2d} skip")
    
    print(f"\n{'='*50}")
    print(f"  TOTAL: +{total_new} new, ~{total_upd} updated, -{total_skip} skipped")
    
    # Print summary
    print(f"\n=== Database Summary ===")
    for r in conn.execute("SELECT r.code, COUNT(*) FROM products p JOIN regions r ON p.region_id=r.id GROUP BY r.code"):
        print(f"  Region {r[0]}: {r[1]} products")
    for r in conn.execute("SELECT c.slug, COUNT(*) FROM products p JOIN categories c ON p.category_id=c.id GROUP BY c.slug"):
        print(f"  {r[0]}: {r[1]} products")
    print(f"  Total: {conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]} products")
    
    conn.close()

if __name__ == '__main__':
    main()
