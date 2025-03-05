import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import numpy as np
import seaborn as sns
from tqdm import tqdm

def analysis_log(result_path):

    log_path = os.path.join(os.getcwd(), result_path)

    for log_dir in os.listdir(log_path):
        # Load combat_log
        combat_log = pd.read_csv(os.path.join(log_path, log_dir, "combat_log.csv"), header=None)
        combat_log.columns = ["source", "target", "skill", "damage", "is_critical", "is_backattack",
                              "episode_length", "episode_id", "state", "type", "damage_value", "shield"]
        combat_log.drop_duplicates(inplace=True)

        # Load gameresult_log
        gameresult_log = pd.read_csv(os.path.join(log_path, log_dir, "gameresult_log.csv"), names=["result", "episode_length"])
        gameresult_log['episode_id'] = gameresult_log.index + 1

        damage_dealt = combat_log.query('source != "Patchwerk"').groupby(["episode_id", "source"])["damage_value"].sum().unstack(fill_value=0)
        damage_taken = combat_log.query('source == "Patchwerk"').groupby(["episode_id", "target"])["damage_value"].sum().unstack(fill_value=0)

        win_rate = 100 * gameresult_log['result'].eq('PlayerWin').mean()
        draw_rate = 100 * gameresult_log['result'].eq('Draw').mean()
        episode_length = gameresult_log['episode_length'].mean()

        avg_dealt = -damage_dealt.sum(axis=1).mean()
        avg_taken = -damage_taken.sum(axis=1).mean()

        print('============================================================================')
        print(f"Folder: {log_dir}")
        print('win_rate:', win_rate)
        print('episode_length:', episode_length)
        print('avg_dealt:', avg_dealt)
        print('avg_taken:', avg_taken)
        print('game_length', len(gameresult_log))
        print('============================================================================')

    return win_rate, episode_length, avg_dealt, avg_taken


def make_dir(save_path):
    # This code will be moved to utils.py in future
    if not os.path.exists(save_path):
        os.makedirs(save_path)


def visulaize_trajectory(path, args):
    method_name = path.split('/')[-1]
    agent_skill = path.split('/')[-2]

    save_dir = args.save_path
    new_save_dir = os.path.join(save_dir, agent_skill, method_name)
    os.makedirs(new_save_dir, exist_ok=True)

    for config_name in tqdm(sorted(os.listdir(path))):
        csv_path = os.path.join(path, config_name, 'movement_log.csv')

        combined_df = pd.read_csv(csv_path, header=None)
        combined_df.rename(columns={0: 'agent', 1: 'time', 2: 'X', 3: 'Y', 4: 'Z', 5: 'health'}, inplace=True)

        agents = combined_df[combined_df['agent'] != 'Boss']

        dx = agents['X'] + 12
        dy = agents['Z'] + 12

        canvas = np.zeros((24, 24), dtype=np.uint8)
        for x, y in zip(dx, dy):
            if 0 <= int(x) < 24 and 0 <= int(y) < 24:  # 범위 체크
                canvas[23 - int(y), int(x)] += 1

        if np.max(canvas) > 0:
            canvas = (canvas - np.min(canvas)) / (np.max(canvas) - np.min(canvas))

        plt.figure(figsize=(6, 6))
        plt.title(f"Trajectory Heatmap ({method_name} - {config_name})", fontsize=14)
        sns.heatmap(canvas, cmap="viridis", alpha=1, annot=False, cbar_ax=None, yticklabels=False, xticklabels=False)

        save_path = os.path.join(new_save_dir, f'trajectory_{method_name}_{config_name}.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"Saved: {save_path}")


def run_analysis(attributename):
    results_dir = os.path.join(os.getcwd(), 'result')
    matching_folders = [d for d in os.listdir(results_dir) if
                        d.startswith(attributename + '_')]

    data = []

    for folder in matching_folders:
        log_dir = os.path.join(results_dir, folder)
        win_rate, episode_length, avg_dealt, avg_taken = analysis_log(log_dir)

        variable = folder.split('_')[-1]
        data.append([win_rate, episode_length, avg_dealt, avg_taken, variable])

    df = pd.DataFrame(data, columns=['win_rate', 'episode_length', 'avg_dealt', 'avg_taken', 'variable'])
    df['variable'] = pd.to_numeric(df['variable'], errors='coerce')

    df.sort_values(by='variable', inplace=True)

    df.reset_index(drop=True, inplace=True)
    df.set_index('variable', inplace=True)

    result_path = os.path.join(os.getcwd(), 'analysis')
    make_folder(result_path)
    result_csv_path = os.path.join(result_path, f"{attributename}_results.csv")
    df.to_csv(result_csv_path)

    show_plot(result_csv_path)
    return df

def show_plot(data_path):
    csv_data = pd.read_csv(data_path)
    attribute_name = os.path.basename(data_path)
    attribute_name = attribute_name.split('_')[-2]

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    titles = ['Win Rate vs '+attribute_name,
              'Episode Length vs '+attribute_name,
              'Average Damage Dealt vs '+attribute_name,
              'Average Damage Taken vs '+attribute_name]
    y_data = ['win_rate', 'episode_length', 'avg_dealt', 'avg_taken']

    for ax, y, title in zip(axs.flat, y_data, titles):
        ax.plot(csv_data['variable'], csv_data[y], marker='o', linestyle='-', markersize=4)
        ax.set_title(title)
        ax.set_xlabel(attribute_name)
        ax.set_ylabel(y.replace('_', ' ').title())
        ax.grid()

    plt.tight_layout()
    plt.show()


def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="example")
    parser.add_argument("--result_path", default="human_result", type=str)
    parser.add_argument("--folder_path", default="human_40m", type=str)
    parser.add_argument("--save_path", default="./figure", type=str)
    args = parser.parse_args()
    # run_analysis('casttime')
    # run_analysis('cooltime')
    # run_analysis('damage')
    # run_analysis('range')
    # run_analysis('healthMax')
    # run_analysis('armor')
    # run_analysis('moveSpeed')
    # analysis_log(args.result_path)
    # regret
    # rulebased
    path = "Z:/MMORPG/2025/MA/results_test/agent2_skill1/rulebased"
    # path = "s1"
    visulaize_trajectory(path, args)