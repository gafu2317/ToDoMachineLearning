from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Set
import random
from config import TASK_DIFFICULTY_CONFIG, TASK_GENERATION_CONFIG


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    id: int
    name: str
    base_duration_minutes: int
    priority: Priority
    deadline: datetime
    difficulty: int = 1  # 難易度 1(簡単) ~ 3(難しい)
    is_completed: bool = False
    dependencies: List[int] = field(default_factory=list)  # 依存タスクのIDリスト
    
    def get_score(self) -> int:
        return self.base_duration_minutes * self.priority.value
    
    def is_overdue(self, current_time: datetime) -> bool:
        return current_time > self.deadline and not self.is_completed

    def is_ready_to_start(self, completed_task_ids: Set[int]) -> bool:
        """
        依存タスクが全て完了しているか確認

        Args:
            completed_task_ids: 完了済みタスクのIDセット

        Returns:
            実行可能ならTrue
        """
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)
    
    @staticmethod
    def generate_random_task(task_id: int, current_time: datetime) -> 'Task':
        name = f"Task_{task_id}"

        config = TASK_GENERATION_CONFIG

        # 時間分布: 短時間が多め
        rand = random.random()
        if rand < config['short_task_ratio']:
            base_duration = random.randint(config['short_task_min'], config['short_task_max'])
        elif rand < config['short_task_ratio'] + config['medium_task_ratio']:
            base_duration = random.randint(config['short_task_max'], config['medium_task_max'])
        else:
            base_duration = random.randint(config['medium_task_max'], config['long_task_max'])

        # 重要度分布: LOWが多め
        rand = random.random()
        if rand < config['priority_low_ratio']:
            priority = Priority.LOW
        elif rand < config['priority_low_ratio'] + config['priority_medium_ratio']:
            priority = Priority.MEDIUM
        else:
            priority = Priority.HIGH

        # 難易度: 重要度と相関（重要なタスクほど難しい傾向）
        difficulty_rand = random.random()
        if priority == Priority.HIGH:
            # 重要度高: 難しいタスクが多い
            if difficulty_rand < 0.6:  # 60%
                difficulty = 3
            elif difficulty_rand < 0.9:  # 30%
                difficulty = 2
            else:  # 10%
                difficulty = 1
        elif priority == Priority.MEDIUM:
            # 重要度中: 普通のタスクが多い
            if difficulty_rand < 0.6:  # 60%
                difficulty = 2
            elif difficulty_rand < 0.8:  # 20%
                difficulty = 3
            else:  # 20%
                difficulty = 1
        else:  # Priority.LOW
            # 重要度低: 簡単なタスクが多い
            if difficulty_rand < 0.7:  # 70%
                difficulty = 1
            elif difficulty_rand < 0.9:  # 20%
                difficulty = 2
            else:  # 10%
                difficulty = 3
        
        # 締切: 時間と重要度の両方を考慮（より余裕を持たせる）
        time_factor = base_duration / 60  # 時間の影響
        priority_factor = priority.value  # 重要度の影響
        base_days = 3 + time_factor * 2 + priority_factor * 2  # 締切を緩和（5～13日後）
        deadline = current_time + timedelta(days=base_days)
        
        return Task(
            id=task_id,
            name=name,
            base_duration_minutes=base_duration,
            priority=priority,
            deadline=deadline,
            difficulty=difficulty
        )