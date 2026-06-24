"""
种子数据填充 — 从前期分析中提取的真实竞品样本数据
用于 App 首次启动时展示完整功能
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import get_conn, init_db
from collectors.eu_amazon import save_products, get_region_id, get_category_id

SEED_DATA = {
    'powerbank': [
        {"brand":"Anker","name":"Anker MagGo 10K Qi2 Magnetic Power Bank","price":49.99,"rating":4.5,"review_count":3240,"capacity":"10000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"Belkin","name":"Belkin BoostCharge Pro Qi2 10K","price":59.99,"rating":4.4,"review_count":2150,"capacity":"10000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"Anker","name":"Anker PowerCore 20K PD 65W","price":44.99,"rating":4.6,"review_count":8900,"capacity":"20000mAh","wattage":"65W","qi2":False,"has_pd":True,"form_factor":"brick"},
        {"brand":"Baseus","name":"Baseus 30W Magnetic Power Bank 10K","price":35.99,"rating":4.3,"review_count":1560,"capacity":"10000mAh","wattage":"30W","magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"UGREEN","name":"UGREEN 10000mAh Qi2 Magnetic Power Bank","price":39.99,"rating":4.2,"review_count":890,"capacity":"10000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"INIU","name":"INIU MagPro 10K Magnetic Power Bank","price":29.99,"rating":4.4,"review_count":2100,"capacity":"10000mAh","wattage":"20W","magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"Anker","name":"Anker Prime 9.6K 65W Fusion","price":69.99,"rating":4.5,"review_count":1230,"capacity":"9600mAh","wattage":"65W","has_pd":True,"form_factor":"brick"},
        {"brand":"Xiaomi","name":"Xiaomi 50W Power Bank 20000mAh","price":42.99,"rating":4.3,"review_count":3200,"capacity":"20000mAh","wattage":"50W","form_factor":"brick"},
        {"brand":"Samsung","name":"Samsung 10000mAh 25W PD Power Bank","price":34.99,"rating":4.5,"review_count":4500,"capacity":"10000mAh","wattage":"25W","has_pd":True,"form_factor":"brick"},
        {"brand":"ESR","name":"ESR Qi2 10K MagSafe Power Bank with Stand","price":44.99,"rating":4.4,"review_count":1870,"capacity":"10000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"Anker","name":"Anker 335 Power Bank 20K 20W","price":25.99,"rating":4.6,"review_count":12000,"capacity":"20000mAh","wattage":"20W","form_factor":"brick"},
        {"brand":"INIU","name":"INIU B63 20K 22.5W Power Bank","price":23.99,"rating":4.5,"review_count":3600,"capacity":"20000mAh","wattage":"22.5W","form_factor":"brick"},
        {"brand":"Spigen","name":"Spigen ArcField Qi2 10K MagSafe","price":42.99,"rating":4.3,"review_count":950,"capacity":"10000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"Mophie","name":"Mophie Powerstation 10K Qi2","price":54.99,"rating":4.2,"review_count":780,"capacity":"10000mAh","wattage":"15W","qi2":True,"wireless":True,"form_factor":"magnetic"},
        {"brand":"RAVPower","name":"RAVPower 20000mAh 65W PD","price":39.99,"rating":4.4,"review_count":2800,"capacity":"20000mAh","wattage":"65W","has_pd":True,"form_factor":"brick"},
        {"brand":"Sharge","name":"Shargeek Storm² 25600mAh 100W","price":89.99,"rating":4.3,"review_count":650,"capacity":"25600mAh","wattage":"100W","has_pd":True,"form_factor":"brick"},
        {"brand":"OtterBox","name":"OtterBox 15W Qi2 MagSafe 5K","price":39.99,"rating":4.1,"review_count":430,"capacity":"5000mAh","wattage":"15W","qi2":True,"magsafe":True,"wireless":True,"form_factor":"magnetic"},
    ],
    'wireless_charger': [
        {"brand":"Belkin","name":"Belkin BoostCharge Pro 3-in-1 Qi2","price":129.99,"rating":4.4,"review_count":2100,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
        {"brand":"Anker","name":"Anker MagGo 3-in-1 Qi2 Charging Station","price":99.99,"rating":4.5,"review_count":1650,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
        {"brand":"ESR","name":"ESR Qi2 3-in-1 Travel Charger","price":69.99,"rating":4.3,"review_count":1200,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
        {"brand":"Mophie","name":"Mophie 3-in-1 Qi2 Travel Charger","price":149.99,"rating":4.2,"review_count":560,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
        {"brand":"Nomad","name":"Nomad Stand One Qi2","price":99.99,"rating":4.5,"review_count":780,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
        {"brand":"INIU","name":"INIU Qi 15W Fast Wireless Charger Pad","price":15.99,"rating":4.4,"review_count":3500,"wattage":"15W","wireless":True,"form_factor":"pad"},
        {"brand":"Anker","name":"Anker 313 Wireless Charger Pad","price":13.99,"rating":4.5,"review_count":12000,"wattage":"10W","wireless":True,"form_factor":"pad"},
        {"brand":"Samsung","name":"Samsung Fast Wireless Charger Duo","price":69.99,"rating":4.4,"review_count":2800,"wattage":"15W","wireless":True,"form_factor":"stand"},
        {"brand":"Apple","name":"Apple MagSafe Charger","price":39.99,"rating":4.3,"review_count":15000,"wattage":"15W","magsafe":True,"wireless":True,"form_factor":"pad"},
        {"brand":"Belkin","name":"Belkin BoostCharge 2-in-1 Qi2","price":79.99,"rating":4.3,"review_count":940,"wattage":"15W","qi2":True,"wireless":True,"form_factor":"stand"},
    ],
    'adapter_cable': [
        {"brand":"Anker","name":"Anker Nano II 65W GaN Charger","price":39.99,"rating":4.6,"review_count":12000,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"UGREEN","name":"UGREEN Nexode 65W GaN Charger","price":34.99,"rating":4.5,"review_count":5600,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Anker","name":"Anker Prime 100W GaN Wall Charger","price":59.99,"rating":4.5,"review_count":3400,"wattage":"100W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Baseus","name":"Baseus GaN5 65W Wall Charger","price":29.99,"rating":4.3,"review_count":2100,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Spigen","name":"Spigen 45W GaN Charger","price":25.99,"rating":4.4,"review_count":1800,"wattage":"45W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"INIU","name":"INIU 65W GaN PD Wall Charger","price":27.99,"rating":4.4,"review_count":2400,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Anker","name":"Anker 735 65W GaNPrime","price":49.99,"rating":4.6,"review_count":4500,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Samsung","name":"Samsung 45W PD Fast Charger","price":29.99,"rating":4.3,"review_count":5600,"wattage":"45W","has_pd":True,"form_factor":"brick"},
        {"brand":"Apple","name":"Apple 35W Dual USB-C Charger","price":59.99,"rating":4.2,"review_count":8900,"wattage":"35W","form_factor":"brick"},
        {"brand":"Belkin","name":"Belkin 65W Dual USB-C GaN","price":44.99,"rating":4.2,"review_count":890,"wattage":"65W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"RAVPower","name":"RAVPower 90W GaN Charger","price":42.99,"rating":4.4,"review_count":2100,"wattage":"90W","has_gan":True,"has_pd":True,"form_factor":"brick"},
        {"brand":"Baseus","name":"Baseus 100W GaN3 Pro","price":45.99,"rating":4.3,"review_count":1600,"wattage":"100W","has_gan":True,"has_pd":True,"form_factor":"brick"},
    ],
    'car_charger': [
        {"brand":"Anker","name":"Anker PowerDrive 40W Dual USB-C","price":19.99,"rating":4.5,"review_count":5600,"wattage":"40W","has_pd":True,"form_factor":"car"},
        {"brand":"Belkin","name":"Belkin BoostCharge 45W USB-C Car","price":24.99,"rating":4.3,"review_count":1200,"wattage":"45W","has_pd":True,"form_factor":"car"},
        {"brand":"Baseus","name":"Baseus 60W Retractable Cable Car Charger","price":22.99,"rating":4.2,"review_count":890,"wattage":"60W","has_pd":True,"has_retractable":True,"form_factor":"car"},
        {"brand":"Spigen","name":"Spigen 45W Dual USB-C PD Car Charger","price":18.99,"rating":4.4,"review_count":1450,"wattage":"45W","has_pd":True,"form_factor":"car"},
        {"brand":"Ainope","name":"Ainope 48W Retractable Cable Car","price":14.99,"rating":4.2,"review_count":2300,"wattage":"48W","has_retractable":True,"form_factor":"car"},
        {"brand":"INIU","name":"INIU 36W Dual Port Car Charger","price":12.99,"rating":4.4,"review_count":1800,"wattage":"36W","form_factor":"car"},
        {"brand":"Anker","name":"Anker PowerDrive Speed+ Duo 63W","price":29.99,"rating":4.5,"review_count":3200,"wattage":"63W","has_pd":True,"form_factor":"car"},
        {"brand":"Samsung","name":"Samsung 45W Fast Car Charger","price":24.99,"rating":4.3,"review_count":2100,"wattage":"45W","has_pd":True,"form_factor":"car"},
    ],
    'desktop_charger': [
        {"brand":"Anker","name":"Anker Prime 200W Desktop Charger","price":129.99,"rating":4.5,"review_count":2100,"wattage":"200W","port_count":6,"has_gan":True,"has_pd":True,"form_factor":"desktop"},
        {"brand":"UGREEN","name":"UGREEN Nexode 100W Desktop Charger","price":59.99,"rating":4.4,"review_count":1800,"wattage":"100W","port_count":4,"has_gan":True,"has_pd":True,"form_factor":"desktop"},
        {"brand":"Baseus","name":"Baseus 100W GaN Desktop Charger","price":49.99,"rating":4.3,"review_count":1200,"wattage":"100W","port_count":5,"has_gan":True,"has_pd":True,"form_factor":"desktop"},
        {"brand":"Anker","name":"Anker 547 65W Desktop Charger","price":45.99,"rating":4.4,"review_count":890,"wattage":"65W","port_count":4,"has_gan":True,"form_factor":"desktop"},
        {"brand":"Satechi","name":"Satechi 165W GaN Desktop Charger","price":119.99,"rating":4.3,"review_count":560,"wattage":"165W","port_count":4,"has_gan":True,"has_pd":True,"form_factor":"desktop"},
        {"brand":"Belkin","name":"Belkin 108W GaN Desktop Charger","price":74.99,"rating":4.2,"review_count":430,"wattage":"108W","port_count":4,"has_gan":True,"has_pd":True,"form_factor":"desktop"},
    ],
    'energy_storage': [
        {"brand":"Jackery","name":"Jackery Explorer 1000 Pro","price":1099.99,"rating":4.6,"review_count":3400,"capacity":"1002Wh","wattage":"1000W","form_factor":"station"},
        {"brand":"EcoFlow","name":"EcoFlow Delta 2","price":999.99,"rating":4.5,"review_count":2100,"capacity":"1024Wh","wattage":"1800W","form_factor":"station"},
        {"brand":"Bluetti","name":"Bluetti AC180","price":799.99,"rating":4.4,"review_count":1600,"capacity":"1152Wh","wattage":"1800W","form_factor":"station"},
        {"brand":"Anker","name":"Anker SOLIX C1000","price":899.99,"rating":4.4,"review_count":980,"capacity":"1056Wh","wattage":"1800W","form_factor":"station"},
        {"brand":"Goal Zero","name":"Goal Zero Yeti 1000X","price":1199.99,"rating":4.3,"review_count":1200,"capacity":"983Wh","wattage":"1500W","form_factor":"station"},
        {"brand":"Jackery","name":"Jackery Explorer 300 Plus","price":279.99,"rating":4.5,"review_count":4500,"capacity":"288Wh","wattage":"300W","form_factor":"station"},
        {"brand":"Bluetti","name":"Bluetti EB3A","price":199.99,"rating":4.3,"review_count":3200,"capacity":"268Wh","wattage":"600W","form_factor":"station"},
    ],
}


def seed():
    """填充种子数据到数据库"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    eu_region_id = get_region_id(cur, 'EU')
    total_new = 0

    for slug, products in SEED_DATA.items():
        cat_id = get_category_id(cur, slug)
        if not cat_id:
            print(f"  ⚠️ 跳过: {slug}")
            continue

        print(f"📦 种子数据: {slug} ({len(products)} 条)")

        # 分别以 EU 和 NA 区域导入
        for region_id, region_code, source in [
            (eu_region_id, 'EU', 'amazon.de'),
            (2, 'NA', 'amazon.com'),
        ]:
            new, upd = save_products(products, region_id, slug, source, conn)
            total_new += new
            print(f"  {region_code}: {new} 新增, {upd} 更新")

    print(f"\n✅ 种子数据导入完成! 共新增 {total_new} 条产品记录")
    conn.close()


if __name__ == '__main__':
    seed()
