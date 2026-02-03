"""ConcentrationModelのテスト"""
import pytest
from src.models.concentration import ConcentrationModel


class TestConcentrationModel:
    """集中力モデルのテストクラス"""

    def test_priority_fatigue_effect(self):
        """重要度別の疲労効果を検証"""
        concentration_model = ConcentrationModel()

        # LOWタスクで60分作業
        concentration_model.reset()
        concentration_model.work(60, task_priority=1)
        low_level = concentration_model.current_level

        # MEDIUMタスクで60分作業
        concentration_model.reset()
        concentration_model.work(60, task_priority=2)
        medium_level = concentration_model.current_level

        # HIGHタスクで60分作業
        concentration_model.reset()
        concentration_model.work(60, task_priority=3)
        high_level = concentration_model.current_level

        # 集中力レベルの順序を検証
        assert high_level < medium_level < low_level, \
            f"集中力レベルの順序が正しくない: HIGH={high_level}, MEDIUM={medium_level}, LOW={low_level}"

        # 差が十分にあることを確認
        assert low_level - medium_level > 0.05, \
            f"LOWとMEDIUMの差が小さすぎる: {low_level - medium_level}"
        assert medium_level - high_level > 0.05, \
            f"MEDIUMとHIGHの差が小さすぎる: {medium_level - high_level}"

    def test_priority_fatigue_with_multiple_tasks(self):
        """複数タスクを連続実行した場合の疲労蓄積を検証"""
        concentration_model = ConcentrationModel()

        # LOWタスクを3回（各30分）
        concentration_model.reset()
        for _ in range(3):
            concentration_model.work(30, task_priority=1)
        low_level_after_3 = concentration_model.current_level

        # HIGHタスクを3回（各30分）
        concentration_model.reset()
        for _ in range(3):
            concentration_model.work(30, task_priority=3)
        high_level_after_3 = concentration_model.current_level

        # HIGHタスクを連続で実行すると疲労が蓄積
        assert high_level_after_3 < low_level_after_3, \
            f"HIGHタスク連続実行後の集中力がLOWタスクより高い: HIGH={high_level_after_3}, LOW={low_level_after_3}"

    def test_default_priority(self):
        """デフォルトの重要度（1）が正しく動作するか検証"""
        concentration_model = ConcentrationModel()

        # task_priorityを指定しない場合
        concentration_model.reset()
        concentration_model.work(60)
        no_priority_level = concentration_model.current_level

        # task_priority=1を明示的に指定した場合
        concentration_model.reset()
        concentration_model.work(60, task_priority=1)
        low_priority_level = concentration_model.current_level

        # デフォルトとLOWは同じ結果になるはず
        assert abs(no_priority_level - low_priority_level) < 0.001, \
            f"デフォルトとLOWで異なる結果: デフォルト={no_priority_level}, LOW={low_priority_level}"
