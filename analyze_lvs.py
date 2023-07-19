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
    cfg_lines.append("TITLE:: Prepare LVS")
    cfg_lines.append(f"GLAUNCH:: Prepare-LVS {os.path.join(os.path.dirname(sys.argv[0]),'prepare_lvs')} 1")
    cfg_lines.append("$lvs_setup::$circuit file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$layout file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$Edtext file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$LVS cal file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$LVS cellmap file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$cell list file::$Input_File::$File")
    cfg_lines.append("HEADER END")


    return cfg_lines

def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)

    cfg_lines = []
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Prepare LVS")
    cfg_lines.append(f"GLAUNCH:: Prepare-LVS {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_lvs')} 1")
    cfg_lines.append("$lvs_setup::$circuit file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$layout file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$Edtext file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$LVS cal file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$LVS cellmap file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$cell list file::$Input_File::$File")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'analyze_lvs.cfg')

    if not os.path.exists(cfg_file_path):
        print("UETG")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return cfg_file_path
    # with open(filename, "w") as cfg_file:
    #     cfg_file.write("\n".join(cfg_lines))

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

    new_loc = os.path.join(def_files_path, 'analyze_lvs.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occured: {e}")

    return new_loc

def gen_json(project_dir, cfg_loc, def_loc):
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    current_step = "analyze_lvs"

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
        data = {'analyze_lvs': {
            "cfg": f"{cfg_loc}",
            "def": f"{def_loc}",
        }}
        dgui_json.update(data)
        with open(json_loc, 'w') as file:
            json.dump(dgui_json, file, indent=4)

if __name__ == "__main__":

    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    print(project_dir)
    # Copy default file to project structure
    def_path = save_def(input_file,project_dir)
    # os.remove(input_file)
    # cfg_filename = os.path.abspath(args.output)

    cfg_file_path = save_cfg(project_dir)
    gen_json(project_dir,cfg_file_path,def_path)
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir}"
    print(command)
    print("Launching DGUI...")
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        print(line.decode('utf-8').strip())
    process.wait()
    # os.system(command)
    sys.exit(0)