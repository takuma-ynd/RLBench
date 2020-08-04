from rlbench.environment import Environment
from rlbench.action_modes import ArmActionMode, ActionMode
from rlbench.observation_config import ObservationConfig
from rlbench.tasks import ReachTarget as Task
import numpy as np
import cv2
import os


class Agent(object):

    def __init__(self, action_size):
        self.action_size = action_size
        print('action size:', self.action_size)

    def act(self, obs):
        # arm = np.array([float(input('input {}'.format(i))) for i in range(self.action_size - 1)])
        arm = np.random.normal(0.0, 0.1, size=(self.action_size - 1,))
        gripper = [1.0]  # Always open
        return np.concatenate([arm, gripper], axis=-1)


obs_config = ObservationConfig()
obs_config.set_all(True)

# action_mode = ActionMode(ArmActionMode.ABS_JOINT_VELOCITY)
action_mode = ActionMode(ArmActionMode.ABS_EE_XYZ_VELOCITY)
env = Environment(
    action_mode, obs_config=obs_config, headless=False)
env.launch()

task = env.get_task(Task)

agent = Agent(env.action_size)

training_steps = 40 * 4
episode_length = 40
obs = None
for i in range(training_steps):
    if i % episode_length == 0:
        print('Reset Episode')
        descriptions, obs = task.reset()
        print(descriptions)

    action = agent.act(obs)
    # print('action', action[:3])
    # print('action norm', np.linalg.norm(action[:3]))
    # normalized_action = 0.5 * (action[:3] / np.linalg.norm(action[:3]))
    # normalized_action = np.concatenate((normalized_action, action[:3]), axis=0)
    # print('normalized action', normalized_action[:3])
    # print('normalized action norm', np.linalg.norm(normalized_action[:3]))
    # print(action)
    obs, reward, terminate = task.step(action)
    print(reward)

    # path = os.path.join(os.path.dirname(__file__), 'observations' , '{:03}.jpg'.format(i))
    # print(path)
    # print(np.sum(obs.front_rgb))
    # print(np.max(obs.front_rgb))
    # print(np.min(obs.front_rgb))
    # img_obs = (obs.wrist_rgb * 255).astype(np.uint8)
    # img_obs = cv2.cvtColor(img_obs, cv2.COLOR_BGR2RGB)
    # cv2.imwrite(path, img_obs)

print('Done')
env.shutdown()
