#!/usr/bin/env python3
"""
淘宝蓝海猎手 — CLI 入口
用法: python main.py <command> [options]
"""

import argparse
import json
import sys
from datetime import datetime

from src.keyword_hunter import KeywordHunter
from src.competition import CompetitionAnalyzer
from src.product_hunter import ProductHunter
from src.trend_monitor import TrendMonitor
from src.report import ReportGenerator
from src.skincare_selector import SkincareSelector


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
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
