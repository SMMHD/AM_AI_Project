# tester.py

import csv
import numpy as np
from dataclasses import dataclass
from typing import Dict, Type

# وارد کردن کلاس‌های مورد نیاز از ماژول‌های دیگر پروژه
from common import Position
from environment import GridWorld
from agents import Agent, SimpleReflexAgent, ModelBasedReflexAgent, GoalBasedAgent


@dataclass
class ExperimentConfig:
    """دیتاکلاسی برای نگهداری پیکربندی هر سناریوی آزمایشی."""
    name: str
    grid_size: tuple[int, int]
    num_agents: int
    num_resources: int
    num_goals: int
    num_hazards: int
    max_steps: int
    num_trials: int = 5  # طبق نیازمندی پروژه، هر آزمایش ۵ بار تکرار می‌شود


class ProjectTester:
    """
    این کلاس مسئولیت کامل اجرای آزمایش‌ها و جمع‌آوری نتایج را بر عهده دارد.
    """

    def __init__(self):
        """تعریف سناریوهای آزمایشی و انواع عامل‌ها."""
        self.experiment_configs = [
            ExperimentConfig(
                name="simple_collection",
                grid_size=(8, 8),
                num_agents=2,
                num_resources=4,
                num_goals=2,
                num_hazards=0,
                max_steps=200,
            ),
            ExperimentConfig(
                name="maze_navigation",
                grid_size=(10, 10),
                num_agents=2,
                num_resources=4,
                num_goals=2,
                num_hazards=3,
                max_steps=300,
            ),
            ExperimentConfig(
                name="competitive_collection",
                grid_size=(12, 12),
                num_agents=3,
                num_resources=3,
                num_goals=2,
                num_hazards=2,
                max_steps=400,
            )
        ]

        self.agent_types: Dict[str, Type[Agent]] = {
            "SimpleReflexAgent": SimpleReflexAgent,
            "ModelBasedReflexAgent": ModelBasedReflexAgent,
            "GoalBasedAgent": GoalBasedAgent
        }

    def run_single_experiment(self, agent_class: Type[Agent], config: ExperimentConfig) -> Dict:
        """یک آزمایش کامل را برای یک عامل و یک سناریو با چندین بار تکرار اجرا می‌کند."""
        completion_times = []
        tasks_completed_list = []

        for i in range(config.num_trials):
            # برای هر اجرا، یک محیط و عامل جدید می‌سازیم تا نتایج مستقل باشند
            env = GridWorld(config.grid_size[0], config.grid_size[1])

            # (در یک پروژه واقعی، این بخش باید به صورت دینامیک دیوارها و ... را بسازد)
            # در اینجا برای سادگی از یک نمونه ثابت استفاده می‌کنیم
            walls = [Position(x, 0) for x in range(env.width)] + [Position(x, env.height - 1) for x in range(env.width)]
            walls += [Position(0, y) for y in range(env.height)] + [Position(env.width - 1, y) for y in
                                                                    range(env.height)]
            env.add_walls(walls)

            # این مقادیر باید بر اساس config تنظیم شوند، اما برای سادگی ثابت در نظر گرفته شده‌اند
            resources = [Position(3, 3), Position(5, 5)]
            goals = [Position(2, 2), Position(6, 6)]
            env.add_resources(resources)
            env.add_goals(goals)

            agent = agent_class(f"{agent_class.__name__}_trial_{i}")
            agent.reset()
            env.add_agent(agent, Position(1, 1))

            # اجرای گام‌های شبیه‌سازی
            for _ in range(config.max_steps):
                if agent.total_rewards <= 0: break
                env.step()

            metrics = env.get_performance_metrics()
            completion_times.append(metrics['task_completion_time'])
            tasks_completed_list.append(metrics['total_resources_collected'])

        # محاسبه میانگین نتایج پس از تمام تکرارها
        # اگر در هیچ اجرایی وظیفه انجام نشود، زمان تکمیل صفر خواهد بود
        valid_completion_times = [t for t in completion_times if t > 0]
        avg_completion_time = np.mean(valid_completion_times) if valid_completion_times else 0

        return {
            "config_name": config.name,
            "agent_type": agent_class.__name__,
            "avg_tasks_completed": np.mean(tasks_completed_list),
            "avg_completion_time": avg_completion_time,
            "num_trials": config.num_trials
        }

    def run_comparison(self):
        """تمام آزمایش‌ها را اجرا کرده و نتایج نهایی را در فایل CSV ذخیره می‌کند."""
        all_results = []

        for config in self.experiment_configs:
            for agent_name, agent_class in self.agent_types.items():
                print(f"\nRunning experiment for '{agent_name}' in '{config.name}'...")

                final_metrics = self.run_single_experiment(agent_class, config)
                all_results.append(final_metrics)

                print(f"✓ Experiment for '{agent_name}' in '{config.name}' completed.")

        # ذخیره نتایج در فایل CSV
        if all_results:
            output_file = "experimental_results.csv"
            print(f"\nSaving final results to {output_file}...")
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)
            print("✓ Results saved.")