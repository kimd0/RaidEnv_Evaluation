import subprocess
import time
import os
import pandas as pd
import argparse
import shutil
from tqdm import tqdm
import platform
import secrets


def parse_args():
    parser = argparse.ArgumentParser('make gstar_config')
    parser.add_argument('--config_path', type=str, default="./configs")
    parser.add_argument('--log_path', type=str, default="./log")
    parser.add_argument('--save_path', type=str, default='./results_rulebased')
    parser.add_argument('--build_exe_path', type=str, default=r'Z:\MMORPG\2024\MA\Build\Build_window_gstar_rule\MMORPG.exe')
    parser.add_argument('--agent_index', type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument('--skill_index', type=int, default=1, choices=[0, 1])
    parser.add_argument('--epi_num', type=int, default=100)
    parser.add_argument('--verbose', type=str, default='info', choices=['info', 'debug'])

    return parser.parse_args()


def log_time():
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}]", end=" ")


class MMORPGTestRunner:
    def __init__(self, args):
        self.config_path = os.path.join(args.config_path)
        self.log_path = args.log_path
        self.result_path = os.path.join(
            args.save_path, f"agent{args.agent_index}_skill{args.skill_index}", os.path.basename(args.config_path))
        self.build_exe_path = args.build_exe_path
        self.slice_index = None
        self.epi_num = args.epi_num
        self.os_type = platform.system().lower()

        self.verbose = args.verbose

        # make folders
        folder_list = [self.log_path, self.result_path]
        self.make_folders(folder_list)

    def run_test(self):

        config_list = sorted(os.listdir(self.config_path), key=lambda x: int(x.split('_')[1].split('.')[0]))
        if isinstance(self.slice_index, int):
            slice_size = len(config_list) // 4
            start = self.slice_index * slice_size
            end = start + slice_size if self.slice_index < 4 - 1 else len(config_list)
            config_list_to_run = config_list[start:end]
        else:
            config_list_to_run = config_list

        self.pbar = tqdm(total=len(config_list_to_run))
        for i, file in enumerate(config_list_to_run):
            run_id = secrets.token_hex(16)
            self.pbar.set_description(f"{file.split('.')[0]} ({run_id})")
            file_path = os.path.join(self.config_path, file)

            if os.path.isfile(file_path):
                if self.verbose == 'debug':
                    log_time()
                log_dir = self.run_env(file, run_id, self.epi_num)
                self.save_result(log_dir, file)
                shutil.rmtree(os.path.dirname(log_dir))
            self.pbar.update(1)
        log_time()
        print("Test Done")

    def run_env(self, config, run_id, episode=100):
        config_path = ['--configPath', os.path.join(self.config_path, config)]
        log_path = ['--logPath', os.path.join(self.log_path, config.split('.')[0] + "_" + run_id)]

        if self.os_type == "linux":
            command = [self.build_exe_path, '-quit', '-batchmode', '-nographics']
            command += config_path + log_path

        elif self.os_type == "windows":
            command = self.build_exe_path + ' -quit -batchmode -nographics'
            for arg in config_path + log_path:
                command += ' ' + arg
            command += ' --maEvalEpisodeLimit ' + str(episode)
        else:
            raise ValueError("Unsupported OS type, only support windows and linux")

        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_dir = self.get_log(log_path[-1], self.verbose)

        while True:
            current_length = self.check_log_length(log_dir)
            self.pbar.set_postfix(progress=f"{current_length/episode*100:.1f}%")  # 진행도 업데이트

            if current_length >= episode:
                process.terminate()
                process.wait()
                return log_dir

            time.sleep(0.1)

    @staticmethod
    def check_log_length(log_dir):
        file_path = os.path.join(log_dir, "gameresult_log.csv")
        try:
            gameresult_log = pd.read_csv(file_path, header=None)
            line_count = len(gameresult_log)
        except FileNotFoundError:
            line_count = 0
        except pd.errors.EmptyDataError:
            line_count = 0
        return line_count

    @staticmethod
    def get_log(log_path, verbose):
        while True:
            try:
                existing_folders = set(os.listdir(log_path))
                break
            except FileNotFoundError:
                time.sleep(0.1)

        while True:
            current_folders = set(os.listdir(log_path))
            new_folders = current_folders - existing_folders

            if new_folders:
                new_folder = new_folders.pop()
                new_folder_path = os.path.join(log_path, new_folder)
                required_files = {"combat_log.csv", "gameresult_log.csv"}
                while True:
                    current_files = set(os.listdir(new_folder_path))
                    if required_files.issubset(current_files):
                        all_files_valid = True
                        for file in required_files:
                            file_path = os.path.join(new_folder_path, file)
                            try:
                                with open(file_path, 'r') as f:
                                    if f.readline():
                                        continue
                                    else:
                                        all_files_valid = False
                                        break
                            except IOError:
                                all_files_valid = False
                                break

                        if all_files_valid:
                            if verbose == 'debug':
                                log_time()
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
        old_config_path = os.path.join(self.config_path, config)
        new_config_path = os.path.join(new_dir_path, config)

        while True:
            try:
                shutil.move(src=old_dir_path, dst=new_dir_path)
                shutil.copy(src=old_config_path, dst=new_config_path)
                break
            except Exception as e:
                time.sleep(0.1)

        if self.verbose == 'debug':
            log_time()
            print("Saved result with", config)

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
