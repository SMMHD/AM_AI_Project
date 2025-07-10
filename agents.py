# agents.py

from abc import ABC, abstractmethod
import random
import heapq
from typing import Dict, List, Set, Tuple, Optional

# وارد کردن کلاس‌های داده‌ای مورد نیاز از ماژول مشترک
from common import Action, Perception, Position, Direction, CellType, PlanStep


class Agent(ABC):
    """
    کلاس پایه و انتزاعی (Abstract) برای تمام عامل‌ها.
    هر عاملی باید متدهای decide_action و reset را پیاده‌سازی کند.
    """

    def __init__(self, name: str):
        self.name = name
        self.agent_id: int = -1
        self.action_history: List[Action] = []
        # مقدار اولیه انرژی را روی ۱۰۰ تنظیم می‌کنیم
        self.total_rewards: float = 100.0
        # برای تحلیل رفتار، تعداد فعال‌سازی هر قانون را می‌شماریم
        self.rule_activations: Dict[str, int] = {}

    @abstractmethod
    def decide_action(self, perception: Perception) -> Tuple[Action, str]:
        """این متد باید توسط هر کلاس فرزند پیاده‌سازی شود تا تصمیم بگیرد چه اقدامی انجام دهد."""
        pass

    def reset(self):
        """وضعیت داخلی عامل را برای یک اجرای جدید ریست می‌کند."""
        self.action_history.clear()
        self.total_rewards = 100.0
        self.rule_activations.clear()


class SimpleReflexAgent(Agent):
    """
    پیاده‌سازی عامل واکنش‌گر ساده که تنها بر اساس ادراکات لحظه‌ای تصمیم می‌گیرد.
    """

    def decide_action(self, perception: Perception) -> Tuple[Action, str]:
        my_pos = perception.position
        visible_cells = perception.visible_cells

        # قوانین با اولویت بالا
        if perception.has_resource and visible_cells.get(my_pos) == CellType.GOAL:
            return Action.DROP, "Rule 2.5: On goal with resource, dropping."

        if not perception.has_resource and visible_cells.get(my_pos) == CellType.RESOURCE:
            return Action.PICKUP, "Rule 2: On a resource, picking up."

        # قوانین حرکتی
        if perception.has_resource:
            goal_positions = [pos for pos, cell_type in visible_cells.items() if cell_type == CellType.GOAL]
            if goal_positions:
                direction = self._get_direction_toward(my_pos, goal_positions[0])
                if direction:
                    return self._direction_to_action(direction), "Rule 3: Carrying resource, moving toward goal."
        else:
            resource_positions = [pos for pos, cell_type in visible_cells.items() if cell_type == CellType.RESOURCE]
            if resource_positions:
                direction = self._get_direction_toward(my_pos, resource_positions[0])
                if direction:
                    return self._direction_to_action(direction), "Rule 4: Seeking resource, moving toward it."

        # قانون آخر: حرکت اکتشافی تصادفی
        action = self._random_valid_move(visible_cells, my_pos)
        return action, "Rule 5: Random exploration."

    def _get_direction_toward(self, from_pos: Position, to_pos: Position) -> Optional[Direction]:
        if from_pos.y > to_pos.y: return Direction.NORTH
        if from_pos.y < to_pos.y: return Direction.SOUTH
        if from_pos.x < to_pos.x: return Direction.EAST
        if from_pos.x > to_pos.x: return Direction.WEST
        return None

    def _direction_to_action(self, direction: Direction) -> Action:
        return Action[f"MOVE_{direction.name}"]

    def _random_valid_move(self, visible_cells: Dict[Position, CellType], current_pos: Position) -> Action:
        valid_moves = []
        for direction in Direction:
            next_pos = current_pos + direction
            if visible_cells.get(next_pos) not in [CellType.WALL, CellType.HAZARD]:
                valid_moves.append(self._direction_to_action(direction))
        return random.choice(valid_moves) if valid_moves else Action.WAIT


class ModelBasedReflexAgent(Agent):
    """
    عامل واکنش‌گر مبتنی بر مدل که یک حافظه داخلی از محیط را نگهداری می‌کند.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.reset()

    def reset(self):
        super().reset()
        self.visited_positions: Set[Position] = set()
        self.known_walls: Set[Position] = set()
        self.known_resources: Set[Position] = set()
        self.known_goals: Set[Position] = set()
        self.known_hazards: Set[Position] = set()

        # در فایل agents.py، داخل کلاس ModelBasedReflexAgent

    def _update_world_model(self, perception: Perception):
        self.visited_positions.add(perception.position)
        for pos, cell_type in perception.visible_cells.items():
            if cell_type == CellType.WALL:
                self.known_walls.add(pos)
            elif cell_type == CellType.RESOURCE:
                self.known_resources.add(pos)
            elif cell_type == CellType.GOAL:
                self.known_goals.add(pos)
            elif cell_type == CellType.HAZARD:
                self.known_hazards.add(pos)

        # [تغییر کلیدی] - ابتدا بررسی می‌کنیم که لیست تاریخچه خالی نباشد
        if self.action_history and perception.position in self.known_resources and \
                not perception.has_resource and self.action_history[-1] == Action.PICKUP:
            self.known_resources.remove(perception.position)

    def decide_action(self, perception: Perception) -> Tuple[Action, str]:
        self._update_world_model(perception)
        my_pos = perception.position

        # قوانین مشابه عامل ساده اما با استفاده از مدل داخلی
        if perception.has_resource and perception.position in self.known_goals:
            return Action.DROP, "Rule 3: On goal with resource, dropping"

        if not perception.has_resource and perception.position in self.known_resources:
            return Action.PICKUP, "Rule 2: On a resource, picking up"

        if perception.has_resource and self.known_goals:
            closest_goal = self._find_closest_target(my_pos, self.known_goals)
            if closest_goal:
                direction = self._get_direction_toward(my_pos, closest_goal)
                if direction:
                    return self._direction_to_action(direction), f"Rule 4: Moving toward known goal at {closest_goal}"

        if not perception.has_resource and self.known_resources:
            closest_resource = self._find_closest_target(my_pos, self.known_resources)
            if closest_resource:
                direction = self._get_direction_toward(my_pos, closest_resource)
                if direction:
                    return self._direction_to_action(
                        direction), f"Rule 5: Moving toward known resource at {closest_resource}"

        # اکتشاف هوشمند
        return self._intelligent_exploration(perception)

    def _find_closest_target(self, start_pos: Position, targets: Set[Position]) -> Optional[Position]:
        if not targets: return None
        return min(targets, key=lambda p: abs(p.x - start_pos.x) + abs(p.y - start_pos.y))

    def _intelligent_exploration(self, perception: Perception) -> Tuple[Action, str]:
        # این یک نسخه ساده از اکتشاف است، می‌توان آن را بسیار هوشمندتر کرد
        return self._random_valid_move(perception.visible_cells, perception.position), "Rule 6: Intelligent exploration"

    # متدهای کمکی از عامل ساده را کپی می‌کنیم
    _get_direction_toward = SimpleReflexAgent._get_direction_toward
    _direction_to_action = SimpleReflexAgent._direction_to_action
    _random_valid_move = SimpleReflexAgent._random_valid_move


class GoalBasedAgent(Agent):
    """
    عامل مبتنی بر هدف که با استفاده از الگوریتم A* برنامه‌ریزی می‌کند.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.reset()

    def reset(self):
        super().reset()
        self.current_plan: List[PlanStep] = []
        self.visited_positions: Set[Position] = set()
        self.known_walls: Set[Position] = set()
        self.known_resources: Set[Position] = set()
        self.known_goals: Set[Position] = set()

        # در فایل agents.py، داخل کلاس GoalBasedAgent

    def _update_world_model(self, perception: Perception):
        self.visited_positions.add(perception.position)
        for pos, cell_type in perception.visible_cells.items():
            if cell_type == CellType.WALL:
                self.known_walls.add(pos)
            elif cell_type == CellType.RESOURCE:
                self.known_resources.add(pos)
            elif cell_type == CellType.GOAL:
                self.known_goals.add(pos)

        # [تغییر کلیدی] - اینجا هم شرط ایمنی را اضافه می‌کنیم
        if self.action_history and perception.position in self.known_resources and \
                not perception.has_resource and self.action_history[-1] == Action.PICKUP:
            self.known_resources.remove(perception.position)

    def decide_action(self, perception: Perception) -> Tuple[Action, str]:
        self._update_world_model(perception)
        my_pos = perception.position

        if not self.current_plan:
            self._create_new_plan(perception)

        if self.current_plan:
            next_step = self.current_plan.pop(0)
            return next_step.action, f"Executing plan: {next_step.action.name}"

        # اگر هیچ برنامه‌ای وجود ندارد، به صورت اکتشافی حرکت کن
        return self._random_valid_move(perception.visible_cells,
                                       my_pos), "No plan available. Falling back to exploration."

    def _create_new_plan(self, perception: Perception):
        my_pos = perception.position
        goals = []

        if perception.has_resource and self.known_goals:
            for goal_pos in self.known_goals:
                dist = abs(my_pos.x - goal_pos.x) + abs(my_pos.y - goal_pos.y)
                goals.append({"type": "DELIVER", "pos": goal_pos, "utility": 20.0 / (dist + 1)})
        elif not perception.has_resource and self.known_resources:
            for res_pos in self.known_resources:
                dist = abs(my_pos.x - res_pos.x) + abs(my_pos.y - res_pos.y)
                goals.append({"type": "COLLECT", "pos": res_pos, "utility": 10.0 / (dist + 1)})

        if not goals: return  # هیچ هدف ممکنی وجود ندارد

        best_goal = max(goals, key=lambda g: g['utility'])
        path_actions = self._find_path_astar(my_pos, best_goal["pos"], self.known_walls)

        if path_actions:
            self.current_plan = [PlanStep(action=act) for act in path_actions]
            final_action = Action.PICKUP if best_goal["type"] == "COLLECT" else Action.DROP
            self.current_plan.append(PlanStep(action=final_action))
            print(f"Agent {self.agent_id} created a new plan: {best_goal['type']} at {best_goal['pos']}")

        # در فایل agents.py، داخل کلاس GoalBasedAgent

    def _find_path_astar(self, start: Position, goal: Position, walls: Set[Position]) -> List[Action]:
        """الگوریتم A* با یک گره‌گشا برای جلوگیری از خطای مقایسه."""

        def heuristic(a: Position, b: Position) -> int:
            return abs(a.x - b.x) + abs(a.y - b.y)

        # [تغییر ۱] یک شمارنده برای گره‌گشایی اضافه می‌کنیم
        tie_breaker_counter = 0

        # [تغییر ۲] آیتم اولیه در صف اکنون شامل گره‌گشا است
        frontier = [(0, tie_breaker_counter, start)]  # (priority, tie_breaker, position)
        heapq.heapify(frontier)

        came_from: Dict[Position, Tuple[Position, Action]] = {start: None}
        cost_so_far = {start: 0}

        iteration_limit = 200
        iteration_count = 0

        while frontier:
            iteration_count += 1
            if iteration_count > iteration_limit:
                print(f"!!! A* Pathfinding Warning: Exceeded iteration limit from {start} to {goal}. Aborting.")
                return []

            # [تغییر ۳] اکنون سه مقدار از صف خارج می‌شود
            _, _, current_pos = heapq.heappop(frontier)

            if current_pos == goal:
                break

            for direction in Direction:
                action = self._direction_to_action(direction)
                next_pos = current_pos + direction
                if next_pos in walls:
                    continue

                new_cost = cost_so_far[current_pos] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(next_pos, goal)

                    # [تغییر ۴] گره‌گشا را قبل از افزودن به صف افزایش می‌دهیم
                    tie_breaker_counter += 1
                    heapq.heappush(frontier, (priority, tie_breaker_counter, next_pos))

                    came_from[next_pos] = (current_pos, action)

        if goal not in came_from:
            return []

        path = []
        temp = goal
        while temp != start:
            prev_pos, action = came_from[temp]
            path.append(action)
            temp = prev_pos
        path.reverse()
        return path

    # def _find_path_astar(self, start: Position, goal: Position, walls: Set[Position]) -> List[Action]:
    #     def heuristic(a: Position, b: Position) -> int:
    #         return abs(a.x - b.x) + abs(a.y - b.y)
    #
    #     frontier = [(0, start)]
    #     heapq.heapify(frontier)
    #     came_from: Dict[Position, Tuple[Position, Action]] = {start: None}
    #     cost_so_far = {start: 0}
    #
    #     iteration_limit = 200
    #     iteration_count = 0
    #
    #     while frontier:
    #         iteration_count += 1
    #         if iteration_count > iteration_limit:
    #             print(f"!!! A* Pathfinding Warning: Exceeded iteration limit from {start} to {goal}. Aborting.")
    #             return []
    #
    #         _, current_pos = heapq.heappop(frontier)
    #         if current_pos == goal: break
    #
    #         for direction in Direction:
    #             action = self._direction_to_action(direction)
    #             next_pos = current_pos + direction
    #             if next_pos in walls: continue
    #
    #             new_cost = cost_so_far[current_pos] + 1
    #             if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
    #                 cost_so_far[next_pos] = new_cost
    #                 priority = new_cost + heuristic(next_pos, goal)
    #                 heapq.heappush(frontier, (priority, next_pos))
    #                 came_from[next_pos] = (current_pos, action)
    #
    #     if goal not in came_from: return []
    #     path = []
    #     temp = goal
    #     while temp != start:
    #         prev_pos, action = came_from[temp]
    #         path.append(action)
    #         temp = prev_pos
    #     path.reverse()
    #     return path

    _direction_to_action = SimpleReflexAgent._direction_to_action
    _random_valid_move = SimpleReflexAgent._random_valid_move