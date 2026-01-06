"""
詳細スケジュールログの生成
各スケジューラーがどのような順序でタスクを実行したかを可視化
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment.simulation import TaskSchedulingSimulation
from src.models.concentration import ConcentrationModel
from src.schedulers.scheduler import Scheduler
from src.schedulers.task_selectors import DeadlineTaskSelector, PriorityTaskSelector, RandomTaskSelector
from src.schedulers.break_strategies import ConcentrationBreakStrategy
from src.schedulers.rl_learning_scheduler import RLLearningScheduler
from src.evaluation.log_analyzer import SimulationLogAnalyzer


def main():
    """各スケジューラーの詳細ログを生成"""
    print("詳細スケジュールログ生成を開始...")
    
    # シミュレーション設定（1週間フル）
    simulation = TaskSchedulingSimulation(
        simulation_days=7,    # 7日間（1週間）
        work_hours_per_day=8, # 8時間（フルタイム）
        num_tasks=80          # 80個のタスク
    )
    
    # スケジューラー設定
    schedulers = {}
    
    # 期限順スケジューラー
    concentration1 = ConcentrationModel()
    break_strategy1 = ConcentrationBreakStrategy(concentration1)
    task_selector1 = DeadlineTaskSelector()
    schedulers["deadline_scheduler"] = Scheduler(task_selector1, break_strategy1)
    
    # 重要度順スケジューラー
    concentration2 = ConcentrationModel()
    break_strategy2 = ConcentrationBreakStrategy(concentration2)
    task_selector2 = PriorityTaskSelector()
    schedulers["priority_scheduler"] = Scheduler(task_selector2, break_strategy2)
    
    # ランダムスケジューラー
    concentration3 = ConcentrationModel()
    break_strategy3 = ConcentrationBreakStrategy(concentration3)
    task_selector3 = RandomTaskSelector()
    schedulers["random_scheduler"] = Scheduler(task_selector3, break_strategy3)
    
    # 強化学習スケジューラー
    concentration4 = ConcentrationModel()
    schedulers["rl_scheduler"] = RLLearningScheduler(
        concentration_model=concentration4,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.3  # 探索率を上げて多様な行動を試す
    )
    
    # ログアナライザーを作成
    log_analyzer = SimulationLogAnalyzer()
    
    # resultsディレクトリ作成
    os.makedirs("results/detailed_logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 共通タスクセットを事前生成
    print("共通タスクセットを生成中...")
    common_tasks = simulation.generate_tasks()
    print(f"生成されたタスク数: {len(common_tasks)}")
    
    # 実行サマリーを記録
    summary_lines = []
    summary_lines.append("# 詳細スケジュールログ生成サマリー")
    summary_lines.append(f"\n実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    summary_lines.append(f"\nシミュレーション設定:")
    summary_lines.append(f"- 期間: {simulation.simulation_days}日間")
    summary_lines.append(f"- 1日の作業時間: {simulation.work_hours_per_day}時間")
    summary_lines.append(f"- タスク数: {len(common_tasks)}個")
    summary_lines.append(f"- **重要**: 全スケジューラーで同一のタスクセットを使用")
    summary_lines.append(f"\n## 共通タスクセット情報")
    
    # タスクセットのサマリーを追加
    low_tasks = sum(1 for t in common_tasks if t.priority.value == 1)
    medium_tasks = sum(1 for t in common_tasks if t.priority.value == 2) 
    high_tasks = sum(1 for t in common_tasks if t.priority.value == 3)
    total_score = sum(t.get_score() for t in common_tasks)
    
    summary_lines.append(f"- 重要度LOW: {low_tasks}個")
    summary_lines.append(f"- 重要度MEDIUM: {medium_tasks}個")
    summary_lines.append(f"- 重要度HIGH: {high_tasks}個")
    summary_lines.append(f"- 総スコア（全完了時）: {total_score}点")
    summary_lines.append(f"\n## 各スケジューラーの結果")
    
    # 各スケジューラーでシミュレーション実行
    results_summary = []
    for scheduler_name, scheduler in schedulers.items():
        print(f"シミュレーション実行: {scheduler_name}")
        
        # 同じタスクセットでシミュレーション実行
        result = simulation.run_simulation_with_tasks(scheduler, common_tasks)
        
        # 詳細ログレポート生成
        log_path = f"results/detailed_logs/{scheduler_name}_detailed_log_{timestamp}.md"
        detailed_report = log_analyzer.generate_daily_schedule_report(
            simulation_result=result,
            scheduler_name=scheduler_name,
            save_path=log_path
        )
        
        print(f"  詳細ログ保存: {log_path}")
        
        # コンソールにサマリー表示
        print(f"  総スコア: {result['total_score']}, 完了率: {result['completion_rate']:.1%}")
        
        # サマリー用データ収集
        results_summary.append({
            'name': scheduler_name,
            'score': result['total_score'],
            'completion_rate': result['completion_rate'],
            'work_time': result['total_work_time'],
            'break_time': result['total_break_time'],
            'efficiency': result['efficiency'],
            'log_file': log_path
        })
        
        # サマリーファイルに結果を追加
        summary_lines.append(f"\n### {scheduler_name}")
        summary_lines.append(f"- 総スコア: {result['total_score']}")
        summary_lines.append(f"- 完了率: {result['completion_rate']:.1%} ({result['completed_tasks_count']}/{result['completed_tasks_count'] + result['incomplete_tasks_count']})")
        summary_lines.append(f"- 作業時間: {result['total_work_time']:.0f}分")
        summary_lines.append(f"- 休憩時間: {result['total_break_time']:.0f}分") 
        summary_lines.append(f"- 効率: {result['efficiency']:.1%}")
        summary_lines.append(f"- 詳細ログ: {log_path}")
        
        scheduler.reset()  # 次のシミュレーション用にリセット
    
    # 比較表を追加
    summary_lines.append(f"\n## 比較結果")
    
    # スコア順でソート
    sorted_by_score = sorted(results_summary, key=lambda x: x['score'], reverse=True)
    summary_lines.append(f"\n### スコア順位")
    for i, result in enumerate(sorted_by_score, 1):
        summary_lines.append(f"{i}位. {result['name']}: {result['score']}点")
    
    # 完了率順でソート
    sorted_by_completion = sorted(results_summary, key=lambda x: x['completion_rate'], reverse=True)
    summary_lines.append(f"\n### 完了率順位")
    for i, result in enumerate(sorted_by_completion, 1):
        summary_lines.append(f"{i}位. {result['name']}: {result['completion_rate']:.1%}")
    
    # 生成されたファイル一覧
    summary_lines.append(f"\n## 生成されたファイル")
    import glob
    log_files = glob.glob(f"results/detailed_logs/*_{timestamp}.md")
    for file_path in sorted(log_files):
        summary_lines.append(f"- {file_path}")
    
    # サマリーファイル保存
    summary_path = f"results/detailed_logs/summary_{timestamp}.md"
    summary_text = "\n".join(summary_lines)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(f"\n✅ 全ての詳細ログが生成されました！")
    print(f"保存先: results/detailed_logs/")
    print(f"サマリーファイル: {summary_path}")
    
    # 生成されたファイル一覧表示
    print("\n生成されたファイル:")
    for file_path in sorted(log_files + [summary_path]):
        print(f"  - {file_path}")


if __name__ == "__main__":
    main()