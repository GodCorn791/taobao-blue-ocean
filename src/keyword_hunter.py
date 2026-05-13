"""
蓝海词挖掘引擎
核心逻辑：从种子词出发，通过多层扩展 + 蓝海指数筛选，发现高价值蓝海关键词。
"""

import random
import time
from typing import List, Dict, Optional
from src.config import config
from src.competition import CompetitionAnalyzer


class KeywordHunter:
    """蓝海关键词挖掘器"""
    
    def __init__(self):
        self.analyzer = CompetitionAnalyzer()
        self._expansion_rules = self._load_expansion_rules()
    
    def hunt(self, seed: str, depth: int = 2, top: int = 20) -> List[Dict]:
        """
        从种子词挖掘蓝海关键词
        
        Args:
            seed: 种子关键词
            depth: 扩展深度 (1=直接扩展, 2=二次扩展, 3=三次扩展)
            top: 返回前N个蓝海词
            
        Returns:
            按蓝海指数排序的关键词列表
        """
        all_keywords = set()
        all_keywords.add(seed)
        
        # 多层扩展
        current_layer = [seed]
        for d in range(depth):
            next_layer = []
            for kw in current_layer:
                expanded = self._expand_keyword(kw)
                next_layer.extend(expanded)
                all_keywords.update(expanded)
            current_layer = next_layer
            print(f"  第 {d+1} 层扩展: 新增 {len(next_layer)} 个关键词")
        
        # 过滤无效词
        keywords = [kw for kw in all_keywords if self._is_valid_keyword(kw)]
        print(f"  有效关键词: {len(keywords)} 个")
        
        # 批量计算蓝海指数
        results = []
        for kw in keywords:
            analysis = self.analyzer.analyze(kw)
            results.append({
                'keyword': kw,
                'blue_ocean_score': analysis['blue_ocean_score'],
                'search_volume': analysis['search_volume'],
                'seller_count': analysis['seller_count'],
                'top_concentration': analysis['top_concentration'],
                'ad_ratio': analysis['ad_ratio'],
                'conversion_rate': analysis['conversion_rate'],
                'avg_price': analysis['avg_price'],
                'level': self._score_level(analysis['blue_ocean_score']),
            })
        
        # 按蓝海指数排序
        results.sort(key=lambda x: x['blue_ocean_score'], reverse=True)
        return results[:top]
    
    def get_category_keywords(self, category: str, limit: int = 100) -> List[str]:
        """获取品类下的热门关键词"""
        # 品类 → 种子词映射
        category_seeds = {
            '家居日用': ['收纳盒', '置物架', '挂钩', '垃圾桶', '纸巾盒', '牙刷架', '肥皂盒', '拖鞋架'],
            '美妆护肤': ['面膜', '精华液', '防晒霜', '洗面奶', '口红', '眼影', '粉底液'],
            '数码配件': ['手机壳', '数据线', '充电器', '耳机', '支架', '钢化膜', '收纳包'],
            '服饰配件': ['帽子', '围巾', '手套', '腰带', '发饰', '胸针', '袖扣'],
            '宠物用品': ['猫粮', '狗粮', '猫砂', '宠物玩具', '猫抓板', '宠物衣服', '饮水器'],
            '办公文具': ['笔记本', '笔', '文件夹', '便签', '胶带', '剪刀', '订书机'],
        }
        
        seeds = category_seeds.get(category, [category])
        all_keywords = []
        
        for seed in seeds:
            expanded = self._expand_keyword(seed)
            all_keywords.extend(expanded)
        
        # 去重
        seen = set()
        unique = []
        for kw in all_keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        
        return unique[:limit]
    
    def _expand_keyword(self, keyword: str) -> List[str]:
        """扩展关键词（模拟淘宝联想词/长尾词扩展）"""
        # 前缀扩展
        prefixes = ['家用', '便携', '新款', '创意', 'ins风', '北欧风', '日式', '简约', '可爱', '实用']
        # 后缀扩展
        suffixes = ['推荐', '排行榜', '哪个牌子好', '怎么选', '便宜好用', '宿舍', '办公室', '小户型']
        # 场景扩展
        scenes = ['桌面', '厨房', '卫生间', '卧室', '客厅', '阳台', '书房', '玄关']
        # 人群扩展
        personas = ['学生', '上班族', '宝妈', '租房', '单身', '情侣']
        
        expanded = []
        
        # 组合扩展
        for prefix in random.sample(prefixes, min(3, len(prefixes))):
            expanded.append(f"{prefix}{keyword}")
        
        for suffix in random.sample(suffixes, min(3, len(suffixes))):
            expanded.append(f"{keyword}{suffix}")
        
        for scene in random.sample(scenes, min(2, len(scenes))):
            expanded.append(f"{scene}{keyword}")
        
        for person in random.sample(personas, min(2, len(personas))):
            expanded.append(f"{person}{keyword}")
        
        return expanded
    
    def _is_valid_keyword(self, keyword: str) -> bool:
        """判断关键词是否有效"""
        if len(keyword) < 2 or len(keyword) > 30:
            return False
        # 过滤明显无意义的组合
        noise = ['的', '了', '吗', '呢', '吧']
        if keyword[-1] in noise:
            return False
        return True
    
    def _score_level(self, score: float) -> str:
        if score > config.deep_blue_threshold: return 'deep_blue'
        if score > config.light_blue_threshold: return 'light_blue'
        if score > config.blue_green_threshold: return 'blue_green'
        return 'red_ocean'
    
    def _load_expansion_rules(self) -> dict:
        """加载关键词扩展规则"""
        return {
            'suffixes': ['推荐', '排行', '怎么选', '哪个好', '便宜', '好用'],
            'prefixes': ['新款', '2025', '爆款', '网红', 'ins', '北欧'],
            'modifiers': ['家用', '便携', '迷你', '大容量', '多功能', '创意'],
        }
