"""
供应商管理器
记录、评分、追踪供应商，避免踩坑。
好的供应商 = 省心 + 省钱 + 少退货。
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


DATA_FILE = "data/suppliers.json"


class SupplierTracker:
    """供应商管理器"""

    def __init__(self):
        self.suppliers = self._load()

    def add(self, supplier: Dict) -> Dict:
        """
        添加供应商

        Args:
            supplier: {
                "name": "供应商名",
                "platform": "1688/拼多多/线下",
                "contact": "联系方式",
                "category": "主营品类",
                "products": ["商品1", "商品2"],
                "moq": 最小起订量,
                "delivery_days": 发货天数,
                "price_level": "低/中/高",
                "quality_score": 质量评分(0-100),
                "notes": "备注",
            }

        Returns:
            添加结果
        """
        supplier_id = f"SUP{len(self.suppliers) + 1:04d}"
        supplier["id"] = supplier_id
        supplier["created_at"] = datetime.now().isoformat()
        supplier["orders"] = 0
        supplier["total_amount"] = 0
        supplier["issues"] = []
        supplier["rating"] = self._calc_rating(supplier)

        self.suppliers[supplier_id] = supplier
        self._save()

        return {
            "id": supplier_id,
            "name": supplier["name"],
            "rating": supplier["rating"],
            "message": f"✅ 供应商「{supplier['name']}」已添加，评分 {supplier['rating']}/100",
        }

    def record_order(self, supplier_id: str, amount: float, issues: list = None) -> Dict:
        """记录一笔采购订单"""
        if supplier_id not in self.suppliers:
            return {"error": f"供应商 {supplier_id} 不存在"}

        s = self.suppliers[supplier_id]
        s["orders"] += 1
        s["total_amount"] += amount
        if issues:
            s["issues"].extend(issues)
        s["rating"] = self._calc_rating(s)
        self._save()

        return {
            "supplier": s["name"],
            "total_orders": s["orders"],
            "total_amount": s["total_amount"],
            "rating": s["rating"],
        }

    def list_all(self, sort_by: str = "rating") -> List[Dict]:
        """列出所有供应商"""
        suppliers = list(self.suppliers.values())
        suppliers.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        return suppliers

    def get_recommendation(self, category: str) -> Optional[Dict]:
        """获取品类推荐供应商"""
        candidates = [
            s for s in self.suppliers.values()
            if s.get("category") == category and s.get("rating", 0) >= 60
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x["rating"], reverse=True)
        return candidates[0]

    def _calc_rating(self, supplier: Dict) -> int:
        """计算供应商综合评分"""
        score = 0

        # 质量评分 (40%)
        score += supplier.get("quality_score", 50) * 0.4

        # 发货速度 (20%)
        days = supplier.get("delivery_days", 3)
        if days <= 1:
            score += 20
        elif days <= 2:
            score += 15
        elif days <= 3:
            score += 10
        else:
            score += 5

        # 起订量 (15%)
        moq = supplier.get("moq", 5)
        if moq <= 2:
            score += 15
        elif moq <= 5:
            score += 12
        elif moq <= 10:
            score += 8
        else:
            score += 4

        # 问题率 (15%)
        orders = supplier.get("orders", 0)
        issues = len(supplier.get("issues", []))
        if orders > 0:
            issue_rate = issues / orders
            score += max(0, 15 * (1 - issue_rate))
        else:
            score += 10  # 新供应商默认中等

        # 价格竞争力 (10%)
        price_level = supplier.get("price_level", "中")
        if price_level == "低":
            score += 10
        elif price_level == "中":
            score += 7
        else:
            score += 3

        return min(100, int(score))

    def _load(self) -> dict:
        """加载供应商数据"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self):
        """保存供应商数据"""
        os.makedirs(os.path.dirname(DATA_FILE) if os.path.dirname(DATA_FILE) else '.', exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.suppliers, f, ensure_ascii=False, indent=2)
