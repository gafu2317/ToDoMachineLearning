"""
本格的な実験実行とレポート生成
結果をファイルに保存する
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator


def main():
    """本格的な実験を実行してレポートを生成"""
    print("本格実験を開始...")
    
    # 実験設定
    evaluator = SchedulerEvaluator(
        num_experiments=50,   # 50回実験
        simulation_days=7,    # 1週間
        work_hours_per_day=8, # 8時間
        num_tasks=80          # 80個のタスク
    )
    
    print("実験実行中... (数分かかります)")
    results_df = evaluator.run_experiments()
    
    # 結果を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # CSVファイルに詳細データを保存
    csv_path = f"results/experiment_results_{timestamp}.csv"
    os.makedirs("results", exist_ok=True)
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"詳細データを保存: {csv_path}")
    
    # レポートを生成・保存
    report_path = f"results/experiment_report_{timestamp}.md"
    report = evaluator.generate_report(results_df, save_path=report_path)
    print(f"レポートを保存: {report_path}")
    
    # コンソールにも表示
    print("\n" + "="*50)
    print("実験レポート")
    print("="*50)
    print(report)
    
    print(f"\n✅ 実験完了！結果は以下に保存されました:")
    print(f"  - 詳細データ: {csv_path}")
    print(f"  - レポート: {report_path}")


if __name__ == "__main__":
    main()