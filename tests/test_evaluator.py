import pytest
from src.evaluation.evaluator import SchedulerEvaluator


class TestSchedulerEvaluator:
    """SchedulerEvaluator の基本テスト"""

    def test_initialization(self):
        """初期化の検証"""
        evaluator = SchedulerEvaluator(
            num_experiments=10,
            simulation_days=7,
            work_hours_per_day=8,
            num_tasks=20
        )

        assert evaluator is not None
        assert evaluator.num_experiments == 10
        assert evaluator.simulation_days == 7
        assert evaluator.work_hours_per_day == 8
        assert evaluator.num_tasks == 20

    def test_initialization_defaults(self):
        """デフォルト値での初期化の検証"""
        evaluator = SchedulerEvaluator()

        assert evaluator is not None
        assert evaluator.num_experiments == 100
        assert evaluator.simulation_days == 7
        assert evaluator.work_hours_per_day == 8
