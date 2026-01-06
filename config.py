"""
プロジェクト設定ファイル
実験パラメータを一元管理する
"""

# シミュレーション設定
DEFAULT_SIMULATION_CONFIG = {
    'simulation_days': 7,
    'work_hours_per_day': 8,
    'num_tasks': 80
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