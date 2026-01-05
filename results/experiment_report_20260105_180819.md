# タスクスケジューリング実験結果レポート

実験設定:
- 実験回数: 50
- シミュレーション期間: 7日
- 1日の作業時間: 8時間

## スケジューラー別結果

### deadline_scheduler
- 平均スコア: 3880.18 ± 278.39
- 完了率: 0.792 ± 0.038
- 締切遵守率: 0.792 ± 0.038
- 効率: 0.912 ± 0.003

### priority_scheduler
- 平均スコア: 5644.70 ± 540.58
- 完了率: 0.800 ± 0.056
- 締切遵守率: 0.800 ± 0.056
- 効率: 0.913 ± 0.003

### random_scheduler
- 平均スコア: 4867.90 ± 384.75
- 完了率: 0.659 ± 0.054
- 締切遵守率: 0.659 ± 0.054
- 効率: 0.921 ± 0.004

## 総合結果
- スコアが最も高い: priority_scheduler
- 完了率が最も高い: priority_scheduler
- 締切遵守率が最も高い: priority_scheduler

## 統計的有意差検定結果
- deadline_scheduler_vs_priority_scheduler: p=0.0000 **
- deadline_scheduler_vs_random_scheduler: p=0.0000 **
- priority_scheduler_vs_random_scheduler: p=0.0000 **