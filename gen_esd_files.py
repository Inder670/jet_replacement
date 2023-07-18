import os
import subprocess
import sys
import argparse

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

def generate_cfg():
    cfg_lines = []
    cfg_lines.append("HEADER START")
    cfg_lines.append("VARIABLES")
    cfg_lines.append("TITLE:: Prepare esra")
    cfg_lines.append(f"GLAUNCH:: prepare_esra {os.path.join(os.path.dirname(sys.argv[0]),'prepare_esra')} 1")
    cfg_lines.append("$technology_files::$itf file::$Input_File::$File")
    cfg_lines.append("$technology_files::$map file::$Input_File::$File")
    cfg_lines.append("$MOS Max Stress Limits::$PLACEHOLDER::$Input_File::$File")
    cfg_lines.append("$CDM Stress Current::$Direct Entry::$String::$ANY")
    cfg_lines.append("$CDM Stress Current::$Technology::$String::$ANY")
    cfg_lines.append("$Chip Bond::$Chip Bond::$String::$Flip-Chip Wire-Bond")
    cfg_lines.append("$Esd Grid::$NX::$String::$ANY")
    cfg_lines.append("$Esd Grid::$NY::$String::$ANY")
    cfg_lines.append("$Die Size::$X::$String::$ANY")
    cfg_lines.append("$Die Size::$Y::$String::$ANY")
    cfg_lines.append("$em_store/preem_store::$preem_store::$String::$True False")
    cfg_lines.append("$em_store/preem_store::$em_store::$String::$True False")



    # cfg_lines.append("$lvs_setup::$layout file::$Input_File::$File")
    # cfg_lines.append("$lvs_setup::$Edtext file::$Input_File::$File")
    # cfg_lines.append("$lvs_setup::$LVS cal file::$Input_File::$File")
    # cfg_lines.append("$lvs_setup::$LVS cellmap file::$Input_File::$File")
    # cfg_lines.append("$lvs_setup::$cell list file::$Input_File::$File")
    cfg_lines.append("HEADER END")


    return cfg_lines

def save_cfg(cfg_lines, filename):
    with open(filename, "w") as cfg_file:
        cfg_file.write("\n".join(cfg_lines))

def generate_txt_file(file_list):
    txt_lines = []
    for index, file in enumerate(file_list, start=1):
        txt_lines.append(f"$View Files::$File{index}::${os.path.abspath(file)}")

    return txt_lines

def save_txt_file(txt_lines, filename):
    with open(filename, "w") as txt_file:
        txt_file.write("\n".join(txt_lines))
def save_def(input):
    config_files_path = os.path.join(os.path.dirname(sys.argv[0]), "def_files")

    if not os.path.exists(config_files_path):
        os.mkdir(config_files_path)

    new_loc = os.path.join(config_files_path, 'gen_tech_files.txt')
    try:
        shutil.copy2(input, new_loc)
    except Exception as e:
        print(f"An error occurred: {e}")

    return new_loc

if __name__ == "__main__":

    # Prompt the user to enter a directory path
    input_file = args.input

    # Copy default file to project structure
    def_path = save_def(input_file)
    os.remove(input_file)
    # Search for files in the specified directory (including subdirectories)
    path = ''
    # Generate the cfg lines
    cfg_lines = generate_cfg()

    # Save the cfg file
    # cfg_filename = os.path.abspath(args.output)
    cfg_filename = "gen_esd_files.cfg"

    save_cfg(cfg_lines, cfg_filename)

    # Generate the txt file content
    print(f"Generated {len(cfg_lines)} cfg lines. Saved as {cfg_filename}.")

    command = f"dgui -c {cfg_filename} -g  -dir ./ -j ./ --splash"

    print("Launching DGUI...")
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        print(line.decode('utf-8').strip())
    process.wait()
    # os.system(command)
    sys.exit(0)