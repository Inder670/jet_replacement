import json
import os



def check_existing_message_center(project_dir):
    dgui_dir = os.path.join(project_dir, '.dgui')
    dgui_dir_exists = os.path.exists(dgui_dir)
    messages = []
    if not dgui_dir_exists:
        os.makedirs(dgui_dir)
    msg_center_path = os.path.join(dgui_dir, 'dgui_message_center.txt')
    msg_cntr_exists = os.path.exists(msg_center_path)
    print(os.path.join(dgui_dir, 'dgui_message_center.txt'))
    if not msg_cntr_exists:
        with open(msg_center_path,'w') as file:
            file.write('.dgui directory created\n')
        return ['.dgui directory created']
    else:
        with open(msg_center_path, 'r') as file:
            print(type(file))
            for line in file:
                messages.append(line)
            return messages

def save_message_center(project_dir,msg_center):
    with open(os.path.join(project_dir, '.dgui', 'dgui_message_center.txt'), 'w') as file:
        cleaned_strings = [s.strip() for s in msg_center if s.strip()]
        for item in cleaned_strings:
            file.write(f"{item}\n")  # Adding a newline character at the end of eac

