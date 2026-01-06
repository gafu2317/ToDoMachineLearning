"""
強化学習スケジューラーのテスト
"""

import sys
import os

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator


def main():
    """強化学習スケジューラーを含むテスト"""
    print("強化学習スケジューラーテストを開始...")
    print()
    
    # 小規模テスト（強化学習は時間がかかるため）
    evaluator = SchedulerEvaluator(
        num_experiments=5,    # 5回だけ
        simulation_days=2,    # 2日
        work_hours_per_day=4, # 4時間
        num_tasks=15          # 15個のタスク
    )
    
    print("実験を実行中... (強化学習含む)")
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
        print(f"  効率: {stats['mean_efficiency']:.3f} ± {stats['std_efficiency']:.3f}")
    
    print(f"\n=== 総合結果 ===")
    summary = analysis['summary']
    print(f"スコアが最も高い: {summary['best_scheduler_by_score']}")
    print(f"完了率が最も高い: {summary['best_scheduler_by_completion']}")
    
    # 強化学習の学習統計を表示
    print(f"\n=== 強化学習統計 ===")
    rl_data = results_df[results_df['scheduler_name'] == 'rl_scheduler']
    if len(rl_data) > 0:
        print(f"RLスケジューラーの結果:")
        for idx, row in rl_data.iterrows():
            print(f"  実験{row['experiment_id']}: スコア={row['total_score']:.0f}, 完了率={row['completion_rate']:.3f}")
    
    print("\n🎉 強化学習テスト完了！")


if __name__ == "__main__":
    main()