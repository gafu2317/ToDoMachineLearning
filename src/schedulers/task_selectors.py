from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import random
from ..models.task import Task


class TaskSelector(ABC):
    """タスク選択戦略の基底クラス"""
    
    @abstractmethod
    def select_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        """
        未完了タスクから次に実行するタスクを選択する
        
        Args:
            tasks: 未完了タスクのリスト
            current_time: 現在時刻
            
        Returns:
            選択されたタスク。タスクがない場合はNone
        """
        pass


class DeadlineTaskSelector(TaskSelector):
    """期限順タスク選択戦略"""
    
    def select_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        if not tasks:
            return None
        
        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if not incomplete_tasks:
            return None
        
        # 締切順でソート
        sorted_tasks = sorted(incomplete_tasks, key=lambda task: task.deadline)
        return sorted_tasks[0]


class PriorityTaskSelector(TaskSelector):
    """重要度順タスク選択戦略"""
    
    def select_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        if not tasks:
            return None
        
        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if not incomplete_tasks:
            return None
        
        # 重要度順（高い順）でソート、同じ重要度の場合は締切順
        sorted_tasks = sorted(incomplete_tasks, 
                             key=lambda task: (-task.priority.value, task.deadline))
        return sorted_tasks[0]


class RandomTaskSelector(TaskSelector):
    """ランダムタスク選択戦略"""
    
    def select_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        if not tasks:
            return None
        
        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if not incomplete_tasks:
            return None
        
        return random.choice(incomplete_tasks)