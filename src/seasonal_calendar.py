"""
护肤品季节选品日历
不同季节卖不同的品，踩对节奏就是印钱。
"""

from typing import Dict, List
from datetime import datetime


# 月度选品策略库
MONTHLY_STRATEGY = {
    1: {
        "name": "一月 · 年货节",
        "season": "冬季",
        "hot_categories": ["护手霜", "身体乳", "润唇膏", "面膜"],
        "reason": "冬季干燥+年货节大促，保湿滋润类产品爆发",
        "traffic_peak": "年货节（1月初-1月中旬）",
        "action": [
            "主推：护手霜套装、身体乳大容量装",
            "备货：提前2周备足库存",
            "定价：套装定价，配合满减活动",
            "关键词：年货、送礼、囤货、冬季必备",
        ],
        "profit_tip": "年货节客单价高，套装利润比单件高60%",
    },
    2: {
        "name": "二月 · 开学季+情人节",
        "season": "冬季→春季",
        "hot_categories": ["洁面", "面膜", "精华液", "护手霜"],
        "reason": "开学季学生党采购+情人节礼物需求",
        "traffic_peak": "开学前一周、情人节前一周",
        "action": [
            "学生线：平价洁面+面膜组合，定价39.9-59.9",
            "情人节线：精致包装+手写卡片，溢价空间大",
            "关键词：学生、开学、情人节、礼物",
        ],
        "profit_tip": "情人节溢价空间大，礼盒装利润可达80%+",
    },
    3: {
        "name": "三月 · 换季敏感期",
        "season": "春季",
        "hot_categories": ["面膜", "爽肤水", "精华液", "乳液"],
        "reason": "换季皮肤敏感，舒缓修护类产品需求暴增",
        "traffic_peak": "3月中旬-4月初",
        "action": [
            "主推：舒缓面膜、修护精华、温和洁面",
            "卖点：敏感肌可用、换季急救、温和不刺激",
            "关键词：换季、敏感肌、舒缓、修护",
        ],
        "profit_tip": "敏感肌产品溢价空间大，用户价格敏感度低",
    },
    4: {
        "name": "四月 · 防晒+美白季启动",
        "season": "春季→夏季",
        "hot_categories": ["面膜", "精华液", "爽肤水", "乳液"],
        "reason": "清明后气温上升，美白补水需求启动",
        "traffic_peak": "4月中旬起持续上升",
        "action": [
            "主推：补水面膜、保湿精华、清爽乳液",
            "注意：不能宣称美白（需要特证），但可以推补水",
            "关键词：补水、清爽、控油、春夏护肤",
        ],
        "profit_tip": "补水面膜是全年通用品，4月开始走量",
    },
    5: {
        "name": "五月 · 618预热",
        "season": "夏季",
        "hot_categories": ["面膜", "洁面", "爽肤水", "乳液"],
        "reason": "618大促预热期，提前蓄水加购",
        "traffic_peak": "5月下旬起",
        "action": [
            "蓄水期：低价引流款冲销量+加购数",
            "备货：618库存提前1个月备好",
            "关键词：618、大促、囤货、限时",
        ],
        "profit_tip": "618靠量赚钱，单件利润可以压低，走量为主",
    },
    6: {
        "name": "六月 · 618大促+夏季清爽",
        "season": "夏季",
        "hot_categories": ["洁面", "爽肤水", "面膜", "乳液"],
        "reason": "618爆发+夏季出油多，清爽控油类热销",
        "traffic_peak": "6月1日-6月20日",
        "action": [
            "主推：控油洁面、清爽乳液、补水面膜",
            "定价：活动价+满减+赠品，多重优惠叠加",
            "关键词：618、控油、清爽、夏季",
        ],
        "profit_tip": "618期间转化率高2-3倍，投产比最好",
    },
    7: {
        "name": "七月 · 暑假学生潮",
        "season": "夏季",
        "hot_categories": ["洁面", "面膜", "乳液", "精华液"],
        "reason": "暑假学生群体集中护肤需求，平价品爆发",
        "traffic_peak": "7月上旬-8月中旬",
        "action": [
            "主推：学生平价套装（洁面+水+乳 三件套）",
            "定价：59.9-89.9 学生党可接受",
            "关键词：学生、平价、开学必备、控油",
        ],
        "profit_tip": "学生党复购率高，一个客户能买3-4次",
    },
    8: {
        "name": "八月 · 开学季备货",
        "season": "夏末",
        "hot_categories": ["洁面", "乳液", "面膜", "身体乳"],
        "reason": "开学季采购高峰，军训晒后修护需求",
        "traffic_peak": "8月中旬-9月初",
        "action": [
            "主推：晒后修护面膜、保湿乳液、洁面",
            "卖点：军训必备、晒后急救、温和修护",
            "关键词：开学、军训、晒后修护、学生",
        ],
        "profit_tip": "开学季客单价适中，但转化率高",
    },
    9: {
        "name": "九月 · 秋季换季",
        "season": "秋季",
        "hot_categories": ["乳液", "精华液", "面膜", "身体乳"],
        "reason": "入秋干燥，保湿修护需求回升",
        "traffic_peak": "9月中旬起",
        "action": [
            "主推：保湿乳液、修护精华、滋润身体乳",
            "卖点：换季必备、深层保湿、修护屏障",
            "关键词：秋季、保湿、换季、滋润",
        ],
        "profit_tip": "秋季是护肤品第二个黄金期，利润空间大",
    },
    10: {
        "name": "十月 · 双11蓄水",
        "season": "秋季→冬季",
        "hot_categories": ["面膜", "精华液", "身体乳", "护手霜"],
        "reason": "双11大促蓄水期，提前锁客",
        "traffic_peak": "10月下旬起",
        "action": [
            "蓄水：低价引流款冲加购+收藏",
            "备货：双11库存提前6周备好",
            "关键词：双11、预售、囤货、必买",
        ],
        "profit_tip": "双11是全年最大促，目标是平时3-5倍销量",
    },
    11: {
        "name": "十一月 · 双11爆发",
        "season": "冬季",
        "hot_categories": ["身体乳", "护手霜", "面膜", "润唇膏"],
        "reason": "双11大促+冬季干燥，全年销售最高峰",
        "traffic_peak": "11月1日-11月11日",
        "action": [
            "主推：冬季保湿套装、护手霜礼盒、面膜囤货装",
            "定价：全年最低价+赠品，冲量为主",
            "关键词：双11、限时、最低价、囤货",
        ],
        "profit_tip": "双11靠量取胜，日销可以是平时的10倍",
    },
    12: {
        "name": "十二月 · 年末冲刺",
        "season": "冬季",
        "hot_categories": ["护手霜", "身体乳", "润唇膏", "面膜"],
        "reason": "圣诞+元旦+冬季干燥，礼盒装热销",
        "traffic_peak": "12月中旬-12月底",
        "action": [
            "主推：圣诞礼盒、冬季滋润套装、护手霜组合",
            "卖点：送礼首选、圣诞限定、冬季必备",
            "关键词：圣诞、礼物、冬季、滋润",
        ],
        "profit_tip": "礼盒装溢价空间大，利润可达70%+",
    },
}


class SeasonalCalendar:
    """护肤品季节选品日历"""

    def get_current_month(self) -> Dict:
        """获取当月选品策略"""
        month = datetime.now().month
        return self.get_month(month)

    def get_month(self, month: int) -> Dict:
        """获取指定月份的选品策略"""
        return MONTHLY_STRATEGY.get(month, {})

    def get_year_overview(self) -> List[Dict]:
        """获取全年选品概览"""
        overview = []
        for month in range(1, 13):
            strategy = MONTHLY_STRATEGY[month]
            overview.append({
                "month": month,
                "name": strategy["name"],
                "hot_categories": strategy["hot_categories"],
                "traffic_peak": strategy["traffic_peak"],
            })
        return overview

    def get_category_peak_months(self, category: str) -> List[int]:
        """获取某品类的销售旺季月份"""
        peak_months = []
        for month, strategy in MONTHLY_STRATEGY.items():
            if category in strategy["hot_categories"]:
                peak_months.append(month)
        return peak_months
