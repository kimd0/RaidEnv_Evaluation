import os
import pandas as pd
import matplotlib.pyplot as plt

def analysis_log(log_dir):
    log_path = os.path.join(os.getcwd(), 'result')
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

    return win_rate, episode_length, avg_dealt, avg_taken

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
    run_analysis('casttime')
    run_analysis('cooltime')
    run_analysis('damage')
    run_analysis('range')
    run_analysis('healthMax')
    run_analysis('armor')
    run_analysis('moveSpeed')

    #analysis_log('casttime_0.0')