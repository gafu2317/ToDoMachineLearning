"""
強化学習モデルの事前学習スクリプト
大量のエピソードで学習し、Q-tableを保存する
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment.simulation import TaskSchedulingSimulation
from src.schedulers.rl_learning_scheduler import RLLearningScheduler
from src.models.concentration import ConcentrationModel
from config import DEFAULT_SIMULATION_CONFIG, RL_CONFIG, CONCENTRATION_CONFIG


def main():
    """強化学習モデルを事前学習"""
    print("=" * 60)
    print("強化学習モデルの事前学習")
    print("=" * 60)

    # 学習エピソード数（改良版なので増やす）
    num_episodes = 1000

    # シミュレーション環境を作成
    simulation = TaskSchedulingSimulation(**DEFAULT_SIMULATION_CONFIG)

    print(f"\nシミュレーション設定:")
    print(f"  - 期間: {simulation.simulation_days}日間")
    print(f"  - 1日の作業時間: {simulation.work_hours_per_day}時間")
    print(f"  - タスク数: {simulation.num_tasks}個程度")

    # 強化学習スケジューラーを作成
    concentration = ConcentrationModel(**CONCENTRATION_CONFIG)
    rl_scheduler = RLLearningScheduler(
        concentration_model=concentration,
        **RL_CONFIG
    )

    print(f"\n強化学習設定:")
    print(f"  - 学習率: {RL_CONFIG['learning_rate']}")
    print(f"  - 割引率: {RL_CONFIG['discount_factor']}")
    print(f"  - 初期探索率: {RL_CONFIG['epsilon']}")
    print(f"  - 学習エピソード数: {num_episodes}")

    # 事前学習を実行
    print(f"\n事前学習を開始...")
    print(f"（{num_episodes}エピソード、数分かかる可能性がある）")

    training_stats = rl_scheduler.train_episodes(
        simulation_environment=simulation,
        num_episodes=num_episodes,
        verbose=True
    )

    # モデルを保存
    os.makedirs("trained_models", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"trained_models/rl_model_{timestamp}.pkl"

    rl_scheduler.save_model(model_path)

    print(f"\n✅ 学習完了！モデルを保存: {model_path}")

    # 学習統計を保存
    stats_path = f"trained_models/training_stats_{timestamp}.txt"
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write("# 強化学習モデル学習統計\n\n")
        f.write(f"学習日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"学習エピソード数: {num_episodes}\n")
        f.write(f"最終平均報酬: {training_stats['final_average_reward']:.2f}\n")
        f.write(f"Q-tableサイズ: {training_stats['q_table_size']} 状態\n\n")

        f.write("## エピソードごとの報酬推移\n")
        for i, reward in enumerate(training_stats['episode_rewards'], 1):
            if i % 10 == 0 or i == 1:  # 10エピソードごとに記録
                f.write(f"エピソード {i}: {reward:.2f}\n")

    print(f"学習統計を保存: {stats_path}")

    # デフォルトモデルとしてコピー
    default_model_path = "trained_models/rl_model_default.pkl"
    import shutil
    shutil.copy(model_path, default_model_path)
    print(f"\nデフォルトモデルとして保存: {default_model_path}")
    print(f"（今後の実験ではこのモデルが使用される）")

    print("\n" + "=" * 60)
    print("学習完了！")
    print("=" * 60)
    print("\n次のコマンドで実験を実行できる:")
    print("  python generate_detailed_log.py   # 詳細ログ生成")
    print("  python run_full_experiment.py     # 大規模実験実行")


if __name__ == "__main__":
    main()
