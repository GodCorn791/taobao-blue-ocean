"""配置管理"""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # 数据源配置
    data_source: str = "mock"  # mock / api / crawler
    
    # 蓝海指数权重
    weight_search_volume: float = 0.30
    weight_conversion_rate: float = 0.20
    weight_seller_count: float = 0.25
    weight_top_concentration: float = 0.15
    weight_ad_ratio: float = 0.10
    
    # 蓝海阈值
    deep_blue_threshold: float = 80
    light_blue_threshold: float = 50
    blue_green_threshold: float = 30
    
    # 挖掘参数
    max_expand_depth: int = 3
    default_top_n: int = 20
    min_search_volume: int = 100  # 日均搜索量下限
    max_seller_count: int = 5000  # 卖家数上限
    
    # 监控参数
    monitor_intervals: dict = field(default_factory=lambda: {
        'hourly': 3600,
        'daily': 86400,
        'weekly': 604800,
    })
    
    # 报告配置
    report_format: str = "html"  # html / json / csv
    report_dir: str = "data/reports"


config = Config()
