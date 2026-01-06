from typing import List, Optional
from datetime import datetime
from .scheduler import Scheduler
from .rl_scheduler import QLearningTaskSelector
from .break_strategies import ConcentrationBreakStrategy
from ..models.task import Task
from ..models.concentration import ConcentrationModel


class RLLearningScheduler(Scheduler):
    """学習機能付きの強化学習スケジューラー"""
    
    def __init__(self, 
                 concentration_model: ConcentrationModel,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.1):
        
        # Q-learningタスク選択戦略を作成
        ql_task_selector = QLearningTaskSelector(
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=epsilon
        )
        
        # 集中力ベース休憩戦略を作成
        break_strategy = ConcentrationBreakStrategy(concentration_model)
        
        # 親クラス初期化
        super().__init__(ql_task_selector, break_strategy)
        
        # 強化学習用の追加情報
        self.last_task = None
        self.last_action_time = None
        
    def work_on_task(self, task: Task) -> float:
        """
        タスクを実行し、Q値を更新する
        """
        start_time = datetime.now()
        start_concentration = self.concentration_model.current_level
        
        # 通常の作業処理
        actual_duration = super().work_on_task(task)
        
        # 報酬計算
        reward = self.task_selector.calculate_reward(
            task=task,
            completed=task.is_completed,
            current_time=start_time,
            concentration_level=start_concentration
        )
        
        # Q値更新
        self.task_selector.update_q_value(
            reward=reward,
            done=task.is_completed
        )
        
        self.last_task = task
        self.last_action_time = start_time
        
        return actual_duration
    
    def take_break(self) -> int:
        """
        休憩を取り、Q値を更新する
        """
        # 通常の休憩処理
        break_duration = super().take_break()
        
        # 休憩の報酬（小さな負の報酬：時間コスト）
        break_reward = -break_duration * 0.1
        
        # Q値更新
        self.task_selector.update_q_value(
            reward=break_reward,
            done=False
        )
        
        return break_duration
    
    def reset(self):
        """スケジューラーをリセット"""
        super().reset()
        self.task_selector.reset_episode()
        self.last_task = None
        self.last_action_time = None
    
    def get_learning_stats(self):
        """学習統計を取得"""
        return self.task_selector.get_learning_stats()
    
    def set_epsilon(self, epsilon: float):
        """探索率を設定（学習段階の調整用）"""
        self.task_selector.epsilon = epsilon