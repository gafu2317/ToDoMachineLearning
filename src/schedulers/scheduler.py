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
    
    def work_on_task(self, task: Task) -> float:
        """
        タスクを実行し、集中力に応じた実際の所要時間を返す

        Args:
            task: 実行するタスク

        Returns:
            実際の所要時間（分）
        """
        # ジャンル切り替えによる集中力への影響を適用
        self.concentration_model.apply_genre_switch_effect(task.genre)

        # 集中力に応じた作業効率を取得
        efficiency = self.concentration_model.work(task.base_duration_minutes)
        actual_duration = task.base_duration_minutes * efficiency

        # タスクは常に完了する
        task.is_completed = True

        return actual_duration
    
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