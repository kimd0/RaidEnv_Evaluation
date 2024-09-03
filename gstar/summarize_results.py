import argparse
import os
import json
from tqdm import tqdm
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser('summarize gstar_result')
    parser.add_argument('--result_dir', type=str, required=True)
    parser.add_argument('--agent_index', type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument('--skill_index', type=int, default=1, choices=[0, 1])
    parser.add_argument('--epi_num', type=int, default=100)

    return parser.parse_args()


def analysis_log(result_dir: str, epi_num: int):
    # Load gameresult_log
    gameresult_log = pd.read_csv(os.path.join(result_dir, "gameresult_log.csv"), names=["result", "episode_length"])
    gameresult_log = gameresult_log.iloc[:epi_num]
    count = gameresult_log.shape[0]

    # Load combat_log
    combat_log_org = pd.read_csv(os.path.join(result_dir, "combat_log.csv"), header=None, names=[
        "source", "target", "skill", "damage", "is_critical", "is_backattack",
        "episode_length", "episode_id", "state", "type", "damage_value", "shield"])
    combat_log = combat_log_org[combat_log_org.episode_id <= epi_num]
    combat_log.drop_duplicates(inplace=True)
    if count != combat_log['episode_id'].max():
        print(f"Warning: episode count mismatch: {count} vs {combat_log['episode_id'].max()}")

    # Analysis
    damage_dealt = combat_log.query('source != "Patchwerk"').groupby(["episode_id", "source"])["damage_value"].sum().unstack(fill_value=0)
    damage_taken = combat_log.query('source == "Patchwerk"').groupby(["episode_id", "target"])["damage_value"].sum().unstack(fill_value=0)

    win_rate = 100 * gameresult_log['result'].eq('PlayerWin').mean()
    episode_length = gameresult_log['episode_length'].mean()

    avg_dealt = -damage_dealt.sum(axis=1).mean()
    avg_taken = -damage_taken.sum(axis=1).mean()

    return win_rate, episode_length, avg_dealt, avg_taken, count


def get_skill_parameters(result_dir: str, agent_index: int, skill_index: int):
    config_name = os.path.basename(result_dir)
    with open(os.path.join(result_dir, f'{config_name}.json'), 'r') as f:
        data = json.load(f)
    agent_config = data['agentConfigs'][agent_index]
    status_config = agent_config['statusConfig']
    skill_config = agent_config['skillConfigs'][skill_index]
    return (status_config['healthMax'][0], status_config['armor'][0], status_config['moveSpeed'][0],
            skill_config['cooltime'][0], skill_config['range'][0],
            skill_config['casttime'][0], skill_config['damage'][0])


def summarize_gameresult_log(result_dir: str, epi_num: int):
    gameresult_log_org = pd.read_csv(os.path.join(result_dir, "gameresult_log.csv"), names=["result", "episode_length"])
    gameresult_log = gameresult_log_org.iloc[:epi_num]
    win_rate = 100 * gameresult_log['result'].eq('PlayerWin').mean()
    episode_length = gameresult_log['episode_length'].mean()
    return episode_length, win_rate


def main(args):
    df = list()

    for d in tqdm(os.listdir(args.result_dir)):
        result_path = os.path.join(args.result_dir, d)
        healthMax, armor, moveSpeed, cooltime, range, casttime, damage = get_skill_parameters(result_path, args.agent_index, args.skill_index)
        win_rate, episode_length, dealt, taken, count = analysis_log(result_path, args.epi_num)
        df.append([healthMax, armor, moveSpeed,
                   cooltime, range, casttime, damage,
                   win_rate, episode_length, dealt, taken, count])

    return pd.DataFrame(df, columns=['healthMax', 'armor', 'moveSpeed',
                                     'cooltime', 'range', 'casttime', 'damage',
                                     'win_rate', 'episode_length', 'dealt', 'taken', 'count'])


if __name__ == '__main__':
    args = parse_args()
    df = main(args)
    print(df)
    df.to_csv(os.path.join(args.result_dir, os.pardir, f'summary_{os.path.basename(args.result_dir)}.csv'), index=False)
