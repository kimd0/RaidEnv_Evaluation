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
                log_dir = self.run_env(file, self.epi_num)
                self.save_result(log_dir, file)
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

        process = subprocess.Popen(command)
        log_dir = self.get_log()

        with tqdm(total=episode, desc="Progress", unit="episode") as pbar:
            previous_length = 0
            while True:
                current_length = self.check_log_length(log_dir)
                pbar.update(current_length - previous_length)  # 진행도 업데이트
                previous_length = current_length

                if current_length >= episode:
                    process.terminate()
                    process.wait()
                    return log_dir

                time.sleep(0.1)

    def check_log_length(self, log_dir):
        file_path = os.path.join(log_dir, "gameresult_log.csv")
        gameresult_log = pd.read_csv(file_path, header=None)
        line_count = len(gameresult_log)
        return line_count

    def get_log(self):
        existing_folders = set(os.listdir(self.log_path))

        while True:
            current_folders = set(os.listdir(self.log_path))
            new_folders = current_folders - existing_folders

            if new_folders:
                new_folder = new_folders.pop()
                new_folder_path = os.path.join(self.log_path, new_folder)
                required_files = {"combat_log.csv", "gameresult_log.csv"}
                while True:
                    if required_files.issubset(set(os.listdir(new_folder_path))):
                        self.log_time()
                        print(f"Log directory: {new_folder_path}")
                        return new_folder_path
                    time.sleep(0.1)

            existing_folders = current_folders
            time.sleep(0.1)

    def save_result(self, log_dir, config):
        old_dir_path = log_dir

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
