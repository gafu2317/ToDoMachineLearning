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
from src.environment.simulation import TaskSchedulingSimulation, attach_hidden_params
from src.utils.scheduler_factory import create_baseline_schedulers, create_rl_scheduler
from src.visualization.schedule_gantt import generate_schedule_comparison, generate_planned_vs_actual
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
    
    # CSVファイルに詳細データを保存
    csv_path = f"{EXPERIMENT_CONFIG['output_dir']}/full_experiment_results_{timestamp}.csv"
    os.makedirs(EXPERIMENT_CONFIG['output_dir'], exist_ok=True)
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"詳細データを保存: {csv_path}")
    
    # レポートを生成・保存
    report_path = f"{EXPERIMENT_CONFIG['output_dir']}/full_experiment_report_{timestamp}.md"
    report = evaluator.generate_report(results_df, save_path=report_path)
    print(f"レポートを保存: {report_path}")
    
    # 強化学習の詳細分析
    rl_analysis_path = f"{EXPERIMENT_CONFIG['output_dir']}/rl_analysis_{timestamp}.txt"
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

    run_dir = f"{EXPERIMENT_CONFIG['output_dir']}/{timestamp}"
    os.makedirs(run_dir, exist_ok=True)

    gantt_path = f"{run_dir}/schedule_comparison.png"
    generate_schedule_comparison(schedule_results, gantt_path)
    print(f"スケジュール比較グラフ: {gantt_path}")

    # --- 箱ひげ図生成 ---
    import matplotlib.pyplot as plt

    scheduler_names = ['deadline_scheduler', 'priority_scheduler', 'random_scheduler', 'rl_scheduler']
    box_data = [results_df[results_df['scheduler_name'] == name]['total_score'].values for name in scheduler_names]
    box_colors = ['#4A90D9', '#E67E22', '#2ECC71', '#E74C3C']

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(box_data, labels=[n.replace('_scheduler', '') for n in scheduler_names], patch_artist=True)
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(2)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Scheduler Score Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle=':', alpha=0.4)
    plt.tight_layout()

    boxplot_path = f"{run_dir}/score_boxplot.png"
    plt.savefig(boxplot_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f"箱ひげ図: {boxplot_path}")

    # --- 3週間の可視化 ---
    # RL は1インスタンスで3週間を通じて学習を継続
    # Week N: 予定実行(学習なし) → 実際実行(学習あり) → Q-table更新
    rl_weekly = create_rl_scheduler()

    for week in range(3):
        week_num = week + 1
        week_dir = f"{run_dir}/week_{week_num}"
        os.makedirs(week_dir, exist_ok=True)

        week_task_index = (int(representative_exp_id) + week) % test_loader.get_num_datasets()
        clean_tasks = test_loader.load_tasks(week_task_index)
        hidden_tasks = attach_hidden_params(copy.deepcopy(clean_tasks))

        simulation = TaskSchedulingSimulation(**DEFAULT_SIMULATION_CONFIG)

        # --- 予定スケジュール（隠しパラメータなし） ---
        planned_results = {}
        for name, scheduler in create_baseline_schedulers().items():
            planned_results[name] = simulation.run_simulation_with_tasks(scheduler, clean_tasks)

        # RL 予定: 学習なし
        rl_weekly.set_learning_mode(False)
        planned_results["rl_scheduler"] = simulation.run_simulation_with_tasks(rl_weekly, clean_tasks)

        # --- 実際スケジュール（Planned の順番を固定、隠しパラメータで再実行） ---
        actual_results = {}
        for name in planned_results:
            actual_results[name] = simulation.run_replay(
                planned_results[name]['simulation_log'], hidden_tasks
            )

        # RL の Q-table 更新は独立実行（可視化には使わない）
        rl_weekly.set_learning_mode(True)
        simulation.run_simulation_with_tasks(rl_weekly, hidden_tasks)

        # --- 画像生成 ---
        # 1. planned_comparison.png
        generate_schedule_comparison(
            planned_results,
            f"{week_dir}/planned_comparison.png",
            fig_title=f"Week {week_num}: Planned Schedule Comparison"
        )

        # 2-5. planned_vs_actual per scheduler
        for sched_name in ["deadline_scheduler", "priority_scheduler", "random_scheduler", "rl_scheduler"]:
            generate_planned_vs_actual(
                planned_results[sched_name],
                actual_results[sched_name],
                sched_name,
                f"{week_dir}/planned_vs_actual_{sched_name}.png"
            )

        print(f"Week {week_num} 画像生成完了: {week_dir}")

    print(f"\n✅ 実験完了！結果は以下に保存されました:")
    print(f"  - 詳細データ: {csv_path}")
    print(f"  - レポート: {report_path}")
    print(f"  - 強化学習分析: {rl_analysis_path}")
    print(f"  - ガンツチャート: {gantt_path}")
    print(f"  - 箱ひげ図: {boxplot_path}")
    for week_num in range(1, 4):
        print(f"  - Week {week_num} 可視化: {run_dir}/week_{week_num}/")


if __name__ == "__main__":
    main()