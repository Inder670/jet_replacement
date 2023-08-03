import json
import os
import shutil
import subprocess
import sys
import argparse

from PyQt5.QtWidgets import QApplication, QMessageBox

from utilities.utils import *

# Create the parser
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments
parser.add_argument('-i', type=str, help='input file(def file)')
parser.add_argument('-o', type=str, help='output directory')
parser.add_argument('-p', type=str, help='project directory')
parser.add_argument('-b', help='Launch previous gui flag', action='store_true')

# Parse the command-line arguments
args = parser.parse_args()


def search_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list



def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)


    cfg_file_path = os.path.join(cfg_file_dir, 'prepare_esra.cfg')

    return cfg_file_path


def generate_txt_file(file_list):
    txt_lines = []
    for index, file in enumerate(file_list, start=1):
        txt_lines.append(f"$View Files::$File{index}::${os.path.abspath(file)}")

    return txt_lines


def save_txt_file(txt_lines, filename):
    with open(filename, "w") as txt_file:
        txt_file.write("\n".join(txt_lines))


def save_def(input, path):
    path = path.strip('\n')
    def_files_path = os.path.join(path, '.dgui', "def_files")

    if not os.path.exists(def_files_path):
        os.makedirs(def_files_path)

    new_loc = os.path.join(def_files_path, 'prepare_esra.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc


def gen_json(json_loc, project_dir, def_loc):
    if os.path.exists(json_loc) and os.path.getsize(json_loc) > 0:
        print(json_loc)
        with open(json_loc, 'r') as file:
            try:
                dgui_json = json.load(file)
                if args.b:
                    for key in dgui_json:
                        if key != 'Generate-ESD-Files':
                            dgui_json[key]['current_step'] = 0
                        else:
                            dgui_json[key]['current_step'] = 1
                else:
                    pass
                    #
                    # for key in dgui_json:
                    #     if key != 'Prepare-LVS':
                    #         dgui_json[key]['current_step'] = 0
                    #     else:
                    #         dgui_json[key]['current_step'] = 1
            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}
    else:
        dgui_json = {}

    dgui_json['Prepare-ESRA']['def'] = def_loc

    # if dgui_json['Prepare-CCI'] is None:
    #     cfg_data = {'cfg': f"{cfg_loc}"}
    #     dgui_json["Prepare-CCI"] = cfg_data
    with open(json_loc, 'w') as file:
        json.dump(dgui_json, file, indent=4)

def check_json(json_loc):
    with open(json_loc, 'r') as file:
        data = json.load(file)
        if "Prepare-ESRA" in data:
            if 'def' in data['Prepare-ESRA']:
                path_to_def = data['Prepare-ESRA']['def']
                return path_to_def
        else:
            return None

def message_box(message):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.exec_()

def mainforward(project_dir, def_path):
    #Delete lock file
    lock_file_path = os.path.join(project_dir, '.dgui', 'dgui.lock')
    message_center_file = os.path.join(project_dir, '.dgui', 'dgui_message_center.txt')
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
    # if os.path.exists(message_center_file):
    #     os.remove(message_center_file)
    message_box("You are now ready to run the ESRA Simulation")
    # cfg_file_path = save_cfg(project_dir)
    # command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir}"
    #
    # print("Launching DGUI...")
    # print(command)
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    # for line in iter(process.stdout.readline, b''):
    #     print(line.decode('utf-8').strip())
    # # os.system(command)
    # sys.exit(0)


def mainback(project_dir):
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    with open(json_loc, 'r') as file:
        data = json.load(file)

        command = f"dgui -c {data['Generate-ESD-Files']['cfg']} -g  -dir ./ -j ./ --splash -p {project_dir} -d {data['Generate-ESD-Files']['def']}"
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = process.communicate()
        # os.system(command)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    msg_center = check_existing_message_center(project_dir)
    def_path = save_def(input_file, project_dir)
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    gen_json(json_loc, project_dir, def_path)


    # os.remove(input_file)
    if args.b:
        mainback(project_dir)
    else:
        mainforward(project_dir, def_path)