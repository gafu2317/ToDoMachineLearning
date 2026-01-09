"""
プロジェクト設定ファイル
実験パラメータを一元管理する
"""

# シミュレーション設定
DEFAULT_SIMULATION_CONFIG = {
    'simulation_days': 7,
    'work_hours_per_day': 8,
    'num_tasks': 50  # スケジューラの差を見るために適度な負荷
}

QUICK_TEST_CONFIG = {
    'simulation_days': 2,
    'work_hours_per_day': 4,
    'num_tasks': 20
}

# 実験設定
EXPERIMENT_CONFIG = {
    'num_experiments': 50,
    'output_dir': 'results'
}

# 集中力モデル設定
CONCENTRATION_CONFIG = {
    'max_work_time_minutes': 120,
    'rest_recovery_minutes': 15,
    'initial_level': 1.0
}

# 休憩戦略設定
BREAK_STRATEGY_CONFIG = {
    'threshold': 0.4
}

# 強化学習設定
RL_CONFIG = {
    'learning_rate': 0.1,
    'discount_factor': 0.9,
    'epsilon': 0.1
}

# タスク生成設定
TASK_GENERATION_CONFIG = {
    # タスク時間の範囲（分）
    'short_task_min': 15,
    'short_task_max': 60,
    'medium_task_max': 120,
    'long_task_max': 180,

    # タスク時間分布（確率）
    'short_task_ratio': 0.7,  # 70%が短時間タスク
    'medium_task_ratio': 0.2,  # 20%が中時間タスク
    # 残り10%が長時間タスク

    # 重要度分布（確率）
    'priority_low_ratio': 0.6,    # 60%がLOW
    'priority_medium_ratio': 0.25, # 25%がMEDIUM
    # 残り15%がHIGH

    # 依存関係設定
    'dependency_ratio': 0.3,  # 30%のタスクが依存関係を持つ
    'dependency_window_size': 20,  # 直近20個のタスクから依存先を選択

    # 再試行設定
    'max_attempts': 3,  # タスクの最大試行回数
}

# タスク難易度設定
TASK_DIFFICULTY_CONFIG = {
    # 難易度別の必要集中力レベル
    'concentration_thresholds': {
        1: 0.3,  # 簡単: 30%以上で成功
        2: 0.6,  # 普通: 60%以上で成功
        3: 0.8,  # 難しい: 80%以上で成功
    },

    # 成功確率計算
    'min_success_probability': 0.1,
    'base_success_probability': 0.7,
    'success_multiplier': 2.0,
    'failure_multiplier': 0.5,
}

# スケジューリング設定
SCHEDULING_CONFIG = {
    # タスク時間の分類閾値（分）
    'short_task_threshold': 90,
    'medium_task_threshold': 120,

    # 安全なタスク選択の閾値
    'safe_success_probability': 0.7,

    # 秒数定数
    'seconds_per_day': 86400,
}

# 強化学習報酬設定
RL_REWARD_CONFIG = {
    # ボーナス報酬
    'high_concentration_bonus': 20,
    'difficulty_bonus': 30,

    # ペナルティ
    'failure_time_penalty_multiplier': 0.5,
    'reckless_attempt_penalty': 50,

    # ボーナス条件
    'high_concentration_threshold': 0.7,
    'difficulty_bonus_threshold': 0.8,
    'reckless_concentration_threshold': 0.6,
}

# 集中力モデル追加設定
CONCENTRATION_LIMITS = {
    'min_level': 0.2,  # 最低集中力レベル
}