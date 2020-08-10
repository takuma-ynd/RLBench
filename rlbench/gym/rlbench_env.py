from typing import Union, Dict, Tuple

import gym
from gym import spaces
from pyrep.const import RenderMode
from pyrep.objects.dummy import Dummy
from pyrep.objects.vision_sensor import VisionSensor
from rlbench.environment import Environment
from rlbench.action_modes import ArmActionMode, ActionMode
from rlbench.observation_config import ObservationConfig
import numpy as np


class RLBenchEnv(gym.Env):
    """An gym wrapper for RLBench."""

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, task_class, observation_mode='state',
                 render_mode: Union[None, str] = None,
                 action_mode: Union[None, str] = None):
        self._raw_observation_mode = observation_mode
        obs_split = self._raw_observation_mode.split('-')
        if len(obs_split) == 2:
            self._observation_mode, self._observation_submode = obs_split
        else:
            self._observation_mode = obs_split[0]
            self._observation_submode = None

        self._render_mode = render_mode
        self._action_mode = action_mode
        obs_config = ObservationConfig()


        if self._observation_mode == 'state':
            assert self._observation_submode is None
            obs_config.set_all_high_dim(False)
            obs_config.set_all_low_dim(True)
        elif self._observation_mode == 'pose':
            assert self._observation_submode is None
            obs_config.set_only_poses()
        elif self._observation_mode == 'vision':
            obs_config.set_all_low_dim(True)
            obs_config.set_all_high_dim(False)
            if self._observation_submode == 'front':
                obs_config.front_camera.set_all(True)
            elif self._observation_submode == 'wrist':
                obs_config.wrist_camera.set_all(True)
            elif self._observation_submode == 'right_shoulder':
                obs_config.right_shoulder_camera.set_all(True)
            elif self._observation_submode == 'left_shoulder':
                obs_config.left_shoulder_camera.set_all(True)
            else:
                assert self._observation_submode is None
                obs_config.set_all(True)
        else:
            raise ValueError(
                'Unrecognised observation_mode: %s.' % observation_mode)

        if self._action_mode is not None:
            if not hasattr(ArmActionMode, self._action_mode):
                raise ValueError(
                    'Unrecognised action_mode: %s' % action_mode)
            self._action_mode = getattr(ArmActionMode, self._action_mode)
        else:
            self._action_mode = ArmActionMode.ABS_JOINT_VELOCITY

        action_mode = ActionMode(self._action_mode)
        self.env = Environment(
            action_mode, obs_config=obs_config, headless=True)
        self.env.launch()
        self.task = self.env.get_task(task_class)

        _, obs = self.task.reset()

        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.env.action_size,))

        if self._observation_mode == 'state' or observation_mode == 'pose':
            self.observation_space = spaces.Box(
                low=-np.inf, high=np.inf, shape=obs.get_low_dim_data().shape)
        elif self._observation_mode == 'vision':
            # Ah.., it's dirty...
            space_dict = {}
            space_dict['state'] = spaces.Box(low=-np.inf, high=np.inf, shape=obs.get_low_dim_data().shape)
            if self._observation_submode == 'front':
                space_dict['front_rgb'] = spaces.Box(low=0, high=1, shape=obs.front_rgb.shape)
            elif self._observation_submode == 'left_shoulder':
                space_dict['left_shoulder_rgb'] = spaces.Box(low=0, high=1, shape=obs.left_shoulder_rgb.shape)
            elif self._observation_submode == 'right_shoulder':
                space_dict['right_shoulder_rgb'] = spaces.Box(low=0, high=1, shape=obs.right_shoulder_rgb.shape)
            elif self._observation_submode == 'wrist':
                space_dict['wrist_rgb'] = spaces.Box(low=0, high=1, shape=obs.wrist_rgb.shape)
            else:
                assert self._observation_submode is None
                space_dict = {'state': spaces.Box(low=-np.inf, high=np.inf, shape=obs.get_low_dim_data().shape),
                              'front_rgb': spaces.Box(low=0, high=1, shape=obs.front_rgb.shape),
                              'left_shoulder_rgb': spaces.Box(low=0, high=1, shape=obs.left_shoulder_rgb.shape),
                              'right_shoulder_rgb': spaces.Box(low=0, high=1, shape=obs.right_shoulder_rgb.shape),
                              "wrist_rgb": spaces.Box(low=0, high=1, shape=obs.wrist_rgb.shape)
                }

            self.observation_space = spaces.Dict(space_dict)

        if render_mode is not None:
            # Add the camera to the scene
            cam_placeholder = Dummy('cam_cinematic_placeholder')
            self._gym_cam = VisionSensor.create([640, 360])
            self._gym_cam.set_pose(cam_placeholder.get_pose())
            if render_mode == 'human':
                self._gym_cam.set_render_mode(RenderMode.OPENGL3_WINDOWED)
            else:
                self._gym_cam.set_render_mode(RenderMode.OPENGL3)

    def _extract_obs(self, obs) -> Dict[str, np.ndarray]:
        if self._observation_mode == 'state' or self._observation_mode == 'pose':
            return obs.get_low_dim_data()
        elif self._observation_mode == 'vision':
            return {
                "state": obs.get_low_dim_data(),
                "left_shoulder_rgb": obs.left_shoulder_rgb,
                "right_shoulder_rgb": obs.right_shoulder_rgb,
                "wrist_rgb": obs.wrist_rgb,
                "front_rgb": obs.front_rgb,
            }

    def render(self, mode='human') -> Union[None, np.ndarray]:
        if mode != self._render_mode:
            raise ValueError(
                'The render mode must match the render mode selected in the '
                'constructor. \nI.e. if you want "human" render mode, then '
                'create the env by calling: '
                'gym.make("reach_target-state-v0", render_mode="human").\n'
                'You passed in mode %s, but expected %s.' % (
                    mode, self._render_mode))
        if mode == 'rgb_array':
            return self._gym_cam.capture_rgb()

    def reset(self) -> Dict[str, np.ndarray]:
        print('calling self.task.reset()...')
        descriptions, obs = self.task.reset()
        del descriptions  # Not used.
        return self._extract_obs(obs)

    def step(self, action) -> Tuple[Dict[str, np.ndarray], float, bool, dict]:
        obs, reward, terminate = self.task.step(action)
        return self._extract_obs(obs), reward, terminate, {}

    def close(self) -> None:
        self.env.shutdown()
