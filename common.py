# common.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

# این شمارنده، انواع مختلف خانه‌های موجود در شبکه را تعریف می‌کند.
class CellType(Enum):
    EMPTY = 0
    WALL = 1
    GOAL = 2
    RESOURCE = 3
    HAZARD = 4

# این شمارنده، جهت‌های ممکن برای حرکت را تعریف می‌کند.
class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

# این شمارنده، تمام اقدامات ممکن برای یک عامل را تعریف می‌کند.
class Action(Enum):
    MOVE_NORTH = "MOVE_NORTH"
    MOVE_SOUTH = "MOVE_SOUTH"
    MOVE_EAST = "MOVE_EAST"
    MOVE_WEST = "MOVE_WEST"
    PICKUP = "PICKUP"
    DROP = "DROP"
    WAIT = "WAIT"

# این دیتاکلاس، یک موقعیت (x, y) را در شبکه نمایندگی می‌کند.
# استفاده از frozen=True آن را غیرقابل تغییر (immutable) می‌کند که برای استفاده به عنوان کلید دیکشنری مناسب است.
@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, direction: Direction):
        """یک موقعیت جدید با اعمال یک جهت به موقعیت فعلی برمی‌گرداند."""
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)

# این دیتاکلاس، اطلاعاتی که یک عامل در هر گام دریافت می‌کند را بسته‌بندی می‌کند.
@dataclass
class Perception:
    position: Position
    visible_cells: Dict[Position, CellType]
    visible_agents: Dict[int, Position]
    energy_level: float
    has_resource: bool
    messages: List

# این دیتاکلاس، یک گام از برنامه یک عامل مبتنی بر هدف را نمایندگی می‌کند.
@dataclass
class PlanStep:
    action: Action