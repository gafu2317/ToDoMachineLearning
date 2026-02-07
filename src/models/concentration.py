import numpy as np
from config import CONCENTRATION_LIMITS


class ConcentrationModel:
    def __init__(self,
                 max_work_time_minutes: int = 120,  # 連続作業可能時間
                 rest_recovery_minutes: int = 15,   # 休憩による回復時間
                 initial_level: float = 1.0,        # 初期集中レベル
                 personal_data_file: str = None):   # パーソナルデータファイル

        self.max_work_time = max_work_time_minutes
        self.rest_recovery = rest_recovery_minutes
        self.initial_level = initial_level

        self.current_level = initial_level
        self.continuous_work_time = 0  # 連続作業時間

        # パーソナルデータの読み込み
        if personal_data_file is None:
            from config import PERSONAL_DATA_FILE
            personal_data_file = PERSONAL_DATA_FILE

        import json
        with open(personal_data_file, 'r') as f:
            personal_config = json.load(f)

        self.genre_preference_type = personal_config['genre_preference_type']

        if self.genre_preference_type == 'same':
            self.genre_params = personal_config['same_genre_preference']
        else:
            self.genre_params = personal_config['switch_genre_preference']

        # 集中力の持続力設定を読み込み
        from config import CONCENTRATION_SUSTAINABILITY_CONFIG
        sustainability_type = personal_config.get('concentration_sustainability', 'medium')
        self.decay_factor = CONCENTRATION_SUSTAINABILITY_CONFIG[sustainability_type]['decay_factor']

        # 前回のジャンルと重要度を記憶
        self.last_genre = None
        self.last_priority = None

    def reset(self):
        """毎朝のリセット時にジャンル履歴と重要度履歴もクリア"""
        self.current_level = self.initial_level
        self.continuous_work_time = 0
        self.last_genre = None
        self.last_priority = None
        
    def work(self, duration_minutes: int, task_priority: int = 1) -> float:
        """
        作業により集中力を減少させる

        Args:
            duration_minutes: 作業時間（分）
            task_priority: タスクの重要度（Priority.valueを渡す、デフォルト1）

        Returns:
            作業効率の倍率

        Raises:
            ValueError: duration_minutesが負の値の場合
        """
        if duration_minutes < 0:
            raise ValueError(f"作業時間は0以上である必要があります: {duration_minutes}")

        # 重要度に応じた疲労係数を取得
        priority_decay_multiplier = self._get_priority_decay_multiplier(task_priority)

        # 重要度連続作業ペナルティを適用
        consecutive_penalty = self._get_consecutive_priority_penalty(task_priority)
        priority_decay_multiplier *= consecutive_penalty

        # 作業による疲労で集中力低下（重要度と連続作業を考慮）
        effective_work_time = duration_minutes * priority_decay_multiplier
        self.continuous_work_time += effective_work_time

        # 集中力の減少（指数的に減衰、個人特性とタスク重要度の両方を考慮）
        fatigue_factor = np.exp(-self.decay_factor * self.continuous_work_time / self.max_work_time)
        self.current_level = self.initial_level * fatigue_factor

        # 最低値を制限
        min_level = CONCENTRATION_LIMITS['min_level']
        self.current_level = max(min_level, self.current_level)

        # 現在の重要度を記憶
        self.last_priority = task_priority

        return self.get_efficiency_multiplier()

    def _get_priority_decay_multiplier(self, task_priority: int) -> float:
        """
        タスクの重要度に応じた疲労係数の倍率を返す

        Args:
            task_priority: Priority.value (1=LOW, 2=MEDIUM, 3=HIGH)

        Returns:
            疲労係数の倍率（1.0が基準）
        """
        from config import PRIORITY_FATIGUE_CONFIG
        return PRIORITY_FATIGUE_CONFIG.get(task_priority, 1.0)

    def _get_consecutive_priority_penalty(self, task_priority: int) -> float:
        """
        同じ重要度のタスクを連続で実行した場合の追加疲労倍率を返す

        Args:
            task_priority: Priority.value (1=LOW, 2=MEDIUM, 3=HIGH)

        Returns:
            連続作業時の追加疲労倍率（1.0が基準、連続HIGHの場合は1.3など）
        """
        # 最初のタスクまたは前回と異なる重要度の場合はペナルティなし
        if self.last_priority is None or self.last_priority != task_priority:
            return 1.0

        # 連続して同じ重要度のタスクを実行する場合
        from config import PRIORITY_CONSECUTIVE_PENALTY
        return PRIORITY_CONSECUTIVE_PENALTY.get(task_priority, 1.0)

    def rest(self, duration_minutes: int = None):
        if duration_minutes is None:
            duration_minutes = self.rest_recovery
            
        # 休憩による回復
        recovery = duration_minutes / self.rest_recovery
        self.current_level = min(1.0, self.current_level + recovery * 0.5)
        
        # 連続作業時間をリセット
        if duration_minutes >= self.rest_recovery:
            self.continuous_work_time = 0
    
    def get_efficiency_multiplier(self) -> float:
        if self.current_level >= 0.7:
            return 0.8  # 高集中時: 20%効率アップ
        elif self.current_level <= 0.4:
            return 1.2  # 低集中時: 20%効率ダウン
        else:
            return 1.0  # 通常時
    
    def should_rest(self, threshold: float = 0.4) -> bool:
        return self.current_level < threshold

    def apply_genre_switch_effect(self, current_genre: str):
        """
        ジャンル切り替えによる集中力への影響を適用

        Args:
            current_genre: 現在のタスクのジャンル
        """
        # 最初のタスクの場合は影響なし
        if self.last_genre is None:
            self.last_genre = current_genre
            return

        # ジャンルが同じか違うかを判定
        is_same_genre = (self.last_genre == current_genre)

        # パーソナルデータに基づいて集中力を調整
        from config import CONCENTRATION_LIMITS

        if self.genre_preference_type == 'same':
            if is_same_genre:
                # 同じジャンルを続ける → ボーナス
                bonus = self.genre_params['same_genre_bonus']
                self.current_level = min(1.0, self.current_level + bonus)
            else:
                # ジャンルを変更 → ペナルティ
                penalty = self.genre_params['switch_genre_penalty']
                self.current_level = max(CONCENTRATION_LIMITS['min_level'],
                                        self.current_level - penalty)
        else:  # 'switch'
            if is_same_genre:
                # 同じジャンルを続ける → ペナルティ
                penalty = self.genre_params['same_genre_penalty']
                self.current_level = max(CONCENTRATION_LIMITS['min_level'],
                                        self.current_level - penalty)
            else:
                # ジャンルを変更 → ボーナス
                bonus = self.genre_params['switch_genre_bonus']
                self.current_level = min(1.0, self.current_level + bonus)

        # 現在のジャンルを記憶
        self.last_genre = current_genre

    def get_observable_state(self) -> dict:
        """エージェントが観測可能な状態情報を返す"""
        return {
            'concentration_level': self.current_level,
            'continuous_work_time': self.continuous_work_time,
            'fatigue_accumulation': self.get_fatigue_accumulation()
        }

    def get_fatigue_accumulation(self) -> float:
        """疲労蓄積度を計算（0.0～1.0）"""
        return min(1.0, self.continuous_work_time / self.max_work_time)