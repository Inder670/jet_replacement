import json
import os
import subprocess
import sys
import argparse
import shutil

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


def save_def(input, path):
    path = path.strip('\n')
    def_files_path = os.path.join(path, '.dgui', "def_files")

    if not os.path.exists(def_files_path):
        os.makedirs(def_files_path)

    new_loc = os.path.join(def_files_path, 'project_dir.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc


def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)
    print(cfg_file_dir)
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Analyze LVS")
    cfg_lines.append(
        f"GLAUNCH:: Analyze-LVS {os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'analyze_lvs')} 1")
    cfg_lines.append("$lvs_setup::$Calibre.run file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$sourceme file::$Input_File::$File")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'analyze_lvs.cfg')
    if not os.path.exists(cfg_file_path):
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return cfg_file_path


def find_project_dir(input_file):
    with open(input_file, 'r') as file:
        for line in file:
            print(line)
            tokens = line.split('::')
            if tokens[1] == "$Directory":
                path = tokens[2].strip('$')
                print(f"Token found : {path}")
            break
    return path


def gen_json(json_loc,project_dir, cfg_loc, def_loc):

    if os.path.exists(json_loc) and os.path.getsize(json_loc) > 0:
        with open(json_loc, 'r') as file:
            try:
                dgui_json = json.load(file)
            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}
    else:
        dgui_json = {}

    if dgui_json:
        pass
    else:
        data = {
            'Analyze-LVS':{
                'cfg':f'{cfg_loc}',
                'current_step': 1
            },
            'Prepare-LVS': {
                'current_step': 0
            },
            'Prepare-CCI': {
                'current_step': 0
            },
            'Generate-esd_dev': {
                'current_step': 0
            },
            'Generate-Tech-Files': {
                'current_step': 0
            },
            'Generate-ESD-Files': {
                'current_step': 0
            }
        }

        dgui_json.update(data)
        with open(json_loc, 'w') as file:
            json.dump(dgui_json, file, indent=4)


def check_json(json_loc):
    with open(json_loc, 'r') as file:
        data = json.load(file)
        if "Analyze-LVS" in data:
            if 'def' in data['Analyze-LVS']:
                path_to_def = data['Analyze-LVS']['def']
                return path_to_def
        else:
            return None


def mainforward(def_path, project_dir):

    check_json_for_existing_def = check_json(json_loc)
    if check_json_for_existing_def is not None:
        def_file = f"-d {check_json_for_existing_def}"
    else:
        def_file = ''

    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"

    print("Launching DGUI...")
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        print(line.decode('utf-8').strip())
    # os.system(command)
    sys.exit(0)


def mainback():
    pass


if __name__ == "__main__":
    input_file = args.i
    project_dir = find_project_dir(input_file).strip('\n')

    # Copy default file to project structure
    def_path = save_def(input_file, project_dir)
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, project_dir, cfg_file_path, def_path)
    # os.remove(input_file)
    if args.b:
        mainback()
    else:
        print('B is not true')
        mainforward(def_path, project_dir)
