
import argparse
from utilities.utils import *

# Create the parser
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments
parser.add_argument('-i', type=str, help='input file(def file)')
parser.add_argument('-o', type=str, help='output directory')
parser.add_argument('-p', type=str, help='project directory')

# Parse the command-line arguments
args = parser.parse_args()


def save_cfg(project_dir):
    project_dir = project_dir.strip('\n')
    cfg_file_dir = os.path.join(project_dir, '.dgui', 'config_files')
    if not os.path.exists(cfg_file_dir):
        os.makedirs(cfg_file_dir)

    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Prepare LVS")
    cfg_lines.append(f"GLAUNCH:: Next(Prepare-LVS) prepare_lvs 1")
    cfg_lines.append("$lvs_setup*::$circuit file::$Input_File::$File::$TXT: HEHEHEHE")
    cfg_lines.append("$lvs_setup*::$layout file::$Input_File::$File::$TXT: HEHEHEHE")
    cfg_lines.append("$lvs_setup*::$Edtext file::$Input_File::$File")
    cfg_lines.append("$lvs_setup*::$LVS cal file::$Input_File::$File")
    cfg_lines.append("$lvs_setup*::$LVS cellmap file::$Input_File::$File")
    cfg_lines.append("$lvs_setup*::$cell list file::$Input_File::$File")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'prepare_lvs.cfg')

    if not os.path.exists(cfg_file_path):
        add_to_message_center(project_dir,f"-> cfg saved: prepare_lvs.cfg")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return cfg_file_path

def main(project_dir, cfg_file_path,json_loc):
    def_file = get_def_file(json_loc, "Prepare-LVS")
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"
    print("Launching DGUI...")
    execute_subprocess(command)

if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir, "analyze_lvs.txt")
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, cfg_file_path, def_path, "Analyze-LVS", "Prepare-LVS")
    # os.remove(input_file)

    main(project_dir,cfg_file_path,json_loc)
