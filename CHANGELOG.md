# Changelog

## [Unreleased]

### Removed
- タスクのdifficulty属性を削除
- 未使用のRL実装（QLearningTaskSelector in rl_scheduler.py）を削除

### Changed
- 集中力マッチングをpriorityベースに変更
- 報酬計算をpriorityベースに変更
- ログと結果からdifficulty情報を削除
- `rl_policy_selector.py`のハードコードされた値を設定ファイルから読み込むよう変更

### Added
- TASK_PRIORITY_THRESHOLDS設定（priority値から集中力要件をマッピング）
- RL状態空間の離散化パラメータを`config.py`に追加（`RL_STATE_SPACE_CONFIG`）
- ユニットテストを追加（pytest）
  - RLスケジューラーのテスト
  - ポリシーセレクターのテスト
  - シミュレーション環境のテスト
  - 評価器のテスト

### Breaking Changes
- 学習済みモデル（rl_model_default.pkl）の再学習が必要
- 古いシミュレーションログとの互換性がなくなる
