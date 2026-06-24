"""
数据采集助手模块
提供AI Agent采集竞品数据的辅助函数
"""
import json
import os

# 采集配置：所有需要采集的URL和参数
COLLECTION_TASKS = [
    {
        'id': 'eu_powerbank_de',
        'name': '欧洲-移动电源-Amazon.de',
        'url': 'https://www.amazon.de/s?k=power+bank+10000mAh+Qi2&rh=n%3A2811685031&s=review-rank',
        'category': 'powerbank',
        'region': 'EU',
        'source': 'amazon.de',
        'prompt': '提取搜索结果中的所有移动电源产品数据：品牌、产品名、价格(欧元)、评分、评论数、容量(mAh)、是否Qi2/磁吸、功率(W)。用表格形式输出，尽可能多提取产品。'
    },
    {
        'id': 'eu_powerbank_pl',
        'name': '欧洲-移动电源-Amazon.pl',
        'url': 'https://www.amazon.pl/s?k=power+bank+10000mAh+magsafe&s=review-rank',
        'category': 'powerbank',
        'region': 'EU',
        'source': 'amazon.pl',
        'prompt': '提取搜索结果中的所有移动电源产品数据：品牌、产品名、价格(兹罗提)、评分、评论数、容量(mAh)。用表格形式输出。'
    },
    {
        'id': 'eu_wireless_de',
        'name': '欧洲-无线充电器-Amazon.de',
        'url': 'https://www.amazon.de/s?k=qi2+wireless+charger+3-in-1&rh=n%3A2811692031&s=review-rank',
        'category': 'wireless_charger',
        'region': 'EU',
        'source': 'amazon.de',
        'prompt': '提取所有无线充电器产品：品牌、产品名、价格(欧元)、评分、评论数、形态(3-in-1/pad/stand/2-in-1)、Qi2支持、功率、磁吸。表格输出'
    },
    {
        'id': 'eu_adapter_de',
        'name': '欧洲-适配器-Amazon.de',
        'url': 'https://www.amazon.de/s?k=usb+c+ladeger%C3%A4t+gan+65w&rh=n%3A2811676031&s=review-rank',
        'category': 'adapter_cable',
        'region': 'EU',
        'source': 'amazon.de',
        'prompt': '提取所有充电器产品数据：品牌、产品名、价格(欧元)、评分、功率、端口数、GaN技术、是否折叠插脚。表格形式输出'
    },
    {
        'id': 'eu_car_de',
        'name': '欧洲-车充-Amazon.de',
        'url': 'https://www.amazon.de/s?k=auto+ladeger%C3%A4t+einziehbares+kabel&rh=n%3A2811688031&s=review-rank',
        'category': 'car_charger',
        'region': 'EU',
        'source': 'amazon.de',
        'prompt': '提取所有车充产品数据：品牌、产品名、价格(欧元)、评分、功率、伸缩线、端口数。表格输出'
    },
    {
        'id': 'eu_desktop_de',
        'name': '欧洲-桌面充-Amazon.de',
        'url': 'https://www.amazon.de/s?k=desktop+charging+station+100w+gan&rh=n%3A2811687031&s=review-rank',
        'category': 'desktop_charger',
        'region': 'EU',
        'source': 'amazon.de',
        'prompt': '提取所有桌面充电站产品：品牌、产品名、价格(欧元)、评分、评论数、总功率、端口配置、GaN技术。表格输出'
    },
]


def get_collection_tasks(category=None, region=None):
    """获取采集任务列表"""
    tasks = COLLECTION_TASKS
    if category:
        tasks = [t for t in tasks if t['category'] == category]
    if region:
        tasks = [t for t in tasks if t['region'] == region]
    return tasks


def format_task_for_agent(task):
    """格式化任务，供AI Agent执行"""
    return {
        'task_id': task['id'],
        'instruction': f"""
请使用 WebFetch 工具采集以下页面的竞品数据：

URL: {task['url']}
页面类型: {task['source']}
品类: {task['category']}
区域: {task['region']}

采集要求:
{task['prompt']}

请将提取的数据格式化为JSON数组，每个产品包含以下字段：
- brand: 品牌名
- name: 产品全名
- price: 价格（数字）
- rating: 评分（1-5）
- review_count: 评论数
- capacity_mAh: 容量（移动电源）
- wattage: 功率(W)
- has_qi2: 是否支持Qi2 (0/1)
- has_gan: 是否GaN (0/1)
- has_wireless: 是否无线充电 (0/1)
- has_magsafe: 是否磁吸 (0/1)
- form_factor: 形态(brick/magnetic/stand/pad/desktop/car)

输出格式: JSON数组
""".strip()
    }


def save_collected_data_to_db(data, category, region, source, db_path=None):
    """将采集到的数据保存到数据库"""
    if not db_path:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'competitors.db')

    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from db.schema import get_conn
    from collectors.eu_amazon import save_products, get_region_id, get_category_id

    conn = get_conn()
    cur = conn.cursor()

    # 获取region_id
    cur.execute("SELECT id FROM regions WHERE code=?", (region,))
    row = cur.fetchone()
    if not row:
        print(f"❌ 未知区域: {region}")
        return 0, 0
    region_id = row['id']

    # 保存产品
    new_count, update_count = save_products(data, region_id, category, source, conn)

    conn.close()
    print(f"✅ 数据已保存: {new_count} 新增, {update_count} 更新")
    return new_count, update_count


if __name__ == '__main__':
    # 测试：打印所有采集任务
    tasks = get_collection_tasks()
    print(f"📋 共 {len(tasks)} 个采集任务:\n")
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task['name']}")
        print(f"   URL: {task['url'][:80]}...")
        print(f"   品类: {task['category']} | 区域: {task['region']}\n")
