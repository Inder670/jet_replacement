import json
import logging
import os
import shutil
import subprocess
import sys
from time import sleep


def gen_json(json_loc, cfg_loc, def_loc, current_step, next_step):
    if os.path.exists(json_loc) and os.path.getsize(json_loc) > 0:
        with open(json_loc, 'r') as file:
            try:
                dgui_json = json.load(file)
                for key in dgui_json:
                    if next_step is None:
                        pass
                    elif key != next_step:
                        dgui_json[key]['current_step'] = 0
                    else:
                        dgui_json[key]['current_step'] = 1

            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}

    else:
        dgui_json = {}

    dgui_json[current_step]['def'] = def_loc
    if cfg_loc is not None:
        if not 'cfg' in dgui_json[next_step]:
                cfg_data = f"{cfg_loc}"
                dgui_json[next_step]['cfg'] = cfg_data

        with open(json_loc, 'w') as file:
            json.dump(dgui_json, file, indent=4)
def on_subprocess_completed(stdout, stderr, returncode):
    # Process the results after the subprocess completes.
    if returncode == 0:
        print("Subprocess completed successfully.")
        print("Standard Output:")
        print(stdout.decode())
    else:
        print("Subprocess failed.")
        print("Error Output:")
        print(stderr)
    sys.exit(returncode)

def setup_logger(log_file, name):
    # Create the directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if the log file exists
    file_exists = os.path.exists(log_file)

    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='a' if file_exists else 'w')

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Create a formatter and attach it to the handlers
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def add_to_message_center(project_dir, text_to_append):
    try:
        # Open the file in append mode
        message_center = os.path.join(project_dir, '.dgui', 'dgui_message_center.txt')
        if not os.path.exists(message_center):
            with open(message_center, 'w') as file:
                file.write(f'{text_to_append}\n')
        else:
            with open(message_center, 'a') as file:
                file.write(f"{text_to_append}\n")
                print("MESSGAGE APPENEDED")
    except Exception as e:
        print("An error occurred:", str(e))

def check_existing_message_center(project_dir):
    dgui_dir = os.path.join(project_dir, '.dgui')
    dgui_dir_exists = os.path.exists(dgui_dir)
    messages = []
    if not dgui_dir_exists:
        os.makedirs(dgui_dir)

    msg_center_path = os.path.join(dgui_dir, 'dgui_message_center.txt')
    msg_cntr_exists = os.path.exists(msg_center_path)
    print(os.path.join(dgui_dir, 'dgui_message_center.txt'))
    if not msg_cntr_exists:
        with open(msg_center_path, 'w') as file:
            file.write('.dgui directory created\n')
        return ['.dgui directory created']
    else:
        with open(msg_center_path, 'r') as file:
            print(type(file))
            for line in file:
                messages.append(line)
            return messages

def save_def(input, path, name):
    path = path.strip('\n')
    def_files_path = os.path.join(path, '.dgui', "def_files")

    if not os.path.exists(def_files_path):
        os.makedirs(def_files_path)

    new_loc = os.path.join(def_files_path, name)
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc

def save_message_center(project_dir, msg_center):
    with open(os.path.join(project_dir, '.dgui', 'dgui_message_center.txt'), 'w') as file:
        cleaned_strings = [s.strip() for s in msg_center if s.strip()]
        for item in cleaned_strings:
            if item.startswith("->"):
                file.write(f"{item}\n")  # Adding a newline character at the end of eac
            else:
                file.write(f"-> {item}\n")  # Adding a newline character at the end of eac

def check_json(json_loc,step):
    with open(json_loc, 'r') as file:
        data = json.load(file)
        if step in data:
            if 'def' in data[step]:
                path_to_def = data[step]['def']
                return path_to_def
        else:
            return None


def execute_subprocess(command):
    # sleep(5)

    process = subprocess.Popen(command, shell=True)
    print("Script Finished")

    sys.exit(0)
    # while True:
    #     output_line = process.stdout.readline()
    #     if not output_line:
    #         break  # No more stdout output
    #     print(output_line.decode('utf-8'), end='')
    #
    # # Capture stderr using communicate()
    #
    #
    # _, stderr_output = process.communicate()
    #
    # if stderr_output:
    #     print(stderr_output.decode('utf-8'))

    # stdout, stderr = process.communicate()
    # on_subprocess_completed(stdout, stderr, process.returncode)

def get_def_file(json_loc, step):
    check_if_exists = check_json(json_loc, step)

    if check_if_exists is not None:
        def_file = f"-d {check_if_exists}"
    else:
        def_file = ''
    return def_file
