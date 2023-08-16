#!/bin/bash

pyinstaller -F start.py -n start --clean
pyinstaller -F analyze_lvs.py -n analyze_lvs
pyinstaller -F prepare_lvs.py -n prepare_lvs
pyinstaller -F prepare_cci.py -n prepare_cci
pyinstaller -F gen_esd_dev.py -n gen_esd_dev
pyinstaller -F gen_tech_files.py -n gen_tech_files
pyinstaller -F gen_esd_files.py -n gen_esd_files
pyinstaller -F prepare_esra.py -n prepare_esra


cp ./dist/start ./dist/analyze_lvs ./dist/prepare_lvs ./dist/gen_esd_dev ./dist/gen_tech_files ./dist/gen_esd_files /home/inder/PycharmProjects/hza_DGUI_v2_new/test/dgui/binaries
