"""
蓝海品发现器
从蓝海关键词匹配可售商品，评估利润空间和供应链可行性。
"""

import hashlib
from typing import List, Dict
from src.config import config


class ProductHunter:
    """蓝海商品发现器"""
    
    def find_products(self, keyword: str, top: int = 10) -> List[Dict]:
        """
        从蓝海关键词匹配可售商品
        
        Args:
            keyword: 蓝海关键词
            top: 返回前N个商品
            
        Returns:
            按综合得分排序的商品列表
        """
        products = self._generate_product_candidates(keyword)
        
        for p in products:
            p['profit_score'] = self._calc_profit_score(p)
            p['supply_score'] = self._calc_supply_score(p)
            p['total_score'] = p['profit_score'] * 0.6 + p['supply_score'] * 0.4
        
        products.sort(key=lambda x: x['total_score'], reverse=True)
        return products[:top]
    
    def _generate_product_candidates(self, keyword: str) -> List[Dict]:
        """生成候选商品（模拟）"""
        h = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        
        # 商品类型模板
        product_types = [
            {'name': f'{keyword} 基础款', 'cost': 5 + h % 15, 'price': 15 + h % 35, 'category': '标品'},
            {'name': f'{keyword} 升级版', 'cost': 10 + h % 25, 'price': 30 + h % 60, 'category': '升级品'},
            {'name': f'{keyword} 套装组合', 'cost': 15 + h % 30, 'price': 45 + h % 80, 'category': '套装'},
            {'name': f'创意{keyword}', 'cost': 8 + h % 20, 'price': 25 + h % 50, 'category': '创意品'},
            {'name': f'便携{keyword}', 'cost': 3 + h % 10, 'price': 12 + h % 25, 'category': '便携品'},
        ]
        
        return product_types
    
    def _calc_profit_score(self, product: Dict) -> float:
        """计算利润空间得分 (0-100)"""
        margin = (product['price'] - product['cost']) / product['price']
        # 毛利率 > 60% 得分高
        return min(100, margin * 150)
    
    def _calc_supply_score(self, product: Dict) -> float:
        """计算供应链可行性得分 (0-100)"""
        h = int(hashlib.md5(product['name'].encode()).hexdigest()[:8], 16)
        # 模拟：标品供应链成熟，创意品供应链难
        base_score = {
            '标品': 85, '升级品': 70, '套装': 60, '创意品': 50, '便携品': 80
        }.get(product['category'], 60)
        
        return base_score + (h % 20) - 10
