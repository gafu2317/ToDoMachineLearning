"""
ファイル保存テスト
小規模実験で保存機能をテストする
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.evaluator import SchedulerEvaluator


def main():
    """小規模実験でファイル保存をテスト"""
    print("ファイル保存テストを開始...")
    
    # 小規模実験
    evaluator = SchedulerEvaluator(
        num_experiments=5,    # 5回だけ
        simulation_days=1,    # 1日
        work_hours_per_day=4, # 4時間
        num_tasks=10          # 10個のタスク
    )
    
    print("小規模実験実行中...")
    results_df = evaluator.run_experiments()
    
    # 結果を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # resultsディレクトリを作成
    os.makedirs("results", exist_ok=True)
    
    # CSVファイルに詳細データを保存
    csv_path = f"results/test_results_{timestamp}.csv"
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ 詳細データを保存: {csv_path}")
    
    # レポートを生成・保存
    report_path = f"results/test_report_{timestamp}.md"
    report = evaluator.generate_report(results_df, save_path=report_path)
    print(f"✅ レポートを保存: {report_path}")
    
    # 保存されたファイルの確認
    if os.path.exists(csv_path):
        file_size = os.path.getsize(csv_path)
        print(f"CSV ファイルサイズ: {file_size} bytes")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f"レポート行数: {lines} 行")
    
    print("\n" + "="*30)
    print("レポート内容（一部）")
    print("="*30)
    print(report[:500] + "...")  # 最初の500文字だけ表示
    
    print(f"\n🎉 ファイル保存テスト完了！")


if __name__ == "__main__":
    main()