import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic']
plt.rcParams['axes.unicode_minus'] = False


class ScheduleVisualizer:
    """Visualize schedules in Gantt chart format"""

    # Colors by priority
    PRIORITY_COLORS = {
        'HIGH': '#FF6B6B',    # Red
        'MEDIUM': '#FFD93D',  # Yellow
        'LOW': '#6BCF7F'      # Green
    }

    BREAK_COLOR = '#CCCCCC'  # Gray (break)
    FAIL_MARKER = 'X'
    SUCCESS_MARKER = 'O'

    def __init__(self, start_hour: int = 9, end_hour: int = 17, simulation_days: int = 7):
        """
        Args:
            start_hour: Start hour
            end_hour: End hour
            simulation_days: Number of simulation days
        """
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.simulation_days = simulation_days
        self.work_hours = end_hour - start_hour

    def visualize_schedules(self,
                           results: Dict[str, Dict[str, Any]],
                           output_path: str = 'results/schedule_comparison.png'):
        """
        Visualize multiple scheduler results side-by-side

        Args:
            results: Dict of {scheduler_name: simulation_result}
            output_path: Output image file path
        """
        num_schedulers = len(results)

        # Determine figure size (arrange horizontally with space for incomplete tasks chart)
        fig = plt.figure(figsize=(6 * num_schedulers, 12))

        # Create grid: main schedule + incomplete task chart
        gs = fig.add_gridspec(2, num_schedulers, height_ratios=[3, 1], hspace=0.3)

        schedule_axes = []
        incomplete_axes = []

        for i in range(num_schedulers):
            schedule_axes.append(fig.add_subplot(gs[0, i]))
            incomplete_axes.append(fig.add_subplot(gs[1, i]))

        # Draw schedule for each scheduler
        for ax, incomplete_ax, (scheduler_name, result) in zip(schedule_axes, incomplete_axes, results.items()):
            self._draw_schedule(ax, scheduler_name, result)
            self._draw_incomplete_tasks_chart(incomplete_ax, scheduler_name, result)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Schedule saved: {output_path}")
        plt.close()

    def _draw_schedule(self, ax, scheduler_name: str, result: Dict[str, Any]):
        """
        Draw schedule for one scheduler

        Args:
            ax: matplotlib axes
            scheduler_name: Scheduler name
            result: Simulation result
        """
        # Title
        completion_rate = result['completion_rate'] * 100
        total_score = result['total_score']
        ax.set_title(f"{scheduler_name}\nCompletion: {completion_rate:.1f}% | Score: {total_score}",
                    fontsize=12, fontweight='bold')

        # Extract tasks and breaks from log
        simulation_log = result.get('simulation_log', [])

        # Simulation start time
        start_time = datetime(2024, 1, 1, self.start_hour, 0)

        # Draw each log entry
        for entry in simulation_log:
            time = datetime.fromisoformat(entry['time'])
            action = entry['action']
            duration = entry['duration']

            # Calculate task start time (entry['time'] is end time)
            task_end_time = time
            task_start_time = task_end_time - timedelta(minutes=duration)

            # Calculate day and time within day
            # Day is based on calendar date
            day = (task_start_time.date() - start_time.date()).days

            # Time within day (in minutes from work start hour)
            time_in_day_start = (task_start_time.hour - self.start_hour) * 60 + task_start_time.minute
            time_in_day_end = (task_end_time.hour - self.start_hour) * 60 + task_end_time.minute

            # Skip if outside working hours or day range
            if day < 0 or day >= self.simulation_days:
                continue

            if action == 'work':
                task_id = entry['task_id']
                completed = entry.get('completed', False)

                # Get task info
                task_info = self._find_task_info(result, task_id)
                if task_info:
                    priority = task_info['priority']
                    color = self.PRIORITY_COLORS.get(priority, '#888888')

                    label = f"T{task_id}"

                    # Draw bar
                    self._draw_bar(ax, day, time_in_day_start, duration, color, label)

            elif action == 'break':
                # Break bar
                self._draw_bar(ax, day, time_in_day_start, duration, self.BREAK_COLOR, 'Break')

        # Axis settings
        ax.set_xlim(-0.5, self.simulation_days - 0.5)
        ax.set_ylim(0, self.work_hours * 60)

        # X-axis (date)
        ax.set_xticks(range(self.simulation_days))
        ax.set_xticklabels([f'Day {i+1}' for i in range(self.simulation_days)])
        ax.set_xlabel('Date', fontsize=10)

        # Y-axis (time)
        y_ticks = np.arange(0, self.work_hours * 60 + 1, 60)
        y_labels = [f'{self.start_hour + i}:00' for i in range(self.work_hours + 1)]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_ylabel('Time', fontsize=10)

        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.invert_yaxis()  # Time flows from top to bottom

        # Legend
        high_patch = mpatches.Patch(color=self.PRIORITY_COLORS['HIGH'], label='Priority: High')
        medium_patch = mpatches.Patch(color=self.PRIORITY_COLORS['MEDIUM'], label='Priority: Medium')
        low_patch = mpatches.Patch(color=self.PRIORITY_COLORS['LOW'], label='Priority: Low')
        break_patch = mpatches.Patch(color=self.BREAK_COLOR, label='Break')
        ax.legend(handles=[high_patch, medium_patch, low_patch, break_patch],
                 loc='upper right', fontsize=8)

        # Display incomplete tasks (bottom of figure)
        incomplete_tasks = result['tasks']['incomplete']
        if incomplete_tasks:
            incomplete_text = f"Incomplete: {len(incomplete_tasks)} tasks"
            ax.text(0.02, 0.98, incomplete_text,
                   transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    def _draw_bar(self, ax, day: int, start_minutes: float, duration: float,
                  color: str, label: str):
        """
        Draw bar on Gantt chart

        Args:
            ax: matplotlib axes
            day: Day number (0-indexed)
            start_minutes: Start time (minutes from work start hour)
            duration: Duration (minutes)
            color: Bar color
            label: Label
        """
        # Bar width
        bar_width = 0.8

        # Draw bar
        rect = mpatches.Rectangle((day - bar_width/2, start_minutes),
                                  bar_width, duration,
                                  facecolor=color, edgecolor='black', linewidth=0.5)
        ax.add_patch(rect)

        # Draw label (only if bar is long enough)
        if duration > 15:  # Only show label for tasks > 15 minutes
            text_y = start_minutes + duration / 2
            ax.text(day, text_y, label,
                   ha='center', va='center',
                   fontsize=7, fontweight='bold',
                   color='black' if color == self.BREAK_COLOR else 'white')

    def _find_task_info(self, result: Dict[str, Any], task_id: int) -> Dict[str, Any]:
        """
        Get task info from completed/incomplete tasks by task ID

        Args:
            result: Simulation result
            task_id: Task ID

        Returns:
            Task info dict (None if not found)
        """
        # Search in completed tasks
        for task in result['tasks']['completed']:
            if task['id'] == task_id:
                return task

        # Search in incomplete tasks
        for task in result['tasks']['incomplete']:
            if task['id'] == task_id:
                return task

        return None

    def _draw_incomplete_tasks_chart(self, ax, scheduler_name: str, result: Dict[str, Any]):
        """
        Draw incomplete tasks visualization with overdue status

        Args:
            ax: matplotlib axes
            scheduler_name: Scheduler name
            result: Simulation result
        """
        incomplete_tasks = result['tasks']['incomplete']

        if not incomplete_tasks:
            ax.text(0.5, 0.5, 'All tasks completed!',
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   transform=ax.transAxes)
            ax.axis('off')
            return

        # Get simulation end time
        sim_end_time = datetime(2024, 1, 1 + self.simulation_days, self.start_hour, 0)

        # Check each task's deadline to determine if overdue
        def is_overdue(task):
            deadline_str = task.get('deadline', '')
            if deadline_str:
                try:
                    deadline = datetime.fromisoformat(deadline_str)
                    return sim_end_time > deadline
                except:
                    pass
            return False

        # Count overdue tasks
        overdue_count = sum(1 for task in incomplete_tasks if is_overdue(task))
        total_incomplete = len(incomplete_tasks)

        # Sort tasks by priority (HIGH -> MEDIUM -> LOW) and duration
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        priority_value = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}

        # Calculate duration from score (score = duration * priority_value)
        def get_duration(task):
            score = task.get('score', 0)
            priority = task['priority']
            return score / priority_value[priority]

        sorted_tasks = sorted(incomplete_tasks,
                             key=lambda t: (priority_order[t['priority']], -get_duration(t)))

        # Calculate total time and individual task durations
        task_durations = []
        total_time = 0
        for task in sorted_tasks:
            duration = get_duration(task)
            task_durations.append(duration)
            total_time += duration

        # Draw individual task bars with separators
        left = 0
        for task, duration in zip(sorted_tasks, task_durations):
            priority = task['priority']
            color = self.PRIORITY_COLORS[priority]
            width = duration / total_time if total_time > 0 else 0

            # Check if this task is overdue
            task_overdue = is_overdue(task)

            # Draw task bar with hatching for overdue tasks
            if task_overdue:
                # Overdue: add hatching pattern
                ax.barh(0, width, left=left, height=0.5, color=color,
                       edgecolor='red', linewidth=2.0, hatch='///', alpha=0.8)
            else:
                # Not overdue: normal bar
                ax.barh(0, width, left=left, height=0.5, color=color,
                       edgecolor='black', linewidth=1.0)

            # Add task ID label if segment is large enough
            if width > 0.05:  # Show label for segments > 5%
                task_label = f"T{task['id']}"
                ax.text(left + width/2, 0, task_label,
                       ha='center', va='center', fontsize=7, fontweight='bold', color='white')

            left += width

        # Title with overdue info
        if overdue_count > 0:
            title_text = f'Incomplete: {total_incomplete} tasks ({int(total_time)}min)\n[OVERDUE: {overdue_count} tasks]'
        else:
            title_text = f'Incomplete: {total_incomplete} tasks ({int(total_time)}min)'

        ax.set_title(title_text, fontsize=10, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')
