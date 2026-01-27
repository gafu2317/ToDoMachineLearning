"""
プロジェクト設定ファイル
実験パラメータを一元管理する
"""

# シミュレーション設定
DEFAULT_SIMULATION_CONFIG = {
    'simulation_days': 7,
    'work_hours_per_day': 8,
    'num_tasks': 60  # スケジューラの差を見るために適度な負荷
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

# 集中力の持続力設定（減衰係数）
CONCENTRATION_SUSTAINABILITY_CONFIG = {
    'short': {
        'decay_factor': 1.3,
        'description': '集中力が早く低下（疲れやすい）'
    },
    'medium': {
        'decay_factor': 1.0,
        'description': '標準的な低下速度'
    },
    'long': {
        'decay_factor': 0.8,
        'description': '集中力がゆっくり低下（疲れにくい）'
    }
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

# 強化学習の状態空間離散化設定
# 警告: これらの値を変更すると、既存の学習済みQ-tableと互換性がなくなる可能性があります。
# 変更後は必ずtrain_rl_model.pyを再実行してモデルを再学習してください。
RL_STATE_SPACE_CONFIG = {
    # タスク数の離散化
    'num_tasks_bin_divisor': 10,      # タスク数を何個ずつの区間に分けるか
    'num_tasks_bin_max': 10,          # タスク数区間の最大値

    # 重要度比率の離散化
    'high_priority_ratio_bins': 5,    # 重要度比率の区間数（0-5）

    # 締切の離散化
    'deadline_bin_hours': 12,         # 締切を何時間ごとに区間化するか
    'deadline_bin_max': 10,           # 締切区間の最大値

    # 平均時間の離散化
    'avg_duration_bin_minutes': 20,   # 平均時間を何分ごとに区間化するか
    'avg_duration_bin_max': 5,        # 平均時間区間の最大値

    # 集中力レベルの離散化
    'concentration_bins': 4,          # 集中力レベルの区間数（0-4）
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

# タスク優先度別の必要集中力レベル
TASK_PRIORITY_THRESHOLDS = {
    # Priority.value -> 必要集中力レベル
    1: 0.3,  # LOW: 30%以上で最適
    2: 0.6,  # MEDIUM: 60%以上で最適
    3: 0.8,  # HIGH: 80%以上で最適
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
    'high_priority_bonus': 30,

    # ペナルティ
    'failure_time_penalty_multiplier': 0.5,
    'reckless_attempt_penalty': 50,

    # ボーナス条件
    'high_concentration_threshold': 0.7,
    'high_priority_threshold': 0.8,
    'reckless_concentration_threshold': 0.6,
}

# 集中力モデル追加設定
CONCENTRATION_LIMITS = {
    'min_level': 0.2,  # 最低集中力レベル
}

# ジャンル設定
GENRE_CONFIG = {
    'genres': ['1', '2', '3', '4'],  # 意味を持たない数字タグ
    'genre_distribution': {
        '1': 0.25,
        '2': 0.25,
        '3': 0.25,
        '4': 0.25
    }
}

# パーソナルデータファイルのパス
PERSONAL_DATA_FILE = 'personal_data.json'