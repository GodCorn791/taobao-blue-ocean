"""
竞争度分析器
评估关键词的竞争激烈程度，计算蓝海指数。
"""

import random
import hashlib
from typing import Dict
from src.config import config


class CompetitionAnalyzer:
    """关键词竞争度分析器"""
    
    def analyze(self, keyword: str) -> Dict:
        """
        分析关键词的竞争状况，计算蓝海指数
        
        Returns:
            包含完整竞争分析数据的字典
        """
        # 获取多维度数据
        search_data = self._get_search_volume(keyword)
        seller_data = self._get_seller_data(keyword)
        market_data = self._get_market_data(keyword)
        
        # 计算蓝海指数
        score = self._calc_blue_ocean_score(
            search_volume=search_data['volume'],
            conversion_rate=search_data['conversion'],
            seller_count=seller_data['count'],
            top_concentration=seller_data['top_concentration'],
            ad_ratio=market_data['ad_ratio'],
        )
        
        return {
            'keyword': keyword,
            'blue_ocean_score': score,
            'search_volume': search_data['volume'],
            'seller_count': seller_data['count'],
            'top_concentration': seller_data['top_concentration'],
            'ad_ratio': market_data['ad_ratio'],
            'conversion_rate': search_data['conversion'],
            'avg_price': market_data['avg_price'],
            'verdict': self._generate_verdict(score, search_data, seller_data, market_data),
        }
    
    def _calc_blue_ocean_score(self, search_volume, conversion_rate, seller_count, 
                                top_concentration, ad_ratio) -> float:
        """
        蓝海指数计算公式
        
        蓝海指数 = (搜索量 × 转化率) / (卖家数 × 头部集中度 × 广告占比)
        
        分数越高 = 需求大 + 竞争小 = 蓝海
        """
        # 需求侧得分 (搜索量 + 转化率)
        demand_score = min(search_volume / 10000, 1.0) * 50 + conversion_rate * 100
        
        # 供给侧得分 (卖家数 + 集中度 + 广告) — 越低越好
        supply_penalty = (
            min(seller_count / 10000, 1.0) * 30 +
            top_concentration * 40 +
            ad_ratio * 30
        )
        
        # 综合得分
        score = demand_score * (1 - supply_penalty / 100)
        
        return max(0, min(100, score))
    
    def _get_search_volume(self, keyword: str) -> Dict:
        """获取搜索量数据（模拟）"""
        # 基于关键词哈希生成稳定的模拟数据
        h = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        
        # 短词搜索量高，长尾词搜索量低
        base_volume = max(100, 50000 // max(len(keyword), 2))
        volume = int(base_volume * (0.5 + (h % 100) / 100))
        
        # 转化率：一般 1%-5%
        conversion = 0.01 + (h % 40) / 1000
        
        return {'volume': volume, 'conversion': round(conversion, 4)}
    
    def _get_seller_data(self, keyword: str) -> Dict:
        """获取卖家竞争数据（模拟）"""
        h = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        
        # 卖家数：蓝海词卖家少，红海词卖家多
        seller_count = int(500 + (h % 9500))
        
        # 头部集中度：前10名销量占比 (0.1 = 分散, 0.9 = 集中)
        top_concentration = round(0.1 + (h % 80) / 100, 2)
        
        return {'count': seller_count, 'top_concentration': top_concentration}
    
    def _get_market_data(self, keyword: str) -> Dict:
        """获取市场数据（模拟）"""
        h = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        
        # 广告占比
        ad_ratio = round(0.05 + (h % 50) / 100, 2)
        
        # 平均客单价
        avg_price = 10 + (h % 490)
        
        return {'ad_ratio': ad_ratio, 'avg_price': avg_price}
    
    def _generate_verdict(self, score, search_data, seller_data, market_data) -> str:
        """生成智能判断建议"""
        if score > 80:
            return (f"🟢 强烈推荐！这是一个优质蓝海词。"
                    f"日均搜索 {search_data['volume']:,} 次，仅 {seller_data['count']:,} 个卖家竞争，"
                    f"头部集中度低 ({seller_data['top_concentration']:.0%})，入局门槛低。")
        elif score > 50:
            return (f"🔵 值得关注。搜索需求存在，竞争中等偏低。"
                    f"建议差异化切入，找到细分卖点。")
        elif score > 30:
            return (f"🟡 谨慎评估。竞争正在上升，"
                    f"头部集中度 {seller_data['top_concentration']:.0%}，需要有明显优势才能突围。")
        else:
            return (f"🔴 不建议进入。竞争激烈，"
                    f"已有 {seller_data['count']:,} 个卖家，头部效应明显，新卖家难以获得流量。")
