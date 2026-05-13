# 🌊 淘宝蓝海猎手 — 蓝海词 & 蓝海品自动挖掘平台

> 基于 AI Agent 的淘宝蓝海市场分析工具，自动发现高搜索量、低竞争的蓝海关键词和蓝海商品。

[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 解决的核心痛点

淘宝卖家最大的困境：**红海品类打不过大卖家，蓝海品类找不到**。

- 🔴 **找词难**：手动用生意参谋翻关键词，一天看不了几个品类
- 🔴 **判断难**：搜出来一堆词，哪些是真蓝海、哪些是假需求，缺乏量化标准
- 🔴 **跟踪难**：好不容易找到蓝海，过两周就变红海了，缺乏持续监控
- 🔴 **选品难**：知道蓝海词，但对应什么商品能赚钱，还是得靠经验猜

**蓝海猎手** 通过 AI 分析 + 自动化数据采集，把蓝海发现效率提升 **10 倍**。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    🌊 蓝海猎手                           │
├─────────────┬─────────────┬─────────────┬───────────────┤
│  🔍 词猎手  │  📊 竞争分析 │  🏷️ 品猎手  │  📈 趋势监控  │
│  挖掘关键词  │  评估竞争度  │  发现蓝海品  │  持续追踪    │
├─────────────┴─────────────┴─────────────┴───────────────┤
│                   📋 蓝海报告生成器                      │
├─────────────────────────────────────────────────────────┤
│            🤖 AI Agent (OpenClaw / MiMo)                │
└─────────────────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 功能 | 核心算法 |
|------|------|---------|
| **词猎手** (KeywordHunter) | 从种子词扩展蓝海关键词 | 搜索量/竞争度比值排序 |
| **竞争分析** (CompetitionAnalyzer) | 评估关键词竞争激烈程度 | 卖家数、头部集中度、广告占比 |
| **品猎手** (ProductHunter) | 从蓝海词匹配可售商品 | 利润空间、供应链可行性评分 |
| **趋势监控** (TrendMonitor) | 持续追踪蓝海词变化 | 时间序列分析、拐点检测 |
| **报告生成** (ReportGenerator) | 输出可视化蓝海报告 | 多维评分矩阵 |
| **🧴 护肤品选品** (SkincareSelector) | 护肤品合规+利润筛选 | 合规检查、利润计算、供应商评估 |

---

## 🚀 快速开始

```bash
cd taobao-blue-ocean
pip install -r requirements.txt

# 从种子词挖掘蓝海词
python main.py hunt --seed "桌面收纳" --depth 3

# 分析特定关键词的蓝海指数
python main.py analyze --keyword "宿舍收纳盒 桌面"

# 批量分析品类
python main.py scan --category "家居日用" --top 50

# 持续监控蓝海词变化
python main.py monitor --keywords keywords.txt --interval daily

# 生成完整蓝海报告
python main.py report --output report.html
```

### 🧴 护肤品选品（合规 + 利润筛选）

```bash
# 列出支持的护肤品品类
python main.py skincare categories

# 扫描品类合规蓝海选品（利润>20元）
python main.py skincare scan --category "面膜" --profit-min 20

# 扫描身体乳品类
python main.py skincare scan --category "身体乳" --profit-min 20 --profit-max 30

# 检查单个商品的合规性和利润
python main.py skincare check \
  --name "烟酰胺身体乳" \
  --category "身体乳" \
  --cost 8 --price 45.9 \
  --claims "保湿,滋润" \
  --ingredients "烟酰胺,甘油" \
  --filing "粤G妆网备字2024001234" \
  --license "粤妆20240001"
```

---

## 📊 蓝海指数计算

核心公式：

```
蓝海指数 = (搜索量 × 转化率) / (卖家数 × 头部集中度 × 广告占比)
```

| 指标 | 权重 | 说明 |
|------|------|------|
| 搜索量 | 30% | 日均搜索次数，代表需求大小 |
| 转化率 | 20% | 搜索→购买的比例 |
| 卖家数 | 25% | 竞争对手数量（越少越好）|
| 头部集中度 | 15% | 前10名卖家占总销量比例（越低越好）|
| 广告占比 | 10% | 搜索结果中广告位比例（越低越好）|

### 蓝海等级划分

| 等级 | 蓝海指数 | 建议 |
|------|---------|------|
| 🟢 **深蓝海** | > 80 | 强烈推荐入局，竞争极低 |
| 🔵 **浅蓝海** | 50-80 | 值得关注，有一定机会 |
| 🟡 **蓝绿交界** | 30-50 | 谨慎评估，竞争正在上升 |
| 🔴 **红海** | < 30 | 不建议进入，竞争激烈 |

---

## 📁 项目结构

```
taobao-blue-ocean/
├── main.py                  # CLI 入口
├── requirements.txt
├── src/
│   ├── keyword_hunter.py    # 蓝海词挖掘引擎
│   ├── competition.py       # 竞争度分析
│   ├── product_hunter.py    # 蓝海品发现
│   ├── trend_monitor.py     # 趋势监控
│   ├── report.py            # 报告生成
│   ├── skincare_selector.py # 护肤品选品引擎（合规+利润）
│   └── config.py            # 配置管理
├── analyzers/
│   ├── blue_ocean_score.py  # 蓝海指数算法
│   ├── demand_analyzer.py   # 需求分析
│   └── supply_analyzer.py   # 供给分析
├── data/
│   └── sample_keywords.json # 示例数据
├── examples/
│   └── demo.py              # 演示脚本
└── docs/
    └── methodology.md       # 方法论说明
```

---

## 💡 使用场景

1. **选品调研**：输入一个品类，自动找出该品类下的蓝海细分市场
2. **关键词优化**：为已有商品找到竞争更低的长尾关键词
3. **市场监控**：持续追踪蓝海词变化，第一时间发现新机会
4. **竞品分析**：分析竞争对手的关键词布局，找到差异化切入点

---

## 📄 License

MIT License
