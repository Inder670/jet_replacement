#!/global/sys_signoff/users/inder/pycharmprojects/jet_replacement/venv/bin/python

import argparse
import os
from utilities.utils import *

DEFAULT_FILE_NAME = 'proj_dir.txt'

CONFIG_FILE_NAME = 'proj_dir.cfg'

def save_cfg():
    def_file_loc = os.path.join(os.getcwd(), DEFAULT_FILE_NAME)
    cfg_file_loc = os.path.join(os.getcwd(), CONFIG_FILE_NAME)
    cfg_lines = []
    def_lines = []

    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Project Directory")
    cfg_lines.append("GLAUNCH:: Start-Setup start.py 1")
    cfg_lines.append("$Setup::$Project-Directory::$Input_File::$Dir")
    def_lines.append(f"$Setup::$Project-Directory::${os.getcwd()}")
    cfg_lines.append("HEADER END")

    with open(cfg_file_loc, 'w') as cfg_file:
        cfg_file.write('\n'.join(cfg_lines))

    with open(def_file_loc, 'w') as def_file:
        def_file.write('\n'.join(def_lines))

    return cfg_file_loc, def_file_loc


def gen_def(proj_dir):
        def_file_loc = os.path.join(os.getcwd(), DEFAULT_FILE_NAME)
        def_lines = []

        def_lines.append(f"$Setup::$Project-Directory::${os.path.abspath(proj_dir)}")


        with open(def_file_loc, 'w') as def_file:
            def_file.write('\n'.join(def_lines))

        return def_file_loc
def launch_dgui(args):
    # 1. generate configuration file and save it to cwd
    # 2. generate def file with project directory set to cwd with abs path and save it to cwd
    # 3. launch dgui and delete cfg and def file in start.py

    cfg_file_path, def_file_path = save_cfg()

    command = f"dgui -c {cfg_file_path} -g -dir {os.getcwd()} --splash -d {def_file_path}"
    execute_subprocess(command)

def start_setup(args):
    # 1. create a def file containing user provided project directory, save it to cwd and pass it to start.py
    # 2.start.py should delete the def file after extracting the proejct directory from it and initiate setup
    def_file_path = gen_def(args.proj_dir)
    command = f'start.py -i {def_file_path}'
    print("EXECUTING")
    execute_subprocess(command)

def main(args):
    if args.batch:
        batch_file = os.path.join(os.getcwd(), '.batch')
        with open(batch_file, 'w') as file:
            file.write('')
            print("batch file created in ", batch_file)
    if args.proj_dir == os.getcwd() and not os.path.exists(os.path.join(os.getcwd(), '.dgui')):
        if args.batch:
            print("Error: To run in batch mode, please provide the project directory using: --proj_dir <project directory>\n"
                  "Alternatively, please launch this program from a directory containing existing project")
            sys.exit(0)
        print("project directory is ", os.getcwd())
        launch_dgui(args)
    else:
        start_setup(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ESRA SETUP TOOL ARGUMENTS')

    # Add arguments
    parser.add_argument('-i', type=str, help='input file(def file)')
    parser.add_argument('-o', type=str, help='output directory')
    parser.add_argument('-p', '--proj_dir', help='Project Directory', default=os.getcwd())
    parser.add_argument('-b','--batch', help="Run in batch mode", default=False, action='store_true')

    # Parse the command-line arguments
    args = parser.parse_args()
    main(args)