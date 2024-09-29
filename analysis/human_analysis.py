import argparse
import os
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--logdir_path', type=str, default="./human_data/")
    parser.add_argument('--control_agent', type=str, default='MeleeDealer')
    return parser.parse_args()


class Log_analysis:

    def __init__(self, args):
        self.logdir_path = args.logdir_path
        self.movement_column = ['episodeLogcount', 'Agent_name', 'Time', 'Position_x', 'Position_y',
                                'Position_z', 'heath.current']
        self.combat_column = ['SourceAgent', 'TargetAgent', 'SkillName', 'Value', 'isCritical', 'isBackAttack',
                              'hittime', 'episodeLogcount', 'skillState', 'skillType', 'damageValue', 'shieldValue']
        self.gameresult_column = ['Result', 'EpisodeLength']

    def result(self):
        movement_diff_list = []
        combat_skill_count_list = []

        folder_list = os.listdir(self.logdir_path)
        for folder in folder_list:
            folder_path = os.path.join(self.logdir_path, folder)
            movement_log_pd = pd.read_csv(folder_path + '/movement_log.csv', header=None, names=self.movement_column)
            combat_log_pd = pd.read_csv(folder_path + '/combat_log.csv', header=None, names=self.combat_column)
            gameresult_log_pd = pd.read_csv(folder_path + '/gameresult_log.csv', header=None, names=self.gameresult_column)

            movement_diff = self.cal_movement(movement_log_pd)
            combat_skill_count = self.cal_combat(combat_log_pd)

            movement_diff_list.append(movement_diff)
            combat_skill_count_list.append(combat_skill_count)

        return movement_diff_list, combat_skill_count_list

    @staticmethod
    def cal_movement(log):
        patchwerk = log[log['Agent_name'] == 'Patchwerk']
        melee_dealer = log[log['Agent_name'] == 'MeleeDealer']

        merged_new = pd.merge(patchwerk, melee_dealer, on=['episodeLogcount', 'Time'],
                              suffixes=('_patchwerk', '_melee'))
        position_diff_epi = merged_new[['episodeLogcount', 'Time']].copy()
        position_diff_epi['Position_x_diff'] = merged_new['Position_x_patchwerk'] - merged_new['Position_x_melee']
        position_diff_epi['Position_y_diff'] = merged_new['Position_y_patchwerk'] - merged_new['Position_y_melee']
        position_diff_epi['Position_z_diff'] = merged_new['Position_z_patchwerk'] - merged_new['Position_z_melee']

        episode_diff_mean_df = position_diff_epi.groupby('episodeLogcount').mean().reset_index()

        return episode_diff_mean_df

    @staticmethod
    def cal_combat(log):
        pass


if __name__ == '__main__':
    log_args = parse_args()
    analysis = Log_analysis(log_args)
    analysis.result()
