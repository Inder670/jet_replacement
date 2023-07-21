import json
import os
import shutil
import subprocess
import sys
import argparse

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


def generate_cfg():
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Prepare cci")
    cfg_lines.append(f"GLAUNCH:: prepare_cci {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_cci')} 1")
    cfg_lines.append("$svdb_directory::$svdb_directory::$Input_File::$Dir")
    cfg_lines.append("HEADER END")

    return cfg_lines


def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Prepare cci")
    cfg_lines.append(f"BACK::Prepare-LVS  {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_cci')} 1")
    cfg_lines.append(f"GLAUNCH:: prepare_cci {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_cci')} 1")
    cfg_lines.append("$svdb_directory::$svdb_directory::$Input_File::$Dir")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'prepare_cci.cfg')

    if not os.path.exists(cfg_file_path):
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))
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

    new_loc = os.path.join(def_files_path, 'prepare_lvs.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc


def gen_json(json_loc,project_dir, cfg_loc, def_loc):
    current_step = "prepare_cci"

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

    if current_step in dgui_json:
        print("already there")
    else:
        data = {'prepare_cci': {
            "cfg": f"{cfg_loc}",
            "def": f"{def_loc}",
        }}
        dgui_json.update(data)
        with open(json_loc, 'w') as file:
            json.dump(dgui_json, file, indent=4)
def check_json(json_loc):
    with open(json_loc,'r') as file:
        data = json.load(file)
        if "gen_esd_dev" in data:
            path_to_def = data['gen_esd_dev']['def']
            return path_to_def
        else:
            return None
def mainforward(project_dir, def_path):
    cfg_file_path = save_cfg(project_dir)
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    gen_json(json_loc,project_dir, cfg_file_path, def_path)
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


def mainback(project_dir):
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    with open(json_loc, 'r') as file:
        data = json.load(file)
        for key in data:
            print(f"key: {key}, Value: {data[key]}")

        command = f"dgui -c {data['analyze_lvs']['cfg']} -g  -dir ./ -j ./ --splash -p {project_dir} -d {data['prepare_lvs']['def']}"
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in iter(process.stdout.readline, b''):
            print(line.decode('utf-8').strip())
        sys.exit(0)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir)
    # os.remove(input_file)
    if args.b:
        mainback(project_dir)
    else:
        mainforward(project_dir, def_path)
