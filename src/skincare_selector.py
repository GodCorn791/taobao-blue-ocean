"""
护肤品选品引擎
专注护肤品品类，集成1688货源筛选、合规检查、利润计算。
目标：筛选出可上架且利润>20-30元的护肤商品。
"""

import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ComplianceRule:
    """合规规则"""
    needs_special_cert: bool = False  # 是否需要特殊许可证
    allowed_claims: List[str] = None  # 允许的功效宣称
    forbidden_claims: List[str] = None  # 禁止的功效宣称
    risk_level: str = "low"  # low / medium / high


# 护肤品品类合规规则库
CATEGORY_RULES = {
    "身体乳": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["保湿", "滋润", "补水", "香氛", "嫩肤"],
        forbidden_claims=["美白", "祛斑", "紧致", "抗皱"],
        risk_level="low",
    ),
    "护手霜": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["保湿", "滋润", "防裂", "补水", "香氛"],
        forbidden_claims=["美白", "祛斑", "抗皱"],
        risk_level="low",
    ),
    "润唇膏": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["保湿", "滋润", "防裂", "补水", "修护"],
        forbidden_claims=["丰唇", "去唇纹"],
        risk_level="low",
    ),
    "面膜": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["补水", "保湿", "舒缓", "修护", "清洁"],
        forbidden_claims=["美白", "祛斑", "祛痘", "抗皱", "紧致"],
        risk_level="medium",
    ),
    "洁面": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["清洁", "控油", "保湿", "温和", "毛孔清洁"],
        forbidden_claims=["祛痘", "祛斑", "美白"],
        risk_level="low",
    ),
    "爽肤水": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["补水", "保湿", "舒缓", "收敛", "二次清洁"],
        forbidden_claims=["美白", "祛斑", "抗皱", "紧致"],
        risk_level="low",
    ),
    "乳液": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["保湿", "滋润", "补水", "修护", "舒缓"],
        forbidden_claims=["美白", "祛斑", "抗皱", "紧致"],
        risk_level="low",
    ),
    "精华液": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=["保湿", "补水", "修护", "舒缓", "维稳"],
        forbidden_claims=["美白", "祛斑", "抗皱", "紧致", "祛痘"],
        risk_level="medium",
    ),
    "化妆棉": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=[],
        forbidden_claims=[],
        risk_level="low",
    ),
    "洗脸巾": ComplianceRule(
        needs_special_cert=False,
        allowed_claims=[],
        forbidden_claims=[],
        risk_level="low",
    ),
}

# 违禁成分黑名单（部分）
BANNED_INGREDIENTS = [
    "氢醌", "汞", "铅", "砷", "甲醇", "甲醛",
    "糖皮质激素", "地塞米松", "氯倍他索丙酸酯",
    "氟轻松", "倍他米松", "氢化可的松",
]


class SkincareSelector:
    """护肤品选品引擎"""

    def __init__(self, target_profit_min: float = 20, target_profit_max: float = 30):
        self.target_profit_min = target_profit_min
        self.target_profit_max = target_profit_max

    def scan_category(self, category: str, top: int = 10) -> List[Dict]:
        """
        扫描指定护肤品品类，筛选合规且利润达标的商品

        Args:
            category: 品类名称（如"面膜"、"身体乳"）
            top: 返回前N个推荐

        Returns:
            按综合得分排序的选品推荐列表
        """
        rule = CATEGORY_RULES.get(category)
        if not rule:
            return [{"error": f"未收录品类「{category}」，支持的品类: {list(CATEGORY_RULES.keys())}"}]

        # 生成候选商品（模拟1688搜索结果）
        candidates = self._generate_candidates(category)

        # 逐个评估
        evaluated = []
        for product in candidates:
            result = self._evaluate_product(product, rule)
            if result["pass_compliance"] and result["net_profit"] >= self.target_profit_min:
                evaluated.append(result)

        # 按综合得分排序
        evaluated.sort(key=lambda x: x["total_score"], reverse=True)
        return evaluated[:top]

    def check_product(self, product_info: Dict) -> Dict:
        """
        检查单个商品的合规性和利润

        Args:
            product_info: {
                "name": "商品名",
                "category": "品类",
                "cost": 拿货价,
                "sell_price": 预计售价,
                "express_fee": 快递费,
                "claims": ["功效宣称1", "功效宣称2"],
                "ingredients": ["成分1", "成分2"],
            }

        Returns:
            完整的评估报告
        """
        category = product_info.get("category", "")
        rule = CATEGORY_RULES.get(category, ComplianceRule())

        return self._evaluate_product(product_info, rule)

    def list_categories(self) -> List[Dict]:
        """列出所有支持的品类及其合规要求"""
        result = []
        for name, rule in CATEGORY_RULES.items():
            result.append({
                "category": name,
                "risk_level": rule.risk_level,
                "needs_cert": rule.needs_special_cert,
                "allowed_claims": rule.allowed_claims,
                "forbidden_claims": rule.forbidden_claims,
            })
        return result

    def _evaluate_product(self, product: Dict, rule: ComplianceRule) -> Dict:
        """综合评估单个商品"""
        # 1. 合规检查
        compliance = self._check_compliance(product, rule)

        # 2. 利润计算
        profit = self._calc_profit(product)

        # 3. 1688供应商评估
        supplier = self._evaluate_supplier(product)

        # 4. 上架风险评估
        listing_risk = self._assess_listing_risk(product, rule, compliance)

        # 5. 综合得分
        total_score = self._calc_total_score(compliance, profit, supplier, listing_risk)

        return {
            "name": product.get("name", ""),
            "category": product.get("category", ""),
            "cost": product.get("cost", 0),
            "sell_price": product.get("sell_price", 0),
            "compliance": compliance,
            "profit": profit,
            "supplier": supplier,
            "listing_risk": listing_risk,
            "net_profit": profit["net_profit"],
            "total_score": total_score,
            "pass_compliance": compliance["pass"],
            "recommendation": self._generate_recommendation(
                compliance, profit, supplier, listing_risk, total_score
            ),
        }

    def _check_compliance(self, product: Dict, rule: ComplianceRule) -> Dict:
        """合规性检查"""
        issues = []
        claims = product.get("claims", [])
        ingredients = product.get("ingredients", [])

        # 检查功效宣称
        for claim in claims:
            if rule.forbidden_claims and claim in rule.forbidden_claims:
                issues.append({
                    "type": "forbidden_claim",
                    "severity": "critical",
                    "detail": f"功效宣称「{claim}」属于禁止项，需要特殊许可证",
                    "fix": f"移除「{claim}」宣称，或改为合规表述（如「{claim}」→「保湿」）",
                })

        # 检查违禁成分
        for ing in ingredients:
            if ing in BANNED_INGREDIENTS:
                issues.append({
                    "type": "banned_ingredient",
                    "severity": "critical",
                    "detail": f"成分「{ing}」为违禁成分",
                    "fix": "立即下架，该成分违反《化妆品安全技术规范》",
                })

        # 检查备案号
        if not product.get("filing_number"):
            issues.append({
                "type": "missing_filing",
                "severity": "high",
                "detail": "缺少化妆品备案编号",
                "fix": "向供应商索要备案编号，去国家药监局官网验证真伪",
            })

        # 检查生产许可证
        if not product.get("production_license"):
            issues.append({
                "type": "missing_license",
                "severity": "high",
                "detail": "缺少生产许可证编号",
                "fix": "确认供应商持有有效的《化妆品生产许可证》",
            })

        # 检查成分表
        if not ingredients:
            issues.append({
                "type": "missing_ingredients",
                "severity": "medium",
                "detail": "未提供成分表",
                "fix": "要求供应商提供完整的INCI成分表",
            })

        pass_all = not any(i["severity"] == "critical" for i in issues)
        score = max(0, 100 - len(issues) * 15)

        return {
            "pass": pass_all,
            "score": score,
            "issues": issues,
            "risk_level": rule.risk_level,
        }

    def _calc_profit(self, product: Dict) -> Dict:
        """利润计算"""
        cost = product.get("cost", 0)
        sell_price = product.get("sell_price", 0)
        express_fee = product.get("express_fee", 3.5)
        packaging_fee = product.get("packaging_fee", 1.5)
        platform_rate = 0.05  # 淘宝扣点约5%

        platform_fee = sell_price * platform_rate
        total_cost = cost + express_fee + packaging_fee + platform_fee
        net_profit = sell_price - total_cost
        profit_rate = net_profit / sell_price if sell_price > 0 else 0

        return {
            "cost": cost,
            "sell_price": sell_price,
            "express_fee": express_fee,
            "packaging_fee": packaging_fee,
            "platform_fee": round(platform_fee, 2),
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "profit_rate": round(profit_rate, 4),
            "meets_target": net_profit >= self.target_profit_min,
        }

    def _evaluate_supplier(self, product: Dict) -> Dict:
        """1688供应商评估"""
        score = 0
        tags = []

        # 模拟评估维度
        h = int(hashlib.md5(product.get("name", "").encode()).hexdigest()[:8], 16)

        is_verified = h % 3 != 0
        if is_verified:
            score += 30
            tags.append("实商家认证")

        has_samples = h % 4 != 0
        if has_samples:
            score += 20
            tags.append("支持拿样")

        moq = 2 + h % 8
        if moq <= 3:
            score += 25
            tags.append(f"低起订量({moq}件)")
        else:
            score += 10
            tags.append(f"起订量{moq}件")

        delivery_days = 1 + h % 5
        if delivery_days <= 2:
            score += 25
            tags.append("48h内发货")
        else:
            score += 10
            tags.append(f"{delivery_days}天发货")

        return {
            "score": min(100, score),
            "tags": tags,
            "moq": moq,
            "delivery_days": delivery_days,
            "is_verified": is_verified,
            "supports_samples": has_samples,
        }

    def _assess_listing_risk(self, product: Dict, rule: ComplianceRule, compliance: Dict) -> Dict:
        """上架风险评估"""
        risk_factors = []
        risk_score = 0

        # 品类基础风险
        if rule.risk_level == "high":
            risk_score += 30
            risk_factors.append("品类管控严格")
        elif rule.risk_level == "medium":
            risk_score += 15
            risk_factors.append("品类管控中等")

        # 合规问题带来的风险
        critical_count = sum(1 for i in compliance["issues"] if i["severity"] == "critical")
        high_count = sum(1 for i in compliance["issues"] if i["severity"] == "high")

        risk_score += critical_count * 30 + high_count * 15

        if critical_count > 0:
            risk_factors.append(f"存在{critical_count}个严重合规问题")
        if high_count > 0:
            risk_factors.append(f"存在{high_count}个高风险合规问题")

        # 特殊宣称风险
        claims = product.get("claims", [])
        dangerous_claims = ["美白", "祛斑", "祛痘", "防晒", "抗皱"]
        for claim in claims:
            if claim in dangerous_claims:
                risk_score += 25
                risk_factors.append(f"宣称「{claim}」需要特殊许可证")

        risk_level = "low" if risk_score < 20 else "medium" if risk_score < 50 else "high"

        return {
            "score": max(0, 100 - risk_score),
            "level": risk_level,
            "factors": risk_factors,
            "can_list": risk_score < 50,
        }

    def _calc_total_score(self, compliance: Dict, profit: Dict, supplier: Dict, listing_risk: Dict) -> float:
        """综合得分计算"""
        # 权重：合规30% + 利润35% + 供应商15% + 上架风险20%
        score = (
            compliance["score"] * 0.30 +
            min(100, profit["net_profit"] * 2) * 0.35 +
            supplier["score"] * 0.15 +
            listing_risk["score"] * 0.20
        )
        return round(score, 1)

    def _generate_recommendation(self, compliance, profit, supplier, listing_risk, total_score) -> str:
        """生成选品建议"""
        if not compliance["pass"]:
            return "❌ 不推荐：存在严重合规问题，上架风险极高"

        if not profit["meets_target"]:
            return f"⚠️ 利润不足：净利润¥{profit['net_profit']}，未达到目标¥{self.target_profit_min}"

        if not listing_risk["can_list"]:
            return "❌ 不推荐：上架风险过高，容易被处罚"

        if total_score >= 80:
            return f"✅ 强烈推荐：合规通过，净利润¥{profit['net_profit']}，供应商可靠，上架风险低"
        elif total_score >= 60:
            return f"🔵 值得考虑：基本合规，净利润¥{profit['net_profit']}，建议优化后再上架"
        else:
            return f"🟡 谨慎选择：综合得分偏低，建议寻找更优供应商或调整定价"

    def _generate_candidates(self, category: str) -> List[Dict]:
        """生成品类候选商品（模拟1688搜索结果）"""
        base_products = {
            "身体乳": [
                {"name": "烟酰胺身体乳 保湿滋润", "category": "身体乳", "cost": 8, "sell_price": 45.9,
                 "claims": ["保湿", "滋润"], "ingredients": ["烟酰胺", "甘油", "透明质酸"],
                 "filing_number": "粤G妆网备字2024001234", "production_license": "粤妆20240001"},
                {"name": "樱花香氛身体乳 持久留香", "category": "身体乳", "cost": 6, "sell_price": 39.9,
                 "claims": ["保湿", "香氛"], "ingredients": ["甘油", "樱花提取物", "角鲨烷"],
                 "filing_number": "粤G妆网备字2024005678", "production_license": "粤妆20240002"},
                {"name": "果酸身体乳 去鸡皮", "category": "身体乳", "cost": 10, "sell_price": 49.9,
                 "claims": ["保湿", "去鸡皮"], "ingredients": ["果酸", "甘油", "乳木果油"],
                 "filing_number": "沪G妆网备字2024009999", "production_license": "沪妆20240003"},
            ],
            "面膜": [
                {"name": "玻尿酸补水面膜 10片装", "category": "面膜", "cost": 4, "sell_price": 39.9,
                 "claims": ["补水", "保湿"], "ingredients": ["透明质酸钠", "甘油", "积雪草提取物"],
                 "filing_number": "粤G妆网备字2024011111", "production_license": "粤妆20240001"},
                {"name": "积雪草舒缓面膜 10片装", "category": "面膜", "cost": 5, "sell_price": 45.9,
                 "claims": ["舒缓", "修护"], "ingredients": ["积雪草提取物", "神经酰胺", "甘油"],
                 "filing_number": "粤G妆网备字2024022222", "production_license": "粤妆20240001"},
                {"name": "烟酰胺亮肤面膜 10片装", "category": "面膜", "cost": 4, "sell_price": 35.9,
                 "claims": ["美白", "补水"], "ingredients": ["烟酰胺", "甘油", "熊果苷"],
                 "filing_number": "粤G妆网备字2024033333", "production_license": "粤妆20240001"},
            ],
            "护手霜": [
                {"name": "乳木果护手霜 滋润防裂 3支装", "category": "护手霜", "cost": 6, "sell_price": 39.9,
                 "claims": ["滋润", "防裂"], "ingredients": ["乳木果油", "甘油", "维生素E"],
                 "filing_number": "浙G妆网备字2024044444", "production_license": "浙妆20240001"},
                {"name": "樱花香氛护手霜 3支套装", "category": "护手霜", "cost": 8, "sell_price": 49.9,
                 "claims": ["保湿", "香氛"], "ingredients": ["樱花提取物", "甘油", "角鲨烷"],
                 "filing_number": "浙G妆网备字2024055555", "production_license": "浙妆20240001"},
            ],
            "精华液": [
                {"name": "玻尿酸精华液 补水保湿 30ml", "category": "精华液", "cost": 12, "sell_price": 59.9,
                 "claims": ["补水", "保湿"], "ingredients": ["透明质酸钠", "烟酰胺", "甘油"],
                 "filing_number": "粤G妆网备字2024066666", "production_license": "粤妆20240001"},
                {"name": "烟酰胺精华液 美白淡斑 30ml", "category": "精华液", "cost": 15, "sell_price": 69.9,
                 "claims": ["美白", "祛斑"], "ingredients": ["烟酰胺", "熊果苷", "甘油"],
                 "filing_number": "粤G妆网备字2024077777", "production_license": "粤妆20240001"},
            ],
            "洁面": [
                {"name": "氨基酸洁面乳 温和清洁 120ml", "category": "洁面", "cost": 6, "sell_price": 39.9,
                 "claims": ["清洁", "温和"], "ingredients": ["氨基酸表面活性剂", "甘油", "透明质酸"],
                 "filing_number": "粤G妆网备字2024088888", "production_license": "粤妆20240001"},
            ],
            "爽肤水": [
                {"name": "薏仁水 大容量补水 500ml", "category": "爽肤水", "cost": 5, "sell_price": 35.9,
                 "claims": ["补水", "保湿"], "ingredients": ["薏仁提取物", "甘油", "透明质酸"],
                 "filing_number": "沪G妆网备字2024099999", "production_license": "沪妆20240001"},
            ],
            "乳液": [
                {"name": "神经酰胺保湿乳液 100ml", "category": "乳液", "cost": 10, "sell_price": 49.9,
                 "claims": ["保湿", "修护"], "ingredients": ["神经酰胺", "角鲨烷", "甘油"],
                 "filing_number": "粤G妆网备字2024100000", "production_license": "粤妆20240001"},
            ],
            "润唇膏": [
                {"name": "蜂蜜润唇膏 保湿防裂 3支装", "category": "润唇膏", "cost": 4, "sell_price": 29.9,
                 "claims": ["保湿", "防裂"], "ingredients": ["蜂蜡", "可可脂", "维生素E"],
                 "filing_number": "浙G妆网备字2024111111", "production_license": "浙妆20240001"},
            ],
            "化妆棉": [
                {"name": "卸妆棉 省水湿敷 200片", "category": "化妆棉", "cost": 3, "sell_price": 25.9,
                 "claims": [], "ingredients": ["棉花"],
                 "filing_number": None, "production_license": None},
            ],
            "洗脸巾": [
                {"name": "一次性洗脸巾 纯棉 100抽 6包", "category": "洗脸巾", "cost": 8, "sell_price": 39.9,
                 "claims": [], "ingredients": ["棉"],
                 "filing_number": None, "production_license": None},
            ],
        }

        return base_products.get(category, [])
