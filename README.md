# ToDoMachineLearning
知能プログラミング演習グループ課題

機械学習（強化学習）と単純なルールベース手法によるタスクスケジューリング性能の比較検証システム。

## 概要
集中力の変動を考慮した環境で、複数のタスクスケジューリング手法を比較し、最適なスケジューリング戦略を検証する。

## プロジェクト構成
```
├── src/                    # 核となるライブラリ
│   ├── models/            # タスク・集中力モデル
│   ├── schedulers/        # スケジューリング手法
│   ├── environment/       # シミュレーション環境
│   ├── evaluation/        # 評価・分析システム
│   └── utils/            # 共通ユーティリティ
├── results/              # 実験結果ファイル
├── config.py            # 設定ファイル
├── requirements.txt     # 依存関係
├── generate_detailed_log.py     # 詳細ログ生成
└── run_full_experiment.py      # 本格実験実行
```

## 実装済み機能
- ✅ 複数スケジューリング手法（期限順・重要度順・ランダム・強化学習）
- ✅ 集中力変動モデル
- ✅ 統計的有意差検定
- ✅ 詳細ログ出力・分析
- ✅ 公平な比較環境

## 使用方法
```bash
# 依存関係インストール
pip install -r requirements.txt

# 詳細ログ付き比較実験
python generate_detailed_log.py

# 本格統計実験
python run_full_experiment.py
```

## 実験結果
重要度順スケジューラーが最も高い性能を示し、期限順スケジューラーは完了率では優秀だがスコア効率が劣ることが判明。詳細な結果は`results/`フォルダを参照。
