#!/usr/bin/env python3
"""
淘宝蓝海猎手 — CLI 入口
用法: python main.py <command> [options]
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict

from src.keyword_hunter import KeywordHunter
from src.competition import CompetitionAnalyzer
from src.product_hunter import ProductHunter
from src.trend_monitor import TrendMonitor
from src.report import ReportGenerator
from src.skincare_selector import SkincareSelector
from src.listing_optimizer import ListingOptimizer
from src.launch_checklist import LaunchChecklist
from src.combo_builder import ComboBuilder
from src.seasonal_calendar import SeasonalCalendar
from src.roi_calculator import ROICalculator
from src.supplier_tracker import SupplierTracker


def cmd_hunt(args):
    """从种子词挖掘蓝海关键词"""
    hunter = KeywordHunter()
    print(f"\n🔍 从种子词「{args.seed}」挖掘蓝海词（深度={args.depth}）...\n")
    results = hunter.hunt(seed=args.seed, depth=args.depth, top=args.top or 20)
    
    print(f"{'排名':<4} {'关键词':<25} {'蓝海指数':<10} {'等级':<8} {'搜索量':<10} {'卖家数':<10}")
    print("-" * 75)
    for i, kw in enumerate(results, 1):
        level = _level_label(kw['blue_ocean_score'])
        print(f"{i:<4} {kw['keyword']:<25} {kw['blue_ocean_score']:<10.1f} {level:<8} {kw['search_volume']:<10} {kw['seller_count']:<10}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 结果已保存: {args.output}")


def cmd_analyze(args):
    """分析单个关键词的蓝海指数"""
    analyzer = CompetitionAnalyzer()
    print(f"\n📊 分析关键词「{args.keyword}」...\n")
    result = analyzer.analyze(args.keyword)
    
    print(f"  关键词: {result['keyword']}")
    print(f"  蓝海指数: {result['blue_ocean_score']:.1f} {_level_label(result['blue_ocean_score'])}")
    print(f"  日均搜索量: {result['search_volume']:,}")
    print(f"  竞争卖家数: {result['seller_count']:,}")
    print(f"  头部集中度: {result['top_concentration']:.1%}")
    print(f"  广告占比: {result['ad_ratio']:.1%}")
    print(f"  预估转化率: {result['conversion_rate']:.2%}")
    print(f"  平均客单价: ¥{result['avg_price']:.0f}")
    print(f"\n  💡 判断: {result['verdict']}")


def cmd_scan(args):
    """批量扫描品类下的蓝海机会"""
    hunter = KeywordHunter()
    analyzer = CompetitionAnalyzer()
    
    print(f"\n🌊 扫描品类「{args.category}」的蓝海机会（Top {args.top}）...\n")
    
    # Step 1: 获取品类关键词
    keywords = hunter.get_category_keywords(args.category, limit=args.top * 3)
    
    # Step 2: 批量分析
    results = []
    for kw in keywords:
        result = analyzer.analyze(kw)
        results.append(result)
    
    # Step 3: 按蓝海指数排序
    results.sort(key=lambda x: x['blue_ocean_score'], reverse=True)
    results = results[:args.top]
    
    print(f"{'排名':<4} {'关键词':<25} {'蓝海指数':<10} {'等级':<8} {'搜索量':<10} {'客单价':<8}")
    print("-" * 75)
    for i, r in enumerate(results, 1):
        level = _level_label(r['blue_ocean_score'])
        print(f"{i:<4} {r['keyword']:<25} {r['blue_ocean_score']:<10.1f} {level:<8} {r['search_volume']:<10} ¥{r['avg_price']:<7.0f}")


def cmd_monitor(args):
    """持续监控蓝海词变化"""
    monitor = TrendMonitor()
    
    if args.keywords:
        with open(args.keywords, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    else:
        keywords = args.keyword_list or []
    
    if not keywords:
        print("❌ 请提供关键词列表（--keywords 文件 或 --keyword-list）")
        return
    
    print(f"\n📈 开始监控 {len(keywords)} 个关键词（间隔: {args.interval}）...\n")
    monitor.start(keywords=keywords, interval=args.interval, callback=_on_trend_change)


def cmd_report(args):
    """生成完整蓝海报告"""
    generator = ReportGenerator()
    print(f"\n📋 生成蓝海分析报告...\n")
    report = generator.generate(output=args.output or 'report.html')
    print(f"✅ 报告已生成: {report['path']}")


def cmd_skincare_scan(args):
    """扫描护肤品品类的合规蓝海选品"""
    selector = SkincareSelector(
        target_profit_min=args.profit_min,
        target_profit_max=args.profit_max,
    )
    print(f"\n🧴 扫描护肤品品类「{args.category}」...")
    print(f"   目标利润: ¥{args.profit_min}-{args.profit_max}/单\n")

    results = selector.scan_category(args.category, top=args.top)

    if not results:
        print("  ❌ 未找到符合条件的商品（利润未达标或无合规商品）")
        return
    if results[0].get("error"):
        print(f"  ❌ {results[0].get('error')}")
        return

    # 打印表格
    print(f"{'排名':<4} {'商品':<25} {'拿货':<7} {'售价':<7} {'净利':<7} {'合规':<5} {'建议':<20}")
    print("-" * 100)
    for i, r in enumerate(results, 1):
        compliance_icon = "✅" if r["pass_compliance"] else "❌"
        rec_short = r["recommendation"][:18] + ".." if len(r["recommendation"]) > 20 else r["recommendation"]
        print(f"{i:<4} {r['name']:<25} ¥{r['cost']:<5} ¥{r['sell_price']:<5} ¥{r['net_profit']:<5} {compliance_icon:<5} {rec_short}")

    # 打印详细信息
    print(f"\n{'='*60}")
    print("  📋 详细评估")
    print(f"{'='*60}")
    for i, r in enumerate(results[:3], 1):
        print(f"\n  [{i}] {r['name']}")
        print(f"      💰 利润: ¥{r['net_profit']} (利润率 {r['profit']['profit_rate']:.0%})")
        print(f"      🔒 合规评分: {r['compliance']['score']}/100")
        if r["compliance"]["issues"]:
            for issue in r["compliance"]["issues"]:
                icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "high" else "🔵"
                print(f"         {icon} {issue['detail']}")
        print(f"      🏭 供应商: {' / '.join(r['supplier']['tags'])}")
        print(f"      📦 上架风险: {r['listing_risk']['level']} {'可上架' if r['listing_risk']['can_list'] else '不建议上架'}")
        print(f"      💡 {r['recommendation']}")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 结果已保存: {args.output}")


def cmd_skincare_check(args):
    """检查单个护肤品的合规性和利润"""
    selector = SkincareSelector(
        target_profit_min=args.profit_min,
        target_profit_max=args.profit_max,
    )

    # 解析宣称和成分
    claims = args.claims.split(",") if args.claims else []
    ingredients = args.ingredients.split(",") if args.ingredients else []

    product = {
        "name": args.name,
        "category": args.category,
        "cost": args.cost,
        "sell_price": args.price,
        "claims": claims,
        "ingredients": ingredients,
        "filing_number": args.filing,
        "production_license": args.license,
    }

    result = selector.check_product(product)

    print(f"\n🔍 商品合规检查: {args.name}")
    print(f"{'='*50}")
    print(f"  品类: {args.category}")
    print(f"  拿货价: ¥{args.cost} → 售价: ¥{args.price}")
    print(f"  净利润: ¥{result['net_profit']} ({'✅ 达标' if result['profit']['meets_target'] else '❌ 未达标'})")
    print(f"  合规评分: {result['compliance']['score']}/100")

    if result["compliance"]["issues"]:
        print(f"\n  ⚠️  合规问题:")
        for issue in result["compliance"]["issues"]:
            icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "high" else "🔵"
            print(f"    {icon} {issue['detail']}")
            print(f"       → 修复建议: {issue['fix']}")
    else:
        print(f"\n  ✅ 合规检查通过，无问题")

    print(f"\n  📦 上架风险: {result['listing_risk']['level']}")
    if result["listing_risk"]["factors"]:
        for factor in result["listing_risk"]["factors"]:
            print(f"    ⚠️  {factor}")

    print(f"\n  💡 综合建议: {result['recommendation']}")


def cmd_skincare_categories(args):
    """列出所有支持的护肤品品类"""
    selector = SkincareSelector()
    categories = selector.list_categories()

    print(f"\n🧴 支持的护肤品品类 ({len(categories)} 个)")
    print(f"{'='*70}")
    print(f"{'品类':<10} {'风险等级':<10} {'需特证':<8} {'允许宣称':<20} {'禁止宣称':<20}")
    print("-" * 70)
    for c in categories:
        risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(c["risk_level"], "❓")
        cert = "是" if c["needs_cert"] else "否"
        allowed = ", ".join(c["allowed_claims"][:3]) or "无"
        forbidden = ", ".join(c["forbidden_claims"][:3]) or "无"
        print(f"{c['category']:<10} {risk_icon} {c['risk_level']:<8} {cert:<8} {allowed:<20} {forbidden:<20}")


def cmd_listing(args):
    """生成商品上架方案"""
    optimizer = ListingOptimizer()

    # 解析参数
    ingredients = args.ingredients.split(",") if args.ingredients else []

    product = {
        "name": args.name,
        "category": args.category,
        "cost": args.cost,
        "sell_price": args.price,
        "ingredients": ingredients,
        "target_audience": args.audience or "年轻女性",
    }

    result = optimizer.generate_listing(product)

    print(f"\n📝 商品上架方案: {args.name}")
    print(f"{'='*60}")
    print(f"\n  📌 推荐标题:")
    print(f"     {result.title}")
    print(f"\n  💬 副标题:")
    print(f"     {result.subtitle}")
    print(f"\n  ✨ 卖点 ({len(result.selling_points)} 个):")
    for i, sp in enumerate(result.selling_points, 1):
        print(f"     {i}. {sp}")
    print(f"\n  💰 定价策略:")
    for k, v in result.price_strategy["strategy"].items():
        print(f"     {k}: {v}")
    print(f"\n  📦 SKU 建议:")
    for sku in result.price_strategy["sku建议"]:
        print(f"     • {sku}")
    print(f"\n  📸 主图建议:")
    for tip in result.main_image_tips:
        print(f"     • {tip}")
    print(f"\n  📋 详情页结构:")
    for sec in result.detail_sections:
        print(f"     [{sec['section']}] {sec['content']}")


def cmd_checklist(args):
    """执行上架前检查"""
    checklist = LaunchChecklist()

    product = {
        "name": args.name,
        "category": args.category,
        "cost": args.cost,
        "sell_price": args.price,
        "filing_number": args.filing,
        "production_license": args.license,
        "ingredients": args.ingredients.split(",") if args.ingredients else [],
        "claims": args.claims.split(",") if args.claims else [],
        "image_count": args.images or 0,
        "has_detail": args.detail,
        "stock": args.stock or 0,
    }

    result = checklist.check(product)

    print(f"\n✅ 上架检查清单: {args.name}")
    print(f"{'='*60}")
    print(f"\n  总评: {result['summary']}")
    print(f"  通过: {result['passed']}/{result['total']} | 评分: {result['score']}/100")
    print(f"  可上架: {'是' if result['can_launch'] else '否'}")

    # 按优先级分组显示
    for priority in ["critical", "high", "medium", "low"]:
        priority_items = [i for i in result["items"] if i.priority == priority]
        if not priority_items:
            continue

        priority_label = {"critical": "🔴 关键项", "high": "🟠 高优先级", "medium": "🟡 中优先级", "low": "🔵 低优先级"}
        print(f"\n  {priority_label[priority]}:")
        for item in priority_items:
            icon = "✅" if item.passed else "❌"
            print(f"    {icon} {item.name}: {item.detail}")
            if not item.passed and item.fix:
                print(f"       → 修复: {item.fix}")


def cmd_combo(args):
    """生成套装组合策略"""
    builder = ComboBuilder()

    # 构建商品列表
    products = []
    for item in args.products:
        parts = item.split(":")
        if len(parts) >= 3:
            products.append({
                "name": parts[0],
                "category": parts[1],
                "cost": float(parts[2]),
                "sell_price": float(parts[3]) if len(parts) > 3 else 39.9,
            })

    if len(products) < 2:
        print("❌ 至少需要2个商品来生成套装组合")
        print("   用法: --products '商品名:品类:成本:售价' '商品名:品类:成本:售价'")
        return

    combos = builder.suggest_combos(products, target_profit=args.profit or 40)

    print(f"\n🎁 套装组合策略 ({len(products)} 个商品)")
    print(f"{'='*60}")

    for i, combo in enumerate(combos, 1):
        print(f"\n  [{i}] {combo['type']}: {combo['name']}")
        print(f"      💰 套装价: ¥{combo['combo_price']}")
        print(f"      📦 总成本: ¥{combo['total_cost']}")
        print(f"      💵 净利润: ¥{combo['net_profit']} (利润率 {combo['margin']:.0%})")
        print(f"      🏷️ 买家省: ¥{combo['savings']}")
        if "match_score" in combo:
            print(f"      🎯 搭配度: {combo['match_score']}/100")
        print(f"      📣 营销文案: {combo['marketing_text']}")


def cmd_season(args):
    """查看季节选品日历"""
    calendar = SeasonalCalendar()

    if args.month:
        strategy = calendar.get_month(args.month)
        if not strategy:
            print(f"❌ 无效月份: {args.month}")
            return
        _print_month_strategy(strategy)
    elif args.category:
        months = calendar.get_category_peak_months(args.category)
        print(f"\n📅 「{args.category}」旺季月份: {', '.join(f'{m}月' for m in months)}")
        for m in months:
            s = calendar.get_month(m)
            print(f"\n  📌 {m}月 — {s['name']}")
            print(f"     流量高峰: {s['traffic_peak']}")
            for action in s["action"][:2]:
                print(f"     • {action}")
    else:
        overview = calendar.get_year_overview()
        print(f"\n📅 护肤品全年选品日历")
        print(f"{'='*70}")
        for item in overview:
            cats = ", ".join(item["hot_categories"][:3])
            print(f"  {item['month']:>2}月 | {item['name']:<20} | 热门品类: {cats}")
        print(f"\n💡 用 --month N 查看具体月份策略，用 --category 品类 查看旺季")


def _print_month_strategy(strategy: Dict):
    """打印单月策略详情"""
    print(f"\n📅 {strategy['name']}")
    print(f"{'='*60}")
    print(f"  季节: {strategy['season']}")
    print(f"  热门品类: {', '.join(strategy['hot_categories'])}")
    print(f"  流量高峰: {strategy['traffic_peak']}")
    print(f"  原因: {strategy['reason']}")
    print(f"\n  📋 执行动作:")
    for action in strategy["action"]:
        print(f"     • {action}")
    print(f"\n  💰 利润提示: {strategy['profit_tip']}")


def cmd_roi(args):
    """计算投产比"""
    calculator = ROICalculator()

    if args.quick:
        # 快速估算
        result = calculator.quick_estimate(
            cost=args.cost,
            sell_price=args.price,
            daily_orders=args.orders or 10,
        )
        print(f"\n💰 快速利润估算")
        print(f"{'='*50}")
        print(f"  拿货价: ¥{args.cost} → 售价: ¥{args.price}")
        print(f"  单件利润: ¥{result['unit_profit']}")
        print(f"  日利润 (按{args.orders or 10}单): ¥{result['daily_profit']}")
        print(f"  月利润: ¥{result['monthly_profit']}")
        print(f"  年利润: ¥{result['annual_profit']}")
        print(f"  利润率: {result['margin']:.0%}")
        print(f"  保本单量: {result['break_even_orders']} 单/天")
    else:
        # 完整投产比计算
        result = calculator.calculate({
            "daily_budget": args.budget or 100,
            "cpc": args.cpc or 1.5,
            "conversion_rate": args.conversion or 0.03,
            "avg_order_value": args.price,
            "product_cost": args.cost,
            "express_fee": args.express or 3.5,
        })
        d = result["daily"]
        m = result["monthly"]
        b = result["breakeven"]

        print(f"\n💰 投产比分析")
        print(f"{'='*60}")
        print(f"  📊 日数据:")
        print(f"     广告花费: ¥{d['ad_spend']} | 展现: {d['impressions']:,} | 点击: {d['clicks']}")
        print(f"     订单: {d['orders']}单 | 营收: ¥{d['revenue']} | 利润: ¥{d['profit']}")
        print(f"     ROI: {d['roi']:.2f} | CPC: ¥{d['cpc']} | CPA: ¥{d['cpa']}")
        print(f"     转化率: {d['conversion_rate']:.2%}")
        print(f"\n  📈 月预估:")
        print(f"     广告花费: ¥{m['ad_spend']:,.0f} | 订单: {m['orders']}单 | 利润: ¥{m['profit']:,.0f}")
        print(f"\n  ⚖️ 盈亏平衡点:")
        print(f"     最低日单量: {b['min_orders']}单 | 最低日点击: {b['min_clicks']} | 最低日预算: ¥{b['min_budget']}")
        print(f"\n  💡 优化建议:")
        for s in result["suggestions"]:
            print(f"     {s}")


def cmd_supplier(args):
    """供应商管理"""
    tracker = SupplierTracker()

    if args.supplier_cmd == "add":
        result = tracker.add({
            "name": args.name,
            "platform": args.platform or "1688",
            "contact": args.contact or "",
            "category": args.category or "",
            "moq": args.moq or 5,
            "delivery_days": args.delivery or 3,
            "price_level": args.price_level or "中",
            "quality_score": args.quality or 70,
            "notes": args.notes or "",
        })
        print(f"\n  {result['message']}")

    elif args.supplier_cmd == "list":
        suppliers = tracker.list_all()
        if not suppliers:
            print("\n  📭 暂无供应商记录")
            return
        print(f"\n📋 供应商列表 ({len(suppliers)} 家)")
        print(f"{'='*70}")
        print(f"{'ID':<8} {'名称':<15} {'品类':<10} {'评分':<6} {'订单':<6} {'采购额':<10}")
        print("-" * 70)
        for s in suppliers:
            print(f"{s['id']:<8} {s['name']:<15} {s.get('category',''):<10} {s['rating']:<6} {s['orders']:<6} ¥{s['total_amount']:<9.0f}")

    elif args.supplier_cmd == "order":
        result = tracker.record_order(args.supplier_id, args.amount)
        if "error" in result:
            print(f"\n  ❌ {result['error']}")
        else:
            print(f"\n  ✅ 记录成功: {result['supplier']} | 总订单: {result['total_orders']} | 评分: {result['rating']}")

    elif args.supplier_cmd == "recommend":
        result = tracker.get_recommendation(args.category)
        if result:
            print(f"\n  🏆 推荐供应商: {result['name']} (评分: {result['rating']})")
            print(f"     平台: {result.get('platform', '')} | 起订量: {result.get('moq', '')} | 发货: {result.get('delivery_days', '')}天")
        else:
            print(f"\n  ❌ 品类「{args.category}」暂无推荐供应商")


def _level_label(score):
    if score > 80: return '🟢 深蓝'
    if score > 50: return '🔵 浅蓝'
    if score > 30: return '🟡 蓝绿'
    return '🔴 红海'


def _on_trend_change(keyword, old_score, new_score):
    change = new_score - old_score
    direction = '📈' if change > 0 else '📉'
    print(f"  {direction} {keyword}: {old_score:.1f} → {new_score:.1f} ({change:+.1f})")


def main():
    parser = argparse.ArgumentParser(description='🌊 淘宝蓝海猎手 — 蓝海词 & 蓝海品自动挖掘')
    sub = parser.add_subparsers(dest='command')

    # hunt
    p_hunt = sub.add_parser('hunt', help='从种子词挖掘蓝海关键词')
    p_hunt.add_argument('--seed', required=True, help='种子关键词')
    p_hunt.add_argument('--depth', type=int, default=2, help='扩展深度 (1-3)')
    p_hunt.add_argument('--top', type=int, default=20, help='返回数量')
    p_hunt.add_argument('--output', '-o', help='输出文件路径')

    # analyze
    p_analyze = sub.add_parser('analyze', help='分析单个关键词')
    p_analyze.add_argument('--keyword', required=True, help='关键词')

    # scan
    p_scan = sub.add_parser('scan', help='批量扫描品类')
    p_scan.add_argument('--category', required=True, help='品类名称')
    p_scan.add_argument('--top', type=int, default=50, help='返回数量')

    # monitor
    p_monitor = sub.add_parser('monitor', help='持续监控蓝海词')
    p_monitor.add_argument('--keywords', help='关键词文件路径')
    p_monitor.add_argument('--keyword-list', nargs='+', help='关键词列表')
    p_monitor.add_argument('--interval', default='daily', choices=['hourly', 'daily', 'weekly'])

    # report
    p_report = sub.add_parser('report', help='生成蓝海报告')
    p_report.add_argument('--output', '-o', help='输出路径')

    # skincare scan
    p_skincare = sub.add_parser('skincare', help='护肤品选品（合规+利润筛选）')
    skincare_sub = p_skincare.add_subparsers(dest='skincare_cmd')

    p_sk_scan = skincare_sub.add_parser('scan', help='扫描品类合规蓝海选品')
    p_sk_scan.add_argument('--category', required=True, help='品类（面膜/身体乳/护手霜/精华液/洁面/爽肤水/乳液/润唇膏/化妆棉/洗脸巾）')
    p_sk_scan.add_argument('--top', type=int, default=10, help='返回数量')
    p_sk_scan.add_argument('--profit-min', type=float, default=20, help='最低利润（元）')
    p_sk_scan.add_argument('--profit-max', type=float, default=30, help='最高利润（元）')
    p_sk_scan.add_argument('--output', '-o', help='输出文件路径')

    p_sk_check = skincare_sub.add_parser('check', help='检查单个商品合规性')
    p_sk_check.add_argument('--name', required=True, help='商品名称')
    p_sk_check.add_argument('--category', required=True, help='品类')
    p_sk_check.add_argument('--cost', type=float, required=True, help='拿货价（元）')
    p_sk_check.add_argument('--price', type=float, required=True, help='售价（元）')
    p_sk_check.add_argument('--claims', help='功效宣称（逗号分隔）')
    p_sk_check.add_argument('--ingredients', help='成分（逗号分隔）')
    p_sk_check.add_argument('--filing', help='备案编号')
    p_sk_check.add_argument('--license', help='生产许可证编号')
    p_sk_check.add_argument('--profit-min', type=float, default=20, help='最低利润')
    p_sk_check.add_argument('--profit-max', type=float, default=30, help='最高利润')

    p_sk_cat = skincare_sub.add_parser('categories', help='列出支持的品类')

    # listing - 上架方案生成
    p_listing = sub.add_parser('listing', help='生成商品上架方案（标题+卖点+定价）')
    p_listing.add_argument('--name', required=True, help='商品名称')
    p_listing.add_argument('--category', required=True, help='品类')
    p_listing.add_argument('--cost', type=float, required=True, help='拿货价（元）')
    p_listing.add_argument('--price', type=float, required=True, help='售价（元）')
    p_listing.add_argument('--ingredients', help='成分（逗号分隔）')
    p_listing.add_argument('--audience', help='目标人群（默认：年轻女性）')

    # checklist - 上架检查
    p_check = sub.add_parser('checklist', help='上架前检查清单')
    p_check.add_argument('--name', required=True, help='商品名称')
    p_check.add_argument('--category', required=True, help='品类')
    p_check.add_argument('--cost', type=float, required=True, help='拿货价')
    p_check.add_argument('--price', type=float, required=True, help='售价')
    p_check.add_argument('--filing', help='备案编号')
    p_check.add_argument('--license', help='生产许可证')
    p_check.add_argument('--ingredients', help='成分（逗号分隔）')
    p_check.add_argument('--claims', help='功效宣称（逗号分隔）')
    p_check.add_argument('--images', type=int, help='主图数量')
    p_check.add_argument('--detail', action='store_true', help='是否有详情页')
    p_check.add_argument('--stock', type=int, help='库存数量')

    # combo - 套装组合
    p_combo = sub.add_parser('combo', help='生成套装组合策略')
    p_combo.add_argument('--products', nargs='+', required=True, help='商品列表（格式: 名称:品类:成本:售价）')
    p_combo.add_argument('--profit', type=float, default=40, help='目标套装利润（元）')

    # season - 季节选品日历
    p_season = sub.add_parser('season', help='护肤品季节选品日历')
    p_season.add_argument('--month', type=int, help='查看指定月份(1-12)')
    p_season.add_argument('--category', help='查看某品类的旺季')

    # roi - 投产比计算
    p_roi = sub.add_parser('roi', help='投产比计算器')
    p_roi.add_argument('--cost', type=float, required=True, help='拿货价（元）')
    p_roi.add_argument('--price', type=float, required=True, help='售价（元）')
    p_roi.add_argument('--budget', type=float, help='日广告预算（元）')
    p_roi.add_argument('--cpc', type=float, help='单次点击成本（元）')
    p_roi.add_argument('--conversion', type=float, help='转化率')
    p_roi.add_argument('--express', type=float, help='快递费（元）')
    p_roi.add_argument('--orders', type=int, help='日单量（快速估算用）')
    p_roi.add_argument('--quick', action='store_true', help='快速估算模式')

    # supplier - 供应商管理
    p_supplier = sub.add_parser('supplier', help='供应商管理（添加/列表/记录采购）')
    supplier_sub = p_supplier.add_subparsers(dest='supplier_cmd')

    p_sup_add = supplier_sub.add_parser('add', help='添加供应商')
    p_sup_add.add_argument('--name', required=True, help='供应商名称')
    p_sup_add.add_argument('--platform', help='平台（1688/拼多多/线下）')
    p_sup_add.add_argument('--contact', help='联系方式')
    p_sup_add.add_argument('--category', help='主营品类')
    p_sup_add.add_argument('--moq', type=int, help='最小起订量')
    p_sup_add.add_argument('--delivery', type=int, help='发货天数')
    p_sup_add.add_argument('--price-level', choices=['低', '中', '高'], help='价格水平')
    p_sup_add.add_argument('--quality', type=int, help='质量评分(0-100)')
    p_sup_add.add_argument('--notes', help='备注')

    p_sup_list = supplier_sub.add_parser('list', help='列出所有供应商')

    p_sup_order = supplier_sub.add_parser('order', help='记录采购订单')
    p_sup_order.add_argument('--supplier-id', required=True, help='供应商ID')
    p_sup_order.add_argument('--amount', type=float, required=True, help='采购金额')

    p_sup_rec = supplier_sub.add_parser('recommend', help='获取品类推荐供应商')
    p_sup_rec.add_argument('--category', required=True, help='品类')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        'hunt': cmd_hunt,
        'analyze': cmd_analyze,
        'scan': cmd_scan,
        'monitor': cmd_monitor,
        'report': cmd_report,
        'listing': cmd_listing,
        'checklist': cmd_checklist,
        'combo': cmd_combo,
        'season': cmd_season,
        'roi': cmd_roi,
    }

    if args.command == 'skincare':
        skincare_commands = {
            'scan': cmd_skincare_scan,
            'check': cmd_skincare_check,
            'categories': cmd_skincare_categories,
        }
        if args.skincare_cmd:
            skincare_commands[args.skincare_cmd](args)
        else:
            p_skincare.print_help()
    elif args.command == 'supplier':
        cmd_supplier(args)
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
