"""
事前生成されたタスクデータを読み込むユーティリティ
"""

import json
import os
from typing import List
from datetime import datetime
from ..models.task import Task, Priority

class TaskDataLoader:
    """タスクデータセットローダー"""

    def __init__(self, dataset_type: str = 'train'):
        """
        Args:
            dataset_type: 'train' or 'test'
        """
        if dataset_type not in ['train', 'test']:
            raise ValueError(f"dataset_type must be 'train' or 'test', got {dataset_type}")

        self.dataset_type = dataset_type
        self.dataset_dir = f"dataset/{dataset_type}"

        if not os.path.exists(self.dataset_dir):
            raise FileNotFoundError(
                f"データセットディレクトリが見つかりません: {self.dataset_dir}\n"
                f"generate_task_dataset.pyを実行してデータセットを生成してください"
            )

        # 利用可能なファイル一覧
        self.task_files = sorted([
            f for f in os.listdir(self.dataset_dir)
            if f.startswith('tasks_') and f.endswith('.json')
        ])

        if not self.task_files:
            raise FileNotFoundError(f"{self.dataset_dir}にタスクファイルが見つかりません")

        print(f"✅ {dataset_type}データセット読み込み: {len(self.task_files)}ファイル")

    def load_tasks(self, index: int) -> List[Task]:
        """
        指定インデックスのタスクセットを読み込む

        Args:
            index: タスクセットのインデックス（0から始まる）

        Returns:
            Taskオブジェクトのリスト
        """
        if index < 0 or index >= len(self.task_files):
            raise IndexError(
                f"インデックスが範囲外です: {index} "
                f"(利用可能: 0-{len(self.task_files)-1})"
            )

        filename = os.path.join(self.dataset_dir, self.task_files[index])

        with open(filename, 'r', encoding='utf-8') as f:
            task_data_list = json.load(f)

        tasks = [dict_to_task(td) for td in task_data_list]
        return tasks

    def get_num_datasets(self) -> int:
        """利用可能なデータセット数を返す"""
        return len(self.task_files)

def dict_to_task(task_dict: dict) -> Task:
    """辞書からTaskオブジェクトを復元"""
    task = Task(
        id=task_dict['id'],
        name=task_dict.get('name', f"Task_{task_dict['id']}"),
        base_duration_minutes=task_dict['base_duration_minutes'],
        priority=Priority[task_dict['priority']],
        deadline=datetime.fromisoformat(task_dict['deadline']),
        genre=task_dict['genre']
    )
    task.is_completed = task_dict['is_completed']
    return task
