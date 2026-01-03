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
        base_duration = random.randint(15, 180)  # 15分-3時間
        priority = random.choice(list(Priority))
        
        # 締切は1-7日後
        deadline_days = random.randint(1, 7)
        deadline = current_time + timedelta(days=deadline_days)
        
        return Task(
            id=task_id,
            name=name,
            base_duration_minutes=base_duration,
            priority=priority,
            deadline=deadline
        )