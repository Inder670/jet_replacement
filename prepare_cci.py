#!/global/sys_signoff/users/inder/pycharmprojects/jet_replacement/venv/bin/python


import argparse
from utilities.utils import *
from utilities.variables import *

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
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Generate ESD_Dev")
    cfg_lines.append(f"GLAUNCH:: Next(Generate-ESD-Dev) gen_esd_dev.py 0")
    cfg_lines.append("$Esd_Dev-File::$clamp rule file::$Input_File::$File")
    cfg_lines.append("HEADER END")
    cfg_file_path = os.path.join(cfg_file_dir, 'gen_esd_dev.cfg')

    if not os.path.exists(cfg_file_path):
        message_center_logger.info(f"-> cfg saved: gen_esd_dev.cfg")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))
    return cfg_file_path

def main(project_dir, cfg_file_path,json_loc):
    def_file = get_def_file(json_loc, "Generate-esd_dev")
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"

    print("Launching DGUI...")
    print(command)
    execute_subprocess(command)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir, "prepare_cci.txt")
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, cfg_file_path, def_path, "Prepare-CCI", "Generate-esd_dev")
    main(project_dir, cfg_file_path,json_loc)
