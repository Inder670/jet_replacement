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
    cfg_lines.append("TITLE:: Prepare esra")
    cfg_lines.append(f"GLAUNCH:: prepare_esra {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_esra')} 1")
    cfg_lines.append("$technology_files*::$itf file::$Input_File::$File")
    cfg_lines.append("$technology_files*::$map file::$Input_File::$File")
    cfg_lines.append("$MOS Max Stress Limits*::$PLACEHOLDER::$Input_File::$File")
    cfg_lines.append("$CDM Stress Current*::$Direct Entry::$String::$ANY")
    cfg_lines.append("$CDM Stress Current*::$Technology::$String::$ANY")
    cfg_lines.append("$Chip Bond::$Chip Bond*::$String::$Flip-Chip Wire-Bond")
    cfg_lines.append("$Esd Grid*::$NX::$String::$ANY")
    cfg_lines.append("$Esd Grid*::$NY::$String::$ANY")
    cfg_lines.append("$Die Size*::$X::$String::$ANY")
    cfg_lines.append("$Die Size*::$Y::$String::$ANY")
    cfg_lines.append("$em_store/preem_store*::$preem_store::$String::$True False")
    cfg_lines.append("$em_store/preem_store*::$em_store::$String::$True False")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'prepare_esra.cfg')

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

    new_loc = os.path.join(def_files_path, 'gen_esd_files.txt')
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
                        if key != 'Generate-Tech-Files':
                            dgui_json[key]['current_step'] = 0
                        else:
                            dgui_json[key]['current_step'] = 1
                else:

                    for key in dgui_json:
                        if key != 'Prepare-ESRA':
                            dgui_json[key]['current_step'] = 0
                        else:
                            dgui_json[key]['current_step'] = 1
            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}

    else:
        dgui_json = {}

    dgui_json['Generate-ESD-Files']['def'] = def_loc

    if not 'cfg' in dgui_json['Prepare-ESRA']:
        cfg_data = f"{cfg_loc}"
        if not args.b:
            dgui_json["Prepare-ESRA"]['cfg'] = cfg_data
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
def mainforward(project_dir, def_path):
    cfg_file_path = save_cfg(project_dir)
    check_json_for_existing_def = check_json(json_loc)
    if check_json_for_existing_def is not None:
        def_file = f"-d {check_json_for_existing_def}"
    else:
        def_file = ''
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir}"

    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = process.communicate()
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

        command = f"dgui -c {data['Generate-Tech-Files']['cfg']} -g  -dir ./ -j ./ --splash -p {project_dir} -d {data['Generate-Tech-Files']['def']}"
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = process.communicate()
        # os.system(command)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir)
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc,project_dir, cfg_file_path, def_path)
    # os.remove(input_file)
    if args.b:
        mainback(project_dir)
    else:
        mainforward(project_dir, def_path)