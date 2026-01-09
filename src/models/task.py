from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Set
import random


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
    failed_attempts: int = 0  # 失敗回数
    dependencies: List[int] = field(default_factory=list)  # 依存タスクのIDリスト
    
    def get_score(self) -> int:
        return self.base_duration_minutes * self.priority.value
    
    def is_overdue(self, current_time: datetime) -> bool:
        return current_time > self.deadline and not self.is_completed

    def can_execute_successfully(self, concentration_level: float) -> bool:
        """
        現在の集中力でタスクを成功できるか判定

        Args:
            concentration_level: 現在の集中力レベル (0.0 ~ 1.0)

        Returns:
            成功確率が50%以上ならTrue
        """
        # 必要な集中力レベル（難易度に応じて）
        required_concentration = {
            1: 0.3,  # 簡単なタスク: 30%以上で成功
            2: 0.6,  # 普通のタスク: 60%以上で成功
            3: 0.8,  # 難しいタスク: 80%以上で成功
        }

        return concentration_level >= required_concentration.get(self.difficulty, 0.5)

    def get_success_probability(self, concentration_level: float) -> float:
        """
        現在の集中力での成功確率を取得

        Args:
            concentration_level: 現在の集中力レベル (0.0 ~ 1.0)

        Returns:
            成功確率 (0.0 ~ 1.0)
        """
        # 必要な集中力レベル
        required_concentration = {
            1: 0.3,
            2: 0.6,
            3: 0.8,
        }.get(self.difficulty, 0.5)

        # 集中力が要件を満たしていれば成功確率は高い
        if concentration_level >= required_concentration:
            return min(1.0, 0.7 + (concentration_level - required_concentration) * 2)
        else:
            # 要件を満たしていない場合は低い成功確率
            return max(0.1, concentration_level / required_concentration * 0.5)

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
        
        # 時間分布: 短時間が多め
        rand = random.random()
        if rand < 0.7:  # 70%
            base_duration = random.randint(15, 60)
        elif rand < 0.9:  # 20%
            base_duration = random.randint(60, 120)
        else:  # 10%
            base_duration = random.randint(120, 180)
        
        # 重要度分布: LOWが多め
        rand = random.random()
        if rand < 0.6:  # 60%
            priority = Priority.LOW
        elif rand < 0.85:  # 25%
            priority = Priority.MEDIUM
        else:  # 15%
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
        
        # 締切: 時間と重要度の両方を考慮
        time_factor = base_duration / 60  # 時間の影響
        priority_factor = priority.value  # 重要度の影響
        base_days = 1 + time_factor + priority_factor
        deadline = current_time + timedelta(days=base_days)
        
        return Task(
            id=task_id,
            name=name,
            base_duration_minutes=base_duration,
            priority=priority,
            deadline=deadline,
            difficulty=difficulty
        )