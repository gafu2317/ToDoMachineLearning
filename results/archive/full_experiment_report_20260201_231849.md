# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3623.68 ± 373.96
- 完了率: 0.872 ± 0.045
- 締切遵守率: 0.427 ± 0.063
- 効率: 0.921 ± 0.004

### priority_scheduler
- 平均スコア: 4731.62 ± 451.70
- 完了率: 0.894 ± 0.043
- 締切遵守率: 0.419 ± 0.069
- 効率: 0.921 ± 0.005

### random_scheduler
- 平均スコア: 4212.50 ± 416.08
- 完了率: 0.765 ± 0.063
- 締切遵守率: 0.320 ± 0.062
- 効率: 0.927 ± 0.005

### rl_scheduler
- 平均スコア: 4372.16 ± 345.50
- 完了率: 0.909 ± 0.031
- 締切遵守率: 0.427 ± 0.063
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
- priority_scheduler_vs_rl_scheduler: p=0.0000 **
- random_scheduler_vs_rl_scheduler: p=0.0395 **