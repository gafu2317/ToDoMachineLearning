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

# タスク重要度別の疲労係数設定
# 重要度が高いほど集中力の低下が速くなる（疲れやすい）
PRIORITY_FATIGUE_CONFIG = {
    # Priority.value -> 疲労係数の倍率
    1: 1.0,   # LOW: 標準の疲労度（ベースライン）
    2: 1.3,   # MEDIUM: 1.3倍速く疲れる（30%増加）
    3: 1.6,   # HIGH: 1.6倍速く疲れる（60%増加）
}

# 重要度連続作業ペナルティ設定
# 同じ重要度（特にHIGH）のタスクを連続でやった場合の追加疲労
PRIORITY_CONSECUTIVE_PENALTY = {
    # Priority.value -> 連続作業時の追加疲労倍率
    3: 1.3,  # HIGH連続: さらに1.3倍の疲労（合計1.6 × 1.3 = 2.08倍）
}

# 休憩戦略設定
BREAK_STRATEGY_CONFIG = {
    'threshold': 0.4
}

# 残り時間の安全マージン設定
# タスク実行中の集中力低下を考慮して、残り時間より余裕を持ってタスクを選択する
TIME_MARGIN_CONFIG = {
    'safety_factor': 0.85  # 残り時間の85%までのタスクを選択（15%のマージン）
}

# 強化学習設定
RL_CONFIG = {
    'learning_rate': 0.05,      # 0.1 → 0.05（学習を安定化）
    'discount_factor': 0.95,    # 0.9 → 0.95（長期的な計画を重視）
    'epsilon': 0.1
}

# 強化学習の状態空間離散化設定
# 警告: これらの値を変更すると、既存の学習済みQ-tableと互換性がなくなる可能性があります。
# 変更後は必ずtrain_rl_model.pyを再実行してモデルを再学習してください。
RL_STATE_SPACE_CONFIG = {
    # タスク数の離散化（粗く）
    'num_tasks_bin_divisor': 15,      # 10 → 15（区間を減らす）
    'num_tasks_bin_max': 5,           # 10 → 5（区間を減らす）

    # 重要度比率の離散化（粗く）
    'high_priority_ratio_bins': 3,    # 5 → 3（区間を減らす）

    # 締切の離散化（粗く）
    'deadline_bin_hours': 24,         # 12 → 24（区間を減らす）
    'deadline_bin_max': 5,            # 10 → 5（区間を減らす）

    # 平均時間の離散化（粗く）
    'avg_duration_bin_minutes': 60,   # 30 → 60（区間を減らす）
    'avg_duration_bin_max': 4,        # 7 → 4（区間を減らす）

    # 集中力レベルの離散化
    'concentration_bins': 3,          # 4 → 3（区間を減らす）

    # 疲労蓄積度の離散化（粗く）
    'fatigue_bins': 3,                # 5 → 3（区間を減らす）

    # 残り日数の離散化（削除して簡略化）
    'remaining_days_bins': 5,         # 8 → 5（区間を減らす）
}

# タスク生成設定
TASK_GENERATION_CONFIG = {
    # タスク時間の範囲（分）
    'short_task_min': 30,
    'short_task_max': 90,
    'medium_task_max': 180,
    'long_task_max': 270,

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
    3: 0.6,  # HIGH: 60%以上で最適（緩和）
}

# スケジューリング設定
SCHEDULING_CONFIG = {
    # タスク時間の分類閾値（分）
    'short_task_threshold': 135,
    'medium_task_threshold': 180,

    # 安全なタスク選択の閾値
    'safe_success_probability': 0.7,

    # 秒数定数
    'seconds_per_day': 86400,
}

# 強化学習報酬設定（バランスを改善）
RL_REWARD_CONFIG = {
    # ボーナス報酬（スケールを統一）
    'high_concentration_bonus': 50,       # 20 → 50（集中力の重要性を強調）
    'high_priority_bonus': 100,           # 500 → 100（過度な偏りを防ぐ）

    # 締切関連の報酬/ペナルティ（新規追加）
    'deadline_met_bonus': 50,             # 締切を守った場合のボーナス
    'deadline_violated_penalty': 200,     # 締切を破った場合のペナルティ
    'early_completion_margin_bonus': 30,  # 締切より余裕を持って完了した場合

    # 効率性ペナルティ
    'time_inefficiency_penalty': 1.0,     # 0.5 → 1.0（時間効率を重視）
    'reckless_attempt_penalty': 80,       # 20 → 80（無謀な選択を抑止）

    # ボーナス条件
    'high_concentration_threshold': 0.7,
    'high_priority_threshold': 0.6,
    'reckless_concentration_threshold': 0.6,
    'early_margin_threshold_hours': 24,   # 締切の24時間前完了で早期ボーナス

    # 長時間タスクの早期完了促進（調整）
    'early_completion_bonus': 80,         # 100 → 80
    'mid_completion_bonus': 40,           # 50 → 40
    'late_selection_penalty': 60,         # 50 → 60
    'long_task_threshold': 180,           # 長時間タスクの閾値（分）
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

# 学習モード設定
RL_LEARNING_MODE_CONFIG = {
    'train_epsilon': 0.5,
    'test_epsilon': 0.0,
    'enable_learning': True,
    'epsilon_decay_rate': 0.9995,  # 0.995 → 0.9995（減衰を緩やかに）
    'min_epsilon': 0.05,           # epsilonの下限
}