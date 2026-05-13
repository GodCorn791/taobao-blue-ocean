"""
趋势监控器
持续追踪蓝海关键词的变化，检测趋势拐点。
"""

import time
import json
from datetime import datetime
from typing import List, Callable, Optional
from src.competition import CompetitionAnalyzer
from src.config import config


class TrendMonitor:
    """蓝海词趋势监控"""
    
    def __init__(self):
        self.analyzer = CompetitionAnalyzer()
        self.history = {}  # keyword -> [(timestamp, score)]
    
    def start(self, keywords: List[str], interval: str = 'daily', 
              callback: Optional[Callable] = None):
        """
        启动趋势监控
        
        Args:
            keywords: 要监控的关键词列表
            interval: 监控间隔 (hourly/daily/weekly)
            callback: 分数变化回调函数
        """
        interval_sec = config.monitor_intervals.get(interval, 86400)
        
        print(f"  监控中... (按 Ctrl+C 停止)")
        print(f"  关键词数: {len(keywords)} | 间隔: {interval} ({interval_sec}s)")
        print()
        
        try:
            while True:
                for kw in keywords:
                    result = self.analyzer.analyze(kw)
                    current_score = result['blue_ocean_score']
                    timestamp = datetime.now().isoformat()
                    
                    if kw not in self.history:
                        self.history[kw] = []
                    
                    # 检查变化
                    if self.history[kw]:
                        old_score = self.history[kw][-1][1]
                        if abs(current_score - old_score) > 5:  # 变化超过5分才通知
                            if callback:
                                callback(kw, old_score, current_score)
                    
                    self.history[kw].append((timestamp, current_score))
                    
                    # 检测趋势
                    trend = self._detect_trend(self.history[kw])
                    if trend:
                        print(f"  ⚠️  {kw}: {trend}")
                
                # 保存历史
                self._save_history()
                
                print(f"\n  ⏰ 下次检查: {interval_sec}秒后\n")
                time.sleep(interval_sec)
                
        except KeyboardInterrupt:
            print("\n\n  📊 监控已停止，正在生成报告...")
            self._print_summary()
    
    def _detect_trend(self, history: list) -> Optional[str]:
        """检测趋势拐点"""
        if len(history) < 3:
            return None
        
        recent = [h[1] for h in history[-3:]]
        
        # 连续下降 → 蓝海变红海
        if recent[0] > recent[1] > recent[2] and recent[0] - recent[2] > 10:
            return "📉 蓝海正在消失，竞争加剧！"
        
        # 连续上升 → 红海变蓝海
        if recent[0] < recent[1] < recent[2] and recent[2] - recent[0] > 10:
            return "📈 蓝海机会正在出现！"
        
        return None
    
    def _print_summary(self):
        """打印监控摘要"""
        print("\n" + "=" * 60)
        print("  📈 趋势监控摘要")
        print("=" * 60)
        
        for kw, history in self.history.items():
            if len(history) < 2:
                continue
            
            first_score = history[0][1]
            last_score = history[-1][1]
            change = last_score - first_score
            direction = '📈' if change > 0 else '📉' if change < 0 else '➡️'
            
            print(f"  {direction} {kw}: {first_score:.1f} → {last_score:.1f} ({change:+.1f})")
    
    def _save_history(self):
        """保存监控历史到文件"""
        try:
            with open('data/trend_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
