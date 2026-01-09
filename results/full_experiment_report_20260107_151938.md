# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3047.38 ± 340.67
- 完了率: 0.706 ± 0.049
- 締切遵守率: 0.706 ± 0.049
- 効率: 0.909 ± 0.004

### priority_scheduler
- 平均スコア: 4782.76 ± 502.12
- 完了率: 0.582 ± 0.109
- 締切遵守率: 0.582 ± 0.109
- 効率: 0.914 ± 0.005

### random_scheduler
- 平均スコア: 3782.42 ± 423.28
- 完了率: 0.527 ± 0.068
- 締切遵守率: 0.527 ± 0.068
- 効率: 0.921 ± 0.005

### rl_scheduler
- 平均スコア: 3828.54 ± 313.56
- 完了率: 0.691 ± 0.080
- 締切遵守率: 0.691 ± 0.080
- 効率: 0.905 ± 0.003

## 総合結果
- スコアが最も高い: priority_scheduler
- 完了率が最も高い: deadline_scheduler
- 締切遵守率が最も高い: deadline_scheduler

## 統計的有意差検定結果
- deadline_scheduler_vs_priority_scheduler: p=0.0000 **
- deadline_scheduler_vs_random_scheduler: p=0.0000 **
- deadline_scheduler_vs_rl_scheduler: p=0.0000 **
- priority_scheduler_vs_random_scheduler: p=0.0000 **
- priority_scheduler_vs_rl_scheduler: p=0.0000 **
- random_scheduler_vs_rl_scheduler: p=0.5374 