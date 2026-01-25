"""
改良版Q-learning: ポリシーベースのタスク選択
アクション = どの基準でタスクを選ぶか（重要度、締切、時間など）
"""
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from .task_selectors import TaskSelector
from ..models.task import Task, Priority
from config import SCHEDULING_CONFIG, RL_REWARD_CONFIG


class PolicyBasedQLearningSelector(TaskSelector):
    """ポリシーベースQ-learningタスク選択戦略"""

    # アクション定義: どの基準でタスクを選ぶか
    ACTIONS = {
        0: "highest_priority",           # 最も重要度が高いタスク
        1: "nearest_deadline",            # 最も締切が近いタスク
        2: "shortest_task",               # 最も短時間で終わるタスク
        3: "highest_score",               # 最もスコアが高いタスク
        4: "priority_deadline_mix",       # 重要度と締切のバランス
        5: "concentration_matched",       # 集中力に合った難易度のタスク
        6: "safe_high_priority",          # 成功確率が高い重要タスク
    }

    def __init__(self,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.1):

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Q-table: state -> action -> Q値
        self.q_table = {}

        # 学習用の履歴
        self.state_history = []
        self.action_history = []
        self.reward_history = []

    def select_task(self, tasks: List[Task], current_time: datetime, concentration_level: float = 1.0) -> Optional[Task]:
        """Q-learningによりタスクを選択"""

        if not tasks:
            return None

        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if not incomplete_tasks:
            return None

        ready_tasks = incomplete_tasks

        # 締切チェック：現在時刻 + タスク所要時間 <= 締切のタスクのみ
        from datetime import timedelta
        feasible_tasks = []
        for task in ready_tasks:
            estimated_completion = current_time + timedelta(minutes=task.base_duration_minutes)
            if estimated_completion <= task.deadline:
                feasible_tasks.append(task)

        # 締切に間に合うタスクがない場合でも、何かを返す
        # （全タスクが締切オーバーでも作業は続けるため）
        if not feasible_tasks:
            feasible_tasks = ready_tasks

        ready_tasks = feasible_tasks

        # 状態を取得（集中力レベルを含む）
        state = self._get_state(ready_tasks, current_time, concentration_level)

        # ε-greedy探索
        if np.random.random() < self.epsilon:
            # ランダム探索
            action = np.random.randint(0, len(self.ACTIONS))
        else:
            # Q値最大の行動を選択
            action = self._get_best_action(state)

        # アクションに基づいてタスクを選択（依存関係を満たすタスクから）
        selected_task = self._select_task_by_policy(
            ready_tasks, action, current_time, concentration_level
        )

        # 履歴に記録
        self.state_history.append(state)
        self.action_history.append(action)

        return selected_task

    def _get_state(self, tasks: List[Task], current_time: datetime, concentration_level: float = 1.0) -> Tuple:
        """現在の状態を取得（改良版）"""

        if not tasks:
            return (0, 0, 0, 0, 0)

        # タスク数の区間
        num_tasks_bin = min(len(tasks) // 10, 10)  # 0-10区間

        # 重要度分布
        high_ratio = sum(1 for t in tasks if t.priority == Priority.HIGH) / len(tasks)
        high_bin = int(high_ratio * 5)  # 0-5区間

        # 締切の緊急度
        min_deadline_hours = min(
            max(0, (task.deadline - current_time).total_seconds() / 3600)
            for task in tasks
        )
        deadline_bin = min(int(min_deadline_hours / 12), 10)  # 12時間ごと、0-10区間

        # タスクの平均時間
        avg_duration = np.mean([t.base_duration_minutes for t in tasks])
        duration_bin = min(int(avg_duration / 20), 5)  # 20分ごと、0-5区間

        # 集中力レベル
        concentration_bin = int(concentration_level * 4)  # 0-4区間（0.0-0.25, 0.25-0.5, 0.5-0.75, 0.75-1.0）

        # NOTE: 依存関係情報は既にready_tasksのフィルタリングで考慮済み
        # 状態空間は変更しない（既存モデルとの互換性維持）
        return (num_tasks_bin, high_bin, deadline_bin, duration_bin, concentration_bin)

    def _select_task_by_policy(self, tasks: List[Task], action: int, current_time: datetime, concentration_level: float = 1.0) -> Task:
        """ポリシーに基づいてタスクを選択"""

        policy = self.ACTIONS[action]
        config = SCHEDULING_CONFIG

        # まず、実行可能なタスクを優先
        # 長時間タスクは時間の余裕がある状態でのみ選択
        short_tasks = [t for t in tasks if t.base_duration_minutes <= config['short_task_threshold']]
        medium_tasks = [t for t in tasks if t.base_duration_minutes <= config['medium_task_threshold']]

        # 選択候補: 短いタスクを優先、なければ中程度、なければ全体
        candidate_tasks = short_tasks if short_tasks else (medium_tasks if medium_tasks else tasks)

        if policy == "highest_priority":
            # 重要度が最も高いタスク
            return max(candidate_tasks, key=lambda t: (t.priority.value, -t.deadline.timestamp()))

        elif policy == "nearest_deadline":
            # 締切が最も近いタスク
            return min(candidate_tasks, key=lambda t: t.deadline)

        elif policy == "shortest_task":
            # 最も短時間で終わるタスク
            return min(candidate_tasks, key=lambda t: t.base_duration_minutes)

        elif policy == "highest_score":
            # スコアが最も高いタスク
            return max(candidate_tasks, key=lambda t: t.get_score())

        elif policy == "priority_deadline_mix":
            # 重要度と締切のバランス
            seconds_per_day = config['seconds_per_day']

            def urgency_score(t):
                days_until_deadline = (t.deadline - current_time).total_seconds() / seconds_per_day
                urgency = 1.0 / max(days_until_deadline, 0.1)  # 締切が近いほど高い
                return t.priority.value * 2 + urgency

            return max(candidate_tasks, key=urgency_score)

        elif policy == "concentration_matched":
            # 集中力に合った難易度のタスクを選ぶ
            # 集中力が高い時は難しいタスク、低い時は簡単なタスクを選ぶ
            def concentration_match_score(t):
                # 集中力閾値との距離を計算
                thresholds = {1: 0.3, 2: 0.6, 3: 0.8}
                required = thresholds.get(t.difficulty, 0.5)

                # 集中力が要件を満たしている場合、スコアが高いタスクを優先
                if concentration_level >= required:
                    return t.get_score() * (1.0 + (concentration_level - required))
                else:
                    # 集中力不足の場合はペナルティ
                    return t.get_score() * (concentration_level / required)

            return max(candidate_tasks, key=concentration_match_score)

        elif policy == "safe_high_priority":
            # 集中力に対して適切な難易度のタスクの中で、重要度が高いものを選ぶ
            thresholds = {1: 0.3, 2: 0.6, 3: 0.8}
            safe_tasks = [t for t in candidate_tasks
                         if concentration_level >= thresholds.get(t.difficulty, 0.5)]

            if safe_tasks:
                return max(safe_tasks, key=lambda t: (t.priority.value, t.get_score()))
            else:
                # 適切なタスクがない場合は最も簡単なタスクを選ぶ
                return min(candidate_tasks, key=lambda t: t.difficulty)

        # デフォルト: 最初のタスク
        return candidate_tasks[0] if candidate_tasks else tasks[0]

    def _get_best_action(self, state: Tuple) -> int:
        """状態に対して最適な行動を取得"""

        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.ACTIONS))

        return np.argmax(self.q_table[state])

    def update_q_value(self, reward: float, next_state: Tuple = None, done: bool = False):
        """Q値を更新"""

        if len(self.state_history) < 1:
            return

        current_state = self.state_history[-1]
        current_action = self.action_history[-1]

        # 現在の状態のQ-tableを初期化（必要なら）
        if current_state not in self.q_table:
            self.q_table[current_state] = np.zeros(len(self.ACTIONS))

        current_q = self.q_table[current_state][current_action]

        if done or next_state is None:
            # 終了状態
            target_q = reward
        else:
            # 次状態の最大Q値を取得
            if next_state not in self.q_table:
                next_max_q = 0
            else:
                next_max_q = np.max(self.q_table[next_state])

            target_q = reward + self.discount_factor * next_max_q

        # Q値更新
        self.q_table[current_state][current_action] = (
            current_q + self.learning_rate * (target_q - current_q)
        )

        # 報酬履歴に記録
        self.reward_history.append(reward)

    def calculate_reward(self,
                        task: Task,
                        completed: bool,
                        current_time: datetime,
                        concentration_level: float,
                        actual_duration: float = None) -> float:
        """報酬を計算（時間効率ベース）"""
        config = RL_REWARD_CONFIG

        # 基本完了報酬（スコアベース）
        reward = task.get_score()

        # 高集中完了ボーナス（効率的に作業できた）
        if concentration_level > config['high_concentration_threshold']:
            reward += config['high_concentration_bonus']

        # 難易度ボーナス（難しいタスクを高集中で完了した場合）
        if task.difficulty == 3 and concentration_level >= config['difficulty_bonus_threshold']:
            reward += config['difficulty_bonus']

        # 効率ペナルティ（集中力不足で時間がかかった場合）
        if actual_duration and actual_duration > task.base_duration_minutes:
            # 余分にかかった時間分をペナルティ
            extra_time = actual_duration - task.base_duration_minutes
            reward -= extra_time * 0.5

        # 集中力が足りないのに難しいタスクを選んだ場合はペナルティ
        thresholds = {1: 0.3, 2: 0.6, 3: 0.8}
        required = thresholds.get(task.difficulty, 0.5)
        if concentration_level < required:
            reward -= config['reckless_attempt_penalty']

        return reward

    def reset_episode(self):
        """エピソード終了時のリセット"""
        self.state_history = []
        self.action_history = []

    def get_learning_stats(self) -> Dict:
        """学習統計を取得"""
        return {
            'q_table_size': len(self.q_table),
            'total_rewards': sum(self.reward_history),
            'avg_reward': np.mean(self.reward_history) if self.reward_history else 0,
            'episodes_trained': len(self.reward_history)
        }

    def save_q_table(self, filepath: str):
        """Q-tableを保存"""
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            save_data = {
                'q_table': self.q_table,
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon
            }
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
        except (IOError, OSError) as e:
            raise IOError(f"Q-tableの保存に失敗しました: {filepath}") from e

    def load_q_table(self, filepath: str):
        """Q-tableを読み込み"""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Q-tableファイルが見つかりません: {filepath}")

            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)

            # データの妥当性チェック
            required_keys = ['q_table', 'learning_rate', 'discount_factor', 'epsilon']
            if not all(key in save_data for key in required_keys):
                raise ValueError(f"Q-tableファイルの形式が不正です: {filepath}")

            self.q_table = save_data['q_table']
            self.learning_rate = save_data['learning_rate']
            self.discount_factor = save_data['discount_factor']
            self.epsilon = save_data['epsilon']
        except (IOError, OSError) as e:
            raise IOError(f"Q-tableの読み込みに失敗しました: {filepath}") from e
        except pickle.UnpicklingError as e:
            raise ValueError(f"Q-tableファイルの形式が不正です: {filepath}") from e
