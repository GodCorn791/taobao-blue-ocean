"""
套装组合策略器
计算最优的套装组合，提升客单价和利润率。
这是"单品利润低但套装赚大钱"的核心策略。
"""

from typing import Dict, List
import math


class ComboBuilder:
    """套装组合策略器"""

    def suggest_combos(self, products: List[Dict], target_profit: float = 40) -> List[Dict]:
        """
        为商品列表推荐最优套装组合

        Args:
            products: 商品列表
            target_profit: 目标套装利润

        Returns:
            按利润排序的套装推荐
        """
        combos = []

        # 1. 同品类多件装
        for p in products:
            combo = self._same_category_combo(p)
            if combo["net_profit"] >= target_profit:
                combos.append(combo)

        # 2. 跨品类搭配
        if len(products) >= 2:
            for i in range(len(products)):
                for j in range(i + 1, len(products)):
                    combo = self._cross_category_combo(products[i], products[j])
                    if combo["net_profit"] >= target_profit:
                        combos.append(combo)

        # 3. 全品类套装
        if len(products) >= 3:
            combo = self._full_set_combo(products)
            if combo["net_profit"] >= target_profit:
                combos.append(combo)

        combos.sort(key=lambda x: x["net_profit"], reverse=True)
        return combos

    def _same_category_combo(self, product: Dict) -> Dict:
        """同品类多件装（如：身体乳x2）"""
        cost = product.get("cost", 0)
        single_price = product.get("sell_price", 39.9)
        name = product.get("name", "")

        # 两件装定价：单件价 × 1.7（打85折的感觉）
        combo_price = math.ceil(single_price * 1.7 / 10) * 10 - 0.1
        total_cost = cost * 2 + 4 + 2 + (combo_price * 0.05)  # 快递+包装+平台
        net_profit = combo_price - total_cost

        return {
            "type": "同品类多件装",
            "name": f"{name} 2件装",
            "products": [name, name],
            "combo_price": combo_price,
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "margin": round(net_profit / combo_price, 4),
            "savings": round(single_price * 2 - combo_price, 2),
            "marketing_text": f"买2件省¥{single_price * 2 - combo_price:.0f}，自用囤货都划算",
        }

    def _cross_category_combo(self, product_a: Dict, product_b: Dict) -> Dict:
        """跨品类搭配（如：面膜+精华液）"""
        cost_a = product_a.get("cost", 0)
        cost_b = product_b.get("cost", 0)
        price_a = product_a.get("sell_price", 39.9)
        price_b = product_b.get("sell_price", 39.9)
        name_a = product_a.get("name", "商品A")
        name_b = product_b.get("name", "商品B")

        # 搭配套定价：总价的85%
        total_single = price_a + price_b
        combo_price = math.ceil(total_single * 0.85 / 10) * 10 - 0.1
        total_cost = cost_a + cost_b + 4 + 2 + (combo_price * 0.05)
        net_profit = combo_price - total_cost

        # 搭配合理性判断
        category_a = product_a.get("category", "")
        category_b = product_b.get("category", "")
        match_score = self._calc_match_score(category_a, category_b)

        return {
            "type": "跨品类搭配",
            "name": f"{name_a} + {name_b} 护肤套装",
            "products": [name_a, name_b],
            "combo_price": combo_price,
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "margin": round(net_profit / combo_price, 4),
            "savings": round(total_single - combo_price, 2),
            "match_score": match_score,
            "marketing_text": f"搭配购买省¥{total_single - combo_price:.0f}，一步到位护肤套装",
        }

    def _full_set_combo(self, products: List[Dict]) -> Dict:
        """全品类套装（洁面+水+乳等）"""
        total_cost_price = sum(p.get("cost", 0) for p in products)
        total_single_price = sum(p.get("sell_price", 39.9) for p in products)
        names = [p.get("name", "") for p in products]

        # 套装定价：总价的75-80%
        combo_price = math.ceil(total_single_price * 0.78 / 10) * 10 - 0.1
        total_cost = total_cost_price + 5 + 3 + (combo_price * 0.05)
        net_profit = combo_price - total_cost

        return {
            "type": "全品类套装",
            "name": f"{' + '.join(names[:3])} 全套护肤",
            "products": names,
            "combo_price": combo_price,
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "margin": round(net_profit / combo_price, 4),
            "savings": round(total_single_price - combo_price, 2),
            "marketing_text": f"全套护肤省¥{total_single_price - combo_price:.0f}，一次配齐不用东拼西凑",
        }

    def _calc_match_score(self, cat_a: str, cat_b: str) -> int:
        """计算两个品类的搭配合理性（0-100）"""
        good_combos = {
            frozenset({"洁面", "爽肤水"}): 95,
            frozenset({"爽肤水", "乳液"}): 95,
            frozenset({"洁面", "乳液"}): 90,
            frozenset({"精华液", "面膜"}): 90,
            frozenset({"精华液", "乳液"}): 85,
            frozenset({"面膜", "爽肤水"}): 85,
            frozenset({"身体乳", "护手霜"}): 80,
            frozenset({"润唇膏", "护手霜"}): 75,
            frozenset({"身体乳", "润唇膏"}): 70,
        }
        key = frozenset({cat_a, cat_b})
        return good_combos.get(key, 60)
