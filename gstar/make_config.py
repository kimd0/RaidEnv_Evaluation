import numpy as np

import json
import copy
import argparse
import itertools
from tqdm import tqdm
import os


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--json_path', type=str, default="./json/dealer_skill.json")
    parser.add_argument('--agent_index', type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument('--skill_index', type=int, default=1, choices=[0, 1])

    return parser.parse_args()


class ConfigManager:
    def __init__(self, args):
        self.source_file_name = args.json_path
        self.target_directory = os.path.join("./config/", args.json_path.split("/")[-1].split(".")[0])
        self.agent_index = args.agent_index
        self.skill_index = args.skill_index
        self.data = self.read_json()
        self.make_folder(self.target_directory)

    def make_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

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

            new_data['agentConfigs'][self.agent_index]['statusConfig']["healthMax"] = [health_V]
            new_data['agentConfigs'][self.agent_index]['statusConfig']["armor"] = [armor_V]
            new_data['agentConfigs'][self.agent_index]['statusConfig']["moveSpeed"] = [move_V]
            new_data['agentConfigs'][self.agent_index]['skillConfigs'][self.skill_index]["cooltime"] = [cool_V]
            new_data['agentConfigs'][self.agent_index]['skillConfigs'][self.skill_index]["range"] = [range_V]
            new_data['agentConfigs'][self.agent_index]['skillConfigs'][self.skill_index]["casttime"] = [cast_V]
            new_data['agentConfigs'][self.agent_index]['skillConfigs'][self.skill_index]["damage"] = [damage_V]

            target_file_name = f'{self.target_directory}/config_{i:05}.json'
            self.write_json(target_file_name, new_data)


_skillConfig_combi = {
    # key: (agent_idx, skill_idx)
    # value: options to be combined in the config
    (2, 0): {
        "healthMax": [5000, 22000, 38000, 55000],
        "armor": [18000, 31000, 44000, 58000],
        "moveSpeed": [0.9, 1.1, 1.3, 1.5],
        "cooltime": [0.1, 1.2, 2.4, 3.6],
        "range": [3, 3.6, 4.3, 5],
        "casttime": [0, 1.3, 2.6, 4],
        "damage": [30000, 37000, 45000, 52000],
    },
    (2, 1): {
        "healthMax": [5000, 22000, 38000, 55000],
        "armor": [18000, 31000, 44000, 58000],
        "moveSpeed": [0.9, 1.1, 1.3, 1.5],
        "cooltime": [0, 3, 6, 9],
        "range": [0, 1.2, 2.5, 3.8],
        "casttime": [1.0, 1.7, 2.4, 3.2],
        "damage": [21000, 25000, 30000, 35000]
    }
}


if __name__ == "__main__":
    args = parse_args()
    # Initialize ConfigManager
    manager = ConfigManager(args)

    # Get combinations
    skillConfig_list = _skillConfig_combi[(manager.agent_index, manager.skill_index)]
    comb_count = np.prod([len(v) for v in skillConfig_list.values()])
    print(f"[INFO] Creating {comb_count} configurations for "
          f"(agent_index={manager.agent_index}, skill_idx={manager.skill_index})")

    # Generate configurations
    manager.generate_configs(skillConfig_list)
