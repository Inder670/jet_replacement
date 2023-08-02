import json
import os


def gen_json(json_loc, cfg_loc, def_loc, def_step, cfg_step):
    if os.path.exists(json_loc) and os.path.getsize(json_loc) > 0:
        with open(json_loc, 'r') as file:
            try:
                dgui_json = json.load(file)
                for key in dgui_json:
                    if key != cfg_step:
                        dgui_json[key]['current_step'] = 0
                    else:
                        dgui_json[key]['current_step'] = 1

            except json.JSONDecodeError:
                # Handle the case when the file contains invalid JSON data
                print(f"Invalid JSON data in {json_loc}.")
                dgui_json = {}

    else:
        dgui_json = {}

    dgui_json[def_step]['def'] = def_loc
    if not 'cfg' in dgui_json[cfg_step]:
        cfg_data = f"{cfg_loc}"
        dgui_json[cfg_step]['cfg'] = cfg_data

    with open(json_loc, 'w') as file:
        json.dump(dgui_json, file, indent=4)