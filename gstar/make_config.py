import json
import copy


def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)


def read_readme(file_name):
    with open(file_name, 'r') as f:
        data = f.read()
    return data


def write_readme(file_name, data):
    with open(file_name, 'a') as f:
        f.write(data)


if __name__ == "__main__":
    # read json file
    source_file_name = 'C:\\Users\\KKGB\\Desktop\\git_local_storage\\RaidEnv_PlayTesting\\MyTest\\config_generator\\default_config.json'
    data = read_json(source_file_name)

    playerConfig = {
        0: ["Fireball", "Pyroblast"],
    }

    skillConfig = {
        "cooltime": [0.5, 6.5],
        "range": [6, 13],
        "casttime": [0, 3.5],
        "damage": [9000, 16000],
    }

    i = 0
    for coolvalue in skillConfig["cooltime"]:
        for rangevalue in skillConfig["range"]:
            for castvalue in skillConfig["casttime"]:
                for damagevalue in skillConfig["damage"]:
                    new_data = copy.deepcopy(data)
                    agentConfigs = new_data["agentConfigs"]
                    skillConfigs = agentConfigs[0]["skillConfigs"]

                    skillConfigs[0]["cooltime"] = [coolvalue]
                    skillConfigs[0]["range"] = [rangevalue]
                    skillConfigs[0]["casttime"] = [castvalue]
                    skillConfigs[0]["damage"] = [damagevalue]

                    readme_data = f'{i:05} - range: {rangevalue}, cool: {coolvalue}, cast: {castvalue}, damage: {damagevalue} <br/> \n'

                    # write json file
                    target_file_name = f'C:\\Users\\KKGB\\Desktop\\git_local_storage\\RaidEnv_PlayTesting\\experiments\\exp_01\\test_configs\\config_{i:05}.json'
                    write_json(target_file_name, new_data)
                    write_readme('C:\\Users\\KKGB\\Desktop\\git_local_storage\\RaidEnv_PlayTesting\\experiments\\exp_01\\test_configs\\README.md', readme_data)
                    i += 1
