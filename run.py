import subprocess
import time
import os
import pandas as pd
import json
from decimal import Decimal, getcontext

def run_test():
    config_path = r'C:\Users\cilab\Desktop\ptester\config'
    for file in os.listdir(config_path):
        file_path = os.path.join(config_path, file)

        if os.path.isfile(file_path):
            log_time()
            print("Running with", file)
            run_env(file, 1000)
            save_result(file)
    log_time()
    print("Test Done")
    return

def generate_config(attribute, start, end, step):
    with open("default.json", 'r') as file:
        data = json.load(file)

    original_value = data['agentConfigs'][0]['skillConfigs'][0][attribute]
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
    config_path = r'C:\Users\cilab\Desktop\ptester\config'
    for value in new_values:
        new_file_name = f"{attribute}_{value[0]}.json"
        new_file_path = os.path.join(config_path, new_file_name)
        data['agentConfigs'][0]['skillConfigs'][0][attribute] = value

        with open(new_file_path, 'w') as new_file:
            json.dump(data, new_file, indent=4)
        log_time()
        print(new_file_name, "generated.")

def run_env(config, episode=1000):
    env = os.environ
    newpath = r'C:\Users\cilab\Desktop\ptester\build;'+env['PATH']
    env['PATH'] = newpath
    config_path = ' --configPath C:/Users/cilab/Desktop/ptester/config/' + config
    log_path = ' --logPath C:/Users/cilab/Desktop/ptester/log/'

    process = subprocess.Popen('MMORPG.exe -quit -batchmode -nographics' + config_path + log_path)
    time.sleep(100)
    while True:
        if check_log(episode):
            process.terminate()
            process.wait()
            return True
        time.sleep(1)

def check_log(length=1000):
    log_path = r'C:\Users\cilab\Desktop\ptester\log'
    sorted_files = sorted([f for f in os.listdir(log_path)], reverse=True)
    if not sorted_files:
        return False
    log_dir = sorted_files[0]
    file_path = os.path.join(log_path, log_dir, "gameresult_log.csv")
    gameresult_log = pd.read_csv(file_path, header=None)
    line_count = len(gameresult_log)
    return line_count >= length

def save_result(config):
    log_path = r'C:\Users\cilab\Desktop\ptester\log'
    log_dir = sorted([f for f in os.listdir(log_path)], reverse=True)[0]
    old_dir_path = os.path.join(log_path, log_dir)

    result_path = r'C:\Users\cilab\Desktop\ptester\result'
    parts = config.split('.')
    result_dir = '.'.join(parts[:-1]) if len(parts) > 1 else parts[0]
    new_dir_path = os.path.join(result_path, result_dir)

    os.rename(old_dir_path, new_dir_path)

    config_path = r'C:\Users\cilab\Desktop\ptester\config'
    old_config_path = os.path.join(config_path, config)
    new_config_path = os.path.join(new_dir_path, config)
    os.rename(old_config_path, new_config_path)
    log_time()
    print("Saved result with", config)

def log_time():
    now = time
    print("["+now.strftime('%Y-%m-%d %H:%M:%S')+"]", end=" ")

if __name__ == '__main__':
    generate_config('range', 3.0, 12.0, 0.1)
    run_test()

    generate_config('casttime', 0.0, 10.0, 0.1)
    run_test()

    generate_config('cooltime', 0.0, 10.0, 0.1)
    run_test()

    generate_config('damage', 0.0, 5.0, 0.1)
    run_test()