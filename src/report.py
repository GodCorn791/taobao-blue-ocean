"""
报告生成器
输出可视化蓝海分析报告（HTML/JSON）。
"""

import json
import os
from datetime import datetime
from typing import Dict
from src.config import config


class ReportGenerator:
    """蓝海分析报告生成器"""
    
    def generate(self, output: str = 'report.html') -> Dict:
        """生成完整蓝海报告"""
        # 示例数据（实际使用时从各模块收集）
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_keywords_scanned': 156,
                'deep_blue_found': 12,
                'light_blue_found': 28,
                'blue_green_found': 45,
                'red_ocean_found': 71,
            },
            'top_blue_ocean': [
                {'keyword': '桌面收纳盒 学生宿舍', 'score': 87.3, 'volume': 8500, 'sellers': 320},
                {'keyword': '便携挂烫机 家用小型', 'score': 82.1, 'volume': 6200, 'sellers': 280},
                {'keyword': '宠物自动喂食器 防潮', 'score': 79.8, 'volume': 5800, 'sellers': 350},
                {'keyword': '北欧风桌面摆件 创意', 'score': 76.5, 'volume': 4200, 'sellers': 190},
                {'keyword': '厨房调料架 壁挂式', 'score': 74.2, 'volume': 7100, 'sellers': 480},
            ],
        }
        
        if output.endswith('.html'):
            self._generate_html(report_data, output)
        elif output.endswith('.json'):
            self._generate_json(report_data, output)
        
        return {'path': output, 'data': report_data}
    
    def _generate_html(self, data: Dict, path: str):
        """生成 HTML 报告"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🌊 蓝海猎手分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0e27; color: #e0e0e0; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ text-align: center; font-size: 2.2em; margin-bottom: 10px; background: linear-gradient(135deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 40px; }}
        .card {{ background: #141832; border-radius: 16px; padding: 30px; margin-bottom: 24px; border: 1px solid #1e2448; }}
        .card h2 {{ font-size: 1.3em; margin-bottom: 20px; color: #00d4ff; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
        .summary-item {{ text-align: center; padding: 20px; border-radius: 12px; background: #1a1f40; }}
        .summary-item .number {{ font-size: 2.5em; font-weight: bold; }}
        .summary-item .label {{ font-size: 0.85em; color: #888; margin-top: 8px; }}
        .deep-blue .number {{ color: #00ff88; }}
        .light-blue .number {{ color: #00d4ff; }}
        .blue-green .number {{ color: #ffaa00; }}
        .red-ocean .number {{ color: #ff4444; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid #1e2448; }}
        th {{ color: #00d4ff; font-weight: 600; }}
        .score {{ font-weight: bold; font-size: 1.1em; }}
        .score.high {{ color: #00ff88; }}
        .score.mid {{ color: #00d4ff; }}
        .score.low {{ color: #ffaa00; }}
        .bar {{ height: 8px; border-radius: 4px; background: #1e2448; margin-top: 6px; }}
        .bar-fill {{ height: 100%; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 蓝海猎手分析报告</h1>
        <p class="subtitle">生成时间: {data['generated_at'][:19]}</p>
        
        <div class="card">
            <h2>📊 扫描概览</h2>
            <div class="summary-grid">
                <div class="summary-item deep-blue">
                    <div class="number">{data['summary']['deep_blue_found']}</div>
                    <div class="label">🟢 深蓝海</div>
                </div>
                <div class="summary-item light-blue">
                    <div class="number">{data['summary']['light_blue_found']}</div>
                    <div class="label">🔵 浅蓝海</div>
                </div>
                <div class="summary-item blue-green">
                    <div class="number">{data['summary']['blue_green_found']}</div>
                    <div class="label">🟡 蓝绿交界</div>
                </div>
                <div class="summary-item red-ocean">
                    <div class="number">{data['summary']['red_ocean_found']}</div>
                    <div class="label">🔴 红海</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🏆 Top 5 蓝海关键词</h2>
            <table>
                <tr><th>排名</th><th>关键词</th><th>蓝海指数</th><th>搜索量</th><th>卖家数</th></tr>
                {''.join(f'<tr><td>{i+1}</td><td>{kw["keyword"]}</td><td><span class="score high">{kw["score"]}</span></td><td>{kw["volume"]:,}</td><td>{kw["sellers"]:,}</td></tr>' for i, kw in enumerate(data['top_blue_ocean']))}
            </table>
        </div>
    </div>
</body>
</html>"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_json(self, data: Dict, path: str):
        """生成 JSON 报告"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
