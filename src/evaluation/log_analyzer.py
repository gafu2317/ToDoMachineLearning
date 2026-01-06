from typing import Dict, List, Any
from datetime import datetime, timedelta
import os


class SimulationLogAnalyzer:
    """シミュレーションログを人間が理解しやすい形で分析・出力するクラス"""
    
    def __init__(self):
        pass
    
    def generate_daily_schedule_report(self, 
                                     simulation_result: Dict[str, Any],
                                     scheduler_name: str,
                                     save_path: str = None) -> str:
        """
        1日ごとのスケジュール詳細レポートを生成
        
        Args:
            simulation_result: シミュレーション結果の辞書
            scheduler_name: スケジューラー名
            save_path: 保存パス（Noneの場合は保存しない）
            
        Returns:
            レポート文字列
        """
        
        simulation_log = simulation_result.get('simulation_log', [])
        completed_tasks = simulation_result.get('tasks', {}).get('completed', [])
        incomplete_tasks = simulation_result.get('tasks', {}).get('incomplete', [])
        
        report = []
        report.append(f"# {scheduler_name} - 詳細スケジュールレポート")
        report.append("")
        report.append(f"## 実験概要")
        report.append(f"- 総スコア: {simulation_result['total_score']}")
        report.append(f"- 完了タスク数: {simulation_result['completed_tasks_count']}")
        report.append(f"- 未完了タスク数: {simulation_result['incomplete_tasks_count']}")
        report.append(f"- 完了率: {simulation_result['completion_rate']:.1%}")
        report.append(f"- 総作業時間: {simulation_result['total_work_time']:.0f}分")
        report.append(f"- 総休憩時間: {simulation_result['total_break_time']:.0f}分")
        report.append("")
        
        # ログをタイムスタンプでソート
        sorted_log = sorted(simulation_log, key=lambda x: x['time'])
        
        # 日ごとにグループ化
        daily_logs = self._group_by_day(sorted_log)
        
        # 各日のレポート生成
        for day_num, day_log in enumerate(daily_logs, 1):
            report.append(f"## 第{day_num}日目")
            report.append("")
            
            day_total_work = 0
            day_total_break = 0
            day_tasks_completed = 0
            
            for entry in day_log:
                time_str = self._format_time(entry['time'])
                
                if entry['action'] == 'work':
                    task_id = entry['task_id']
                    duration = entry['duration']
                    completed = entry['completed']
                    concentration = entry['concentration']
                    
                    # 完了タスクから詳細情報を取得
                    task_info = self._get_task_info(task_id, completed_tasks, incomplete_tasks)
                    
                    status = "✅ 完了" if completed else "⏳ 作業中"
                    
                    report.append(f"**{time_str}** - {status}")
                    report.append(f"- タスク: {task_info['name']} (ID: {task_id})")
                    report.append(f"- 重要度: {task_info['priority']} (スコア: {task_info['score']})")
                    report.append(f"- 作業時間: {duration:.0f}分")
                    report.append(f"- 集中レベル: {concentration:.2f}")
                    report.append("")
                    
                    day_total_work += duration
                    if completed:
                        day_tasks_completed += 1
                        
                elif entry['action'] == 'break':
                    duration = entry['duration']
                    report.append(f"**{time_str}** - 🛌 休憩")
                    report.append(f"- 休憩時間: {duration:.0f}分")
                    report.append("")
                    
                    day_total_break += duration
            
            # 日次サマリー
            report.append(f"### 第{day_num}日目サマリー")
            report.append(f"- 作業時間: {day_total_work:.0f}分")
            report.append(f"- 休憩時間: {day_total_break:.0f}分")
            report.append(f"- 完了タスク数: {day_tasks_completed}")
            total_day_time = day_total_work + day_total_break
            if total_day_time > 0:
                work_ratio = day_total_work / total_day_time
                report.append(f"- 作業効率: {work_ratio:.1%}")
            report.append("")
        
        # 完了タスク一覧
        if completed_tasks:
            report.append("## 完了タスク一覧")
            report.append("")
            total_score = 0
            for task in completed_tasks:
                report.append(f"- **{task['id']}**: 重要度{task['priority']}, スコア{task['score']}")
                total_score += task['score']
            report.append(f"\n**合計スコア: {total_score}**")
            report.append("")
        
        # 未完了タスク一覧
        if incomplete_tasks:
            report.append("## 未完了タスク一覧")
            report.append("")
            for task in incomplete_tasks:
                report.append(f"- **{task['id']}**: 重要度{task['priority']}, スコア{task['score']}")
            report.append("")
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def _group_by_day(self, simulation_log: List[Dict]) -> List[List[Dict]]:
        """ログを日ごとにグループ化"""
        daily_logs = []
        current_day_log = []
        current_date = None
        
        for entry in simulation_log:
            entry_datetime = datetime.fromisoformat(entry['time'])
            entry_date = entry_datetime.date()
            
            if current_date is None:
                current_date = entry_date
            
            if entry_date == current_date:
                current_day_log.append(entry)
            else:
                # 新しい日
                if current_day_log:
                    daily_logs.append(current_day_log)
                current_day_log = [entry]
                current_date = entry_date
        
        # 最後の日のログを追加
        if current_day_log:
            daily_logs.append(current_day_log)
        
        return daily_logs
    
    def _format_time(self, time_str: str) -> str:
        """時刻文字列をフォーマット"""
        dt = datetime.fromisoformat(time_str)
        return dt.strftime("%H:%M")
    
    def _get_task_info(self, task_id: int, completed_tasks: List, incomplete_tasks: List) -> Dict:
        """タスクIDから詳細情報を取得"""
        all_tasks = completed_tasks + incomplete_tasks
        
        for task in all_tasks:
            if task['id'] == task_id:
                return {
                    'name': f"Task_{task_id}",
                    'priority': task['priority'],
                    'score': task['score']
                }
        
        # 見つからない場合のデフォルト
        return {
            'name': f"Task_{task_id}",
            'priority': "Unknown",
            'score': 0
        }