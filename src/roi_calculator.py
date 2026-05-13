"""
投产比计算器
算清楚花多少钱能赚多少钱，不做亏本生意。
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class ROIResult:
    """投产比结果"""
    ad_spend: float
    impressions: int
    clicks: int
    orders: int
    revenue: float
    cost_total: float
    profit: float
    roi: float
    cpc: float
    cpa: float
    conversion_rate: float


class ROICalculator:
    """投产比计算器"""

    def calculate(self, params: Dict) -> Dict:
        """
        计算投产比

        Args:
            params: {
                "daily_budget": 日预算(元),
                "cpc": 单次点击成本(元),
                "conversion_rate": 转化率,
                "avg_order_value": 客单价(元),
                "product_cost": 商品成本(元),
                "express_fee": 快递费(元),
                "platform_rate": 平台扣点,
            }

        Returns:
            完整的投产比分析
        """
        budget = params.get("daily_budget", 100)
        cpc = params.get("cpc", 1.5)
        conversion = params.get("conversion_rate", 0.03)
        aov = params.get("avg_order_value", 49.9)
        product_cost = params.get("product_cost", 10)
        express = params.get("express_fee", 3.5)
        platform_rate = params.get("platform_rate", 0.05)

        # 核心计算
        clicks = int(budget / cpc)
        impressions = int(clicks / 0.03)  # 假设3%点击率
        orders = int(clicks * conversion)
        revenue = orders * aov
        cost_total = orders * (product_cost + express + aov * platform_rate)
        profit = revenue - budget - cost_total
        roi = revenue / budget if budget > 0 else 0
        cpa = budget / orders if orders > 0 else 0

        # 盈亏平衡点
        breakeven_orders = budget / (aov - product_cost - express - aov * platform_rate)
        breakeven_clicks = int(breakeven_orders / conversion)

        # 优化建议
        suggestions = self._generate_suggestions(params, roi, profit, cpa)

        return {
            "daily": {
                "ad_spend": budget,
                "impressions": impressions,
                "clicks": clicks,
                "orders": orders,
                "revenue": round(revenue, 2),
                "cost_total": round(cost_total, 2),
                "profit": round(profit, 2),
                "roi": round(roi, 2),
                "cpc": cpc,
                "cpa": round(cpa, 2),
                "conversion_rate": conversion,
            },
            "monthly": {
                "ad_spend": budget * 30,
                "orders": orders * 30,
                "revenue": round(revenue * 30, 2),
                "profit": round(profit * 30, 2),
                "roi": round(roi, 2),
            },
            "breakeven": {
                "min_orders": int(breakeven_orders) + 1,
                "min_clicks": breakeven_clicks,
                "min_budget": round(breakeven_clicks * cpc, 2),
            },
            "suggestions": suggestions,
        }

    def quick_estimate(self, cost: float, sell_price: float, daily_orders: int = 10) -> Dict:
        """
        快速估算（不需要广告数据）

        Args:
            cost: 拿货价
            sell_price: 售价
            daily_orders: 预估日单量

        Returns:
            利润估算
        """
        express = 3.5
        packaging = 1.5
        platform_fee = sell_price * 0.05

        unit_profit = sell_price - cost - express - packaging - platform_fee
        daily_profit = unit_profit * daily_orders
        monthly_profit = daily_profit * 30

        return {
            "unit_profit": round(unit_profit, 2),
            "daily_profit": round(daily_profit, 2),
            "monthly_profit": round(monthly_profit, 2),
            "annual_profit": round(monthly_profit * 12, 2),
            "margin": round(unit_profit / sell_price, 4),
            "break_even_orders": max(1, int(100 / unit_profit)) if unit_profit > 0 else "亏损",
        }

    def _generate_suggestions(self, params: Dict, roi: float, profit: float, cpa: float) -> list:
        """生成优化建议"""
        suggestions = []

        if roi < 2:
            suggestions.append("⚠️ ROI低于2，广告成本过高，建议优化关键词或降低出价")

        if profit < 0:
            suggestions.append("🔴 亏损状态！必须提高客单价或降低成本，否则立即暂停投放")
        elif profit < 20:
            suggestions.append("🟡 利润偏低，建议：1)推套装提升客单价 2)找更低的快递费 3)优化转化率")

        if cpa > params.get("avg_order_value", 49.9) * 0.4:
            suggestions.append("⚠️ 获客成本过高，建议优化详情页和评价提升转化率")

        if params.get("conversion_rate", 0.03) < 0.02:
            suggestions.append("🟡 转化率低于2%，建议：1)优化主图 2)增加销量和评价 3)调整价格")

        if params.get("cpc", 1.5) > 2:
            suggestions.append("⚠️ 点击成本过高，建议：1)优化关键词质量分 2)使用长尾词 3)调整投放时段")

        if not suggestions:
            suggestions.append("✅ 投产比健康，保持当前策略")

        return suggestions
