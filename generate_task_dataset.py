"""
学習用と検証用のタスクデータセットを事前生成するスクリプト
"""

import json
import os
from datetime import datetime
from src.environment.simulation import TaskSchedulingSimulation
from config import DEFAULT_SIMULATION_CONFIG

def generate_dataset(num_train: int = 8000, num_test: int = 2000):
    """
    タスクデータセットを生成して保存

    Args:
        num_train: 学習用タスクセット数（デフォルト: 8000）
        num_test: テスト用タスクセット数（デフォルト: 2000）
    """
    print(f"タスクデータセット生成開始")
    print(f"  学習用: {num_train}セット")
    print(f"  テスト用: {num_test}セット")

    # ディレクトリ作成
    os.makedirs("dataset/train", exist_ok=True)
    os.makedirs("dataset/test", exist_ok=True)

    # シミュレーション環境（config.pyの設定を使用）
    sim = TaskSchedulingSimulation(
        simulation_days=DEFAULT_SIMULATION_CONFIG['simulation_days'],
        work_hours_per_day=DEFAULT_SIMULATION_CONFIG['work_hours_per_day'],
        num_tasks=DEFAULT_SIMULATION_CONFIG['num_tasks']
    )

    # 学習用データ生成
    print("\n学習用データ生成中...")
    for i in range(num_train):
        tasks = sim.generate_tasks()
        task_data = [task_to_dict(t) for t in tasks]

        filename = f"dataset/train/tasks_{i:04d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, default=str)

        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{num_train} 完了")

    # テスト用データ生成
    print("\nテスト用データ生成中...")
    for i in range(num_test):
        tasks = sim.generate_tasks()
        task_data = [task_to_dict(t) for t in tasks]

        filename = f"dataset/test/tasks_{i:04d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, default=str)

        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{num_test} 完了")

    print(f"\n✅ データセット生成完了")
    print(f"  学習用: dataset/train/ ({num_train}ファイル)")
    print(f"  テスト用: dataset/test/ ({num_test}ファイル)")

def task_to_dict(task):
    """TaskオブジェクトをJSON化可能な辞書に変換"""
    return {
        'id': task.id,
        'name': task.name,
        'base_duration_minutes': task.base_duration_minutes,
        'priority': task.priority.name,
        'deadline': task.deadline.isoformat(),
        'genre': task.genre,
        'is_completed': task.is_completed
    }

if __name__ == "__main__":
    generate_dataset()
