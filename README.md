# ToDoMachineLearning
知能プログラミング演習グループ課題

機械学習（強化学習）と単純なルールベース手法によるタスクスケジューリング性能の比較検証システム。

## 概要
集中力の変動を考慮した環境で、複数のタスクスケジューリング手法を比較し、強化学習の有効性を検証する。

### 仮説
自分で考えた単純な優先順位（期限順や重要度順）よりも、集中力の変動などを考慮した強化学習によるスケジューリングの方が効率的にタスクを完了できるのではないか。

## プロジェクト構成
```
├── src/                          # 核となるライブラリ
│   ├── models/                   # タスク・集中力モデル
│   ├── schedulers/               # スケジューリング手法
│   ├── environment/              # シミュレーション環境
│   ├── evaluation/               # 評価・分析システム
│   ├── visualization/            # 視覚化モジュール
│   └── utils/                    # 共通ユーティリティ
├── dataset/                      # タスクデータセット
│   ├── train/                    # 学習用（8000セット）
│   └── test/                     # テスト用（2000セット）
├── trained_models/               # 学習済みモデル・学習曲線
├── results/                      # 実験結果・グラフ・レポート
├── config.py                     # 設定ファイル
├── requirements.txt              # 依存関係
├── generate_task_dataset.py      # データセット生成
├── train_rl_model.py             # 強化学習モデル学習
├── run_full_experiment.py        # 本格実験実行
├── visualize_schedules.py        # スケジュール可視化
├── generate_detailed_log.py      # 詳細ログ生成
└── EXPERIMENT.md                 # 実験設計書（詳細）
```

## 実装済み機能
- ✅ 複数スケジューリング手法（期限順・重要度順・ランダム・強化学習）
- ✅ 集中力変動モデル（指数減衰・休憩回復・ジャンル切り替え効果）
- ✅ タスクデータセット自動生成（train/test分離）
- ✅ 強化学習モデル事前学習（Q-learning、1000エピソード）
- ✅ 学習曲線の視覚化（エピソード報酬の推移）
- ✅ 統計的有意差検定（Welchのt検定）
- ✅ 実験結果の総合視覚化（スコア比較、各指標比較、分布、有意差）
- ✅ 詳細レポート自動生成（Markdown、PDF）
- ✅ ジャンルシステム（4種類、切り替え効果あり）
- ✅ 公平な比較環境（全手法で同一タスクセット使用）

## 使用方法

### 0. 環境構築
```bash
# 依存関係インストール
pip install -r requirements.txt
```

### 1. タスクデータセット生成（初回のみ）
```bash
python generate_task_dataset.py
```

**生成内容：**
- 学習用データセット: 8,000セット（`dataset/train/`）
- テスト用データセット: 2,000セット（`dataset/test/`）
- 各セット60タスク、合計60万タスク
- 生成時間: 約100秒

**データセット設計：**
- 学習用とテスト用を完全に分離
- テストセットは学習に一切使用しない
- 過学習（オーバーフィッティング）の検出が可能

### 2. 強化学習モデルの学習
```bash
python train_rl_model.py
```

**学習内容：**
- エピソード数: 1,000回
- 学習データ: trainデータセットのみ使用（8,000セット）
- 学習時間: 数分～10分程度
- 出力ファイル:
  - `trained_models/rl_model_default.pkl` - 学習済みモデル
  - `trained_models/learning_curve_YYYYMMDD_HHMMSS.png` - 学習曲線
  - `trained_models/training_stats_YYYYMMDD_HHMMSS.txt` - 学習統計

**学習曲線とは：**
- 横軸: エピソード番号（1〜1000）
- 縦軸: 各エピソードでの累積報酬
- 内容: トレーニングデータを使って学習している最中の報酬の変化
- 確認できること:
  - 学習の進捗（報酬が上昇しているか）
  - 収束の状況（報酬が安定しているか）
  - 過学習の兆候（報酬が不安定になっていないか）

### 3. 実験実行・評価
```bash
# 本格統計実験（推奨）
python run_full_experiment.py

# スケジュール可視化（視覚的に各手法を比較）
python visualize_schedules.py

# 詳細ログ付き比較実験（1回のシミュレーション）
python generate_detailed_log.py
```

**実験内容（run_full_experiment.py）：**
- 評価データ: testデータセットのみ使用（2,000セット）
- 実験回数: 50回（デフォルト）
- 評価対象: 全4スケジューラ（期限順、重要度順、ランダム、強化学習）
- 出力ファイル:
  - `results/full_experiment_results_YYYYMMDD_HHMMSS.csv` - 詳細データ
  - `results/full_experiment_report_YYYYMMDD_HHMMSS.md` - テキストレポート
  - `results/rl_analysis_YYYYMMDD_HHMMSS.txt` - 強化学習詳細分析
  - `results/score_comparison_YYYYMMDD_HHMMSS.png` - スコア比較グラフ
  - `results/metrics_comparison_YYYYMMDD_HHMMSS.png` - 各指標比較グラフ
  - `results/score_distribution_YYYYMMDD_HHMMSS.png` - スコア分布（箱ひげ図）
  - `results/statistical_significance_YYYYMMDD_HHMMSS.png` - 統計的有意差検定
  - `results/comprehensive_report_YYYYMMDD_HHMMSS.pdf` - 総合レポート（PDF）

## 実験結果

### 最新実験結果（2026年1月25日実施、50回試行の平均）

| 手法 | 総スコア | 完了率 | 締切遵守率 | 効率 |
|------|----------|--------|-----------|------|
| **重要度順** | **4602点** ★ | 89.5% | 42.2% | 0.921 |
| **強化学習** | **4359点** | **91.0%** ★ | 42.5% | 0.921 |
| ランダム | 4193点 | 77.1% | 32.0% | 0.928 |
| 期限順 | 3569点 | 87.0% | 42.5% | 0.921 |

### 統計的有意差検定

**強化学習スケジューラとの比較（Welchのt検定、有意水準p<0.05）：**
- 期限順 vs 強化学習: **p=0.0000（有意差あり）**
- 重要度順 vs 強化学習: **p=0.0068（有意差あり）**
- ランダム vs 強化学習: **p=0.0446（有意差あり）**

### 主要な発見

1. **完了率で強化学習が最高を達成**
   - 強化学習: 91.0%（1位）
   - 重要度順: 89.5%
   - 差: +1.5ポイント

2. **スコアでは重要度順が最高**
   - 重要度順: 4602点（1位）
   - 強化学習: 4359点（2位）
   - 差: -243点（約5%）

3. **統計的有意性**
   - 全ての手法との比較で統計的に有意な差を確認
   - 強化学習は他の手法と異なる最適化戦略を学習

4. **性能の解釈**
   - **重要度順**: 高スコアのタスクを優先 → スコアは高いが完了率はやや低い
   - **強化学習**: 多くのタスクを完了させることを学習 → 完了率は最高だがスコアはやや低い
   - **期限順**: 締切重視 → スコアが低い
   - **ランダム**: ベースライン → 完了率が最低

### 結論

強化学習は**完了率**で最高性能を達成し、統計的に有意な差を示した。一方、**総スコア**では重要度順に及ばない結果となった。

これは、強化学習が「多くのタスクを確実に完了させる」戦略を学習したためと考えられる。重要度順は「高スコアのタスクを優先」する単純な戦略だが、その分完了率がやや低くなっている。

どちらが優れているかは、**評価指標をどこに置くか**による：
- タスクの完了数を重視 → 強化学習が有利
- 総スコアを重視 → 重要度順が有利

## 集中力モデル

### 基本パラメータ
- 初期集中力: 1.0（100%）
- 最低集中力: 0.2（20%）
- 連続作業可能時間: 120分（基準値）
- 休憩時間: 15分
- 減衰モデル: 指数減衰

### 減衰式
```
集中力 = 初期レベル × e^(-decay_factor × 連続作業時間 / 120)
```

### 個人差（concentration_sustainability）
- **short**: decay_factor = 1.3（疲れやすい）
- **medium**: decay_factor = 1.0（標準）
- **long**: decay_factor = 0.8（疲れにくい）

### 作業効率への影響
- 集中力 ≥ 0.7: 効率 0.8倍（20%時短）
- 0.4 ≤ 集中力 < 0.7: 効率 1.0倍（通常）
- 集中力 < 0.4: 効率 1.2倍（20%遅延）

### ジャンル切り替え効果
個人設定により2タイプ：
- **同ジャンル継続タイプ**: 同じジャンル継続で+5%、切り替えでペナルティなし
- **ジャンル切り替えタイプ**: ジャンル切り替えで+5%、継続でペナルティなし

## スケジューラ詳細

### 1. Deadline Scheduler（期限順）
- 戦略: 締切が近いタスクから優先的に実行
- 休憩: 集中力が0.4以下で休憩
- 特徴: シンプルで直感的

### 2. Priority Scheduler（重要度順）
- 戦略: 重要度が高いタスクから優先的に実行
- 休憩: 集中力が0.4以下で休憩
- 特徴: スコア最大化を狙う

### 3. Random Scheduler（ランダム）
- 戦略: 残りタスクからランダムに選択
- 休憩: 集中力が0.4以下で休憩
- 特徴: ベースライン（下限性能の確認）

### 4. RL Scheduler（強化学習）
- 戦略: Q-learningによる最適タスク選択
- 状態空間: タスク数、平均重要度、平均時間、最短締切、集中力
- 行動空間: どのタスクを実行するか
- 報酬関数:
  - 基本完了報酬: スコア × 0.1
  - 締切遵守ボーナス: 早期完了で最大+20
  - 締切違反ペナルティ: 遅延で最大-50
  - 高集中完了ボーナス: 集中力0.7以上で+5
- 学習設定:
  - 学習率: 0.1
  - 割引率: 0.9
  - 探索率（学習時）: 0.5 → 0.1
  - 探索率（テスト時）: 0.05

## 技術的詳細

詳細な実験設計は [EXPERIMENT.md](EXPERIMENT.md) を参照。

**主要ファイル：**
- [src/models/task.py](src/models/task.py) - タスクモデル、締切設定
- [src/models/concentration.py](src/models/concentration.py) - 集中力モデル
- [src/schedulers/rl_learning_scheduler.py](src/schedulers/rl_learning_scheduler.py) - 強化学習スケジューラ
- [src/schedulers/scheduler.py](src/schedulers/scheduler.py) - 基本スケジューラ
- [src/environment/simulation.py](src/environment/simulation.py) - シミュレーション環境
- [src/evaluation/evaluator.py](src/evaluation/evaluator.py) - 評価システム
- [src/visualization/result_plotter.py](src/visualization/result_plotter.py) - 視覚化モジュール
- [src/utils/task_loader.py](src/utils/task_loader.py) - タスクデータローダー

## テスト

### テストの実行

```bash
# 全テスト実行
pytest tests/

# カバレッジ付き実行
pytest tests/ --cov=src --cov-report=html
```

### テストの構成

- `tests/test_rl_learning_scheduler.py` - RLスケジューラーのテスト
- `tests/test_rl_policy_selector.py` - ポリシーセレクターのテスト
- `tests/test_simulation.py` - シミュレーション環境のテスト
- `tests/test_evaluator.py` - 評価器のテスト

## FAQ

### Q1. データセットを再生成する必要はありますか？
データセットは一度生成すれば、何度でも使い回せます。ただし、実験条件を変更した場合は再生成が必要です。

### Q2. 学習済みモデルを再利用できますか？
`trained_models/rl_model_default.pkl`が存在する場合、自動的に読み込まれます。再学習したい場合は、`train_rl_model.py`を再実行してください。

### Q3. 実験回数を変更できますか？
`config.py`の`EXPERIMENT_CONFIG['num_experiments']`を変更してください。デフォルトは50回です。

### Q4. 学習曲線が不安定な場合は？
エピソード数を増やす（`train_rl_model.py`の`num_episodes`）か、学習率を調整（`config.py`の`RL_CONFIG['learning_rate']`）してください。

### Q5. 過学習を確認する方法は？
- 学習曲線が収束しているか確認
- train/testスコア差を確認（大きな差がある場合は過学習の可能性）
- テストデータでの性能が学習データより大幅に低い場合は要注意

## ライセンス

このプロジェクトは教育目的で作成されました。

## 貢献者

知能プログラミング演習グループメンバー

---

**最終更新日**: 2026年1月25日
