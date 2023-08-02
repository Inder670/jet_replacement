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

def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Genearte Tech Files")
    cfg_lines.append(f"GLAUNCH:: gen_tech_files {os.path.join(os.path.dirname(sys.argv[0]), 'gen_tech_files')} 1")
    cfg_lines.append("$esd_dev-and-tech_files*::$cci directory file::$Input_File::$Dir")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'gen_tech_files.cfg')

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

    new_loc = os.path.join(def_files_path, 'gen_esd_dev.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc


def gen_json(json_loc, project_dir, cfg_loc, def_loc):
    if os.path.exists(json_loc) and os.path.getsize(json_loc) > 0:
        with open(json_loc, 'r') as file:
            try:
                dgui_json = json.load(file)
                if args.b:
                    for key in dgui_json:
                        if key != 'Prepare-CCI':
                            dgui_json[key]['current_step'] = 0
                        else:
                            dgui_json[key]['current_step'] = 1
                else:

                    for key in dgui_json:
                        if key != 'Generate-Tech-Files':
                            dgui_json[key]['current_step'] = 0
                        else:
                            dgui_json[key]['current_step'] = 1
            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}
    else:
        dgui_json = {}

    dgui_json['Generate-esd_dev']['def'] = def_loc
    if not 'cfg' in dgui_json['Generate-Tech-Files']:
        cfg_data = f"{cfg_loc}"
        if not args.b:
            dgui_json["Generate-Tech-Files"]['cfg'] = cfg_data
    with open(json_loc, 'w') as file:
        json.dump(dgui_json, file, indent=4)
def check_json(json_loc):
    with open(json_loc, 'r') as file:
        data = json.load(file)
        if "Generate-Tech-Files" in data:
            if 'def' in data['Generate-Tech-Files']:
                path_to_def = data['Generate-Tech-Files']['def']
                return path_to_def
        else:
            return None

def mainforward(project_dir):

    check_json_for_existing_def = check_json(json_loc)
    if check_json_for_existing_def is not None:
        def_file = f"-d {check_json_for_existing_def}"
    else:
        def_file = ''

    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"

    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = process.communicate()
    print(process.returncode)
    # os.system(command)
    on_subprocess_completed(stdout, stderr, process.returncode)


def on_subprocess_completed(stdout, stderr, returncode):
    # Process the results after the subprocess completes.
    if returncode == 0:
        print("Subprocess completed successfully.")
        print("Standard Output:")
        print(stdout.decode())
    else:
        print("Subprocess failed.")
        print("Error Output:")
        print(stderr.decode())
    print(f"Return Code: {returncode}")
    sys.exit(returncode)


def mainback(project_dir):
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    with open(json_loc, 'r') as file:
        data = json.load(file)

        command = f"dgui -c {data['Prepare-CCI']['cfg']} -g  -dir ./ -j ./ --splash -p {project_dir} -d {data['Prepare-CCI']['def']}"
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = process.communicate()
        print(process.returncode)
        # os.system(command)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir)
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')

    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, project_dir, cfg_file_path, def_path)
    # os.remove(input_file)
    if args.b:
        mainback(project_dir)
    else:
        mainforward(project_dir)
