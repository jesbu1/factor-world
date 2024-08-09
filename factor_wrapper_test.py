# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Visualizes env wrapped with different factors of variation.

LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGL.so:/usr/lib/x86_64-linux-gnu/libGLEW.so \
python -m factor_wrapper_test \
  --seed=0 \
  --num_episodes=5 \
  --task_name=pick-place-v2
  """
from absl import app
from absl import flags
from typing import Any, Dict
import numpy as np
import time

from factor_world.envs.env_dict import ALL_V2_ENVIRONMENTS_GOAL_HIDDEN
from factor_world.envs.factors.utils import make_env_with_factors

FLAGS = flags.FLAGS

flags.DEFINE_string('task_name', 'pick-place-v2', 'Task name')
# flags.DEFINE_string("task_name", "basketball-v2", "Task name")
flags.DEFINE_integer('seed', 0, 'Random seed')
flags.DEFINE_integer("num_episodes", 5, "Number of episodes to run for each factor")
flags.DEFINE_integer('episode_len', 100, 'Number of timesteps per episode')
flags.DEFINE_boolean('render', True, 'Whether to render environment')

from gym import Wrapper

DEFAULT_CAMERA_CONFIG = {
    "distance": 1.25,
    "azimuth": 145,
    "elevation": -25.0,
    "lookat": np.array([0.0, 0.65, 0.0]),
}

DEFAULT_SIZE = 224


def test_factor_wrapper(
    task_name: str, factor_kwargs: Dict[str, Dict[str, Any]], num_episodes: int = 10
):
    env_cls = ALL_V2_ENVIRONMENTS_GOAL_HIDDEN[f"{task_name}-goal-hidden"]
    env_kwargs = dict(
        camera_name="movable",
        get_image_obs=False,
        image_obs_size=None,
    )
    env = make_env_with_factors(
        env_cls, env_kwargs, use_train_xml=False, factor_kwargs=factor_kwargs
    )
    print(env.factor_names)
    print(env.current_factor_values)

    # Benchmark episode times
    total_episode_time = 0
    total_step_time = 0
    total_steps = 0

    # Test reset and step.
    for _ in range(num_episodes):
        episode_start_time = time.time()
        env.reset()
        #custom_camera(env)
        for _ in range(FLAGS.episode_len):
            step_start_time = time.time()  # Start timing for per-step
            env.step(env.action_space.sample())
            step_duration = time.time() - step_start_time  # End timing for per-step
            total_step_time += step_duration
            total_steps += 1
            if FLAGS.render:
                env.render()
        episode_duration = time.time() - episode_start_time
        total_episode_time += episode_duration

    avg_episode_time = total_episode_time / num_episodes
    avg_step_time = total_step_time / total_steps
    print(f"Average episode duration: {avg_episode_time:.4f} seconds")
    print(f"Average step duration: {avg_step_time:.4f} seconds")

    env.close()


def main(argv):
    # Continuous-valued factors except Table Position
    test_factor_wrapper(
        task_name=FLAGS.task_name,
        factor_kwargs={
            "arm_pos": dict(
                x_range=(-0.5, 0.5),
                y_range=(-0.2, 0.4),
                z_range=(-0.15, 0.1),
                seed=FLAGS.seed,
            ),
            # "camera_pos": dict(
            #    azimuth_range=(np.pi / 2, 3 * np.pi / 4),
            #    inclination_range=(np.pi / 6, np.pi / 3),
            #    radius_range=(1.25, 1.75),
            #    seed=FLAGS.seed,
            # ),
            "light": dict(
                diffuse_range=(0.2, 0.8),
                seed=FLAGS.seed,
            ),
            "object_pos": dict(
                x_range=(-0.3, 0.3),
                y_range=(-0.1, 0.2),
                z_range=(-0.0, 0.0),
                theta_range=(0, 2 * np.pi),
                seed=FLAGS.seed,
            ),
            "object_size": dict(
                scale_range=(0.4, 1.4),
                seed=FLAGS.seed,
            ),
        },
        num_episodes=FLAGS.num_episodes,
    )

    # Textures + Table Position
    test_factor_wrapper(
        task_name=FLAGS.task_name,
        factor_kwargs={
            "floor_texture": dict(
                seed=FLAGS.seed,
            ),
            # TODO(lslee): Not working for basketball-v2
            # "object_texture": dict(
            #    seed=FLAGS.seed,
            # ),
            "table_texture": dict(
                seed=FLAGS.seed,
            ),
            "table_pos": dict(
                x_range=(-0.3, 0.3),
                y_range=(-0.1, 0.2),
                z_range=(-0.0, 0.0),
                seed=FLAGS.seed,
            ),
        },
        num_episodes=FLAGS.num_episodes,
    )

    # Distractor objects
    test_factor_wrapper(
        task_name=FLAGS.task_name,
        factor_kwargs={
            "distractor_xml": dict(
                object_ids_range=(0, 100),
                size_range=(0.3, 0.8),
                theta_range=(0, 6.283185),
                num_resets_per_randomize=5,
                seed=FLAGS.seed,
            ),
            # Distractor pos
            "distractor_pos": dict(
                table_edge_distance=0.05,
                theta_range=(0, 2 * np.pi),
                num_resets_per_randomize=1,
                seed=FLAGS.seed,
            ),
        },
        num_episodes=FLAGS.num_episodes,
    )

    # Varying the main task object
    # test_factor_wrapper(
    #   task_name=FLAGS.task_name,
    #   factor_kwargs={
    #     # Only tested to work for pick-place-v2.
    #     'object_xml': dict(
    #         object_ids_range=(0, 100),
    #         size_range=(0.3, 0.8),
    #         theta_range=(0, 6.283185),
    #         num_resets_per_randomize=5,
    #         seed=FLAGS.seed,
    #     ),
    #     'object_pos': dict(
    #         x_range=(-0.3, 0.3),
    #         y_range=(-0.1, 0.2),
    #         z_range=(-0., 0.),
    #         theta_range=(0, 2 * np.pi),
    #         num_resets_per_randomize=1,
    #         seed=FLAGS.seed,
    #     ),
    #     'object_size': dict(
    #         scale_range=(0.4, 1.4),
    #         num_resets_per_randomize=1,
    #         seed=FLAGS.seed,
    #     ),
    #     'object_texture': dict(
    #         num_resets_per_randomize=1,
    #         seed=FLAGS.seed,
    #     ),
    #   },
    #   num_episodes=FLAGS.num_episodes)

if __name__ == '__main__':
    app.run(main)
