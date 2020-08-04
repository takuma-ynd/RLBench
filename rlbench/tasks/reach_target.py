from typing import List, Tuple
import numpy as np
from pyrep.objects.shape import Shape
from pyrep.objects.dummy import Dummy
from pyrep.objects.proximity_sensor import ProximitySensor
from rlbench.const import colors
from rlbench.backend.task import Task
from rlbench.backend.spawn_boundary import SpawnBoundary
from rlbench.backend.conditions import DetectedCondition


class ReachTarget(Task):

    def init_task(self) -> None:
        self.init_tip = Dummy('init_tip')
        self.target = Shape('target')
        self.boundaries = Shape('boundary')
        success_sensor = ProximitySensor('success')
        self.register_success_conditions(
            [DetectedCondition(self.robot.arm.get_tip(), success_sensor)])

    def init_episode(self, index: int) -> List[str]:
        color_name, color_rgb = colors[index]
        self.target.set_color(color_rgb)
        b = SpawnBoundary([self.boundaries])
        b.sample(self.target, min_distance=0.2,
                 min_rotation=(0, 0, 0), max_rotation=(0, 0, 0))
        init_pos = self.init_tip.get_position()
        print(init_pos)
        init_rot = self.init_tip.get_orientation()
        print(init_rot)
        joint_values = self.robot.arm.solve_ik(init_pos, euler=init_rot)
        self.robot.arm.set_joint_positions(joint_values)
        self._init_tip_pos = self.robot.arm.get_tip().get_position(relative_to=self.target)

        return ['reach the %s target' % color_name,
                'touch the %s ball with the panda gripper' % color_name,
                'reach the %s sphere' %color_name]

    def variation_count(self) -> int:
        # return len(colors)
        return 1

    def base_rotation_bounds(self) -> Tuple[List[float], List[float]]:
        return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]

    def get_low_dim_state(self) -> np.ndarray:
        # One of the few tasks that have a custom low_dim_state function.
        return np.array(self.target.get_position())

    def is_static_workspace(self) -> bool:
        return True

    # def step(self) -> None:
    #     self._old_tip_relative_pos = self.robot.arm.get_tip().get_position(relative_to=self.target)

    def get_reward(self) -> float:
        tip_pos = self.robot.arm.get_tip().get_position(relative_to=self.target)
        print('tip_pos', tip_pos)
        return (np.linalg.norm(self._init_tip_pos) - np.linalg.norm(tip_pos)) / np.linalg.norm(self._init_tip_pos)
