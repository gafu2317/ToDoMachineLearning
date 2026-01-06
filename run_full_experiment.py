"""
強化学習を含む本格実験実行
全結果をファイルに保存する
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator
from config import DEFAULT_SIMULATION_CONFIG, EXPERIMENT_CONFIG


def main():
    """強化学習を含む本格実験を実行してレポートを生成"""
    print("強化学習を含む本格実験を開始...")
    
    # 実験設定
    evaluator = SchedulerEvaluator(
        num_experiments=EXPERIMENT_CONFIG['num_experiments'],
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
    
    print(f"\n✅ 実験完了！結果は以下に保存されました:")
    print(f"  - 詳細データ: {csv_path}")
    print(f"  - レポート: {report_path}")
    print(f"  - 強化学習分析: {rl_analysis_path}")


if __name__ == "__main__":
    main()