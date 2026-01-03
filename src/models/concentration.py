import numpy as np


class ConcentrationModel:
    def __init__(self, 
                 max_work_time_minutes: int = 120,  # 連続作業可能時間
                 rest_recovery_minutes: int = 15,   # 休憩による回復時間
                 initial_level: float = 1.0):       # 初期集中レベル
        
        self.max_work_time = max_work_time_minutes
        self.rest_recovery = rest_recovery_minutes
        self.initial_level = initial_level
        
        self.current_level = initial_level
        self.continuous_work_time = 0  # 連続作業時間
        
    def reset(self):
        self.current_level = self.initial_level
        self.continuous_work_time = 0
        
    def work(self, duration_minutes: int) -> float:
        # 作業による疲労で集中力低下
        self.continuous_work_time += duration_minutes
        
        # 集中力の減少（指数的に減衰）
        fatigue_factor = np.exp(-self.continuous_work_time / self.max_work_time)
        self.current_level = self.initial_level * fatigue_factor
        
        # 最低値は0.2に制限
        self.current_level = max(0.2, self.current_level)
        
        return self.get_efficiency_multiplier()
    
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