from typing import List
from rlbench.backend.task import Task
from rlbench.const import colors
from rlbench.backend.task_utils import sample_procedural_objects
from rlbench.backend.conditions import ConditionSet, DetectedCondition
from rlbench.backend.spawn_boundary import SpawnBoundary
import numpy as np
from pyrep.objects.shape import Shape
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.dummy import Dummy


class MyEmptyContainer(Task):

    def init_task(self) -> None:
        # TODO: This is called once when a task is initialised.
        self.large_container = Shape('large_container')
        self.target_container0 = Shape('small_container0')
        self.target_container1 = Shape('small_container1')
        self.spawn_boundaries = [Shape('spawn_boundary')]
        self.success_detector0 = ProximitySensor('success0')
        self.success_detector1 = ProximitySensor('success1')

        self.register_waypoint_ability_start(1,
                                             self._move_above_object)
        self.register_waypoints_should_repeat(self._repeat)

    def init_episode(self, index: int) -> List[str]:
        # TODO: This is called at the start of each episode.
        self._variation_index = index
        self.bin_objects = sample_procedural_objects(self.get_base(), 3)
        self.bin_objects_not_done = list(self.bin_objects)
        self.register_graspable_objects(self.bin_objects)

        b = SpawnBoundary(self.spawn_boundaries)
        for ob in self.bin_objects:
            ob.set_position(
                [0.0, 0.0, 0.2], relative_to=self.large_container,
                reset_dynamics=False
            )
            b.sample(ob, ignore_collisions=True, min_distance=0.05)

        target_waypoint = Dummy('waypoint3')
        target_pos = [0.17662, 0.3250,-2.9802**(-8)]


        conditions = []
        target_color_name, target_color_rgb = colors[index]
        color_choice = np.random.choice(
            list(range(index)) + list(
                range(index + 1, len(colors))
            ),
            size=1, replace=False
        )[0]
        _, distractor_color_rgb = colors[color_choice]

        if index % 2 == 0:
            self.target_container0.set_color(target_color_rgb)
            self.target_container1.set_color(distractor_color_rgb)
            for ob in self.bin_objects:
                conditions.append(DetectedCondition(ob, self.success_detector0))
        else:
            self.target_container1.set_color(target_color_rgb)
            self.target_container0.set_color(distractor_color_rgb)
            for ob in self.bin_objects:
                conditions.append(DetectedCondition(ob, self.success_detector1))
                target_pos[1] = -target_pos[1]
        target_waypoint.set_position(target_pos,
                                     relative_to=self.large_container,
                                     reset_dynamics=True)
        self.register_success_conditions(
            [ConditionSet(conditions, simultaneously_met=True)]
        )

        return ['empty the container into the %s container' % target_color_name,
                'clear all items from the large tray and put them in the %s '
                'tray ' % target_color_name,
                'move all objects from the large container and drop them into '
                'the smaller %s one' % target_color_name,
                'remove whatever you find in the big box in the middle and '
                'leave them in the %s one' % target_color_name,
                'grasp and move all objects into the %s container'
                % target_color_name]

    def variation_count(self) -> int:
        # TODO: The number of variations for this task.
        return 2*len(colors)

    def step(self) -> None:
        # Called during each sim step. Remove this if not using.

        for ob in self.bin_objects_not_done:
            if self._variation_index % 2 == 0:
                if self.success_detector0.is_detected(ob):
                    self.bin_objects_not_done.remove(ob)
            else:
                if self.success_detector1.is_detected(ob):
                    self.bin_objects_not_done.remove(ob)

    def _move_above_object(self, waypoint):
        if len(self.bin_objects_not_done) <= 0:
            raise RUntimeError('len(self.bin_objects_not_done) == {}'.format(len(self.bin_objects_not_done)))
        x, y, z = self.bin_objects_not_done[0].get_position()
        print('position', x, y, z)
        waypoint.get_waypoint_object().set_position([x, y, z])

    def _repeat(self):
        return len(self.bin_objects_not_done) > 0


    def cleanup(self) -> None:
        # Called during at the end of each episode. Remove this if not using.
        if self.bin_objects is not None:
            [ob.remove() for ob in self.bin_objects if ob.still_exists()]
            self.bin_objects = []
