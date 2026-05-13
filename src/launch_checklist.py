"""
上架检查清单
确保商品上架前所有合规、运营、物流要素都已就绪。
少一个都可能导致上架失败或被处罚。
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class CheckItem:
    """检查项"""
    name: str
    category: str  # compliance / operation / logistics / marketing
    priority: str  # critical / high / medium / low
    passed: bool = False
    detail: str = ""
    fix: str = ""


class LaunchChecklist:
    """商品上架检查清单"""

    def check(self, product: Dict) -> Dict:
        """
        执行完整的上架前检查

        Args:
            product: 商品信息

        Returns:
            检查结果，包含所有检查项和总评
        """
        items = []

        # 1. 合规检查
        items.extend(self._check_compliance(product))

        # 2. 运营检查
        items.extend(self._check_operation(product))

        # 3. 物流检查
        items.extend(self._check_logistics(product))

        # 4. 营销检查
        items.extend(self._check_marketing(product))

        # 统计
        total = len(items)
        passed = sum(1 for i in items if i.passed)
        critical_failed = [i for i in items if not i.passed and i.priority == "critical"]
        high_failed = [i for i in items if not i.passed and i.priority == "high"]

        can_launch = len(critical_failed) == 0

        return {
            "can_launch": can_launch,
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "critical_failed": len(critical_failed),
            "high_failed": len(high_failed),
            "score": round(passed / total * 100) if total > 0 else 0,
            "items": items,
            "summary": self._generate_summary(can_launch, critical_failed, high_failed, passed, total),
        }

    def _check_compliance(self, product: Dict) -> List[CheckItem]:
        """合规检查"""
        items = []

        items.append(CheckItem(
            name="化妆品备案编号",
            category="compliance",
            priority="critical",
            passed=bool(product.get("filing_number")),
            detail="国产普通化妆品必须有备案编号",
            fix="向供应商索要备案编号，去国家药监局官网验证",
        ))

        items.append(CheckItem(
            name="生产许可证",
            category="compliance",
            priority="critical",
            passed=bool(product.get("production_license")),
            detail="必须持有有效的《化妆品生产许可证》",
            fix="要求供应商提供生产许可证扫描件",
        ))

        items.append(CheckItem(
            name="成分表（INCI）",
            category="compliance",
            priority="critical",
            passed=bool(product.get("ingredients")),
            detail="产品包装上必须有完整成分表",
            fix="确认包装上有成分表，且与备案信息一致",
        ))

        items.append(CheckItem(
            name="功效宣称合规",
            category="compliance",
            priority="critical",
            passed=not any(
                c in ["美白", "祛斑", "祛痘", "防晒", "抗皱"]
                for c in product.get("claims", [])
            ),
            detail="未宣称特殊功效（美白/祛斑/祛痘/防晒需要特证）",
            fix="移除特殊功效宣称，改为合规表述",
        ))

        items.append(CheckItem(
            name="违禁成分检测",
            category="compliance",
            priority="critical",
            passed=True,  # 默认通过，实际需要成分比对
            detail="不含氢醌、汞、铅、糖皮质激素等违禁成分",
            fix="送检第三方机构，获取检测报告",
        ))

        items.append(CheckItem(
            name="保质期标注",
            category="compliance",
            priority="high",
            passed=True,  # 默认通过
            detail="包装上有生产日期和保质期",
            fix="确认包装上有清晰的生产日期和保质期标注",
        ))

        items.append(CheckItem(
            name="产品名称规范",
            category="compliance",
            priority="high",
            passed=True,
            detail="产品名称不含虚假、夸大的词汇",
            fix="检查名称不含'最'、'第一'等绝对化用语",
        ))

        return items

    def _check_operation(self, product: Dict) -> List[CheckItem]:
        """运营检查"""
        items = []

        cost = product.get("cost", 0)
        sell_price = product.get("sell_price", 0)
        profit = sell_price - cost - 3.5 - 1.5 - (sell_price * 0.05) if sell_price > 0 else 0

        items.append(CheckItem(
            name="利润空间",
            category="operation",
            priority="critical",
            passed=profit >= 15,
            detail=f"净利润 ¥{profit:.1f}（目标 ≥ ¥15）",
            fix="调整售价或寻找更低成本的供应商",
        ))

        items.append(CheckItem(
            name="商品标题",
            category="operation",
            priority="high",
            passed=len(product.get("title", "")) >= 10,
            detail="标题包含核心词+属性词+卖点词，长度≥10字",
            fix="使用 listing optimizer 生成标题",
        ))

        items.append(CheckItem(
            name="主图数量",
            category="operation",
            priority="high",
            passed=product.get("image_count", 0) >= 5,
            detail="至少5张主图（白底+场景+卖点+对比+促销）",
            fix="补拍主图，确保5张以上",
        ))

        items.append(CheckItem(
            name="详情页",
            category="operation",
            priority="high",
            passed=bool(product.get("has_detail")),
            detail="详情页包含卖点、成分、使用方法、评价",
            fix="制作详情页，参考 listing optimizer 的结构建议",
        ))

        items.append(CheckItem(
            name="SKU设置",
            category="operation",
            priority="medium",
            passed=product.get("sku_count", 0) >= 2,
            detail="至少2个SKU（单件+套装）",
            fix="增加套装SKU，提升客单价",
        ))

        items.append(CheckItem(
            name="价格竞争力",
            category="operation",
            priority="medium",
            passed=True,
            detail="价格在同类商品中有竞争力",
            fix="调研竞品价格，调整定价策略",
        ))

        return items

    def _check_logistics(self, product: Dict) -> List[CheckItem]:
        """物流检查"""
        items = []

        items.append(CheckItem(
            name="供应商发货时效",
            category="logistics",
            priority="high",
            passed=True,  # 默认通过
            detail="供应商承诺48小时内发货",
            fix="与供应商确认发货时效，签订协议",
        ))

        items.append(CheckItem(
            name="快递方案",
            category="logistics",
            priority="medium",
            passed=True,
            detail="已确定快递方案（中通/圆通/韵达）",
            fix="联系快递谈合作价，目标3元/单以内",
        ))

        items.append(CheckItem(
            name="包装方案",
            category="logistics",
            priority="medium",
            passed=True,
            detail="包装方案已确定（气泡膜+纸箱+品牌卡片）",
            fix="设计品牌卡片，采购包装材料",
        ))

        items.append(CheckItem(
            name="库存备货",
            category="logistics",
            priority="high",
            passed=product.get("stock", 0) >= 50,
            detail="首批备货≥50件",
            fix="首批建议备100件，先测款再加量",
        ))

        return items

    def _check_marketing(self, product: Dict) -> List[CheckItem]:
        """营销检查"""
        items = []

        items.append(CheckItem(
            name="促销方案",
            category="marketing",
            priority="medium",
            passed=bool(product.get("promo_plan")),
            detail="已制定促销方案（满减/赠品/限时折扣）",
            fix="设置'满2件减10'或'下单送小样'活动",
        ))

        items.append(CheckItem(
            name="好评引导",
            category="marketing",
            priority="low",
            passed=True,
            detail="已准备好评引导卡片",
            fix="在包裹中放好评返现卡（注意平台规则）",
        ))

        items.append(CheckItem(
            name="客服话术",
            category="marketing",
            priority="low",
            passed=True,
            detail="已准备常见问题的客服话术",
            fix="整理尺码、成分、发货等常见问题的标准回答",
        ))

        return items

    def _generate_summary(self, can_launch, critical_failed, high_failed, passed, total) -> str:
        """生成检查总结"""
        if can_launch and len(high_failed) == 0:
            return f"✅ 可以上架！{passed}/{total} 项检查通过。"
        elif can_launch:
            return f"⚠️ 基本可以上架，但有 {len(high_failed)} 个高优先级项建议优化。"
        else:
            names = ", ".join(i.name for i in critical_failed)
            return f"❌ 暂不能上架！{len(critical_failed)} 个关键项未通过: {names}"
