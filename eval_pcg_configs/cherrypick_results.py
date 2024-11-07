import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser('summarize gstar_result')
    parser.add_argument('--result_dir', type=str, default='./results')
    parser.add_argument('--rulebased_result_dir', type=str, default='./results_rulebased')
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
    results_model_dir = os.path.join(args.result_dir, f"agent{args.agent_index}_skill{args.skill_index}")
    results_rulebased_dir = os.path.join(args.rulebased_result_dir, f"agent{args.agent_index}_skill{args.skill_index}")
    TARGET_WINRATES = [0.1, 0.3]
    better_configs = []

    for target_winrate in TARGET_WINRATES:
        directory_name = f"config_generate-{args.agent_index}-{args.skill_index}-{target_winrate}"
        model_dir = os.path.join(results_model_dir, directory_name)
        rulebased_dir = os.path.join(results_rulebased_dir, directory_name)

        model_l1_distances = []
        rulebased_l1_distances = []
        model_winrates = []
        rulebased_winrates = []
        config_names = []

        for dir_name in sorted(os.listdir(model_dir), key=lambda x: int(x.split("_")[-1])):
            model_path = os.path.join(model_dir, dir_name)
            rulebased_path = os.path.join(rulebased_dir, dir_name)

            model_winrate = get_winrate(model_path, args.epi_num)
            rulebased_winrate = get_winrate(rulebased_path, args.epi_num)

            model_l1_distance = abs(model_winrate - target_winrate * 100)
            rulebased_l1_distance = abs(rulebased_winrate - target_winrate * 100)

            model_winrates.append(model_winrate)
            rulebased_winrates.append(rulebased_winrate)
            model_l1_distances.append(model_l1_distance)
            rulebased_l1_distances.append(rulebased_l1_distance)
            config_names.append(int(dir_name.split("_")[-1]))

            if model_winrate > rulebased_winrate:
                better_configs.append((target_winrate, dir_name, model_winrate, rulebased_winrate))

            print(f"Target: {target_winrate*100:.1f}%, Model Winrate: {model_winrate:.1f}%, "
                  f"Rule-based Winrate: {rulebased_winrate:.1f}%, Model L1 distance: {model_l1_distance:.1f}, "
                  f"Rule-based L1 distance: {rulebased_l1_distance:.1f}")

        # Plotting L1 distances for this target winrate
        plt.figure(figsize=(10, 5))
        plt.plot(config_names, model_l1_distances, label="Model L1 Distance to Target", marker='o')
        plt.plot(config_names, rulebased_l1_distances, label="Rule-based L1 Distance to Target", marker='o')
        plt.axhline(y=0, color='r', linestyle='--', label="Target L1 Distance")
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Configuration Number")
        plt.ylabel("L1 Distance to Target (%)")
        plt.title(f"L1 Distance to Target for Target Winrate {target_winrate*100:.1f}%")
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Plotting Winrates for this target winrate
        plt.figure(figsize=(10, 5))
        plt.plot(config_names, model_winrates, label="Model Winrate", marker='x')
        plt.plot(config_names, rulebased_winrates, label="Rule-based Winrate", marker='s')
        plt.axhline(y=target_winrate * 100, color='r', linestyle='--', label="Target Winrate")
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Configuration Number")
        plt.ylabel("Winrate (%)")
        plt.title(f"Winrate Comparison for Target Winrate {target_winrate*100:.1f}%")
        plt.legend()
        plt.tight_layout()
        plt.show()

    # Output better configurations
    print("\nConfigurations where model winrate was higher than rule-based winrate:")
    for target_winrate, config_name, model_winrate, rulebased_winrate in better_configs:
        print(f"Config: {config_name}, Target Winrate: {target_winrate*100:.1f}%, Model Winrate: {model_winrate:.1f}% > Rule Winrate: {rulebased_winrate:.1f}%")

if __name__ == '__main__':
    args = parse_args()
    main(args)
