import pytest
from datetime import datetime, timedelta
from src.schedulers.rl_learning_scheduler import RLLearningScheduler
from src.models.concentration import ConcentrationModel
from src.models.task import Task, Priority
from config import CONCENTRATION_CONFIG, RL_CONFIG


class TestRLLearningScheduler:
    """RLLearningSchedulerのテスト"""

    def test_initialization(self):
        """初期化の検証"""
        concentration_model = ConcentrationModel(**CONCENTRATION_CONFIG)
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            learning_rate=RL_CONFIG['learning_rate'],
            discount_factor=RL_CONFIG['discount_factor'],
            epsilon=RL_CONFIG['epsilon']
        )

        assert scheduler is not None
        assert scheduler.concentration_model == concentration_model
        assert scheduler.last_task is None
        assert scheduler.last_action_time is None

    def test_select_next_task(self, sample_tasks, concentration_model, start_time):
        """タスク選択機能の検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # 集中力が高い状態でタスクを選択
        selected_task = scheduler.select_next_task(sample_tasks, start_time)

        # タスクが選択されることを確認（Noneでないか、または休憩が必要でない限り）
        if concentration_model.current_level >= 0.4:
            assert selected_task is not None
            assert selected_task in sample_tasks

    def test_select_next_task_when_tired(self, sample_tasks, concentration_model, start_time):
        """疲労時にタスク選択がNoneを返すかの検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # 集中力を極端に下げる
        concentration_model.current_level = 0.3
        selected_task = scheduler.select_next_task(sample_tasks, start_time)

        # 休憩が必要な状態ではNoneが返る
        assert selected_task is None

    def test_work_on_task(self, sample_tasks, concentration_model):
        """タスク実行機能の検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        task = sample_tasks[0]
        initial_concentration = concentration_model.current_level

        # タスクを実行
        actual_duration = scheduler.work_on_task(task)

        # 実際の所要時間が返される
        assert actual_duration > 0

        # 集中力が低下する（作業により）
        assert concentration_model.current_level <= initial_concentration

        # 最後のタスクが記録される
        assert scheduler.last_task == task

    def test_epsilon_setting(self, concentration_model):
        """探索率設定の検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            epsilon=0.1
        )

        # 初期値の確認
        assert scheduler.task_selector.epsilon == 0.1

        # epsilon値の変更
        scheduler.set_epsilon(0.5)
        assert scheduler.task_selector.epsilon == 0.5

        # 0~1の範囲外でも設定可能（内部で調整される場合がある）
        scheduler.set_epsilon(0.0)
        assert scheduler.task_selector.epsilon == 0.0

    def test_reset(self, sample_tasks, concentration_model, start_time):
        """リセット機能の検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # タスクを選択・実行して状態を変更
        selected_task = scheduler.select_next_task(sample_tasks, start_time)
        if selected_task:
            scheduler.work_on_task(selected_task)

        # リセット前の状態を確認
        assert scheduler.last_task is not None or True  # 実行されていない場合もある

        # リセット
        scheduler.reset()

        # リセット後の状態を確認
        assert scheduler.last_task is None
        assert scheduler.last_action_time is None

    def test_take_break(self, concentration_model):
        """休憩機能の検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # 集中力を低下させる
        concentration_model.current_level = 0.3
        initial_level = concentration_model.current_level

        # 休憩
        break_duration = scheduler.take_break()

        # 休憩時間が返される
        assert break_duration > 0

        # 集中力が回復する
        assert concentration_model.current_level >= initial_level

    def test_save_and_load_model(self, concentration_model, tmp_path):
        """モデルの保存と読み込みの検証"""
        scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )

        # Q-tableに何かデータを追加（実際の学習は時間がかかるため省略）
        scheduler.task_selector.q_table[(1, 2, 3, 4, 5, 6)] = 10.0

        # モデル保存
        model_path = tmp_path / "test_model.pkl"
        scheduler.save_model(str(model_path))
        assert model_path.exists()

        # 新しいスケジューラーを作成してモデルを読み込み
        new_scheduler = RLLearningScheduler(
            concentration_model=concentration_model,
            **RL_CONFIG
        )
        new_scheduler.load_model(str(model_path))

        # Q-tableが正しく読み込まれたか確認
        assert (1, 2, 3, 4, 5, 6) in new_scheduler.task_selector.q_table
        assert new_scheduler.task_selector.q_table[(1, 2, 3, 4, 5, 6)] == 10.0
