from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import copy
from ..models.task import Task
from ..models.concentration import ConcentrationModel
from ..schedulers.scheduler import Scheduler
from config import TASK_GENERATION_CONFIG


class TaskSchedulingSimulation:
    """タスクスケジューリングシミュレーション環境"""
    
    def __init__(self, 
                 simulation_days: int = 7,
                 work_hours_per_day: int = 8,
                 num_tasks: int = None,
                 target_total_score: int = None):
        
        self.simulation_days = simulation_days
        self.work_hours_per_day = work_hours_per_day
        self.work_minutes_per_day = work_hours_per_day * 60
        self.total_work_minutes = simulation_days * self.work_minutes_per_day
        
        self.num_tasks = num_tasks or random.randint(50, 100)
        self.target_total_score = target_total_score
        
        self.start_time = datetime(2024, 1, 1, 9, 0)  # 固定開始時刻
        
    def generate_tasks(self) -> List[Task]:
        """バランスの取れたタスクセットを生成する"""
        from config import HIDDEN_PARAMETERS_CONFIG, GENRE_CONFIG
        hidden_config = HIDDEN_PARAMETERS_CONFIG

        # ジャンル適性をランダムに生成
        genre_affinities = {}
        if hidden_config['genre_affinity']['enabled']:
            for genre in GENRE_CONFIG['genres']:
                min_eff, max_eff = hidden_config['genre_affinity']['affinity_range']
                genre_affinities[genre] = random.uniform(min_eff, max_eff)

        tasks = []

        # 基本的なタスクを生成
        for i in range(self.num_tasks):
            task = Task.generate_random_task(i, self.start_time)

            # タスクに隠れパラメータを付与
            if hidden_config['enabled']:
                # 時間変動率
                variance_config = hidden_config['task_duration_variance']
                task._hidden_duration_multiplier = random.gauss(
                    variance_config['mean'],
                    variance_config['std']
                )
                task._hidden_duration_multiplier = max(
                    variance_config['min_multiplier'],
                    min(variance_config['max_multiplier'], task._hidden_duration_multiplier)
                )

                # ジャンル適性
                task._hidden_genre_affinity = genre_affinities.get(task.genre, 0.0)
            else:
                task._hidden_duration_multiplier = 1.0
                task._hidden_genre_affinity = 0.0

            tasks.append(task)

        # 合計スコアを調整（指定がある場合）
        if self.target_total_score:
            tasks = self._adjust_total_score(tasks, self.target_total_score)

        return tasks

    def _adjust_total_score(self, tasks: List[Task], target_score: int) -> List[Task]:
        """タスクの合計スコアを目標値に調整する"""
        current_score = sum(task.get_score() for task in tasks)

        if current_score == target_score:
            return tasks

        # 簡単な調整方法：最後のタスクの時間を変更
        if len(tasks) > 0:
            last_task = tasks[-1]
            score_diff = target_score - current_score
            duration_adjustment = score_diff // last_task.priority.value

            # 最小15分、最大180分の制限内で調整
            new_duration = max(15, min(180, last_task.base_duration_minutes + duration_adjustment))
            last_task.base_duration_minutes = new_duration

        return tasks
    
    def run_simulation(self, scheduler: Scheduler) -> Dict[str, Any]:
        """
        シミュレーションを実行する
        
        Args:
            scheduler: 使用するスケジューラー
            
        Returns:
            シミュレーション結果の辞書
        """
        # 初期化
        tasks = self.generate_tasks()
        return self.run_simulation_with_tasks(scheduler, tasks)
    
    def run_simulation_with_tasks(self, scheduler: Scheduler, tasks: List[Task]) -> Dict[str, Any]:
        """
        事前生成されたタスクセットでシミュレーションを実行する

        Args:
            scheduler: 使用するスケジューラー
            tasks: 実行するタスクのリスト

        Returns:
            シミュレーション結果の辞書
        """
        # タスクリストをディープコピーして、元のタスクに影響しないようにする
        tasks_copy = copy.deepcopy(tasks)
        
        # 初期化
        scheduler.reset()
        current_time = self.start_time
        current_day = 0
        current_day_work_time = 0
        
        completed_tasks = []
        total_work_time = 0
        total_break_time = 0
        simulation_log = []
        
        while current_day < self.simulation_days:
            # 1日の開始
            day_start_time = self.start_time + timedelta(days=current_day)
            current_time = day_start_time
            current_day_work_time = 0

            # 朝は集中力をリセット（新しい1日）
            scheduler.concentration_model.reset()
            
            while current_day_work_time < self.work_minutes_per_day:
                # 残り時間を計算
                remaining_time = self.work_minutes_per_day - current_day_work_time

                # 次のタスクを選択
                selected_task = scheduler.select_next_task(tasks_copy, current_time)

                # タスクが選択された場合、残り時間内に収まるかチェック
                if selected_task is not None:
                    # 現在の集中力レベルでの所要時間を見積もる
                    estimated_efficiency = scheduler.concentration_model.get_efficiency_multiplier()
                    estimated_duration = selected_task.base_duration_minutes * estimated_efficiency
                    if estimated_duration > remaining_time:
                        # 残り時間に収まらないので、このタスクはスキップ
                        selected_task = None

                if selected_task is None:
                    # 休憩が必要または作業可能なタスクがない
                    if scheduler.should_take_break():
                        break_duration = scheduler.take_break()
                        total_break_time += break_duration
                        current_time += timedelta(minutes=break_duration)
                        current_day_work_time += break_duration
                        
                        simulation_log.append({
                            'time': current_time.isoformat(),
                            'action': 'break',
                            'duration': break_duration
                        })
                    else:
                        # 作業可能なタスクがない
                        break
                else:
                    # タスクを実行
                    work_duration = scheduler.work_on_task(selected_task)
                    total_work_time += work_duration
                    current_time += timedelta(minutes=work_duration)
                    current_day_work_time += work_duration

                    if selected_task.is_completed:
                        completed_tasks.append(selected_task)

                    simulation_log.append({
                        'time': current_time.isoformat(),
                        'action': 'work',
                        'task_id': selected_task.id,
                        'duration': work_duration,
                        'base_duration': selected_task.base_duration_minutes,
                        'completed': selected_task.is_completed,
                        'concentration': scheduler.concentration_model.current_level
                    })
                
                # 1日の作業時間を超えた場合は終了
                if current_day_work_time >= self.work_minutes_per_day:
                    break
            
            current_day += 1
        
        # 結果を計算
        return self._calculate_results(tasks_copy, completed_tasks, total_work_time, total_break_time, simulation_log)
    
    def _calculate_results(self,
                          all_tasks: List[Task],
                          completed_tasks: List[Task],
                          total_work_time: float,
                          total_break_time: float,
                          simulation_log: List[Dict]) -> Dict[str, Any]:
        """シミュレーション結果を計算する"""

        # 完了タスクのスコア
        total_score = sum(task.get_score() for task in completed_tasks)

        # 未完了タスクの分析
        incomplete_tasks = [task for task in all_tasks if not task.is_completed]
        overdue_tasks = [task for task in incomplete_tasks
                        if task.is_overdue(self.start_time + timedelta(days=self.simulation_days))]

        # 締切遵守率
        tasks_with_deadline = [task for task in completed_tasks
                              if task.deadline <= self.start_time + timedelta(days=self.simulation_days)]
        deadline_compliance_rate = len(tasks_with_deadline) / len(all_tasks) if all_tasks else 0
        
        return {
            'total_score': total_score,
            'completed_tasks_count': len(completed_tasks),
            'incomplete_tasks_count': len(incomplete_tasks),
            'overdue_tasks_count': len(overdue_tasks),
            'completion_rate': len(completed_tasks) / len(all_tasks) if all_tasks else 0,
            'deadline_compliance_rate': deadline_compliance_rate,
            'total_work_time': total_work_time,
            'total_break_time': total_break_time,
            'efficiency': total_work_time / (total_work_time + total_break_time) if (total_work_time + total_break_time) > 0 else 0,
            'tasks': {
                'total': len(all_tasks),
                'completed': [{'id': t.id, 'score': t.get_score(), 'priority': t.priority.name} for t in completed_tasks],
                'incomplete': [{'id': t.id, 'score': t.get_score(), 'priority': t.priority.name} for t in incomplete_tasks]
            },
            'simulation_log': simulation_log
        }