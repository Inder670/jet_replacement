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
    cfg_lines.append("TITLE:: Generate esd files")
    cfg_lines.append(f"GLAUNCH:: Next(generate_esd_files) {os.path.join(os.path.dirname(sys.argv[0]),'gen_esd_files')} 1")
    cfg_lines.append("$Esd* Files::$APD File::$Input_File::$File")
    cfg_lines.append("$Esd* Files::$Ploc File::$Input_File::$File")
    cfg_lines.append("$Esd* Files::$sp File::$Input_File::$File")
    cfg_lines.append("$Esd* Files::$generation method::$String::$gds+apd gds_only  Resistive-Package-Model Package-Layout other")
    cfg_lines.append("HEADER END")
    cfg_file_path = os.path.join(cfg_file_dir, 'gen_esd_files.cfg')

    if not os.path.exists(cfg_file_path):
        add_to_message_center(project_dir,f"-> cfg saved: gen_esd_files.cfg")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))
    return cfg_file_path

def main(project_dir, cfg_file_path,json_loc):
    def_file = get_def_file(json_loc, "Generate-ESD-Files")
    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"

    print("Launching DGUI...")
    print(command)
    execute_subprocess(command)


if __name__ == "__main__":
    input_file = args.i
    project_dir = args.p
    def_path = save_def(input_file, project_dir, "gen_tech_files.txt")
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, cfg_file_path, def_path, "Generate-Tech-Files", "Generate-ESD-Files")
    # os.remove(input_file)
    main(project_dir, cfg_file_path,json_loc)
