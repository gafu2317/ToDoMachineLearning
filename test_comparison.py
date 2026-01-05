"""
スケジューラー比較テスト
少ない実験回数で3つのスケジューラーを比較する
"""

import sys
import os

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator


def main():
    """スケジューラー比較テスト"""
    print("スケジューラー比較テストを開始...")
    print()
    
    # 少ない実験回数でテスト（時間短縮のため）
    evaluator = SchedulerEvaluator(
        num_experiments=10,  # 10回だけ
        simulation_days=2,   # 2日間
        work_hours_per_day=6, # 6時間
        num_tasks=20         # 20個のタスク
    )
    
    print("実験を実行中...")
    results_df = evaluator.run_experiments()
    
    print(f"\n実験完了！ {len(results_df)} 件の結果を取得")
    print()
    
    # 結果分析
    analysis = evaluator.analyze_results(results_df)
    
    print("=== スケジューラー別結果 ===")
    for scheduler_name, stats in analysis.items():
        if scheduler_name == 'summary':
            continue
        
        print(f"\n{scheduler_name}:")
        print(f"  平均スコア: {stats['mean_score']:.2f} ± {stats['std_score']:.2f}")
        print(f"  完了率: {stats['mean_completion_rate']:.3f} ± {stats['std_completion_rate']:.3f}")
        print(f"  締切遵守率: {stats['mean_deadline_compliance']:.3f} ± {stats['std_deadline_compliance']:.3f}")
        print(f"  効率: {stats['mean_efficiency']:.3f} ± {stats['std_efficiency']:.3f}")
    
    print(f"\n=== 総合結果 ===")
    summary = analysis['summary']
    print(f"スコアが最も高い: {summary['best_scheduler_by_score']}")
    print(f"完了率が最も高い: {summary['best_scheduler_by_completion']}")
    print(f"締切遵守率が最も高い: {summary['best_scheduler_by_deadline']}")
    
    # 統計的有意差検定
    print(f"\n=== 統計的有意差検定 ===")
    significance = evaluator.statistical_significance_test(results_df)
    
    for comparison, test_result in significance.items():
        significance_mark = "**有意差あり**" if test_result['significant'] else "有意差なし"
        print(f"{comparison}:")
        print(f"  p値: {test_result['p_value']:.4f} ({significance_mark})")
        print(f"  平均差: {test_result['mean_diff']:.2f}")
    
    # 詳細データを表示
    print(f"\n=== 詳細データ（スコア） ===")
    for scheduler_name in results_df['scheduler_name'].unique():
        scores = results_df[results_df['scheduler_name'] == scheduler_name]['total_score']
        print(f"{scheduler_name}: {scores.tolist()}")
    
    print("\n🎉 比較テスト完了！")


if __name__ == "__main__":
    main()