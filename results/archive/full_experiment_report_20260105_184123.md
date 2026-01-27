# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 30
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3738.57 ± 296.70
- 完了率: 0.770 ± 0.052
- 締切遵守率: 0.770 ± 0.052
- 効率: 0.912 ± 0.003

### priority_scheduler
- 平均スコア: 5846.33 ± 531.90
- 完了率: 0.778 ± 0.072
- 締切遵守率: 0.778 ± 0.072
- 効率: 0.913 ± 0.003

### random_scheduler
- 平均スコア: 4857.27 ± 417.28
- 完了率: 0.666 ± 0.062
- 締切遵守率: 0.666 ± 0.062
- 効率: 0.921 ± 0.004

### rl_scheduler
- 平均スコア: 2840.93 ± 1693.54
- 完了率: 0.380 ± 0.220
- 締切遵守率: 0.380 ± 0.220
- 効率: 0.921 ± 0.008

## 総合結果
- スコアが最も高い: priority_scheduler
- 完了率が最も高い: priority_scheduler
- 締切遵守率が最も高い: priority_scheduler

## 統計的有意差検定結果
- deadline_scheduler_vs_priority_scheduler: p=0.0000 **
- deadline_scheduler_vs_random_scheduler: p=0.0000 **
- deadline_scheduler_vs_rl_scheduler: p=0.0076 **
- priority_scheduler_vs_random_scheduler: p=0.0000 **
- priority_scheduler_vs_rl_scheduler: p=0.0000 **
- random_scheduler_vs_rl_scheduler: p=0.0000 **