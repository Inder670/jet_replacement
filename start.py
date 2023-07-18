import os
import subprocess
import sys
import argparse
import shutil
# Create the parser
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments
parser.add_argument('input' ,type=str, help='First argument')
parser.add_argument('output' ,type=str, help='Second argument')

# Parse the command-line arguments
args = parser.parse_args()

def search_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def save_def(input,path):
    path = path.strip('\n')
    def_files_path = os.path.join(path, 'dgui', "def_files")

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
    cfg_file_dir = os.path.join(project_dir, 'dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Analyze LVS")
    cfg_lines.append(f"GLAUNCH:: Analyze-LVS {os.path.join(os.path.dirname(sys.argv[0]), 'analyze_lvs')} 1")
    cfg_lines.append("$lvs_setup::$Calibre.run file::$Input_File::$File")
    cfg_lines.append("$lvs_setup::$sourceme file::$Input_File::$File")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir,'analyze_lvs.cfg')
    if not os.path.exists(cfg_file_path):

        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return cfg_file_path

def save_txt_file(txt_lines, filename):
    with open(filename, "w") as txt_file:
        txt_file.write("\n".join(txt_lines))
def find_project_dir(input_file):
    with open(args.input, 'r') as file:
        for line in file:
            print(line)
            tokens=line.split('::')
            if tokens[1] == "$Directory":
                path = tokens[2].strip('$')
                print(f"Token found : {path}")
            break
    return path
if __name__ == "__main__":

    # Prompt the user to enter a directory path
    input_file = args.input
    project_dir = find_project_dir(input_file)
    # Copy default file to project structure
    def_path = save_def(input_file,project_dir)
    # os.remove(input_file)

    cfg_file_path = save_cfg(project_dir)
    print(cfg_file_path)


    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash"

    print("Launching DGUI...")
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        print(line.decode('utf-8').strip())
    process.wait()
    # os.system(command)
    sys.exit(0)