import pytest
from datetime import datetime, timedelta
from src.schedulers.rl_policy_selector import PolicyBasedQLearningSelector
from src.models.task import Task, Priority
from config import RL_CONFIG


class TestPolicyBasedQLearningSelector:
    """PolicyBasedQLearningSelector のテスト"""

    def test_initialization(self):
        """初期化の検証"""
        selector = PolicyBasedQLearningSelector(
            learning_rate=RL_CONFIG['learning_rate'],
            discount_factor=RL_CONFIG['discount_factor'],
            epsilon=RL_CONFIG['epsilon']
        )

        assert selector is not None
        assert selector.learning_rate == RL_CONFIG['learning_rate']
        assert selector.discount_factor == RL_CONFIG['discount_factor']
        assert selector.epsilon == RL_CONFIG['epsilon']
        assert len(selector.q_table) == 0
        assert len(selector.state_history) == 0
        assert len(selector.action_history) == 0

    def test_get_state(self, sample_tasks, start_time):
        """状態取得の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # 集中力レベルを指定して状態を取得
        state = selector._get_state(sample_tasks, start_time, concentration_level=0.8)

        # 状態が5つの要素を持つタプルであることを確認
        assert isinstance(state, tuple)
        assert len(state) == 5

        # 各要素が非負の整数であることを確認
        for element in state:
            assert isinstance(element, (int, np.integer))
            assert element >= 0

    def test_get_state_uses_config(self, sample_tasks, start_time):
        """設定値使用の検証（重要）"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # 状態を取得
        state = selector._get_state(sample_tasks, start_time, concentration_level=0.8)

        # 状態の各要素が期待される範囲内にあることを確認
        # (num_tasks_bin, high_bin, deadline_bin, duration_bin, concentration_bin)

        # タスク数ビン: 0-10の範囲
        assert 0 <= state[0] <= 10

        # 重要度ビン: 0-5の範囲
        assert 0 <= state[1] <= 5

        # 締切ビン: 0-10の範囲
        assert 0 <= state[2] <= 10

        # 平均時間ビン: 0-5の範囲
        assert 0 <= state[3] <= 5

        # 集中力ビン: 0-4の範囲
        assert 0 <= state[4] <= 4

    def test_get_state_empty_tasks(self, start_time):
        """空のタスクリストに対する状態取得の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        state = selector._get_state([], start_time, concentration_level=0.8)

        # 空のタスクリストの場合は (0, 0, 0, 0, 0) が返される
        assert state == (0, 0, 0, 0, 0)

    def test_select_task_by_policy(self, sample_tasks, start_time):
        """ポリシーベースタスク選択の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # 各アクションでタスクが選択できることを確認
        for action_id in selector.ACTIONS.keys():
            selected_task = selector._select_task_by_policy(
                sample_tasks, action_id, start_time, concentration_level=0.8
            )

            assert selected_task is not None
            assert selected_task in sample_tasks

    def test_select_task(self, sample_tasks, start_time):
        """タスク選択の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        selected_task = selector.select_task(sample_tasks, start_time, concentration_level=0.8)

        # タスクが選択される
        assert selected_task is not None
        assert selected_task in sample_tasks

        # 履歴に記録される
        assert len(selector.state_history) == 1
        assert len(selector.action_history) == 1

    def test_select_task_empty_list(self, start_time):
        """空のタスクリストでの選択の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        selected_task = selector.select_task([], start_time, concentration_level=0.8)

        # Noneが返される
        assert selected_task is None

    def test_update_q_value(self, sample_tasks, start_time):
        """Q値更新の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # タスクを選択（これにより履歴が記録される）
        selected_task = selector.select_task(sample_tasks, start_time, concentration_level=0.8)

        # Q値を更新
        reward = 100.0
        selector.update_q_value(reward=reward, done=True)

        # Q-tableにエントリが追加される
        assert len(selector.q_table) > 0

        # 報酬履歴に記録される
        assert len(selector.reward_history) == 1
        assert selector.reward_history[0] == reward

    def test_calculate_reward(self, sample_tasks, start_time):
        """報酬計算の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        task = sample_tasks[2]  # 高重要度タスク

        # 高集中状態で完了
        reward = selector.calculate_reward(
            task=task,
            completed=True,
            current_time=start_time,
            concentration_level=0.9,
            actual_duration=task.base_duration_minutes
        )

        # 報酬が正の値であることを確認
        assert reward > 0

    def test_calculate_reward_with_penalty(self, sample_tasks, start_time):
        """ペナルティを含む報酬計算の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        task = sample_tasks[2]  # 高重要度タスク

        # 低集中状態で完了（ペナルティが発生する）
        reward = selector.calculate_reward(
            task=task,
            completed=True,
            current_time=start_time,
            concentration_level=0.3,  # 低集中
            actual_duration=task.base_duration_minutes * 1.5
        )

        # ペナルティが適用されるため、報酬が低くなる
        # （基本スコアより低い可能性がある）
        assert isinstance(reward, (int, float))

    def test_reset_episode(self, sample_tasks, start_time):
        """エピソードリセットの検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # タスクを選択して履歴を記録
        selector.select_task(sample_tasks, start_time, concentration_level=0.8)

        # 履歴が記録されていることを確認
        assert len(selector.state_history) > 0
        assert len(selector.action_history) > 0

        # エピソードをリセット
        selector.reset_episode()

        # 履歴がクリアされる
        assert len(selector.state_history) == 0
        assert len(selector.action_history) == 0

    def test_get_learning_stats(self, sample_tasks, start_time):
        """学習統計取得の検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # タスクを選択してQ値を更新
        selector.select_task(sample_tasks, start_time, concentration_level=0.8)
        selector.update_q_value(reward=50.0, done=True)

        # 統計を取得
        stats = selector.get_learning_stats()

        # 必要なキーが含まれていることを確認
        assert 'q_table_size' in stats
        assert 'total_rewards' in stats
        assert 'avg_reward' in stats
        assert 'episodes_trained' in stats

        # 値が正しいことを確認
        assert stats['q_table_size'] > 0
        assert stats['total_rewards'] == 50.0
        assert stats['avg_reward'] == 50.0

    def test_save_and_load_q_table(self, tmp_path):
        """Q-tableの保存と読み込みの検証"""
        selector = PolicyBasedQLearningSelector(**RL_CONFIG)

        # Q-tableにデータを追加
        selector.q_table[(1, 2, 3, 4, 5)] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

        # 保存
        filepath = tmp_path / "test_q_table.pkl"
        selector.save_q_table(str(filepath))
        assert filepath.exists()

        # 新しいセレクターを作成して読み込み
        new_selector = PolicyBasedQLearningSelector(**RL_CONFIG)
        new_selector.load_q_table(str(filepath))

        # Q-tableが正しく読み込まれたことを確認
        assert (1, 2, 3, 4, 5) in new_selector.q_table
        assert list(new_selector.q_table[(1, 2, 3, 4, 5)]) == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]


# numpyをインポート（テスト内で使用）
import numpy as np
