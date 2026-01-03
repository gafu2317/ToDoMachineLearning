from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
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
    is_completed: bool = False
    
    def get_score(self) -> int:
        return self.base_duration_minutes * self.priority.value
    
    def is_overdue(self, current_time: datetime) -> bool:
        return current_time > self.deadline and not self.is_completed
    
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
            deadline=deadline
        )