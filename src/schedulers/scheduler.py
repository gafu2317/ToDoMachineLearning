from typing import List, Optional
from datetime import datetime
import random
from .task_selectors import TaskSelector
from .break_strategies import BreakStrategy
from ..models.task import Task
from ..models.concentration import ConcentrationModel


class Scheduler:
    """戦略パターンを使ったスケジューラー"""
    
    def __init__(self, task_selector: TaskSelector, break_strategy: BreakStrategy):
        self.task_selector = task_selector
        self.break_strategy = break_strategy
        self.concentration_model = break_strategy.concentration_model
    
    def select_next_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        """
        次に実行するタスクを選択する
        休憩時間中の場合はNoneを返す
        """
        if self.break_strategy.should_take_break():
            return None
            
        return self.task_selector.select_task(tasks, current_time)
    
    def work_on_task(self, task: Task) -> tuple[float, bool]:
        """
        タスクを実行し、集中力に応じた実際の所要時間と成功・失敗を返す

        Args:
            task: 実行するタスク

        Returns:
            (実際の所要時間（分）, 成功したかどうか)
        """
        current_concentration = self.concentration_model.current_level

        # 成功確率を計算
        success_probability = task.get_success_probability(current_concentration)

        # 成功・失敗を判定
        succeeded = random.random() < success_probability

        # 作業時間は失敗しても消費する
        efficiency = self.concentration_model.work(task.base_duration_minutes)
        actual_duration = task.base_duration_minutes * efficiency

        if succeeded:
            task.is_completed = True
        else:
            task.failed_attempts += 1

        return actual_duration, succeeded
    
    def should_take_break(self) -> bool:
        """休憩を取るべきかどうかを判定する"""
        return self.break_strategy.should_take_break()
    
    def take_break(self) -> int:
        """
        休憩を取る
        
        Returns:
            休憩時間（分）
        """
        break_duration = self.break_strategy.get_break_duration()
        self.concentration_model.rest(break_duration)
        return break_duration
    
    def reset(self):
        """スケジューラーの状態をリセットする"""
        self.concentration_model.reset()
        self.break_strategy.reset()