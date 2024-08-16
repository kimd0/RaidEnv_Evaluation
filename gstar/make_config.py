import json
import copy
import argparse
import itertools
from tqdm import tqdm
import os

def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--json_path', type=str, default="./json/default_dealer_skill1.json")
    parser.add_argument('--save_path', type=str, default="./config/dealer_skill1")
    parser.add_argument('--agent_index', type=int, default=2)
    parser.add_argument('--t_skill_num', type=int, default=0)

    return parser.parse_args()


class ConfigManager:
    def __init__(self, args):
        self.args = args
        self.source_file_name = args.json_path
        self.target_directory = args.save_path
        self.data = self.read_json()

    def read_json(self):
        with open(self.source_file_name, 'r') as f:
            data = json.load(f)
        return data

    def write_json(self, file_name, data):
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    def generate_configs(self, skillconfig):
        origin_data = copy.deepcopy(self.data)

        config_combi = list(itertools.product(
            skillconfig["healthMax"],
            skillconfig["armor"],
            skillconfig["moveSpeed"],
            skillconfig["cooltime"],
            skillconfig["range"],
            skillconfig["casttime"],
            skillconfig["damage"]
        ))

        for i, (health_V, armor_V, move_V, cool_V, range_V, cast_V, damage_V) in tqdm(enumerate(config_combi),
                                                                                      total=len(config_combi)):
            new_data = copy.deepcopy(origin_data)

            new_data['agentConfigs'][self.args.agent_index]['statusConfig']["healthMax"] = [health_V]
            new_data['agentConfigs'][self.args.agent_index]['statusConfig']["armor"] = [armor_V]
            new_data['agentConfigs'][self.args.agent_index]['statusConfig']["moveSpeed"] = [move_V]
            new_data['agentConfigs'][self.args.agent_index]['skillConfigs'][self.args.t_skill_num]["cooltime"] = [cool_V]
            new_data['agentConfigs'][self.args.agent_index]['skillConfigs'][self.args.t_skill_num]["range"] = [range_V]
            new_data['agentConfigs'][self.args.agent_index]['skillConfigs'][self.args.t_skill_num]["casttime"] = [cast_V]
            new_data['agentConfigs'][self.args.agent_index]['skillConfigs'][self.args.t_skill_num]["damage"] = [damage_V]

            target_file_name = f'{self.target_directory}\\config_{i:05}.json'
            self.write_json(target_file_name, new_data)


def make_folders(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == "__main__":
    args = parse_args()
    make_folders(args.save_path)
    # Initialize ConfigManager
    manager = ConfigManager(args)

    skillConfig_list = {
        "healthMax": [5000, 22000, 38000, 55000],
        "armor": [18000, 31000, 44000, 58000],
        "moveSpeed": [0.9, 1.1, 1.3, 1.5],
        "cooltime": [0.1, 1.2, 2.4, 3.6],
        "range": [3, 3.6, 4.3, 5],
        "casttime": [0, 1.3, 2.6, 4],
        "damage": [30000, 37000, 45000, 52000],
    }

    # Generate configurations
    manager.generate_configs(skillConfig_list)
