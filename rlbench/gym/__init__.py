from gym.envs.registration import register
import rlbench.backend.task as task
import os
from rlbench.utils import name_to_task_class
from rlbench.gym.rlbench_env import RLBenchEnv

TASKS = [t for t in os.listdir(task.TASKS_PATH)
         if t != '__init__.py' and t.endswith('.py')]

for task_file in TASKS:
    task_name = task_file.split('.py')[0]
    task_class = name_to_task_class(task_name)
    register(
        id='%s-state-v0' % task_name,
        entry_point='rlbench.gym:RLBenchEnv',
        kwargs={
            'task_class': task_class,
            'observation_mode': 'state'
        }
    )
    register(
        id='%s-vision-v0' % task_name,
        entry_point='rlbench.gym:RLBenchEnv',
        kwargs={
            'task_class': task_class,
            'observation_mode': 'vision'
        }
    )

# TEMP:
register(
    id='reach_target-ee-vision-v0',
    entry_point='rlbench.gym:RLBenchEnv',
    kwargs={
        'task_class': name_to_task_class('reach_target'),
        'observation_mode': 'vision',
        'action_mode': 'ABS_EE_XYZ_VELOCITY'
    }
)

# TEMP:
register(
    id='reach_target-ee-state-v0',
    entry_point='rlbench.gym:RLBenchEnv',
    kwargs={
        'task_class': name_to_task_class('reach_target'),
        'observation_mode': 'state',
        'action_mode': 'ABS_EE_XYZ_VELOCITY'
    }
)

# TEMP:
register(
    id='reach_target-ee-pose-v0',
    entry_point='rlbench.gym:RLBenchEnv',
    kwargs={
        'task_class': name_to_task_class('reach_target'),
        'observation_mode': 'pose',
        'action_mode': 'ABS_EE_XYZ_VELOCITY'
    }
)

# TEMP:
register(
    id='reach_target-ee-vision-v1',
    entry_point='rlbench.gym:RLBenchEnv',
    kwargs={
        'task_class': name_to_task_class('reach_target'),
        'observation_mode': 'vision-front',
        'action_mode': 'ABS_EE_XYZ_VELOCITY'
    }
)

# TEMP:
register(
    id='reach_target-vision-v1',
    entry_point='rlbench.gym:RLBenchEnv',
    kwargs={
        'task_class': name_to_task_class('reach_target'),
        'observation_mode': 'vision-front',
    }
)
