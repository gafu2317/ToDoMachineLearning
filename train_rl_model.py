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
from src.utils.task_loader import TaskDataLoader
from config import DEFAULT_SIMULATION_CONFIG, RL_CONFIG, CONCENTRATION_CONFIG


def main():
    """強化学習モデルを事前学習"""
    print("=" * 60)
    print("強化学習モデルの事前学習")
    print("=" * 60)

    # タスクローダーを作成（学習用）
    train_loader = TaskDataLoader(dataset_type='train')

    # 学習エピソード数（改良版なので増やす）
    num_episodes = 1000

    # シミュレーション環境を作成
    simulation = TaskSchedulingSimulation(**DEFAULT_SIMULATION_CONFIG)

    print(f"\nシミュレーション設定:")
    print(f"  - 期間: {simulation.simulation_days}日間")
    print(f"  - 1日の作業時間: {simulation.work_hours_per_day}時間")
    print(f"  - タスク数: 60個（固定）")
    print(f"  - 学習データセット: {train_loader.get_num_datasets()}セット")

    # 強化学習スケジューラーを作成（学習モードで）
    concentration = ConcentrationModel(**CONCENTRATION_CONFIG)
    rl_scheduler = RLLearningScheduler(
        concentration_model=concentration,
        learning_mode=True,  # 学習モードを明示的に有効化
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

    total_rewards = []
    episode_rewards = []

    for episode in range(num_episodes):
        # 学習用データセットからタスクを読み込み
        task_index = episode % train_loader.get_num_datasets()
        training_tasks = train_loader.load_tasks(task_index)

        # エピソード実行
        result = simulation.run_simulation_with_tasks(rl_scheduler, training_tasks)

        # 報酬記録
        episode_reward = sum(rl_scheduler.task_selector.reward_history[-len(training_tasks):]) \
                         if rl_scheduler.task_selector.reward_history else 0
        total_rewards.append(episode_reward)
        episode_rewards.append(episode_reward)

        # 進捗表示
        if (episode + 1) % 20 == 0:
            avg_reward = sum(total_rewards[-20:]) / 20
            print(f"  エピソード {episode + 1}/{num_episodes}, 平均報酬: {avg_reward:.1f}")

        # エピソード終了処理
        rl_scheduler.reset()

    # 学習統計を作成
    training_stats = {
        'final_average_reward': sum(total_rewards[-100:]) / min(100, len(total_rewards)),
        'q_table_size': len(rl_scheduler.task_selector.q_table),
        'episode_rewards': episode_rewards
    }

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
