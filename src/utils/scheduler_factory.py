"""
スケジューラー作成のファクトリー関数
重複コードを削減し、一貫性を保つ
"""

from typing import Dict
from ..models.concentration import ConcentrationModel
from ..schedulers.scheduler import Scheduler
from ..schedulers.task_selectors import DeadlineTaskSelector, PriorityTaskSelector, RandomTaskSelector
from ..schedulers.break_strategies import ConcentrationBreakStrategy
from ..schedulers.rl_learning_scheduler import RLLearningScheduler
from config import CONCENTRATION_CONFIG, BREAK_STRATEGY_CONFIG, RL_CONFIG


def create_baseline_schedulers() -> Dict[str, Scheduler]:
    """
    ベースラインスケジューラーを作成する
    
    Returns:
        スケジューラー名をキー、スケジューラーインスタンスを値とする辞書
    """
    schedulers = {}
    
    # 期限順スケジューラー
    concentration1 = ConcentrationModel(**CONCENTRATION_CONFIG)
    break_strategy1 = ConcentrationBreakStrategy(concentration1, **BREAK_STRATEGY_CONFIG)
    task_selector1 = DeadlineTaskSelector()
    schedulers["deadline_scheduler"] = Scheduler(task_selector1, break_strategy1)
    
    # 重要度順スケジューラー
    concentration2 = ConcentrationModel(**CONCENTRATION_CONFIG)
    break_strategy2 = ConcentrationBreakStrategy(concentration2, **BREAK_STRATEGY_CONFIG)
    task_selector2 = PriorityTaskSelector()
    schedulers["priority_scheduler"] = Scheduler(task_selector2, break_strategy2)
    
    # ランダムスケジューラー
    concentration3 = ConcentrationModel(**CONCENTRATION_CONFIG)
    break_strategy3 = ConcentrationBreakStrategy(concentration3, **BREAK_STRATEGY_CONFIG)
    task_selector3 = RandomTaskSelector()
    schedulers["random_scheduler"] = Scheduler(task_selector3, break_strategy3)
    
    return schedulers


def create_rl_scheduler(model_path: str = None) -> RLLearningScheduler:
    """
    強化学習スケジューラーを作成する

    Args:
        model_path: 学習済みモデルのパス。Noneの場合はデフォルトモデルを使用

    Returns:
        強化学習スケジューラーインスタンス
    """
    import os

    concentration = ConcentrationModel(**CONCENTRATION_CONFIG)
    rl_scheduler = RLLearningScheduler(
        concentration_model=concentration,
        **RL_CONFIG
    )

    # デフォルトパスを設定
    if model_path is None:
        model_path = "trained_models/rl_model_default.pkl"

    # モデルが存在すれば読み込む
    if os.path.exists(model_path):
        rl_scheduler.load_model(model_path)
        rl_scheduler.set_epsilon(0.05)  # テスト時は探索率を低く
        print(f"✅ 学習済みモデルを読み込み: {model_path}")
    else:
        print(f"⚠️  学習済みモデルが見つからない: {model_path}")
        print(f"   未学習の状態で実行される。事前に train_rl_model.py を実行してください。")

    return rl_scheduler


def get_scheduler_description(scheduler_name: str) -> str:
    """
    スケジューラーの説明を取得する
    
    Args:
        scheduler_name: スケジューラー名
        
    Returns:
        説明文
    """
    descriptions = {
        'deadline_scheduler': '期限が近いタスクを優先して実行',
        'priority_scheduler': '重要度が高いタスクを優先して実行',
        'random_scheduler': '残りタスクからランダムに選択',
        'rl_scheduler': '強化学習により最適なタスクを選択',
        'rl_scheduler_untrained': '未学習の強化学習スケジューラー',
        'rl_scheduler_trained': '事前学習済みの強化学習スケジューラー'
    }
    
    return descriptions.get(scheduler_name, '説明なし')