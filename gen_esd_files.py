import json
import os
import shutil
import subprocess
import sys
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
    cfg_lines.append("TITLE:: Prepare esra")
    cfg_lines.append(f"GLAUNCH:: Finish(prepare_esra) {os.path.join(os.path.dirname(sys.argv[0]), 'prepare_esra')} 1")
    cfg_lines.append("$technology_files*::$itf file::$Input_File::$File")
    cfg_lines.append("$technology_files*::$map file::$Input_File::$File")
    cfg_lines.append("$MOS Max Stress Limits*::$Values::$Table::$mv.dv.dv,ww.wa.we.re->3x4")
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
        add_to_message_center(project_dir,f"-> cfg saved: prepare_esra.cfg")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))
    return cfg_file_path

def main(project_dir, cfg_file_path,json_loc):
    def_file = get_def_file(json_loc, "Prepare-ESRA")
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"

    print(command)
    execute_subprocess(command)


if __name__ == "__main__":
    # Prompt the user to enter a directory path
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir, "gen_esd_files.txt")
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, cfg_file_path, def_path, "Generate-ESD-Files", "Prepare-ESRA")
    # os.remove(input_file)
    main(project_dir, cfg_file_path,json_loc)