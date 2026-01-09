from typing import List, Optional
from datetime import datetime
from .scheduler import Scheduler
from .rl_policy_selector import PolicyBasedQLearningSelector
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
        
        # ポリシーベースQ-learningタスク選択戦略を作成
        ql_task_selector = PolicyBasedQLearningSelector(
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

    def select_next_task(self, tasks: List[Task], current_time: datetime) -> Optional[Task]:
        """
        次に実行するタスクを選択する（集中力レベルを渡すためにオーバーライド）
        """
        if self.break_strategy.should_take_break():
            return None

        # 集中力レベルを含めてタスク選択
        return self.task_selector.select_task(
            tasks,
            current_time,
            concentration_level=self.concentration_model.current_level
        )

    def work_on_task(self, task: Task) -> float:
        """
        タスクを実行し、Q値を更新する
        """
        start_time = datetime.now()
        start_concentration = self.concentration_model.current_level

        # 通常の作業処理
        actual_duration = super().work_on_task(task)

        # 報酬計算（時間効率を考慮）
        reward = self.task_selector.calculate_reward(
            task=task,
            completed=task.is_completed,
            current_time=start_time,
            concentration_level=start_concentration,
            actual_duration=actual_duration
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

    def save_model(self, filepath: str):
        """学習済みモデルを保存"""
        self.task_selector.save_q_table(filepath)

    def load_model(self, filepath: str):
        """学習済みモデルを読み込み"""
        self.task_selector.load_q_table(filepath)

    def train_episodes(self, 
                      simulation_environment,
                      num_episodes: int = 100,
                      verbose: bool = True):
        """
        複数回のエピソードで学習を行う
        
        Args:
            simulation_environment: TaskSchedulingSimulation環境
            num_episodes: 学習エピソード数
            verbose: 学習過程を表示するか
        """
        if verbose:
            print(f"強化学習の事前学習を開始 ({num_episodes}エピソード)")
        
        # 学習中は高い探索率
        original_epsilon = self.task_selector.epsilon
        self.task_selector.epsilon = 0.5  # 高い探索率で学習
        
        total_rewards = []
        
        for episode in range(num_episodes):
            # 新しいタスクセットで学習
            training_tasks = simulation_environment.generate_tasks()
            
            # エピソード実行
            result = simulation_environment.run_simulation_with_tasks(self, training_tasks)
            
            # エピソード報酬を記録
            episode_reward = sum(self.task_selector.reward_history[-len(training_tasks):]) if self.task_selector.reward_history else 0
            total_rewards.append(episode_reward)
            
            # 進捗表示
            if verbose and (episode + 1) % 20 == 0:
                avg_reward = sum(total_rewards[-20:]) / 20
                print(f"  エピソード {episode + 1}/{num_episodes}, 平均報酬: {avg_reward:.1f}")
            
            # エピソード終了処理
            self.reset()
        
        # 学習完了後は探索率を下げる
        self.task_selector.epsilon = max(0.1, original_epsilon)
        
        if verbose:
            final_avg_reward = sum(total_rewards[-10:]) / min(10, len(total_rewards))
            print(f"✅ 学習完了！最終10エピソードの平均報酬: {final_avg_reward:.1f}")
            print(f"Q-table サイズ: {len(self.task_selector.q_table)} 状態")
        
        return {
            'episode_rewards': total_rewards,
            'final_average_reward': final_avg_reward,
            'q_table_size': len(self.task_selector.q_table)
        }