# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3569.08 ± 443.05
- 完了率: 0.870 ± 0.050
- 締切遵守率: 0.425 ± 0.056
- 効率: 0.921 ± 0.005

### priority_scheduler
- 平均スコア: 4601.96 ± 448.84
- 完了率: 0.895 ± 0.045
- 締切遵守率: 0.422 ± 0.064
- 効率: 0.921 ± 0.005

### random_scheduler
- 平均スコア: 4193.46 ± 380.38
- 完了率: 0.771 ± 0.073
- 締切遵守率: 0.320 ± 0.059
- 効率: 0.928 ± 0.006

### rl_scheduler
- 平均スコア: 4358.88 ± 430.83
- 完了率: 0.910 ± 0.035
- 締切遵守率: 0.425 ± 0.056
- 効率: 0.921 ± 0.005

## 総合結果
- スコアが最も高い: priority_scheduler
- 完了率が最も高い: rl_scheduler
- 締切遵守率が最も高い: deadline_scheduler

## 統計的有意差検定結果
- deadline_scheduler_vs_priority_scheduler: p=0.0000 **
- deadline_scheduler_vs_random_scheduler: p=0.0000 **
- deadline_scheduler_vs_rl_scheduler: p=0.0000 **
- priority_scheduler_vs_random_scheduler: p=0.0000 **
- priority_scheduler_vs_rl_scheduler: p=0.0068 **
- random_scheduler_vs_rl_scheduler: p=0.0446 **