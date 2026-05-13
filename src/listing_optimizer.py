"""
商品上架优化器
生成高转化的商品标题、卖点、定价策略。
这是从"选品"到"上架赚钱"的关键一步。
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ListingTemplate:
    """商品上架模板"""
    title: str
    subtitle: str
    selling_points: List[str]
    price_strategy: Dict
    main_image_tips: List[str]
    detail_sections: List[Dict]


# 标题公式库：核心词 + 属性词 + 卖点词 + 场景词
TITLE_FORMULAS = {
    "基础款": "{核心词} {材质/成分} {规格} {卖点}",
    "场景款": "{场景} {核心词} {卖点} {规格}",
    "套装款": "{核心词} {件数}件套 {卖点} {适用人群}",
    "功效款": "{核心成分} {核心词} {功效} {规格}",
}

# 高转化卖点词库
HIGH_CONVERT_WORDS = {
    "通用": ["买一送一", "第二件半价", "拍2件减10", "限时特惠", "今日下单送小样"],
    "品质": ["大牌同厂", "专柜同款", "成分党推荐", "皮肤科测试", "敏感肌可用"],
    "功效": ["7天见效", "28天一个周期", "持续使用效果更佳", "早晚各一次"],
    "信任": ["已售10万+", "回购率85%", "好评率99%", "0差评"],
}

# 定价心理学
PRICE_ENDINGS = {
    "引流款": 9.9,    # 低价引流
    "利润款": 49.9,   # 主力利润
    "形象款": 99.9,   # 提升店铺档次
    "套装款": 79.9,   # 组合优惠
}


class ListingOptimizer:
    """商品上架优化器"""

    def generate_listing(self, product: Dict) -> ListingTemplate:
        """
        根据商品信息生成完整的上架方案

        Args:
            product: {
                "name": "商品名",
                "category": "品类",
                "cost": 拿货价,
                "ingredients": ["成分1", "成分2"],
                "target_audience": "目标人群",
                "selling_points": ["卖点1"],
            }

        Returns:
            完整的上架方案
        """
        category = product.get("category", "")
        cost = product.get("cost", 0)
        ingredients = product.get("ingredients", [])
        audience = product.get("target_audience", "年轻女性")

        # 生成标题
        title = self._generate_title(product)

        # 生成卖点
        selling_points = self._generate_selling_points(product)

        # 定价策略
        price_strategy = self._generate_price_strategy(cost, category)

        # 主图建议
        main_image_tips = self._generate_image_tips(category)

        # 详情页结构
        detail_sections = self._generate_detail_sections(product)

        return ListingTemplate(
            title=title,
            subtitle=self._generate_subtitle(product),
            selling_points=selling_points,
            price_strategy=price_strategy,
            main_image_tips=main_image_tips,
            detail_sections=detail_sections,
        )

    def _generate_title(self, product: Dict) -> str:
        """生成高搜索量标题"""
        category = product.get("category", "")
        ingredients = product.get("ingredients", [])
        audience = product.get("target_audience", "")

        # 标题组件
        core_words = {
            "身体乳": ["身体乳", "润体乳", "身体护肤乳"],
            "面膜": ["面膜", "补水面膜", "贴片面膜"],
            "护手霜": ["护手霜", "手部护理", "护手"],
            "精华液": ["精华液", "面部精华", "精华"],
            "洁面": ["洗面奶", "洁面乳", "洁面"],
            "爽肤水": ["爽肤水", "化妆水", "水"],
            "乳液": ["乳液", "面乳", "保湿乳"],
            "润唇膏": ["润唇膏", "唇膏", "唇部护理"],
            "化妆棉": ["化妆棉", "卸妆棉", "湿敷棉"],
            "洗脸巾": ["洗脸巾", "一次性毛巾", "棉柔巾"],
        }

        cores = core_words.get(category, [category])
        core = cores[0]

        # 成分词
        ingredient_words = []
        ing_map = {
            "烟酰胺": "烟酰胺", "透明质酸": "玻尿酸", "透明质酸钠": "玻尿酸",
            "积雪草": "积雪草", "神经酰胺": "神经酰胺", "角鲨烷": "角鲨烷",
            "乳木果油": "乳木果", "甘油": "保湿", "果酸": "果酸",
        }
        for ing in ingredients[:2]:
            if ing in ing_map:
                ingredient_words.append(ing_map[ing])

        # 卖点词
        benefit_words = {
            "身体乳": ["保湿滋润", "持久留香", "嫩肤"],
            "面膜": ["补水保湿", "深层修护", "舒缓"],
            "护手霜": ["滋润防裂", "保湿", "嫩白"],
            "精华液": ["补水保湿", "修护", "维稳"],
            "洁面": ["温和清洁", "控油", "不紧绷"],
            "爽肤水": ["补水", "收敛毛孔", "二次清洁"],
            "乳液": ["保湿", "不油腻", "好吸收"],
            "润唇膏": ["保湿防裂", "滋润", "淡化唇纹"],
        }
        benefits = benefit_words.get(category, ["好用"])

        # 规格词
        spec_words = ["大容量", "家庭装", "便携装", "旅行装"]

        # 人群词
        audience_map = {
            "学生": "学生党", "上班族": "上班族", "宝妈": "宝妈",
            "敏感肌": "敏感肌", "油皮": "油皮", "干皮": "干皮",
        }
        audience_word = audience_map.get(audience, "男女通用")

        # 组装标题（淘宝标题上限30个汉字，尽量塞满关键词）
        parts = []
        parts.append(core)
        if ingredient_words:
            parts.append(ingredient_words[0])
        parts.append(benefits[0])
        if len(benefits) > 1:
            parts.append(benefits[1])
        parts.append(audience_word)
        if len(ingredient_words) > 1:
            parts.append(ingredient_words[1])

        title = " ".join(parts)

        # 确保不超过30字
        if len(title) > 30:
            title = title[:30]

        return title

    def _generate_subtitle(self, product: Dict) -> str:
        """生成副标题（商品卖点一句话）"""
        category = product.get("category", "")
        subtitles = {
            "身体乳": "一抹即润 全身嫩滑 持久留香12小时",
            "面膜": "15分钟急救补水 肉眼可见的水润",
            "护手霜": "一支解决手部干燥粗糙 嫩滑如初",
            "精华液": "3滴精华=10张面膜 深层修护",
            "洁面": "温和不紧绷 洗出干净脸",
            "爽肤水": "拍一拍就吸收 肌肤喝饱水",
            "乳液": "轻薄好吸收 一整天水润不油腻",
            "润唇膏": "告别干裂脱皮 水润嘟嘟唇",
        }
        return subtitles.get(category, "品质好物 值得拥有")

    def _generate_selling_points(self, product: Dict) -> List[str]:
        """生成高转化卖点"""
        category = product.get("category", "")
        ingredients = product.get("ingredients", [])

        points = []

        # 成分卖点
        ingredient_benefits = {
            "烟酰胺": "烟酰胺成分，提亮肤色",
            "透明质酸钠": "三重玻尿酸，深层补水",
            "透明质酸": "高浓度玻尿酸，锁水力MAX",
            "积雪草提取物": "积雪草精粹，舒缓修护",
            "神经酰胺": "神经酰胺修护屏障，敏感肌友好",
            "角鲨烷": "角鲨烷亲肤配方，滋润不油腻",
            "乳木果油": "乳木果油深层滋养，告别干燥",
            "果酸": "温和果酸焕肤，改善粗糙",
        }
        for ing in ingredients[:2]:
            if ing in ingredient_benefits:
                points.append(ingredient_benefits[ing])

        # 品类通用卖点
        category_points = {
            "身体乳": ["大容量500ml，全家可用", "质地轻薄好吸收，不粘睡衣", "持久留香，自带体香"],
            "面膜": ["30ml精华液，敷完还能敷脖子", "天丝膜布，服帖不滑落", "独立包装，出差旅行方便携带"],
            "护手霜": ["小巧便携，随时随地护手", "不油腻，涂完马上能玩手机", "3支套装，家里/公司/包里各一支"],
            "精华液": ["滴管设计，精准用量不浪费", "30ml大容量，能用2个月", "早晚各3滴，效果肉眼可见"],
            "洁面": ["氨基酸配方，温和不刺激", "泡沫绵密，洗感超舒服", "洗完不紧绷，不假滑"],
        }
        points.extend(category_points.get(category, ["品质保证，假一赔十"]))

        # 促销卖点
        points.append("48小时内发货，顺丰/中通可选")
        points.append("7天无理由退换，不满意包退")

        return points[:6]  # 最多6个卖点

    def _generate_price_strategy(self, cost: float, category: str) -> Dict:
        """生成定价策略"""
        # 利润率目标
        target_margin = 0.65  # 目标毛利率65%

        # 建议售价
        suggested_price = cost / (1 - target_margin)

        # 定价到x.9
        import math
        sell_price = math.ceil(suggested_price / 10) * 10 - 0.1
        if sell_price < 19.9:
            sell_price = 19.9

        # 套装定价
        combo_price = sell_price * 1.6  # 套装溢价60%
        combo_price = math.ceil(combo_price / 10) * 10 - 0.1

        # 促销定价
        promo_price = sell_price * 0.85  # 85折
        promo_price = math.ceil(promo_price / 10) * 10 - 0.1

        net_profit = sell_price - cost - 3.5 - 1.5 - (sell_price * 0.05)
        combo_profit = combo_price - cost * 2 - 4 - 2 - (combo_price * 0.05)

        return {
            "cost": cost,
            "sell_price": sell_price,
            "combo_price": combo_price,
            "promo_price": promo_price,
            "net_profit_single": round(net_profit, 2),
            "net_profit_combo": round(combo_profit, 2),
            "margin_single": round(net_profit / sell_price, 4),
            "margin_combo": round(combo_profit / combo_price, 4),
            "strategy": {
                "日常": f"¥{sell_price}（净利润¥{net_profit:.0f}）",
                "套装": f"¥{combo_price} 两件套（净利润¥{combo_profit:.0f}，提升客单价）",
                "活动": f"¥{promo_price} 限时折扣（配合满减使用）",
                "引流": f"首件¥{max(cost * 1.5, 9.9):.1f} 限量100件（亏本引流冲销量）",
            },
            "sku建议": [
                f"单件装 ¥{sell_price}",
                f"两件套 ¥{combo_price}（省¥{sell_price * 2 - combo_price:.0f}）",
                f"体验装 ¥{max(cost * 2, 14.9):.1f}（小容量试用）",
            ],
        }

    def _generate_image_tips(self, category: str) -> List[str]:
        """生成主图拍摄建议"""
        base_tips = [
            "白底/浅色背景，干净清爽",
            "产品居中，占画面60%以上",
            "第二张放使用场景图",
            "第三张放成分/功效卖点图",
            "第四张放对比图（使用前后）",
            "第五张放促销信息（满减/赠品）",
        ]

        category_specific = {
            "身体乳": ["模特手臂试用图，展示质地", "挤出产品展示乳液质地", "搭配浴巾/浴室场景"],
            "面膜": ["模特敷面膜图，展示服帖度", "精华液滴落图，展示精华量", "成分表特写"],
            "护手霜": ["手部对比图（使用前后）", "挤出护手霜展示质地", "搭配办公桌/包包场景"],
            "精华液": ["滴管滴出精华图", "成分表特写", "模特涂精华图"],
            "洁面": ["泡沫绵密度展示", "模特洁面图", "洗前洗后对比"],
        }

        return base_tips[:3] + category_specific.get(category, [])[:3]

    def _generate_detail_sections(self, product: Dict) -> List[Dict]:
        """生成详情页结构"""
        category = product.get("category", "")
        return [
            {"section": "首屏", "content": "核心卖点 + 促销信息 + 下单理由"},
            {"section": "痛点", "content": f"目标用户的{category}痛点场景（共鸣感）"},
            {"section": "解决方案", "content": "产品如何解决这个痛点（成分+技术）"},
            {"section": "成分表", "content": "核心成分功效解读（专业感）"},
            {"section": "使用方法", "content": "图文教程，降低使用门槛"},
            {"section": "效果展示", "content": "使用前后对比图（真实感）"},
            {"section": "用户评价", "content": "精选好评截图（社交证明）"},
            {"section": "品牌故事", "content": "简短品牌介绍（信任感）"},
            {"section": "售后保障", "content": "7天无理由 + 正品保证 + 包邮"},
        ]
