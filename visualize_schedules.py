"""
スケジュールの視覚化実験
4つのスケジューラを並べて比較する
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment.simulation import TaskSchedulingSimulation
from src.utils.scheduler_factory import create_baseline_schedulers, create_rl_scheduler
from src.evaluation.schedule_visualizer import ScheduleVisualizer
from config import DEFAULT_SIMULATION_CONFIG, EXPERIMENT_CONFIG


def main():
    """4つのスケジューラでシミュレーションを実行し、視覚化する"""
    print("スケジュール視覚化実験を開始...")

    # シミュレーション環境
    sim = TaskSchedulingSimulation(**DEFAULT_SIMULATION_CONFIG)

    # 全スケジューラで同じタスクセットを使用
    tasks = sim.generate_tasks()
    print(f"タスク数: {len(tasks)}")

    # スケジューラを作成
    schedulers = create_baseline_schedulers()
    schedulers['rl_scheduler'] = create_rl_scheduler()

    # 結果を保存する辞書
    results = {}

    # 各スケジューラでシミュレーションを実行
    for scheduler_name, scheduler in schedulers.items():
        print(f"\n{scheduler_name} を実行中...")

        result = sim.run_simulation_with_tasks(scheduler, tasks)
        results[scheduler_name] = result

        print(f"  完了率: {result['completion_rate']*100:.1f}%")
        print(f"  スコア: {result['total_score']}")
        print(f"  完了タスク数: {result['completed_tasks_count']}/{result['tasks']['total']}")

    # 視覚化
    print("\nスケジュールを視覚化中...")
    visualizer = ScheduleVisualizer(
        start_hour=9,
        end_hour=17,
        simulation_days=DEFAULT_SIMULATION_CONFIG['simulation_days']
    )

    # 出力ディレクトリを作成
    os.makedirs(EXPERIMENT_CONFIG['output_dir'], exist_ok=True)

    # タイムスタンプ付きファイル名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{EXPERIMENT_CONFIG['output_dir']}/schedule_comparison_{timestamp}.png"

    # 視覚化を生成
    visualizer.visualize_schedules(results, output_path=output_path)

    print(f"\n✅ 視覚化完了！")
    print(f"ファイル: {output_path}")


if __name__ == "__main__":
    main()
