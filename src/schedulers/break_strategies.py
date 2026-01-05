from abc import ABC, abstractmethod
from ..models.concentration import ConcentrationModel


class BreakStrategy(ABC):
    """休憩戦略の基底クラス"""
    
    def __init__(self, concentration_model: ConcentrationModel):
        self.concentration_model = concentration_model
    
    @abstractmethod
    def should_take_break(self) -> bool:
        """休憩を取るべきかどうかを判定する"""
        pass
    
    @abstractmethod
    def get_break_duration(self) -> int:
        """推奨される休憩時間（分）を返す"""
        pass
    
    @abstractmethod
    def reset(self):
        """戦略の状態をリセットする"""
        pass


class ConcentrationBreakStrategy(BreakStrategy):
    """集中力ベース休憩戦略"""
    
    def __init__(self, concentration_model: ConcentrationModel, threshold: float = 0.4):
        super().__init__(concentration_model)
        self.threshold = threshold
    
    def should_take_break(self) -> bool:
        return self.concentration_model.current_level < self.threshold
    
    def get_break_duration(self) -> int:
        return self.concentration_model.rest_recovery
    
    def reset(self):
        # 集中力ベースは特別なリセット処理なし
        pass


