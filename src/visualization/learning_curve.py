"""
強化学習の学習進行グラフの生成
報酬の推移とEpsilon減衰を一つのグラフで可視化する
"""

import matplotlib.pyplot as plt
from typing import List


def generate_learning_curve(episode_rewards: List[float],
                            epsilon_history: List[float],
                            save_path: str,
                            window_size: int = 20):
    """
    学習進行グラフを生成する

    Args:
        episode_rewards: エピソードごとの報酬リスト
        epsilon_history: エピソードごとのEpsilon値リスト
        save_path: 出力画像パス
        window_size: 移動平均のウィンドウサイズ
    """
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # 移動平均を計算
    smoothed = [
        sum(episode_rewards[max(0, i - window_size + 1):i + 1]) / min(window_size, i + 1)
        for i in range(len(episode_rewards))
    ]

    # 左Y軸: 報酬（移動平均）
    ax1.plot(smoothed, color='#6BCF7F', linewidth=1.5, label='Average Reward')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.set_ylim(bottom=0)

    # 右Y軸: Epsilon
    ax2 = ax1.twinx()
    ax2.plot(epsilon_history, color='#FF6B6B', linewidth=1.5, linestyle='--', label='Epsilon')
    ax2.set_ylabel('Epsilon')
    ax2.set_ylim(0, max(epsilon_history) * 1.1 if epsilon_history else 0.55)

    # 共通レジェンド
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    ax1.set_title('RL Training Progress')
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
