"""
竞品雷达 — 数据库 Schema
表结构：产品 / 品牌 / 品类 / 区域 / 采集日志
"""
import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'competitors.db')


def get_conn():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,       -- 'EU' | 'NA'
            name TEXT NOT NULL,              -- '欧洲' | '北美'
            currency TEXT NOT NULL,          -- 'EUR' | 'USD'
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,       -- 'powerbank' | 'wireless_charger' | ...
            name_zh TEXT NOT NULL,           -- '移动电源'
            name_en TEXT NOT NULL,           -- 'Power Bank'
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            region TEXT,
            market_share_rank INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(normalized_name, region)
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- 基本信息
            name TEXT NOT NULL,
            brand_id INTEGER REFERENCES brands(id),
            brand_name TEXT,
            category_id INTEGER REFERENCES categories(id),
            region_id INTEGER REFERENCES regions(id),
            source TEXT,                     -- 'amazon.de' | 'bestbuy.com' | ...
            source_url TEXT,
            -- 价格
            price REAL,
            price_currency TEXT,
            price_original REAL,
            -- 评分
            rating REAL,
            review_count INTEGER,
            -- 规格
            capacity_mah INTEGER,            -- 移动电源/储能
            wattage REAL,                    -- 功率(W)
            port_count INTEGER,              -- 端口数
            port_config TEXT,                -- JSON: [{"type":"USB-C","wattage":65}]
            -- 技术特性
            has_qi2 INTEGER DEFAULT 0,
            has_magsafe INTEGER DEFAULT 0,
            has_wireless INTEGER DEFAULT 0,
            has_gan INTEGER DEFAULT 0,
            has_pd INTEGER DEFAULT 0,
            has_retractable_cable INTEGER DEFAULT 0,
            -- 形态
            form_factor TEXT,                -- 'brick'|'stick'|'flat'|'desktop'|'magnetic'|...
            color_options TEXT,              -- JSON array
            -- 扩展字段
            features JSON,
            -- 元数据
            is_active INTEGER DEFAULT 1,
            first_seen TEXT,
            last_seen TEXT DEFAULT (datetime('now')),
            collected_at TEXT DEFAULT (datetime('now')),
            data_quality_score REAL DEFAULT 0.0,
            -- 去重
            fingerprint TEXT,                -- hash of brand+name+region for dedup
            UNIQUE(fingerprint)
        );

        CREATE TABLE IF NOT EXISTS collection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER REFERENCES regions(id),
            category_id INTEGER REFERENCES categories(id),
            source TEXT,
            status TEXT DEFAULT 'pending',   -- 'pending'|'running'|'success'|'failed'
            sku_count INTEGER DEFAULT 0,
            new_sku_count INTEGER DEFAULT 0,
            error_message TEXT,
            duration_ms INTEGER,
            started_at TEXT,
            finished_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- 索引
        CREATE INDEX IF NOT EXISTS idx_products_region ON products(region_id);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
        CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_id);
        CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating DESC);
        CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
        CREATE INDEX IF NOT EXISTS idx_products_collected ON products(collected_at DESC);
        CREATE INDEX IF NOT EXISTS idx_product_fingerprint ON products(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_logs_region ON collection_logs(region_id);
        CREATE INDEX IF NOT EXISTS idx_logs_created ON collection_logs(created_at DESC);
    """)

    # 初始化种子数据
    _seed_regions(cur)
    _seed_categories(cur)

    conn.commit()
    conn.close()
    return True


def _seed_regions(cur):
    regions = [
        ('EU', '欧洲', 'EUR'),
        ('NA', '北美', 'USD'),
    ]
    for code, name, currency in regions:
        cur.execute(
            "INSERT OR IGNORE INTO regions (code, name, currency) VALUES (?,?,?)",
            (code, name, currency)
        )


def _seed_categories(cur):
    cats = [
        ('powerbank', '移动电源', 'Power Bank', '便携式充电宝，含磁吸Qi2功能'),
        ('wireless_charger', '无线充电器', 'Wireless Charger', 'Qi/Qi2无线充电板、支架、多合一'),
        ('adapter_cable', '适配器与数据线', 'Adapter & Cable', 'USB充电头、GaN快充、数据线'),
        ('car_charger', '车充', 'Car Charger', '车载充电器，含伸缩线'),
        ('desktop_charger', '桌面充电站', 'Desktop Charger', '多口桌面充电站/充电坞'),
        ('energy_storage', '储能电源', 'Energy Storage', '户外储能电源、太阳能充电'),
    ]
    for slug, zh, en, desc in cats:
        cur.execute(
            "INSERT OR IGNORE INTO categories (slug, name_zh, name_en, description) VALUES (?,?,?,?)",
            (slug, zh, en, desc)
        )
