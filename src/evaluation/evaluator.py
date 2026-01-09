from typing import Dict, List, Any
import numpy as np
import pandas as pd
from ..environment.simulation import TaskSchedulingSimulation
from ..utils.scheduler_factory import create_baseline_schedulers, create_rl_scheduler
from ..schedulers.scheduler import Scheduler


class SchedulerEvaluator:
    """スケジューラーの性能評価を行うクラス"""
    
    def __init__(self, 
                 num_experiments: int = 100,
                 simulation_days: int = 7,
                 work_hours_per_day: int = 8,
                 num_tasks: int = None):
        
        self.num_experiments = num_experiments
        self.simulation_days = simulation_days
        self.work_hours_per_day = work_hours_per_day
        self.num_tasks = num_tasks
    
    
    def run_experiments(self, schedulers: Dict[str, Scheduler] = None) -> pd.DataFrame:
        """
        複数のスケジューラーで実験を実行し、結果を比較する

        Args:
            schedulers: 評価するスケジューラーの辞書。Noneの場合はベースラインを使用

        Returns:
            実験結果のDataFrame
        """
        if schedulers is None:
            # ベースラインスケジューラーを作成
            schedulers = create_baseline_schedulers()
            # 強化学習スケジューラーを追加
            schedulers["rl_scheduler"] = create_rl_scheduler()
        
        results = []
        
        for scheduler_name, scheduler in schedulers.items():
            print(f"実験中: {scheduler_name}")
            scheduler_results = self._run_single_scheduler_experiments(scheduler_name, scheduler)
            results.extend(scheduler_results)
        
        return pd.DataFrame(results)
    
    def _run_single_scheduler_experiments(self, scheduler_name: str, scheduler: Scheduler) -> List[Dict]:
        """単一スケジューラーで複数回実験を実行"""
        results = []
        
        for experiment_id in range(self.num_experiments):
            # シミュレーション環境を作成
            simulation = TaskSchedulingSimulation(
                simulation_days=self.simulation_days,
                work_hours_per_day=self.work_hours_per_day,
                num_tasks=self.num_tasks
            )
            
            # シミュレーション実行
            result = simulation.run_simulation(scheduler)
            
            # 結果にメタデータを追加
            result['scheduler_name'] = scheduler_name
            result['experiment_id'] = experiment_id
            
            results.append(result)
        
        return results
    
    def analyze_results(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        実験結果を分析し、統計サマリーを作成する
        
        Args:
            results_df: run_experiments()で得られた結果のDataFrame
            
        Returns:
            分析結果の辞書
        """
        analysis = {}
        
        # 各スケジューラーごとの統計
        for scheduler_name in results_df['scheduler_name'].unique():
            scheduler_data = results_df[results_df['scheduler_name'] == scheduler_name]
            
            analysis[scheduler_name] = {
                'mean_score': scheduler_data['total_score'].mean(),
                'std_score': scheduler_data['total_score'].std(),
                'mean_completion_rate': scheduler_data['completion_rate'].mean(),
                'std_completion_rate': scheduler_data['completion_rate'].std(),
                'mean_deadline_compliance': scheduler_data['deadline_compliance_rate'].mean(),
                'std_deadline_compliance': scheduler_data['deadline_compliance_rate'].std(),
                'mean_efficiency': scheduler_data['efficiency'].mean(),
                'std_efficiency': scheduler_data['efficiency'].std()
            }
        
        # 全体比較
        analysis['summary'] = {
            'best_scheduler_by_score': results_df.groupby('scheduler_name')['total_score'].mean().idxmax(),
            'best_scheduler_by_completion': results_df.groupby('scheduler_name')['completion_rate'].mean().idxmax(),
            'best_scheduler_by_deadline': results_df.groupby('scheduler_name')['deadline_compliance_rate'].mean().idxmax(),
        }
        
        return analysis
    
    def statistical_significance_test(self, results_df: pd.DataFrame, metric: str = 'total_score') -> Dict[str, Any]:
        """
        スケジューラー間の統計的有意差を検定する
        
        Args:
            results_df: 実験結果のDataFrame
            metric: 比較する指標名
            
        Returns:
            統計検定の結果
        """
        from scipy import stats
        
        schedulers = results_df['scheduler_name'].unique()
        test_results = {}
        
        # 全ペアで t検定を実行
        for i, scheduler1 in enumerate(schedulers):
            for j, scheduler2 in enumerate(schedulers):
                if i < j:  # 重複を避ける
                    data1 = results_df[results_df['scheduler_name'] == scheduler1][metric]
                    data2 = results_df[results_df['scheduler_name'] == scheduler2][metric]
                    
                    # Welchのt検定（等分散を仮定しない）
                    t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)
                    
                    test_results[f"{scheduler1}_vs_{scheduler2}"] = {
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'mean_diff': data1.mean() - data2.mean()
                    }
        
        return test_results
    
    def generate_report(self, results_df: pd.DataFrame, save_path: str = None) -> str:
        """
        実験結果のレポートを生成する
        
        Args:
            results_df: 実験結果のDataFrame
            save_path: レポートを保存するパス（Noneの場合は保存しない）
            
        Returns:
            レポート文字列
        """
        analysis = self.analyze_results(results_df)
        significance = self.statistical_significance_test(results_df)
        
        report = []
        report.append("# タスクスケジューリング実験結果レポート")
        report.append(f"\n実験設定:")
        report.append(f"- 実験回数: {self.num_experiments}")
        report.append(f"- シミュレーション期間: {self.simulation_days}日")
        report.append(f"- 1日の作業時間: {self.work_hours_per_day}時間")
        
        report.append(f"\n## スケジューラー別結果")
        
        for scheduler_name, stats in analysis.items():
            if scheduler_name == 'summary':
                continue
            
            report.append(f"\n### {scheduler_name}")
            report.append(f"- 平均スコア: {stats['mean_score']:.2f} ± {stats['std_score']:.2f}")
            report.append(f"- 完了率: {stats['mean_completion_rate']:.3f} ± {stats['std_completion_rate']:.3f}")
            report.append(f"- 締切遵守率: {stats['mean_deadline_compliance']:.3f} ± {stats['std_deadline_compliance']:.3f}")
            report.append(f"- 効率: {stats['mean_efficiency']:.3f} ± {stats['std_efficiency']:.3f}")
        
        report.append(f"\n## 総合結果")
        summary = analysis['summary']
        report.append(f"- スコアが最も高い: {summary['best_scheduler_by_score']}")
        report.append(f"- 完了率が最も高い: {summary['best_scheduler_by_completion']}")
        report.append(f"- 締切遵守率が最も高い: {summary['best_scheduler_by_deadline']}")
        
        report.append(f"\n## 統計的有意差検定結果")
        for comparison, test_result in significance.items():
            significance_mark = "**" if test_result['significant'] else ""
            report.append(f"- {comparison}: p={test_result['p_value']:.4f} {significance_mark}")
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text