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
    commands[args.command](args)


if __name__ == '__main__':
    main()
