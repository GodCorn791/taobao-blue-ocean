#!/usr/bin/env python3
"""
蓝海猎手 — 演示脚本
展示完整的蓝海分析流程。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.keyword_hunter import KeywordHunter
from src.competition import CompetitionAnalyzer
from src.product_hunter import ProductHunter
from src.report import ReportGenerator


def demo_keyword_hunting():
    """演示：从种子词挖掘蓝海词"""
    print("=" * 60)
    print("  🔍 演示 1: 蓝海词挖掘")
    print("=" * 60)
    
    hunter = KeywordHunter()
    results = hunter.hunt(seed="桌面收纳", depth=2, top=10)
    
    print(f"\n{'排名':<4} {'关键词':<25} {'蓝海指数':<10} {'等级':<8}")
    print("-" * 55)
    for i, kw in enumerate(results, 1):
        level_map = {'deep_blue': '🟢 深蓝', 'light_blue': '🔵 浅蓝', 
                     'blue_green': '🟡 蓝绿', 'red_ocean': '🔴 红海'}
        level = level_map.get(kw['level'], '❓')
        print(f"{i:<4} {kw['keyword']:<25} {kw['blue_ocean_score']:<10.1f} {level}")
    
    return results


def demo_competition_analysis():
    """演示：竞争度分析"""
    print("\n" + "=" * 60)
    print("  📊 演示 2: 竞争度分析")
    print("=" * 60)
    
    analyzer = CompetitionAnalyzer()
    keywords = ['手机壳', '桌面收纳盒 学生宿舍', '宠物自动喂食器']
    
    for kw in keywords:
        result = analyzer.analyze(kw)
        print(f"\n  🔑 {kw}")
        print(f"     蓝海指数: {result['blue_ocean_score']:.1f}")
        print(f"     搜索量: {result['search_volume']:,} | 卖家数: {result['seller_count']:,}")
        print(f"     判断: {result['verdict']}")


def demo_product_hunting():
    """演示：蓝海品发现"""
    print("\n" + "=" * 60)
    print("  🏷️ 演示 3: 蓝海品发现")
    print("=" * 60)
    
    hunter = ProductHunter()
    products = hunter.find_products("桌面收纳盒", top=5)
    
    print(f"\n{'排名':<4} {'商品':<20} {'成本':<8} {'售价':<8} {'利润率':<8} {'综合分':<8}")
    print("-" * 60)
    for i, p in enumerate(products, 1):
        margin = (p['price'] - p['cost']) / p['price'] * 100
        print(f"{i:<4} {p['name']:<20} ¥{p['cost']:<6} ¥{p['price']:<6} {margin:.0f}%{'':<4} {p['total_score']:.1f}")


def demo_report():
    """演示：生成报告"""
    print("\n" + "=" * 60)
    print("  📋 演示 4: 生成蓝海报告")
    print("=" * 60)
    
    generator = ReportGenerator()
    report = generator.generate(output='examples/blue_ocean_report.html')
    print(f"\n  ✅ HTML 报告已生成: {report['path']}")


if __name__ == '__main__':
    print("\n🌊 淘宝蓝海猎手 — 功能演示\n")
    
    demo_keyword_hunting()
    demo_competition_analysis()
    demo_product_hunting()
    demo_report()
    
    print("\n" + "=" * 60)
    print("  ✅ 演示完成！")
    print("=" * 60)
