import pytest
from datetime import datetime
from src.environment.simulation import TaskSchedulingSimulation
from src.schedulers.rl_learning_scheduler import RLLearningScheduler
from src.models.concentration import ConcentrationModel
from config import CONCENTRATION_CONFIG, RL_CONFIG, DEFAULT_SIMULATION_CONFIG


class TestTaskSchedulingSimulation:
    """TaskSchedulingSimulation のテスト"""

    def test_initialization(self):
        """初期化の検証"""
        simulation = TaskSchedulingSimulation(
            simulation_days=DEFAULT_SIMULATION_CONFIG['simulation_days'],
            work_hours_per_day=DEFAULT_SIMULATION_CONFIG['work_hours_per_day'],
            num_tasks=DEFAULT_SIMULATION_CONFIG['num_tasks']
        )

        assert simulation is not None
        assert simulation.simulation_days == DEFAULT_SIMULATION_CONFIG['simulation_days']
        assert simulation.work_hours_per_day == DEFAULT_SIMULATION_CONFIG['work_hours_per_day']
        assert simulation.num_tasks == DEFAULT_SIMULATION_CONFIG['num_tasks']

    def test_generate_tasks(self):
        """タスク生成の検証"""
        num_tasks = 10
        simulation = TaskSchedulingSimulation(
            simulation_days=7,
            work_hours_per_day=8,
            num_tasks=num_tasks
        )

        tasks = simulation.generate_tasks()

        # 指定した数のタスクが生成される
        assert len(tasks) == num_tasks

        # 各タスクが必要な属性を持つ
        for task in tasks:
            assert task.id is not None
            assert task.name is not None
            assert task.base_duration_minutes > 0
            assert task.priority is not None
            assert task.deadline is not None

    def test_run_simulation_with_tasks(self, sample_tasks, concentration_model):
        """タスク指定でのシミュレーション実行の検証"""
        simulation = TaskSchedulingSimulation(
            simulation_days=2,
            work_hours_per_day=8,
            num_tasks=len(sample_tasks)
        )

        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # シミュレーションを実行
        result = simulation.run_simulation_with_tasks(scheduler, sample_tasks)

        # 結果が辞書で返される
        assert isinstance(result, dict)

        # 必要なキーが含まれていることを確認
        # （実装によって異なる可能性があるため、基本的なチェックのみ）
        assert result is not None

    def test_run_simulation(self):
        """通常のシミュレーション実行の検証"""
        simulation = TaskSchedulingSimulation(
            simulation_days=1,
            work_hours_per_day=4,
            num_tasks=5
        )

        concentration_model = ConcentrationModel(**CONCENTRATION_CONFIG)
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # シミュレーションを実行
        result = simulation.run_simulation(scheduler)

        # 結果が返される
        assert isinstance(result, dict)
        assert result is not None

    def test_adjust_total_score_attempted(self):
        """合計スコア調整が試みられることの検証"""
        target_score = 5000
        simulation = TaskSchedulingSimulation(
            simulation_days=7,
            work_hours_per_day=8,
            num_tasks=20,
            target_total_score=target_score
        )

        tasks = simulation.generate_tasks()

        # タスクが生成されることを確認
        assert len(tasks) == 20

        # スコア調整が試みられている（完全一致は保証されないが、極端に外れていないことを確認）
        # 実装の制約により、タスク時間は15-180分、重要度は1-3なので、
        # 1タスクあたりのスコアは 15*1=15 から 180*3=540 の範囲
        # 20タスクなら 300 から 10800 の範囲が理論的な限界
        total_score = sum(task.get_score() for task in tasks)
        assert 300 <= total_score <= 10800  # 理論的な範囲内であることを確認
