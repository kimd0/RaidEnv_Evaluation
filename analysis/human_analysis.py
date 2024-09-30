import argparse
import os
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--logdir_path', type=str, default="./human_data/")
    parser.add_argument('--control_agent', type=str, default='MeleeDealer')
    parser.add_argument('--save_dir', type=str, default="./human_data/")
    return parser.parse_args()


class LogAnalysis:

    def __init__(self, args):
        self.logdir_path = args.logdir_path
        self.movement_column = ['episodeLogcount', 'Agent_name', 'Time', 'Position_x', 'Position_y',
                                'Position_z', 'heath.current']
        self.combat_column = ['SourceAgent', 'TargetAgent', 'SkillName', 'Value', 'isCritical', 'isBackAttack',
                              'hittime', 'episodeLogcount', 'skillState', 'skillType', 'damageValue', 'shieldValue']
        self.result_column = ['Result', 'EpisodeLength']

    def result(self):
        movement_diff_list = []
        combat_skill_count_list = []

        folder_list = os.listdir(self.logdir_path)
        for folder in folder_list:
            folder_path = os.path.join(self.logdir_path, folder)
            movement_log_pd = pd.read_csv(folder_path + '/movement_log.csv', header=None, names=self.movement_column)
            combat_log_pd = pd.read_csv(folder_path + '/combat_log.csv', header=None, names=self.combat_column)
            gameresult_log_pd = pd.read_csv(folder_path + '/gameresult_log.csv', header=None, names=self.result_column)

            movement_diff = self.cal_movement(movement_log_pd)
            combat_skill_count = self.cal_combat(combat_log_pd)

            movement_diff_list.append(movement_diff)
            combat_skill_count_list.append(combat_skill_count)

        movement_df = pd.concat(movement_diff_list, ignore_index=True)
        movement_stat, movement_normal_df = self.calculate_df(movement_df, ['x_diff', 'y_diff', 'z_diff'])

        combat_df = pd.concat(combat_skill_count_list, ignore_index=True)
        skill_pivot = combat_df.pivot(columns='SkillName', values='SkillCount')
        group_size = 3
        combined_rows = []
        for i in range(0, len(skill_pivot), group_size):
            group = skill_pivot.iloc[i:i + group_size].sum()  # 각 그룹을 합산
            combined_rows.append(group)
        combined_combat_df = pd.DataFrame(combined_rows)

        combat_stat, combat_normal_df = self.calculate_df(combined_combat_df, combined_combat_df.keys())

        return movement_stat, movement_normal_df, combat_stat, combat_normal_df

    @staticmethod
    def calculate_df(target_df, columns):
        normal_df = target_df.copy()
        stats = {}
        for column in columns:
            mean_val = target_df[column].mean()
            std_val = target_df[column].std()
            stats[f'{column}_mean'] = mean_val
            stats[f'{column}_std'] = std_val
            normal_df[column] = (target_df[column] - mean_val) / std_val

        return stats, normal_df

    @staticmethod
    def cal_movement(log):
        patchwerk = log[log['Agent_name'] == 'Patchwerk']
        melee_dealer = log[log['Agent_name'] == 'MeleeDealer']

        merged_new = pd.merge(patchwerk, melee_dealer, on=['episodeLogcount', 'Time'],
                              suffixes=('_patchwerk', '_melee'))
        position_diff_epi = merged_new[['episodeLogcount', 'Time']].copy()
        position_diff_epi['x_diff'] = merged_new['Position_x_patchwerk'] - merged_new['Position_x_melee']
        position_diff_epi['y_diff'] = merged_new['Position_y_patchwerk'] - merged_new['Position_y_melee']
        position_diff_epi['z_diff'] = merged_new['Position_z_patchwerk'] - merged_new['Position_z_melee']

        episode_diff_mean_df = position_diff_epi.groupby('episodeLogcount').mean().reset_index()

        return episode_diff_mean_df

    @staticmethod
    def cal_combat(log):
        melee_dealer = log[(log['SourceAgent'] == 'MeleeDealer') & (log['damageValue'] != 0)]
        melee_dealer_skill = melee_dealer.groupby(['episodeLogcount', 'SkillName']).size().reset_index(
                                                                                                    name='SkillCount')

        return melee_dealer_skill


if __name__ == '__main__':
    log_args = parse_args()
    analysis = LogAnalysis(log_args)
    analysis.result()
