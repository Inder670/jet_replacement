import argparse
from PyQt5.QtWidgets import QApplication, QMessageBox

from utilities.utils import *
# Create the parser
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments
parser.add_argument('-i', type=str, help='input file(def file)')
parser.add_argument('-o', type=str, help='output directory')
parser.add_argument('-p', type=str, help='project directory')
parser.add_argument('-b', help='Launch previous gui flag', action='store_true')

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
    cfg_lines.append("TITLE:: Analyze LVS")
    cfg_lines.append(
        f"GLAUNCH:: Skip-LVS-Preparation {os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'prepare_lvs')} 1")
    cfg_lines.append(
        f"GLAUNCH:: Next(Analyze-LVS) {os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'analyze_lvs')} 1")
    cfg_lines.append("$lvs_setup*::$Calibre.run file::$Input_File::$File")
    cfg_lines.append("$lvs_setup*::$sourceme file::$Input_File::$File")
    cfg_lines.append("HEADER END")

    cfg_file_path = os.path.join(cfg_file_dir, 'analyze_lvs.cfg')
    if not os.path.exists(cfg_file_path):
        add_to_message_center(project_dir,f"->cfg saved: analyze_lvs.cfg")
        with open(cfg_file_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return cfg_file_path


def find_project_dir(input_file):
    path = ''
    with open(input_file, 'r') as file:
        for line in file:
            tokens = line.split('::')
            if tokens[1] == "$Directory":
                path = tokens[2].strip('$').strip()
                break  # Move the 'break' statement here
    if not path == '' :
        if not os.path.exists(path):
            message_box(f"Please provide a valid project directory path")
            sys.exit(1)
    else:
        message_box(f"Path cannot be empty")
    return path


def gen_json(json_loc, cfg_loc):

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

    if dgui_json:
        pass
    else:
        data = {
            'Analyze-LVS':{
                'cfg':f'{cfg_loc}',
                'current_step': 1
            },
            'Prepare-LVS': {
                'current_step': 0
            },
            'Prepare-CCI': {
                'current_step': 0
            },
            'Generate-esd_dev': {
                'current_step': 0
            },
            'Generate-Tech-Files': {
                'current_step': 0
            },
            'Generate-ESD-Files': {
                'current_step': 0
            },
            "Prepare-ESRA": {
                'current_step': 0
            }
        }

        dgui_json.update(data)
        with open(json_loc, 'w') as file:
            json.dump(dgui_json, file, indent=4)


def check_json(json_loc):
    with open(json_loc, 'r') as file:
        data = json.load(file)
        if "Analyze-LVS" in data:
            if 'def' in data['Analyze-LVS']:
                path_to_def = data['Analyze-LVS']['def']
                return path_to_def
        else:
            return None

def save_existing_def_files(json_loc):
    if os.path.exists(json_loc):
        with open(json_loc, 'r') as file:
            data = json.load(file)
            def_back_up = os.path.join(os.path.dirname(json_loc), 'def_back_up')
            if not os.path.exists(def_back_up):
                os.makedirs(def_back_up)

            for key in data:
                step = data[key]
                if 'def' in step:
                    if os.path.exists(step['def']):
                        source = step['def']
                        try:
                            shutil.copy2(source, def_back_up)
                        except Exception as e:
                            print(f"An error occured: {e}")

def message_box(message):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    msg_box.exec_()

def question_box(message):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setText(message)
    res = msg_box.exec_()
    return res == QMessageBox.Yes


def lock_file(project_dir):
    lock_file_path = os.path.join(project_dir, '.dgui', 'dgui.lock')
    if os.path.exists(project_dir):
        if not os.path.exists(lock_file_path):
            with open(lock_file_path, 'w') as file:
                file.write(f"owner:{os.environ.get('USER')}")
        else:
            owner_found = False
            with open(lock_file_path, 'r') as file:
                for line in file:
                    if line.startswith('owner'):
                        owner_name = line.split(':')[1].strip()
                        if os.environ.get('USER') == owner_name:
                            owner_found = True
                            result = question_box("This directory contains an existing project. Click yes to continue working on the existing project")
                            if result:
                                pass
                            else:
                                sys.exit(0)
                            break
                        elif os.environ.get('USER') != owner_name:
                            owner_found = True
                            result = question_box(f"This directory is being used by {owner_name}\n"
                                            f"Would you like to transfer ownership of this project to the user : {os.environ.get('USER') }")
                            if result:
                                os.remove(lock_file_path)
                                with open(lock_file_path, 'w') as file:
                                    file.write(f"owner:{os.environ.get('USER')}")
                            else:
                                sys.exit(0)
                        else:
                            pass

            if not owner_found:
                print("lock file corrupted, no owner found.")
                sys.exit(1)



def main(project_dir, json_loc, cfg_file_path):
    check_json_for_existing_def = check_json(json_loc)

    if os.path.exists(json_loc):
        with open(json_loc, 'r') as file:
            data =json.load(file)
            for key in data:

                if data[key]['current_step'] == 1:
                    cfg_file_path = data[key]['cfg']
                    if 'def' in data[key]:
                        def_file = f"-d {data[key]['def']}"
                    else:
                        def_file = ''

                    command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir} {def_file}"
    else:

        command = f"dgui -c {cfg_file_path} -g  -dir ./ -j ./ --splash -p {project_dir}"
    print("Launching DGUI...")
    execute_subprocess(command)


def check_permissions(project_dir):
    if os.path.exists(project_dir):
        if not os.access(project_dir, os.W_OK):
            message_box(
                f"{project_dir} directory is not writable, please launch dgui again and provide a directory with read/write permissions")
            print(f"{project_dir} directory is not writable, please launch dgui again and provide a directory with "
                  f"read/write permissions", file=sys.stderr)
            sys.exit(1)
        elif not os.access(project_dir, os.R_OK):
            message_box(
                f"{project_dir} directory is not readable, please launch dgui again and provide a directory with read/write permissions")
            print(f"{project_dir} directory is not writable, please launch dgui again and provide a directory with "
                  f"read/write permissions", file=sys.stderr)

            sys.exit(1)
    else:
        message_box("Project directory doesn't exist. Please launch dgui again and provide a project directory")
if __name__ == "__main__":
    input_file = args.i
    project_dir = find_project_dir(input_file).strip('\n')
    check_permissions(project_dir)
    def_path = save_def(input_file, project_dir, "project_dir.txt")
    json_loc = os.path.join(project_dir, '.dgui', 'dgui_data.json')
    lock_file(project_dir)
    cfg_file_path = save_cfg(project_dir)
    gen_json(json_loc, cfg_file_path)
    save_existing_def_files(json_loc)
    # os.remove(input_file)

    main(project_dir,json_loc,cfg_file_path)
