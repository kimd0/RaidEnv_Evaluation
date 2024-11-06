import argparse
from collections import defaultdict
import os
import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser('summarize gstar_result')
    parser.add_argument('--result_dir', type=str, default='./results')
    parser.add_argument('--agent_index', type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument('--skill_index', type=int, default=1, choices=[0, 1])
    parser.add_argument('--epi_num', type=int, default=100)

    return parser.parse_args()


def get_winrate(result_dir: str, epi_num: int):
    gameresult_log = pd.read_csv(os.path.join(result_dir, "gameresult_log.csv"), names=["result", "episode_length"])
    gameresult_log = gameresult_log.iloc[:epi_num]
    win_rate = 100 * gameresult_log['result'].eq('PlayerWin').mean()
    return win_rate


def main(args):
    # Load results
    result_dir = os.path.join(args.result_dir, f"agent{args.agent_index}_skill{args.skill_index}")

    l1_distance_by_target = defaultdict(list)
    for target_winrate in TARGET_WINRATES:
        result_path = os.path.join(result_dir, f"WinRate_{target_winrate}")

        for dir_name in sorted(os.listdir(result_path), key=lambda x: int(x.split("_")[-1])):
            dir_path = os.path.join(result_path, dir_name)

            winrate = get_winrate(dir_path, args.epi_num)
            l1_distance = abs(winrate - target_winrate * 100)
            l1_distance_by_target[target_winrate].append(l1_distance)
            print(f"Target winrate: {target_winrate:.1f}, winrate: {winrate:.1f}, L1 distance: {l1_distance:.1f}")

    # Show results
    sorted_winrates = sorted(l1_distance_by_target.items(), key=lambda x: sum(x[1]))
    for target_winrate, l1_distances in sorted_winrates:
        print(f"Target winrate: {target_winrate}")
        print(f"  Average L1 distance: {np.mean(l1_distances)}")


# TARGET_WINRATES = [0.3, 0.5, 0.7, 0.9]
TARGET_WINRATES = [0.3, 0.5, 0.7]


if __name__ == '__main__':
    args = parse_args()
    main(args)
