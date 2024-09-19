import argparse
import os
from collections import defaultdict
import pandas as pd

from ranking.const import ROLES, TARGET_WINRATES, METHODS


def parse_args():
    parser = argparse.ArgumentParser('summarize gstar_result')
    parser.add_argument('--result_dir', type=str, required=True)
    parser.add_argument('--methods', type=str, nargs='+', required=True, default=METHODS)
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
    l1_distances = defaultdict(list)
    for method in args.methods:
        result_dir = os.path.join(args.result_dir, f"{ROLES[args.agent_index]}_{args.skill_index}", method)

        for target_winrate in TARGET_WINRATES:
            result_path = os.path.join(result_dir, f"WinRate_{target_winrate}")

            for dir_name in os.listdir(result_path):
                dir_path = os.path.join(result_path, dir_name)

                l1_distance = abs(get_winrate(dir_path, args.epi_num) - target_winrate)
                l1_distances[method].append(l1_distance)

    # Show ranking
    print("Ranking by winrate gap")
    for method, l1_distance in sorted(l1_distances.items(), key=lambda x: sum(x[1])):
        print(f"{method}: {sum(l1_distance)/len(l1_distance):.2f}% for {len(l1_distance)} configs")


if __name__ == '__main__':
    args = parse_args()
    main(args)
