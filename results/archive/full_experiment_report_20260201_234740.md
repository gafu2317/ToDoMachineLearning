# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3697.12 ± 342.51
- 完了率: 0.887 ± 0.051
- 締切遵守率: 0.432 ± 0.070
- 効率: 0.921 ± 0.005

### priority_scheduler
- 平均スコア: 4640.74 ± 440.52
- 完了率: 0.896 ± 0.065
- 締切遵守率: 0.427 ± 0.083
- 効率: 0.919 ± 0.005

### random_scheduler
- 平均スコア: 4198.72 ± 388.33
- 完了率: 0.775 ± 0.084
- 締切遵守率: 0.329 ± 0.082
- 効率: 0.927 ± 0.007

### rl_scheduler
- 平均スコア: 4357.62 ± 380.26
- 完了率: 0.914 ± 0.039
- 締切遵守率: 0.432 ± 0.070
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
- priority_scheduler_vs_rl_scheduler: p=0.0009 **
- random_scheduler_vs_rl_scheduler: p=0.0413 **