import pytest
from datetime import datetime, timedelta
from src.models.task import Task, Priority
from src.models.concentration import ConcentrationModel
from config import CONCENTRATION_CONFIG


@pytest.fixture
def sample_tasks():
    """テスト用のサンプルタスク"""
    start_time = datetime(2024, 1, 1, 9, 0)
    tasks = []

    # 低重要度タスク
    task1 = Task(
        id=0,
        name="Low Priority Task",
        base_duration_minutes=30,
        priority=Priority.LOW,
        deadline=start_time + timedelta(days=1),
        genre='1'
    )

    # 中重要度タスク
    task2 = Task(
        id=1,
        name="Medium Priority Task",
        base_duration_minutes=60,
        priority=Priority.MEDIUM,
        deadline=start_time + timedelta(days=2),
        genre='2'
    )

    # 高重要度タスク
    task3 = Task(
        id=2,
        name="High Priority Task",
        base_duration_minutes=120,
        priority=Priority.HIGH,
        deadline=start_time + timedelta(days=3),
        genre='3'
    )

    tasks.extend([task1, task2, task3])
    return tasks


@pytest.fixture
def concentration_model():
    """テスト用の集中力モデル"""
    return ConcentrationModel(**CONCENTRATION_CONFIG)


@pytest.fixture
def start_time():
    """テスト用の開始時刻"""
    return datetime(2024, 1, 1, 9, 0)
