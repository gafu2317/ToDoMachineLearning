"""
実験結果の視覚化モジュール
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import os


# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'MS Gothic']
plt.rcParams['axes.unicode_minus'] = False


class ResultPlotter:
    """実験結果を視覚化するクラス"""

    def __init__(self, results_df: pd.DataFrame, output_dir: str = "results"):
        """
        Args:
            results_df: 実験結果のDataFrame
            output_dir: 図を保存するディレクトリ
        """
        self.results_df = results_df
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # スケジューラー名の表示用マッピング
        self.scheduler_labels = {
            'deadline_scheduler': '期限順',
            'priority_scheduler': '重要度順',
            'random_scheduler': 'ランダム',
            'rl_scheduler': '強化学習'
        }

        # カラーマップ
        self.colors = {
            'deadline_scheduler': '#3498db',  # 青
            'priority_scheduler': '#e74c3c',  # 赤
            'random_scheduler': '#95a5a6',    # グレー
            'rl_scheduler': '#2ecc71'         # 緑
        }

    def plot_score_comparison(self, save_path: Optional[str] = None) -> None:
        """スコア比較の棒グラフを作成"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # スケジューラーごとの平均スコアと標準偏差を計算
        score_stats = self.results_df.groupby('scheduler_name')['total_score'].agg(['mean', 'std'])

        # ソート（平均スコア降順）
        score_stats = score_stats.sort_values('mean', ascending=False)

        # 棒グラフ
        x_pos = np.arange(len(score_stats))
        bars = ax.bar(
            x_pos,
            score_stats['mean'],
            yerr=score_stats['std'],
            capsize=5,
            color=[self.colors.get(name, '#cccccc') for name in score_stats.index],
            edgecolor='black',
            linewidth=1.5
        )

        # ラベル設定
        ax.set_xlabel('スケジューラー', fontsize=12, fontweight='bold')
        ax.set_ylabel('総スコア', fontsize=12, fontweight='bold')
        ax.set_title('スケジューラー別総スコア比較', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([self.scheduler_labels.get(name, name) for name in score_stats.index])

        # グリッド
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # 値を棒の上に表示
        for i, (mean_val, std_val) in enumerate(zip(score_stats['mean'], score_stats['std'])):
            ax.text(i, mean_val + std_val + 50, f'{mean_val:.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"スコア比較グラフを保存: {save_path}")
        else:
            plt.savefig(f"{self.output_dir}/score_comparison.png", dpi=300, bbox_inches='tight')

        plt.close()

    def plot_metrics_comparison(self, save_path: Optional[str] = None) -> None:
        """各指標の比較グラフを作成"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        metrics = [
            ('total_score', '総スコア'),
            ('completion_rate', '完了率'),
            ('deadline_compliance_rate', '締切遵守率'),
            ('efficiency', '効率')
        ]

        for ax, (metric, label) in zip(axes.flatten(), metrics):
            stats = self.results_df.groupby('scheduler_name')[metric].agg(['mean', 'std'])
            stats = stats.sort_values('mean', ascending=False)

            x_pos = np.arange(len(stats))
            ax.bar(
                x_pos,
                stats['mean'],
                yerr=stats['std'],
                capsize=5,
                color=[self.colors.get(name, '#cccccc') for name in stats.index],
                edgecolor='black',
                linewidth=1.5
            )

            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels([self.scheduler_labels.get(name, name) for name in stats.index],
                              rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)

            # 値を表示
            for i, mean_val in enumerate(stats['mean']):
                if metric == 'total_score':
                    text = f'{mean_val:.0f}'
                else:
                    text = f'{mean_val:.3f}'
                ax.text(i, mean_val, text, ha='center', va='bottom', fontsize=9)

        plt.suptitle('スケジューラー別各指標の比較', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"各指標比較グラフを保存: {save_path}")
        else:
            plt.savefig(f"{self.output_dir}/metrics_comparison.png", dpi=300, bbox_inches='tight')

        plt.close()

    def plot_score_distribution(self, save_path: Optional[str] = None) -> None:
        """スコア分布の箱ひげ図を作成"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # データを準備
        schedulers = self.results_df['scheduler_name'].unique()
        data = [self.results_df[self.results_df['scheduler_name'] == s]['total_score'].values
                for s in schedulers]

        # 箱ひげ図
        bp = ax.boxplot(
            data,
            labels=[self.scheduler_labels.get(s, s) for s in schedulers],
            patch_artist=True,
            showmeans=True,
            meanprops=dict(marker='D', markerfacecolor='red', markersize=8)
        )

        # 色設定
        for patch, scheduler in zip(bp['boxes'], schedulers):
            patch.set_facecolor(self.colors.get(scheduler, '#cccccc'))
            patch.set_alpha(0.7)

        ax.set_xlabel('スケジューラー', fontsize=12, fontweight='bold')
        ax.set_ylabel('総スコア', fontsize=12, fontweight='bold')
        ax.set_title('スケジューラー別スコア分布', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"スコア分布グラフを保存: {save_path}")
        else:
            plt.savefig(f"{self.output_dir}/score_distribution.png", dpi=300, bbox_inches='tight')

        plt.close()

    def plot_statistical_significance(self, significance_results: Dict, save_path: Optional[str] = None) -> None:
        """統計的有意差を視覚化"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # RLスケジューラーとの比較のみ抽出
        rl_comparisons = {k: v for k, v in significance_results.items() if 'rl_scheduler' in k}

        if not rl_comparisons:
            print("強化学習スケジューラーとの比較データがありません")
            plt.close()
            return

        comparison_names = list(rl_comparisons.keys())
        p_values = [rl_comparisons[k]['p_value'] for k in comparison_names]
        mean_diffs = [rl_comparisons[k]['mean_diff'] for k in comparison_names]

        # p値の棒グラフ
        x_pos = np.arange(len(comparison_names))
        colors = ['green' if p < 0.05 else 'orange' for p in p_values]

        bars = ax.barh(x_pos, p_values, color=colors, edgecolor='black', linewidth=1.5)

        # 有意水準線
        ax.axvline(x=0.05, color='red', linestyle='--', linewidth=2, label='有意水準 (p=0.05)')

        ax.set_yticks(x_pos)
        ax.set_yticklabels([name.replace('_', ' ') for name in comparison_names])
        ax.set_xlabel('p値', fontsize=12, fontweight='bold')
        ax.set_title('強化学習スケジューラーとの統計的有意差検定', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # p値を表示
        for i, (p_val, mean_diff) in enumerate(zip(p_values, mean_diffs)):
            label = f'p={p_val:.4f}\n差={mean_diff:.1f}'
            ax.text(p_val + 0.01, i, label, va='center', fontsize=9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"統計的有意差グラフを保存: {save_path}")
        else:
            plt.savefig(f"{self.output_dir}/statistical_significance.png", dpi=300, bbox_inches='tight')

        plt.close()

    def create_comprehensive_report(self, significance_results: Dict, timestamp: str) -> None:
        """総合レポート（全グラフを1つのPDFに）"""
        from matplotlib.backends.backend_pdf import PdfPages

        pdf_path = f"{self.output_dir}/comprehensive_report_{timestamp}.pdf"

        with PdfPages(pdf_path) as pdf:
            # ページ1: スコア比較
            fig, ax = plt.subplots(figsize=(10, 6))
            score_stats = self.results_df.groupby('scheduler_name')['total_score'].agg(['mean', 'std'])
            score_stats = score_stats.sort_values('mean', ascending=False)
            x_pos = np.arange(len(score_stats))
            ax.bar(x_pos, score_stats['mean'], yerr=score_stats['std'], capsize=5,
                  color=[self.colors.get(name, '#cccccc') for name in score_stats.index],
                  edgecolor='black', linewidth=1.5)
            ax.set_xlabel('スケジューラー', fontsize=12, fontweight='bold')
            ax.set_ylabel('総スコア', fontsize=12, fontweight='bold')
            ax.set_title('スケジューラー別総スコア比較', fontsize=14, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels([self.scheduler_labels.get(name, name) for name in score_stats.index])
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            pdf.savefig(fig, dpi=300, bbox_inches='tight')
            plt.close()

            # ページ2: 各指標比較
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            metrics = [
                ('total_score', '総スコア'),
                ('completion_rate', '完了率'),
                ('deadline_compliance_rate', '締切遵守率'),
                ('efficiency', '効率')
            ]
            for ax, (metric, label) in zip(axes.flatten(), metrics):
                stats = self.results_df.groupby('scheduler_name')[metric].agg(['mean', 'std'])
                stats = stats.sort_values('mean', ascending=False)
                x_pos = np.arange(len(stats))
                ax.bar(x_pos, stats['mean'], yerr=stats['std'], capsize=5,
                      color=[self.colors.get(name, '#cccccc') for name in stats.index],
                      edgecolor='black', linewidth=1.5)
                ax.set_title(label, fontsize=12, fontweight='bold')
                ax.set_xticks(x_pos)
                ax.set_xticklabels([self.scheduler_labels.get(name, name) for name in stats.index],
                                  rotation=45, ha='right')
                ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.suptitle('スケジューラー別各指標の比較', fontsize=16, fontweight='bold')
            plt.tight_layout()
            pdf.savefig(fig, dpi=300, bbox_inches='tight')
            plt.close()

            # ページ3: 箱ひげ図
            fig, ax = plt.subplots(figsize=(10, 6))
            schedulers = self.results_df['scheduler_name'].unique()
            data = [self.results_df[self.results_df['scheduler_name'] == s]['total_score'].values
                    for s in schedulers]
            bp = ax.boxplot(data, labels=[self.scheduler_labels.get(s, s) for s in schedulers],
                          patch_artist=True, showmeans=True,
                          meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
            for patch, scheduler in zip(bp['boxes'], schedulers):
                patch.set_facecolor(self.colors.get(scheduler, '#cccccc'))
                patch.set_alpha(0.7)
            ax.set_xlabel('スケジューラー', fontsize=12, fontweight='bold')
            ax.set_ylabel('総スコア', fontsize=12, fontweight='bold')
            ax.set_title('スケジューラー別スコア分布', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            pdf.savefig(fig, dpi=300, bbox_inches='tight')
            plt.close()

            # ページ4: 統計的有意差
            fig, ax = plt.subplots(figsize=(12, 8))
            rl_comparisons = {k: v for k, v in significance_results.items() if 'rl_scheduler' in k}
            if rl_comparisons:
                comparison_names = list(rl_comparisons.keys())
                p_values = [rl_comparisons[k]['p_value'] for k in comparison_names]
                x_pos = np.arange(len(comparison_names))
                colors = ['green' if p < 0.05 else 'orange' for p in p_values]
                ax.barh(x_pos, p_values, color=colors, edgecolor='black', linewidth=1.5)
                ax.axvline(x=0.05, color='red', linestyle='--', linewidth=2, label='有意水準 (p=0.05)')
                ax.set_yticks(x_pos)
                ax.set_yticklabels([name.replace('_', ' ') for name in comparison_names])
                ax.set_xlabel('p値', fontsize=12, fontweight='bold')
                ax.set_title('強化学習スケジューラーとの統計的有意差検定', fontsize=14, fontweight='bold')
                ax.legend()
                ax.grid(axis='x', alpha=0.3, linestyle='--')
                plt.tight_layout()
                pdf.savefig(fig, dpi=300, bbox_inches='tight')
            plt.close()

        print(f"総合レポート（PDF）を保存: {pdf_path}")


def plot_learning_curve(episode_rewards: List[float], save_path: str, window_size: int = 20) -> None:
    """学習曲線をプロット"""
    fig, ax = plt.subplots(figsize=(12, 6))

    episodes = np.arange(1, len(episode_rewards) + 1)

    # 移動平均を計算
    moving_avg = np.convolve(episode_rewards, np.ones(window_size)/window_size, mode='valid')

    # プロット
    ax.plot(episodes, episode_rewards, alpha=0.3, color='blue', label='エピソード報酬')
    ax.plot(episodes[window_size-1:], moving_avg, color='red', linewidth=2,
           label=f'{window_size}エピソード移動平均')

    ax.set_xlabel('エピソード', fontsize=12, fontweight='bold')
    ax.set_ylabel('累積報酬', fontsize=12, fontweight='bold')
    ax.set_title('強化学習の学習曲線', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"学習曲線を保存: {save_path}")
    plt.close()
