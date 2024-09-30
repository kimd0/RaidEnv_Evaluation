import argparse
import os
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--logdir_path', type=str, default="./human_data/")
    parser.add_argument('--control_agent', type=str, default='MeleeDealer')
    parser.add_argument('--save_dir', type=str, default="./result/")
    return parser.parse_args()


class LogAnalysis:

    def __init__(self, args):
        self.logdir_path = args.logdir_path
        self.save_dir = args.save_dir
        self.movement_column = ['episodeLogcount', 'Agent_name', 'Time', 'Position_x', 'Position_y',
                                'Position_z', 'heath.current']
        self.combat_column = ['SourceAgent', 'TargetAgent', 'SkillName', 'Value', 'isCritical', 'isBackAttack',
                              'hittime', 'episodeLogcount', 'skillState', 'skillType', 'damageValue', 'shieldValue']
        self.result_column = ['Result', 'EpisodeLength']

    def result(self):
        movement_diff_list = []
        combat_skill_count_list = []
        gameresult_list = []

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
            gameresult_list.append(gameresult_log_pd)

        movement_df = pd.concat(movement_diff_list, ignore_index=True)
        movement_stat, movement_normal_df = self.calculate_df(movement_df, ['x_diff', 'y_diff', 'z_diff'])

        combat_df = pd.concat(combat_skill_count_list, ignore_index=True)
        combined_combat_df = self.combine_combat_skills(combat_df)
        combat_stat, combat_normal_df = self.calculate_df(combined_combat_df, combined_combat_df.keys())

        gameresult_df = pd.concat(gameresult_list, ignore_index=True)
        gameresult_df_final = self.cal_gameresult(gameresult_df)

        self.make_dir(self.save_dir)
        self.save_results(movement_stat, movement_normal_df, combat_stat, combat_normal_df, gameresult_df_final)

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
        melee_dealer_skill = melee_dealer.groupby(['episodeLogcount', 'SkillName']).size().reset_index(name='SkillCount')

        return melee_dealer_skill

    @staticmethod
    def cal_gameresult(log):
        avg_epi_length = log['EpisodeLength'].mean()
        player_wins = len(log[log['Result'] == 'PlayerWin'])
        enemy_wins = len(log[log['Result'] == 'EnemyWin'])
        player_win_rate = player_wins / len(log)
        enemy_win_rate = enemy_wins / len(log)

        gameresult = pd.DataFrame({
            'AverageEpisodeLength': [avg_epi_length],
            'PlayerWinRate': [player_win_rate],
            'EnemyWinRate': [enemy_win_rate]
        })

        return gameresult

    @staticmethod
    def combine_combat_skills(df, group_size=3):
        combined_rows = []
        skill_pivot = df.pivot(columns='SkillName', values='SkillCount')
        for i in range(0, len(skill_pivot), group_size):
            group = skill_pivot.iloc[i:i + group_size].sum()  # 각 그룹을 합산
            combined_rows.append(group)
        return pd.DataFrame(combined_rows)

    @staticmethod
    def make_dir(save_path):
        # This code will be moved to utils.py in future
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    def save_results(self, movement_stat, movement_normal_df, combat_stat, combat_normal_df, game_result_df):
        pd.DataFrame([movement_stat]).to_csv(os.path.join(self.save_dir, 'movement_stats.csv'), index=False)
        movement_normal_df.to_csv(os.path.join(self.save_dir, 'movement_normalized.csv'), index=False)
        pd.DataFrame([combat_stat]).to_csv(os.path.join(self.save_dir, 'combat_stats.csv'), index=False)
        combat_normal_df.to_csv(os.path.join(self.save_dir, 'combat_normalized.csv'), index=False)
        game_result_df.to_csv(os.path.join(self.save_dir, 'game_result.csv'), index=False)


if __name__ == '__main__':
    log_args = parse_args()
    analysis = LogAnalysis(log_args)
    analysis.result()
