import argparse
import time
from tqdm import tqdm
import os
import numpy as np

from mlagents import torch_utils
import mlagents.trainers
from mlagents.trainers.learn import (
    parse_command_line,
    run_training
)
import mlagents_envs
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.timers import add_metadata as add_timer_metadata
from mlagents_envs import logging_util

logger = logging_util.get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser('Test PCG configs with trained models')
    parser.add_argument('--base_yaml', type=str, default='./inference.yaml')
    parser.add_argument('--config_path', type=str, default="./configs")
    parser.add_argument('--model_path', type=str, default='./models')
    parser.add_argument('--save_path', type=str, default='./results')
    parser.add_argument('--agent_index', type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument('--skill_index', type=int, default=1, choices=[0, 1])
    parser.add_argument('--target_winrate', type=float, default=0.5, choices=[0.1, 0.3, 0.5, 0.7, 0.9])
    parser.add_argument('--epi_num', type=int, default=100)

    return parser.parse_args()


def prepare_mlagents(options):
    logging_util.set_log_level(logging_util.FATAL)

    # Add some timer metadata
    add_timer_metadata("mlagents_version", mlagents.trainers.__version__)
    add_timer_metadata("mlagents_envs_version", mlagents_envs.__version__)
    add_timer_metadata("communication_protocol_version", UnityEnvironment.API_VERSION)
    add_timer_metadata("pytorch_version", torch_utils.torch.__version__)
    add_timer_metadata("numpy_version", np.__version__)

    run_seed = options.env_settings.seed
    if options.env_settings.seed == -1:
        run_seed = np.random.randint(0, 10000)
        logger.debug(f"run_seed set to {run_seed}")

    return run_seed


def run_mlagents(options, model_path, config_path, save_path, run_seed, n_episodes):
    # Change base_port
    options.env_settings.base_port = 5004 + run_seed

    # Change env_args
    options.env_settings.env_args[
        options.env_settings.env_args.index('--configPath') + 1
    ] = config_path
    options.env_settings.env_args[
        options.env_settings.env_args.index('--logPath') + 1
    ] = save_path
    options.env_settings.env_args[
        options.env_settings.env_args.index('--maEvalEpisodeLimit') + 1
    ] = str(n_episodes)

    # Change model settings
    model_dir = os.path.dirname(model_path)
    model_name = os.path.basename(model_path)
    options.checkpoint_settings.results_dir = model_dir
    options.checkpoint_settings.run_id = model_name
    try:
        run_training(run_seed, options, options.env_settings.num_areas)
    except Exception as e:
        if "Previous data from this run ID was not found" in e.args[0]:
            logger.critical(f"Error occurred. Please check --model_dir: {model_dir} or --model_name: {model_name}")
        else:
            logger.critical(f"Error occurred during training: {e}")

    # Move log files
    temp_dir = os.path.join(save_path, os.listdir(save_path)[0])
    file_names = ["combat_log.csv", "gameresult_log.csv", "movement_log.csv"]
    for file_name in file_names:
        src = os.path.join(temp_dir, file_name)
        dst = os.path.join(save_path, file_name)
        os.rename(src, dst)
    os.rmdir(temp_dir)


def main(args):
    options = parse_command_line([args.base_yaml])
    run_seed = prepare_mlagents(options)

    # Set model_dir
    # model_dir = os.path.join(args.model_path, f"agent_{args.agent_index}_skill{args.skill_index}")
    model_dir = os.path.join(args.model_path, f"agent{args.agent_index}_skill{args.skill_index}_run0")

    for config_number in tqdm(range(NUM_CONFIGS)):
        config_path = os.path.join(
            args.config_path, f"WinRate_{args.target_winrate}", f"config_{config_number}.json")
        save_path = os.path.join(
            args.save_path, f"agent{args.agent_index}_skill{args.skill_index}",
            f"WinRate_{args.target_winrate}", f"config_{config_number}")

        # Run mlagents
        run_mlagents(options, model_dir, config_path, save_path, run_seed, args.epi_num)

        # Wait for 5 seconds
        time.sleep(5)


NUM_CONFIGS = 20


if __name__ == '__main__':
    args = parse_args()
    main(args)
