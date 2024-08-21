import subprocess
import time
import os
import pandas as pd
import argparse
import shutil
from tqdm import tqdm
import platform


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--config_path', type=str, default="./config/dealer_skill1")
    parser.add_argument('--log_path', type=str, default="./log")
    parser.add_argument('--build_exe_path', type=str, default='/app/build_linux/MMORPG.x86_64')
    parser.add_argument('--slice_index', type=int, default=0)
    parser.add_argument('--epi_num', type=int, default=100)

    return parser.parse_args()


class MMORPGTestRunner:
    def __init__(self, args):
        self.config_path = args.config_path
        self.log_path = args.log_path
        self.result_path = os.path.join("/result", args.config_path.split("/")[2])
        self.build_exe_path = args.build_exe_path
        self.slice_index = args.slice_index
        self.epi_num = args.epi_num
        self.os_type = platform.system().lower()

        # make folders
        folder_list = [self.log_path, self.result_path]
        self.make_folders(folder_list)

    def run_test(self):

        config_list = sorted(os.listdir(self.config_path))
        slice_size = len(config_list) // 4
        start = self.slice_index * slice_size
        end = start + slice_size if self.slice_index < 4 - 1 else len(config_list)

        for file in tqdm(config_list[start:end]):
            file_path = os.path.join(self.config_path, file)

            if os.path.isfile(file_path):
                self.log_time()
                print("Running with", file)
                self.run_env(file, self.epi_num)
                self.save_result(file)
        self.log_time()
        print("Test Done")

    def run_env(self, config, episode=100):

        config_path = ['--configPath', os.path.join(self.config_path, config)]
        log_path = ['--logPath', self.log_path]

        if self.os_type == "linux":
            command = [self.build_exe_path, '-quit', '-batchmode', '-nographics']
            command += config_path + log_path

        elif self.os_type == "windows":
            env = os.environ
            newpath = "../build" + ';' + env['PATH']
            env['PATH'] = newpath
            command = 'MMORPG.exe' + ' -quit -batchmode -nographics'
            for arg in config_path + log_path:
                command += ' ' + arg
        else:
            raise ValueError("Unsupported OS type, only support windows and linux")

        # window : MMORPG.exe # linux : MMORPG.x86_64
        process = subprocess.Popen(command)
        time.sleep(10 + episode / 5)
        while True:
            if self.check_log(episode):
                process.terminate()
                process.wait()
                return True
            time.sleep(0.1)

    def check_log(self, length):
        sorted_files = sorted([f for f in os.listdir(self.log_path)], reverse=True)
        if not sorted_files:
            return False
        log_dir = sorted_files[0]
        file_path = os.path.join(self.log_path, log_dir, "gameresult_log.csv")
        gameresult_log = pd.read_csv(file_path, header=None)
        line_count = len(gameresult_log)
        return line_count >= length

    def save_result(self, config):
        log_dir = sorted([f for f in os.listdir(self.log_path)], reverse=True)[0]
        old_dir_path = os.path.join(self.log_path, log_dir)

        parts = config.split('.')
        result_dir = '.'.join(parts[:-1]) if len(parts) > 1 else parts[0]
        new_dir_path = os.path.join(self.result_path, result_dir)

        os.rename(old_dir_path, new_dir_path)

        old_config_path = os.path.join(self.config_path, config)
        new_config_path = os.path.join(new_dir_path, config)
        shutil.copy(old_config_path, new_config_path)
        self.log_time()
        print("Saved result with", config)

    def log_time(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now}]", end=" ")

    def make_folders(self, path_list):
        for path in path_list:
            if not os.path.exists(path):
                os.makedirs(path)


if __name__ == '__main__':
    args = parse_args()
    # Initialize the test runner
    test_runner = MMORPGTestRunner(args)
    # Run the test
    test_runner.run_test()
