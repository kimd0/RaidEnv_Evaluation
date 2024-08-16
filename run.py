import subprocess
import time
import os
import pandas as pd
import json
from decimal import Decimal

BASE_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_PATH, 'config')
LOG_PATH = os.path.join(BASE_PATH, 'log')
RESULT_PATH = os.path.join(BASE_PATH, 'result')
DEFAULT_CONFIG_FILE = os.path.join(BASE_PATH, 'default_dealer.json')  # for dealer
MMORPG_EXECUTABLE = 'MMORPG.exe'


def run_test(attribute, epi_num):
    for file in os.listdir(CONFIG_PATH):
        file_path = os.path.join(CONFIG_PATH, file)

        if os.path.isfile(file_path) and (attribute in file):
            log_time()
            print("Running with", file)
            run_env(file, epi_num)
            save_result(file)
    log_time()
    print("Test Done")
    return


def generate_config(attribute, start, end, step, target_config, target_agent):
    with open(DEFAULT_CONFIG_FILE, 'r') as file:
        data = json.load(file)

    if target_config == "statusConfig":
        original_value = data['agentConfigs'][target_agent][target_config][attribute]
    elif target_config == "skillConfigs":
        original_value = data['agentConfigs'][target_agent][target_config][0][attribute]

    if isinstance(original_value, list):
        original_value = original_value[0]
    original_value = Decimal(str(original_value))

    new_values = []
    # Convert start, end, step to Decimal
    start = Decimal(str(start))
    end = Decimal(str(end))
    step = Decimal(str(step))

    current = start
    while current <= end:
        if attribute == 'damage':
            new_value = round(original_value * current)
        else:
            new_value = current
        new_values.append([float(new_value)])
        current += step

    log_time()
    print("generating configs : ", new_values)

    for value in new_values:
        new_file_name = f"{attribute}_{value[0]}.json"
        new_file_path = os.path.join(CONFIG_PATH, new_file_name)
        if target_config == "statusConfig":
            data['agentConfigs'][target_agent][target_config][attribute] = value
        elif target_config == "skillConfigs":
            data['agentConfigs'][target_agent][target_config][0][attribute] = value

        with open(new_file_path, 'w') as new_file:
            json.dump(data, new_file, indent=4)
        log_time()
        print(new_file_name, "generated.")


def run_env(config, episode=1000):
    env = os.environ
    newpath = os.path.join(BASE_PATH, 'build') + ';' + env['PATH']
    env['PATH'] = newpath
    config_path = f' --configPath {os.path.join(CONFIG_PATH, config)}'
    log_path = f' --logPath {LOG_PATH}\\'

    process = subprocess.Popen(MMORPG_EXECUTABLE + ' -quit -batchmode -nographics' + config_path + log_path)
    time.sleep(10 + episode / 5)
    while True:
        if check_log(episode):
            process.terminate()
            process.wait()
            return True
        time.sleep(0.01)


def check_log(length=1000):
    sorted_files = sorted([f for f in os.listdir(LOG_PATH)], reverse=True)
    if not sorted_files:
        return False
    log_dir = sorted_files[0]
    file_path = os.path.join(LOG_PATH, log_dir, "gameresult_log.csv")
    gameresult_log = pd.read_csv(file_path, header=None)
    line_count = len(gameresult_log)
    return line_count >= length


def save_result(config):
    log_dir = sorted([f for f in os.listdir(LOG_PATH)], reverse=True)[0]
    old_dir_path = os.path.join(LOG_PATH, log_dir)

    parts = config.split('.')
    result_dir = '.'.join(parts[:-1]) if len(parts) > 1 else parts[0]
    new_dir_path = os.path.join(RESULT_PATH, result_dir)

    os.rename(old_dir_path, new_dir_path)

    old_config_path = os.path.join(CONFIG_PATH, config)
    new_config_path = os.path.join(new_dir_path, config)
    os.rename(old_config_path, new_config_path)
    log_time()
    print("Saved result with", config)


def log_time():
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}]", end=" ")


def make_folders(path_list):
    for path in path_list:
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == '__main__':
    PATH_List = [CONFIG_PATH, LOG_PATH, RESULT_PATH]
    make_folders(PATH_List)

    # generate_config('range', start=3.0, end=12.0, step=0.1, target_config='skillConfigs', target_agent=0)
    # run_test('range', epi_num=300)
    #
    # generate_config('casttime', start=0.0, end=10.0, step=0.1, target_config='skillConfigs', target_agent=0)
    # run_test('casttime', epi_num=300)
    #
    # generate_config('cooltime', start=0.0, end=10.0, step=0.1, target_config='skillConfigs', target_agent=0)
    # run_test('cooltime', epi_num=300)
    #
    # generate_config('damage', start=0.0, end=5.0, step=0.1, target_config='skillConfigs', target_agent=0)
    # run_test('damage', epi_num=300)

    generate_config('healthMax', start=12350, end=52350, step=1000, target_config="statusConfig", target_agent=2)  # default 32,350
    run_test('healthMax', epi_num=10)

    generate_config('armor', start=18476, end=38476, step=500, target_config="statusConfig", target_agent=2)  # default 28,476
    run_test('armor', epi_num=300)

    generate_config('moveSpeed', start=0.3, end=2.0, step=0.05, target_config="statusConfig", target_agent=2)  # default 1
    run_test('moveSpeed', epi_num=300)
