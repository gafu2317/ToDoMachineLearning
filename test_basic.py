"""
基本的な動作テスト
各コンポーネントが正常に動作するかを確認する
"""

import sys
import os

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.models.task import Task, Priority
from src.models.concentration import ConcentrationModel
from src.schedulers.task_selectors import DeadlineTaskSelector, PriorityTaskSelector, RandomTaskSelector
from src.schedulers.break_strategies import ConcentrationBreakStrategy
from src.schedulers.scheduler import Scheduler
from src.environment.simulation import TaskSchedulingSimulation


def test_task_creation():
    """タスク作成テスト"""
    print("=== タスク作成テスト ===")
    
    current_time = datetime.now()
    task = Task.generate_random_task(1, current_time)
    
    print(f"タスク名: {task.name}")
    print(f"所要時間: {task.base_duration_minutes}分")
    print(f"重要度: {task.priority.name} (値: {task.priority.value})")
    print(f"締切: {task.deadline}")
    print(f"スコア: {task.get_score()}")
    print(f"完了状態: {task.is_completed}")
    print("✓ タスク作成OK\n")


def test_concentration_model():
    """集中力モデルテスト"""
    print("=== 集中力モデルテスト ===")
    
    concentration = ConcentrationModel()
    print(f"初期集中力: {concentration.current_level:.2f}")
    
    # 30分作業
    efficiency = concentration.work(30)
    print(f"30分作業後の集中力: {concentration.current_level:.2f}")
    print(f"作業効率: {efficiency:.2f}")
    
    # 60分作業
    efficiency = concentration.work(60)
    print(f"90分作業後の集中力: {concentration.current_level:.2f}")
    print(f"作業効率: {efficiency:.2f}")
    
    # 休憩必要？
    print(f"休憩が必要: {concentration.should_rest()}")
    
    # 15分休憩
    concentration.rest(15)
    print(f"15分休憩後の集中力: {concentration.current_level:.2f}")
    print("✓ 集中力モデルOK\n")


def test_scheduler():
    """スケジューラーテスト"""
    print("=== スケジューラーテスト ===")
    
    # タスク作成
    current_time = datetime.now()
    tasks = [Task.generate_random_task(i, current_time) for i in range(5)]
    
    # 期限順スケジューラー
    concentration = ConcentrationModel()
    break_strategy = ConcentrationBreakStrategy(concentration)
    task_selector = DeadlineTaskSelector()
    scheduler = Scheduler(task_selector, break_strategy)
    
    print("期限順スケジューラー:")
    selected_task = scheduler.select_next_task(tasks, current_time)
    if selected_task:
        print(f"選択されたタスク: {selected_task.name}, 締切: {selected_task.deadline}")
    else:
        print("選択されたタスクなし")
    
    print("✓ スケジューラーOK\n")


def test_simple_simulation():
    """簡単なシミュレーションテスト"""
    print("=== 簡単なシミュレーションテスト ===")
    
    # 短期間・少ないタスクでテスト
    simulation = TaskSchedulingSimulation(
        simulation_days=1,  # 1日だけ
        work_hours_per_day=4,  # 4時間だけ
        num_tasks=5  # 5個のタスク
    )
    
    # 期限順スケジューラー
    concentration = ConcentrationModel()
    break_strategy = ConcentrationBreakStrategy(concentration)
    task_selector = DeadlineTaskSelector()
    scheduler = Scheduler(task_selector, break_strategy)
    
    # シミュレーション実行
    result = simulation.run_simulation(scheduler)
    
    print(f"総スコア: {result['total_score']}")
    print(f"完了タスク数: {result['completed_tasks_count']}")
    print(f"未完了タスク数: {result['incomplete_tasks_count']}")
    print(f"完了率: {result['completion_rate']:.2f}")
    print(f"総作業時間: {result['total_work_time']:.1f}分")
    print(f"総休憩時間: {result['total_break_time']:.1f}分")
    print("✓ シミュレーションOK\n")


def main():
    """全テスト実行"""
    print("基本動作テストを開始...")
    print()
    
    try:
        test_task_creation()
        test_concentration_model()
        test_scheduler()
        test_simple_simulation()
        
        print("🎉 全てのテストが成功しました！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()