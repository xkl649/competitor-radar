# 竞品雷达 v1.0 — 使用说明

## 🚀 快速启动

### 1. 启动后端服务器
```bash
cd "C:/Users/10705/WorkBuddy/2026-06-23-19-49-18/competitor-radar"
PYTHONIOENCODING=utf-8 C:/Users/10705/.workbuddy/binaries/python/envs/competitor-radar/Scripts/python app.py
```

### 2. 访问前端页面
打开浏览器访问：**http://localhost:8765**

---

## 📊 功能概览

### 1. 数据总览
- 竞品总数、监测品牌数、平均评分、Qi2产品数
- 按品类和区域统计

### 2. 品类管理（6大品类）
- 🔋 移动电源 (Power Bank)
- 📱 无线充电器 (Wireless Charger)
- 🔌 适配器与数据线 (Adapter & Cable)
- 🚗 车充 (Car Charger)
- 🖥 桌面充电站 (Desktop Charger)
- 🏠 储能电源 (Energy Storage)

### 3. 区域切换
- 🌍 全部市场
- 🇪🇺 欧洲市场 (EU)
- 🇺🇸 北美市场 (NA)

### 4. 竞品列表
- 支持按品牌、产品名搜索
- 支持按价格、评分排序
- 显示：品牌、产品名、品类、区域、价格、评分、容量、功率、技术特性

### 5. 数据可视化
- 品类分布饼图
- 品牌竞品数量Top 10
- 价格 vs 评分散点图
- 技术特性分布（Qi2 / GaN / 无线）

### 6. INIU机会矩阵
- 🔴 P0 — 立即行动
- 🟠 P1 — 季度内启动
- 🔵 P2 — 战略储备

### 7. 数据采集控制台
- 触发自动采集任务
- 查看采集URL列表
- 查看采集日志

---

## 🔧 API端点

| 端点 | 功能 |
|------|------|
| `GET /api/health` | 健康检查 |
| `GET /api/categories` | 获取所有品类 |
| `GET /api/regions` | 获取所有区域 |
| `GET /api/products` | 查询产品（支持过滤） |
| `GET /api/stats/overview` | 统计总览 |
| `GET /api/brands/compare` | 品牌对比 |
| `GET /api/trends` | 趋势分析 |
| `GET /api/collection/urls` | 获取采集URL |
| `POST /api/collection/trigger` | 触发采集任务 |
| `GET /api/collection/logs` | 查看采集日志 |
| `POST /api/products/import` | 导入产品数据 |

---

## 📦 项目结构

```
competitor-radar/
├── app.py                  # Flask主应用
├── db/
│   └── schema.py         # 数据库Schema
├── collectors/
│   ├── eu_amazon.py     # 欧洲Amazon采集器
│   ├── na_aggregator.py # 北美采集器
│   └── collection_helper.py  # 采集助手
├── static/
│   └── index.html       # 前端页面
├── data/
│   └── competiors.db   # SQLite数据库
├── seed.py               # 种子数据
└── README.md            # 使用说明
```

---

## 🎯 下一步计划

### Phase 1: 欧洲数据管道 (1-2周)
- [ ] 完善Amazon.de/.pl/.es/.it/.fr采集
- [ ] 自动化定时采集
- [ ] 数据质量检测

### Phase 2: 北美API突破 (2-3周)
- [ ] 接入Amazon PA-API
- [ ] 集成Keepa价格追踪
- [ ] 聚合站数据抓取

### Phase 3: 实时竞品雷达 (4-6周)
- [ ] 实时监控新上架产品
- [ ] 价格变动预警
- [ ] 竞品动态推送
- [ ] 报告自动生成

---

## 📝 技术栈

- **后端**: Python 3.13 + Flask 3.1 + Flask-CORS
- **数据库**: SQLite 3
- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **图表**: Chart.js 4.4
- **采集**: WebFetch (AI Agent) + 聚合站

---

## ⚡ 当前状态

- ✅ 数据库已初始化（120条种子数据）
- ✅ 后端API全部可用
- ✅ 前端页面已就绪
- ✅ 6大品类全覆盖
- ✅ 欧洲/北美双市场支持
- ⏳ 实时数据采集（待完善）

---

**开发者**: WorkBuddy AI  
**版本**: v1.0.0  
**最后更新**: 2026-06-24
