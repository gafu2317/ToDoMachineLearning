from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random
from config import TASK_GENERATION_CONFIG


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
    genre: str = '1'  # ジャンル（数字タグ）

    def get_score(self) -> int:
        return self.base_duration_minutes * self.priority.value

    def is_overdue(self, current_time: datetime) -> bool:
        return current_time > self.deadline and not self.is_completed
    
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

        # 締切: 時間と重要度の両方を考慮（より余裕を持たせる）
        time_factor = base_duration / 60  # 時間の影響
        priority_factor = priority.value  # 重要度の影響
        base_days = 3 + time_factor * 2 + priority_factor * 2  # 締切を緩和（5～13日後）
        deadline = current_time + timedelta(days=base_days)

        # ジャンルをランダムに割り当て
        from config import GENRE_CONFIG
        genre_config = GENRE_CONFIG
        genres = genre_config['genres']
        distribution = genre_config['genre_distribution']

        # 確率分布に従ってジャンルを選択
        rand = random.random()
        cumulative = 0
        selected_genre = genres[0]
        for genre in genres:
            cumulative += distribution[genre]
            if rand < cumulative:
                selected_genre = genre
                break

        return Task(
            id=task_id,
            name=name,
            base_duration_minutes=base_duration,
            priority=priority,
            deadline=deadline,
            genre=selected_genre
        )