#!/bin/python3

import argparse
from utilities.variables import *
from PyQt5.QtWidgets import QApplication, QMessageBox
from utilities.utils import *

# Create the parser
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments
parser.add_argument('-i', type=str, help='input file(def file)')
parser.add_argument('-p', type=str, help='project directory')

# Parse the command-line arguments
args = parser.parse_args()

message_center_logger = setup_logger(os.path.join(args.p, message_center), message_center)
saved_files_logger = setup_logger(os.path.join(args.p, saved_files),saved_files)

def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)


    cfg_file_path = os.path.join(cfg_file_dir, 'prepare_esra.cfg')

    return cfg_file_path

def message_box(message):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.exec_()

def main(project_dir):
    #Delete lock file
    lock_file_path = os.path.join(project_dir, '.dgui', 'dgui.lock')
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
    message_box("You are now ready to run the ESRA Simulation")

if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir, 'prepare_esra.txt')
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    gen_json(json_loc, None , def_path, "Prepare-ESRA", None)
    # os.remove(input_file)
    main(project_dir)