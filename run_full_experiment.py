"""
強化学習を含む本格実験実行
全結果をファイルに保存する
"""

import sys
import os
import copy
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator
from src.utils.task_loader import TaskDataLoader
from src.environment.simulation import TaskSchedulingSimulation
from src.utils.scheduler_factory import create_baseline_schedulers, create_rl_scheduler
from src.visualization.schedule_gantt import generate_schedule_comparison
from config import DEFAULT_SIMULATION_CONFIG, EXPERIMENT_CONFIG


def main():
    """強化学習を含む本格実験を実行してレポートを生成"""
    print("強化学習を含む本格実験を開始...")

    # タスクローダーを作成（テスト用）
    test_loader = TaskDataLoader(dataset_type='test')

    # 実験設定
    evaluator = SchedulerEvaluator(
        num_experiments=EXPERIMENT_CONFIG['num_experiments'],
        task_loader=test_loader,
        **DEFAULT_SIMULATION_CONFIG
    )

    print("実験実行中... (強化学習含むため時間がかかります)")
    results_df = evaluator.run_experiments()

    # 結果を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"{EXPERIMENT_CONFIG['output_dir']}/{timestamp}"
    os.makedirs(run_dir, exist_ok=True)

    # CSVファイルに詳細データを保存
    csv_path = f"{run_dir}/full_experiment_results.csv"
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"詳細データを保存: {csv_path}")

    # レポートを生成・保存
    report_path = f"{run_dir}/full_experiment_report.md"
    report = evaluator.generate_report(results_df, save_path=report_path)
    print(f"レポートを保存: {report_path}")

    # 強化学習の詳細分析
    rl_analysis_path = f"{run_dir}/rl_analysis.txt"
    with open(rl_analysis_path, 'w', encoding='utf-8') as f:
        f.write("# 強化学習スケジューラー詳細分析\n\n")
        
        # 強化学習データの抽出
        rl_data = results_df[results_df['scheduler_name'] == 'rl_scheduler']
        
        f.write(f"実験回数: {len(rl_data)}\n")
        f.write(f"平均スコア: {rl_data['total_score'].mean():.2f}\n")
        f.write(f"最高スコア: {rl_data['total_score'].max():.2f}\n")
        f.write(f"最低スコア: {rl_data['total_score'].min():.2f}\n")
        f.write(f"標準偏差: {rl_data['total_score'].std():.2f}\n\n")
        
        f.write("各実験の詳細結果:\n")
        for idx, row in rl_data.iterrows():
            f.write(f"実験{row['experiment_id']}: ")
            f.write(f"スコア={row['total_score']:.0f}, ")
            f.write(f"完了率={row['completion_rate']:.3f}, ")
            f.write(f"効率={row['efficiency']:.3f}\n")
    
    print(f"強化学習詳細分析を保存: {rl_analysis_path}")
    
    # コンソールにサマリーを表示
    print("\n" + "="*60)
    print("実験サマリー")
    print("="*60)
    
    analysis = evaluator.analyze_results(results_df)
    
    for scheduler_name, stats in analysis.items():
        if scheduler_name == 'summary':
            continue
        
        print(f"\n{scheduler_name}:")
        print(f"  平均スコア: {stats['mean_score']:.2f} ± {stats['std_score']:.2f}")
        print(f"  完了率: {stats['mean_completion_rate']:.3f} ± {stats['std_completion_rate']:.3f}")
    
    print(f"\n=== 総合結果 ===")
    summary = analysis['summary']
    print(f"スコアが最も高い: {summary['best_scheduler_by_score']}")
    print(f"完了率が最も高い: {summary['best_scheduler_by_completion']}")
    
    # 統計的有意差検定
    print(f"\n=== 統計的有意差検定 ===")
    significance = evaluator.statistical_significance_test(results_df)

    rl_comparisons = {k: v for k, v in significance.items() if 'rl_scheduler' in k}
    for comparison, test_result in rl_comparisons.items():
        significance_mark = "**有意差あり**" if test_result['significant'] else "有意差なし"
        print(f"{comparison}: p={test_result['p_value']:.4f} ({significance_mark})")

    # --- ガンツチャート生成 ---
    # 代表的な実験回を選択（RL schedulerの中央値スコアに近い）
    rl_data = results_df[results_df['scheduler_name'] == 'rl_scheduler']
    median_score = rl_data['total_score'].median()
    representative_idx = (rl_data['total_score'] - median_score).abs().idxmin()
    representative_exp_id = results_df.loc[representative_idx, 'experiment_id']

    task_index = int(representative_exp_id) % test_loader.get_num_datasets()
    tasks = test_loader.load_tasks(task_index)

    schedulers = create_baseline_schedulers()
    schedulers["rl_scheduler"] = create_rl_scheduler()
    simulation = TaskSchedulingSimulation(**DEFAULT_SIMULATION_CONFIG)
    schedule_results = {}
    for name, scheduler in schedulers.items():
        scheduler.reset()
        schedule_results[name] = simulation.run_simulation_with_tasks(scheduler, tasks)

    gantt_path = f"{run_dir}/schedule_comparison.png"
    generate_schedule_comparison(schedule_results, gantt_path)
    print(f"スケジュール比較グラフ: {gantt_path}")

    # --- 箱ひげ図生成 ---
    import matplotlib.pyplot as plt

    scheduler_names = ['deadline_scheduler', 'priority_scheduler', 'random_scheduler', 'rl_scheduler']
    box_colors = ['#4A90D9', '#E67E22', '#2ECC71', '#E74C3C']
    labels = [n.replace('_scheduler', '') for n in scheduler_names]

    metrics = [
        ('total_score',      'Score'),
        ('completion_rate',  'Completion Rate'),
    ]

    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 5))
    fig.suptitle('Scheduler Comparison', fontsize=14, fontweight='bold')

    for ax, (col, ylabel) in zip(axes, metrics):
        data = [results_df[results_df['scheduler_name'] == name][col].values for name in scheduler_names]
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], box_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        for median in bp['medians']:
            median.set_color('black')
            median.set_linewidth(2)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(ylabel, fontsize=11, fontweight='bold')
        ax.grid(axis='y', linestyle=':', alpha=0.4)

    plt.tight_layout()

    boxplot_path = f"{run_dir}/score_boxplot.png"
    plt.savefig(boxplot_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f"箱ひげ図: {boxplot_path}")

    print(f"\n✅ 実験完了！結果は以下に保存されました:")
    print(f"  - 詳細データ: {csv_path}")
    print(f"  - レポート: {report_path}")
    print(f"  - 強化学習分析: {rl_analysis_path}")
    print(f"  - ガンツチャート: {gantt_path}")
    print(f"  - 箱ひげ図: {boxplot_path}")


if __name__ == "__main__":
    main()