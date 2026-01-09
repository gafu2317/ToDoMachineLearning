# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3044.28 ± 313.30
- 完了率: 0.690 ± 0.048
- 締切遵守率: 0.690 ± 0.048
- 効率: 0.910 ± 0.003

### priority_scheduler
- 平均スコア: 4754.54 ± 555.80
- 完了率: 0.562 ± 0.122
- 締切遵守率: 0.562 ± 0.122
- 効率: 0.914 ± 0.005

### random_scheduler
- 平均スコア: 3771.36 ± 458.03
- 完了率: 0.534 ± 0.056
- 締切遵守率: 0.534 ± 0.056
- 効率: 0.921 ± 0.005

### rl_scheduler
- 平均スコア: 4388.70 ± 407.55
- 完了率: 0.767 ± 0.062
- 締切遵守率: 0.767 ± 0.062
- 効率: 0.909 ± 0.003

## 総合結果
- スコアが最も高い: priority_scheduler
- 完了率が最も高い: rl_scheduler
- 締切遵守率が最も高い: rl_scheduler

## 統計的有意差検定結果
- deadline_scheduler_vs_priority_scheduler: p=0.0000 **
- deadline_scheduler_vs_random_scheduler: p=0.0000 **
- deadline_scheduler_vs_rl_scheduler: p=0.0000 **
- priority_scheduler_vs_random_scheduler: p=0.0000 **
- priority_scheduler_vs_rl_scheduler: p=0.0003 **
- random_scheduler_vs_rl_scheduler: p=0.0000 **