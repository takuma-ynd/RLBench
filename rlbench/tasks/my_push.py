import os
from typing import List
from rlbench.backend.task import Task
from rlbench.backend.task_utils import sample_simple_objects
from rlbench.backend.conditions import ConditionSet, DetectedCondition
from rlbench.backend.spawn_boundary import SpawnBoundary
import numpy as np
from pyrep.objects.shape import Shape
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.dummy import Dummy


class MyPush(Task):

    def init_task(self) -> None:
        # TODO: This is called once when a task is initialised.
        self.large_container = Shape('large_container')
        self.success_detector = ProximitySensor('success')
        self.target = Shape('target')
        self.target_boundary = Shape('target_boundary')
        # self.spawn_boundaries = [Shape('spawn_boundary0'),Shape('spawn_boundary1'), Shape('spawn_boundary2'), Shape('spawn_boundary3')]
        self.spawn_boundaries = [Shape('spawn_boundary')]
        self.register_waypoint_ability_start(1, self._move_behind_object)
        self.register_waypoints_should_repeat(self._repeat)
        self.bin_objects = []

    def init_episode(self, index: int) -> List[str]:
        # TODO: This is called at the start of each episode.
        self._variation_index = index
        # self.bin_objects = sample_procedural_objects(self.get_base(), 3)
        print('creating bin_objects =================')
        self.bin_objects = sample_simple_objects(self.get_base(), 1)
        self.bin_objects_not_done = list(self.bin_objects)

        # sample target position
        target_b = SpawnBoundary([self.target_boundary])
        target_b.clear()
        target_b.sample(self.target, min_rotation=(0,0,0), max_rotation=(0,0,0))

        # sample proceduraly generated objects
        b = SpawnBoundary(self.spawn_boundaries)
        for ob in self.bin_objects:
            ob.set_position(
                [0.0, 0.0, 0.5], relative_to=self.large_container,
                reset_dynamics=False
            )
            b.sample(ob, ignore_collisions=True, min_distance=0.05)

        # append to success conditions
        conditions = []
        for ob in self.bin_objects:
            conditions.append(DetectedCondition(ob, self.success_detector))

        # register success conditions
        self.register_success_conditions(
            [ConditionSet(conditions, simultaneously_met=True)]
        )

        return ['simply push the block toward the target ;)']

    def variation_count(self) -> int:
        # TODO: The number of variations for this task.
        return 1

    def step(self) -> None:
        # Called during each sim step. Remove this if not using.
        for ob in self.bin_objects_not_done:
            if self.success_detector.is_detected(ob):
                print('success is detected for object:', ob)
                self.bin_objects_not_done.remove(ob)

    def cleanup(self) -> None:
        # Called during at the end of each episode. Remove this if not using.
        if self.bin_objects is not None:
            [ob.remove() for ob in self.bin_objects if ob.still_exists()]
            self.bin_objects = []

    def _repeat(self):
        return len(self.bin_objects_not_done) > 0

    def _move_behind_object(self, waypoint):
        if len(self.bin_objects_not_done) <= 0:
            raise RuntimeError('weird...')
        # x, y, z = self.bin_objects_not_done[0].get_position()
        # print(x,y,z)
        relative_pos = self.bin_objects_not_done[0].get_position(relative_to=self.target)
        print(relative_pos)
        # pos = self.bin_objects_not_done[0].get_position()
        #
        offset = 0.5*10**(-1)
        relative_waypoint_pos = relative_pos.copy()
        relative_waypoint_pos[:2] += offset * (relative_pos[:2] / np.linalg.norm(relative_pos[:2]))
        relative_waypoint_pos[2] = 1.0 * 10 ** (-4)
        #
        # waypoint.get_waypoint_object().set_position(pos, relative_to=self.target)
        # waypoint.get_waypoint_object().set_position([2.5 *10**(-1), 0.0, 5.0 *10** (-1)])
        waypoint.get_waypoint_object().set_position(relative_waypoint_pos, relative_to=self.target)

