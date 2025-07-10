# environment.py

import numpy as np
from collections import defaultdict
from typing import Dict, List, TYPE_CHECKING

# وارد کردن کلاس‌های داده‌ای مورد نیاز از ماژول مشترک
from common import CellType, Position, Action, Perception, Direction

# این یک تکنیک استاندارد در پایتون برای جلوگیری از خطای وابستگی دایره‌ای (Circular Dependency) است.
# چون environment به Agent نیاز دارد و agents نیز به Perception نیاز دارد که در environment تعریف می‌شود.
if TYPE_CHECKING:
    from agents import Agent


class GridWorld:
    """
    کلاس محیط که مسئولیت مدیریت وضعیت جهان و اجرای اقدامات را بر عهده دارد.
    این نسخه برای ثبت دقیق "زمان تکمیل وظیفه" به‌روزرسانی شده است.
    """

    def __init__(self, width: int, height: int, perception_range: int = 2):
        """سازنده کلاس که محیط را با ابعاد مشخص مقداردهی اولیه می‌کند."""
        self.width = width
        self.height = height
        self.perception_range = perception_range
        self.time_step = 0

        # ساختارهای داده برای نگهداری وضعیت محیط
        self.grid: Dict[Position, CellType] = defaultdict(lambda: CellType.EMPTY)
        self.agents: Dict[int, 'Agent'] = {}
        self.agent_positions: Dict[int, Position] = {}

        # متریک‌های عملکرد برای ارزیابی
        self.initial_resource_count = 0
        self.tasks_completed = 0
        self.task_completion_times: List[int] = []

    def add_walls(self, wall_positions: List[Position]):
        """دیوارها را به محیط اضافه می‌کند."""
        for pos in wall_positions:
            if self.is_valid_position(pos):
                self.grid[pos] = CellType.WALL

    def add_goals(self, goal_positions: List[Position]):
        """اهداف را به محیط اضافه می‌کند."""
        for pos in goal_positions:
            if self.is_valid_position(pos):
                self.grid[pos] = CellType.GOAL

    def add_resources(self, resource_positions: List[Position]):
        """منابع را به محیط اضافه می‌کند."""
        for pos in resource_positions:
            if self.is_valid_position(pos):
                self.grid[pos] = CellType.RESOURCE
        self.initial_resource_count = len(resource_positions)

    def add_hazards(self, hazard_positions: List[Position]):
        """خطرات را به محیط اضافه می‌کند."""
        for pos in hazard_positions:
            if self.is_valid_position(pos):
                self.grid[pos] = CellType.HAZARD

    def add_agent(self, agent: 'Agent', position: Position) -> bool:
        """یک عامل جدید را به محیط اضافه می‌کند."""
        if self.is_position_free(position):
            agent_id = len(self.agents) + 1
            agent.agent_id = agent_id
            self.agents[agent_id] = agent
            self.agent_positions[agent_id] = position
            return True
        return False

    def is_valid_position(self, pos: Position) -> bool:
        """بررسی می‌کند که آیا یک موقعیت در محدوده شبکه قرار دارد یا خیر."""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_position_free(self, pos: Position) -> bool:
        """بررسی می‌کند که آیا یک موقعیت برای قرارگیری عامل آزاد است (دیوار یا عامل دیگری نباشد)."""
        is_wall = self.grid.get(pos) == CellType.WALL
        is_occupied = pos in self.agent_positions.values()
        return self.is_valid_position(pos) and not is_wall and not is_occupied

    def get_perception(self, agent_id: int) -> Perception:
        """ادراک محلی را برای یک عامل مشخص تولید می‌کند."""
        agent_pos = self.agent_positions[agent_id]
        agent = self.agents[agent_id]
        visible_cells: Dict[Position, CellType] = {}

        # ایجاد محدوده دید 5x5
        for y_offset in range(-self.perception_range, self.perception_range + 1):
            for x_offset in range(-self.perception_range, self.perception_range + 1):
                pos = Position(agent_pos.x + x_offset, agent_pos.y + y_offset)
                if not self.is_valid_position(pos):
                    visible_cells[pos] = CellType.WALL
                else:
                    visible_cells[pos] = self.grid.get(pos, CellType.EMPTY)

        return Perception(
            position=agent_pos,
            visible_cells=visible_cells,
            visible_agents={},  # برای سادگی، این بخش پیاده‌سازی نشده است
            energy_level=agent.total_rewards,
            has_resource=(agent.action_history.count(Action.PICKUP) > agent.action_history.count(Action.DROP)),
            messages=[]  # برای سادگی، این بخش پیاده‌سازی نشده است
        )

    def execute_action(self, agent_id: int, action: Action):
        """یک اقدام مشخص را برای یک عامل اجرا می‌کند."""
        agent = self.agents[agent_id]
        current_pos = self.agent_positions[agent_id]
        agent.total_rewards -= 1  # کسر انرژی برای هر اقدام

        if action.name.startswith("MOVE"):
            direction = Direction[action.name.replace("MOVE_", "")]
            next_pos = current_pos + direction
            if self.is_position_free(next_pos):
                self.agent_positions[agent_id] = next_pos

        elif action == Action.PICKUP:
            if self.grid.get(current_pos) == CellType.RESOURCE:
                agent.action_history.append(Action.PICKUP)
                self.grid[current_pos] = CellType.EMPTY

        elif action == Action.DROP:
            if (agent.action_history.count(Action.PICKUP) > agent.action_history.count(Action.DROP)):
                agent.action_history.append(Action.DROP)
                if self.grid.get(current_pos) == CellType.GOAL:
                    self.tasks_completed += 1
                    self.task_completion_times.append(self.time_step)  # ثبت زمان تکمیل وظیفه
                    print(f"Agent {agent_id} delivered a resource at {current_pos}!")
                else:
                    self.grid[current_pos] = CellType.RESOURCE  # منبع روی زمین می‌افتد

        elif action == Action.WAIT:
            agent.total_rewards += 0.5  # بازیابی بخشی از انرژی

    def step(self):
        """یک گام کامل شبیه‌سازی را برای همه عامل‌ها اجرا می‌کند."""
        self.time_step += 1
        for agent_id, agent in self.agents.items():
            if agent.total_rewards <= 0:
                continue
            perception = self.get_perception(agent_id)
            action, reason = agent.decide_action(perception)
            self.execute_action(agent_id, action)

    def get_performance_metrics(self) -> Dict[str, float]:
        """متریک‌های نهایی عملکرد را برای تحلیل محاسبه و برمی‌گرداند."""
        final_task_completion_time = max(self.task_completion_times) if self.task_completion_times else 0
        return {
            'total_resources_collected': self.tasks_completed,
            'time_step': self.time_step,
            'average_energy': np.mean([a.total_rewards for a in self.agents.values()]) if self.agents else 0,
            'task_completion_time': float(final_task_completion_time),
        }