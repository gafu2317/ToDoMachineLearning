import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from .task_selectors import TaskSelector
from ..models.task import Task


class QLearningTaskSelector(TaskSelector):
    """Q-learningによるタスク選択戦略"""
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.1):
        
        self.learning_rate = learning_rate  # 学習率
        self.discount_factor = discount_factor  # 割引率
        self.epsilon = epsilon  # ε-greedy探索
        
        # Q-table: state -> action -> Q値
        self.q_table = {}
        
        # 学習用の履歴
        self.state_history = []
        self.action_history = []
        self.reward_history = []
        
    def select_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        """Q-learningによりタスクを選択"""
        
        if not tasks:
            return None
        
        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if not incomplete_tasks:
            return None
        
        # 状態を取得
        state = self._get_state(incomplete_tasks, current_time)
        
        # ε-greedy探索
        if np.random.random() < self.epsilon:
            # ランダム探索
            selected_task = np.random.choice(incomplete_tasks)
            action = incomplete_tasks.index(selected_task)
        else:
            # Q値最大の行動を選択
            action = self._get_best_action(state, len(incomplete_tasks))
            if action < len(incomplete_tasks):
                selected_task = incomplete_tasks[action]
            else:
                selected_task = None  # 休憩選択
        
        # 履歴に記録
        self.state_history.append(state)
        self.action_history.append(action)
        
        return selected_task
    
    def _get_state(self, tasks: List[Task], current_time: datetime) -> Tuple:
        """現在の状態を取得"""
        
        if not tasks:
            return (0, 0, 0, 0, 0)
        
        # タスク情報の集約
        num_tasks = len(tasks)
        avg_priority = np.mean([task.priority.value for task in tasks])
        avg_duration = np.mean([task.base_duration_minutes for task in tasks])
        
        # 締切までの時間
        min_deadline_hours = min(
            (task.deadline - current_time).total_seconds() / 3600 
            for task in tasks
        )
        
        # 状態を離散化（簡単な実装）
        state = (
            min(num_tasks // 5, 10),  # タスク数を5個ずつの区間に
            int(avg_priority),  # 平均重要度
            min(int(avg_duration // 30), 10),  # 平均時間を30分ずつの区間に  
            max(0, min(int(min_deadline_hours // 24), 10)),  # 最短締切を日単位に
            0  # 集中力レベル（後で追加）
        )
        
        return state
    
    def _get_best_action(self, state: Tuple, num_actions: int) -> int:
        """状態に対して最適な行動を取得"""
        
        if state not in self.q_table:
            # 初回は十分に大きなサイズでQ値を初期化
            max_actions = max(100, num_actions + 1)  # 十分に大きなサイズ
            self.q_table[state] = np.zeros(max_actions)
        
        # 現在のQ-tableサイズが不足している場合は拡張
        current_size = len(self.q_table[state])
        required_size = num_actions + 1
        if current_size < required_size:
            # 配列を拡張
            new_size = max(current_size * 2, required_size)
            old_array = self.q_table[state]
            self.q_table[state] = np.zeros(new_size)
            self.q_table[state][:current_size] = old_array
        
        # Q値最大の行動を返す
        return np.argmax(self.q_table[state][:required_size])
    
    def update_q_value(self, reward: float, next_state: Tuple = None, done: bool = False):
        """Q値を更新"""
        
        if len(self.state_history) < 1:
            return
        
        current_state = self.state_history[-1]
        current_action = self.action_history[-1]
        
        # 現在の状態のQ-tableを初期化（必要なら）
        if current_state not in self.q_table:
            max_actions = 100  # 十分に大きなサイズ
            self.q_table[current_state] = np.zeros(max_actions)
        
        # Q-table配列のサイズチェック
        current_size = len(self.q_table[current_state])
        if current_action >= current_size:
            # 配列を拡張
            new_size = max(current_size * 2, current_action + 1)
            old_array = self.q_table[current_state]
            self.q_table[current_state] = np.zeros(new_size)
            self.q_table[current_state][:current_size] = old_array
        
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
                        concentration_level: float) -> float:
        """報酬を計算（修正版）"""
        
        reward = 0.0
        
        if completed:
            # 基本完了報酬（スコアに基づく、スケールを調整）
            base_reward = task.get_score() * 0.1  # スケールダウン
            reward += base_reward
            
            # 締切遵守ボーナス（穏やかに）
            if current_time <= task.deadline:
                days_early = (task.deadline - current_time).days
                deadline_bonus = min(days_early * 2, 20)  # 早期完了ボーナス（小さく）
                reward += deadline_bonus
            else:
                # 締切違反ペナルティ（穏やかに）
                days_late = (current_time - task.deadline).days
                deadline_penalty = min(days_late * 5, 50)  # 遅延ペナルティ（制限）
                reward -= deadline_penalty
            
            # 高集中完了ボーナス
            if concentration_level > 0.7:
                concentration_bonus = 5
                reward += concentration_bonus
        else:
            # 作業開始の小さな報酬（行動を促す）
            reward += 1.0
        
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