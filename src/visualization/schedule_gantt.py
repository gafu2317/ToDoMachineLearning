"""
スケジュール比較ガンツチャートの生成
4つのスケジューラーの実行スケジュールを横並びで可視化する
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FixedFormatter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


# 色定義
COLOR_HIGH = '#FF6B6B'
COLOR_MEDIUM = '#FFD93D'
COLOR_LOW = '#6BCF7F'
COLOR_BREAK = '#C8C8C8'

PRIORITY_COLORS = {
    'HIGH': COLOR_HIGH,
    'MEDIUM': COLOR_MEDIUM,
    'LOW': COLOR_LOW,
}

PRIORITY_VALUES = {
    'HIGH': 3,
    'MEDIUM': 2,
    'LOW': 1,
}

# シミュレーション基準時刻
SIM_START = datetime(2024, 1, 1, 9, 0)
WORK_MINUTES_PER_DAY = 480  # 8時間


def generate_schedule_comparison(schedule_results: Dict[str, Dict], output_path: str):
    """
    スケジュール比較ガンツチャートを生成する

    Args:
        schedule_results: スケジューラー名をキー、run_simulation_with_tasks()の戻り値を値とする辞書
        output_path: 出力画像パス
    """
    num_schedulers = len(schedule_results)

    fig = plt.figure(figsize=(22, 12))
    gs = fig.add_gridspec(2, num_schedulers, height_ratios=[4, 1], hspace=0.35, wspace=0.3)

    for col, (name, result) in enumerate(schedule_results.items()):
        ax_gantt = fig.add_subplot(gs[0, col])
        _draw_gantt(ax_gantt, name, result)

        ax_inc = fig.add_subplot(gs[1, col])
        _draw_incomplete(ax_inc, result)

    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def _build_task_priority_map(result: Dict) -> Dict[int, str]:
    """
    task_id -> priority名 の辞書を作成する

    完了タスクと未完了タスク両方から収集する
    """
    priority_map = {}
    for task_info in result['tasks']['completed']:
        priority_map[task_info['id']] = task_info['priority']
    for task_info in result['tasks']['incomplete']:
        priority_map[task_info['id']] = task_info['priority']
    return priority_map


def _draw_gantt(ax: plt.Axes, scheduler_name: str, result: Dict):
    """
    1つのガンツチャートを描画する

    Args:
        ax: matplotlib Axes
        scheduler_name: スケジューラー名
        result: シミュレーション結果
    """
    task_priority_map = _build_task_priority_map(result)
    simulation_log = result['simulation_log']

    total_tasks = result['tasks']['total']
    completed_count = result['completed_tasks_count']
    completion_pct = result['completion_rate'] * 100
    total_score = result['total_score']
    incomplete_count = result['incomplete_tasks_count']

    for entry in simulation_log:
        # 終了時刻をパース
        end_time = datetime.fromisoformat(entry['time'])
        duration = entry['duration']

        # 開始時刻を算出
        start_time_dt = end_time - timedelta(minutes=duration)

        # 何日目か（日付の差分で算出）
        day = (start_time_dt.date() - SIM_START.date()).days
        if day < 0 or day > 6:
            continue

        # その日の9:00からの経過分数
        day_9am = datetime(start_time_dt.year, start_time_dt.month, start_time_dt.day, 9, 0)
        day_start_minutes = (start_time_dt - day_9am).total_seconds() / 60.0
        bar_duration = duration

        if bar_duration <= 0:
            continue

        # 色決定
        if entry['action'] == 'break':
            color = COLOR_BREAK
            label_text = None
        else:
            task_id = entry['task_id']
            priority = task_priority_map.get(task_id, 'LOW')
            color = PRIORITY_COLORS.get(priority, COLOR_LOW)
            label_text = f"T{task_id}"

        # バルを描画（x=day, y=day_start_minutes, width=0.9, height=bar_duration）
        rect = Rectangle(
            (day - 0.45, day_start_minutes),
            0.9,
            bar_duration,
            facecolor=color,
            edgecolor='black',
            linewidth=0.7
        )
        ax.add_patch(rect)

        # ラベル（12分未満なら非表示）
        if label_text and bar_duration >= 12:
            ax.text(
                day,
                day_start_minutes + bar_duration / 2,
                label_text,
                ha='center',
                va='center',
                fontsize=6.5,
                color='black',
                fontweight='bold'
            )

    # Y軸を反転（上が9:00、下が17:00）
    ax.set_ylim(WORK_MINUTES_PER_DAY, 0)
    ax.set_xlim(-0.5, 6.5)

    # X軸設定（FixedLocatorで全7日を強制表示）
    ax.xaxis.set_major_locator(FixedLocator(range(7)))
    ax.xaxis.set_major_formatter(FixedFormatter([f"Day {i+1}" for i in range(7)]))
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Date', fontsize=9)

    # Y軸設定
    y_ticks = list(range(0, WORK_MINUTES_PER_DAY + 1, 60))
    y_labels = [f"{9 + h}:00" for h in range(9)]  # 9:00 ~ 17:00
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=7.5)
    ax.set_ylabel('Time', fontsize=9)

    # レジェンド
    legend_patches = [
        mpatches.Patch(color=COLOR_HIGH, label='Priority: High'),
        mpatches.Patch(color=COLOR_MEDIUM, label='Priority: Medium'),
        mpatches.Patch(color=COLOR_LOW, label='Priority: Low'),
        mpatches.Patch(color=COLOR_BREAK, label='Break'),
    ]
    legend = ax.legend(
        handles=legend_patches,
        loc='upper left',
        fontsize=6.5,
        framealpha=0.9,
        title=f'Incomplete: {incomplete_count} tasks',
        title_fontsize=7,
    )

    # タイトル2行
    ax.set_title(
        f"{scheduler_name}\n"
        f"Completion: {completion_pct:.1f}% | Score: {total_score}",
        fontsize=10,
        fontweight='bold',
        pad=10
    )

    ax.grid(axis='y', linestyle=':', alpha=0.3)


def _draw_incomplete(ax: plt.Axes, result: Dict):
    """
    未完了タスクの水平スタックバルグラフを描画する

    Args:
        ax: matplotlib Axes
        result: シミュレーション結果
    """
    incomplete_list = result['tasks']['incomplete']

    if not incomplete_list:
        ax.axis('off')
        ax.set_title('Incomplete: 0 tasks (0min)', fontsize=9, fontweight='bold')
        return

    # 各タスクのdurationを復元: base_duration = score / priority_value
    tasks_with_dur = []
    for task_info in incomplete_list:
        priority = task_info['priority']
        pval = PRIORITY_VALUES.get(priority, 1)
        duration = task_info['score'] / pval
        tasks_with_dur.append({
            'id': task_info['id'],
            'priority': priority,
            'duration': duration,
        })

    # HIGH → MEDIUM → LOW の順にソート
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    tasks_with_dur.sort(key=lambda t: (priority_order.get(t['priority'], 3), t['id']))

    total_min = sum(t['duration'] for t in tasks_with_dur)
    num_incomplete = len(tasks_with_dur)

    # タイトル
    ax.set_title(
        f"Incomplete: {num_incomplete} tasks ({int(total_min)}min)",
        fontsize=9,
        fontweight='bold'
    )

    # 水平スタックバーを描画
    x_offset = 0.0
    for task in tasks_with_dur:
        color = PRIORITY_COLORS.get(task['priority'], COLOR_LOW)
        dur = task['duration']

        rect = Rectangle(
            (x_offset, 0.2),
            dur,
            0.6,
            facecolor=color,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(rect)

        # ラベル（幅が狭ければ非表示）
        if dur >= 12:
            ax.text(
                x_offset + dur / 2,
                0.5,
                f"T{task['id']}",
                ha='center',
                va='center',
                fontsize=6,
                color='black',
                fontweight='bold'
            )

        x_offset += dur

    ax.set_xlim(0, x_offset if x_offset > 0 else 1)
    ax.set_ylim(0, 1)
    ax.axis('off')


def generate_weekly_progression(weekly_results: Dict[str, Dict], output_path: str):
    """
    RL スケジューラーの週ごとの学習進行を可視化する

    Args:
        weekly_results: キー = "Week 1" 等、値 = run_simulation_with_tasks() の戻り値
        output_path: 出力画像パス
    """
    num_weeks = len(weekly_results)

    fig = plt.figure(figsize=(7 * num_weeks, 10))
    gs = fig.add_gridspec(2, num_weeks, height_ratios=[4, 1], hspace=0.35, wspace=0.3)

    for col, (week_label, result) in enumerate(weekly_results.items()):
        ax_gantt = fig.add_subplot(gs[0, col])
        _draw_gantt(ax_gantt, week_label, result)

        ax_inc = fig.add_subplot(gs[1, col])
        _draw_incomplete(ax_inc, result)

    fig.suptitle('RL Scheduler: Weekly Learning Progression', fontsize=14, fontweight='bold', y=1.02)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
