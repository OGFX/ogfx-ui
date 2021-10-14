#!/usr/bin/python3

import logging
import argparse
import os
import subprocess
import json

arguments_parser = argparse.ArgumentParser(description='ogfx_ui - a web interface for OGFX')
arguments_parser.add_argument('--log-level', type=int, dest='log_level', help='5: DEBUG, 4: INFO, 3: WARNING, 2: ERROR, 1: CRITICAL, default: %(default)s', action='store', default=4)
arguments_parser.add_argument('--setup', dest='setup', action='store', help='A file containing a setup to load at startup')
arguments = arguments_parser.parse_args()

log_levels_map = {5: logging.DEBUG, 4: logging.INFO, 3: logging.WARNING, 2: logging.ERROR, 1: logging.CRITICAL}

logging.basicConfig(level=log_levels_map[arguments.log_level], format='ogfx: %(asctime)s %(message)s')

import ogfx_ui

logging.info((os.path.dirname(__file__)))

setups_path = os.path.join(ogfx_ui.xdg.XDG_DATA_HOME, 'ogfx', 'setups')
racks_path = os.path.join(ogfx_ui.xdg.XDG_DATA_HOME, 'ogfx', 'racks')
units_path = os.path.join(ogfx_ui.xdg.XDG_DATA_HOME, 'ogfx', 'units')

for path in [setups_path, racks_path, units_path]:
    if not os.path.exists(path):
        logging.info('creating path {}'.format(path))
        os.makedirs(path)

logging.info('using setups path {}'.format(setups_path))
logging.info('using racks path {}'.format(racks_path))
logging.info('using units path {}'.format(units_path))
default_setup_file_path = os.path.join(setups_path, 'default.ogfx-setup')

logging.info('scanning for lv2 plugins...')
lv2_world_json_string = subprocess.check_output(['ogfx_lv2ls'])
lv2_world = json.loads(lv2_world_json_string)
logging.info('number of plugins: {}'.format(len(lv2_world)))

og = ogfx_ui.backends.jalv(lv2_world)
og.start_threads()

try:
    if arguments.setup:
        logging.info('loading setup {}...'.format(arguments.setup))
        with open(arguments.setup) as f:
            json_content = f.read()
            setup = json.loads(json_content)
            og.setup = setup
            og.setup_filename = arguments.setup
            og.rewire()
    else:
        if os.path.exists(default_setup_file_path):
            with open(default_setup_file_path) as f:
                setup_json_string = f.read()
                setup = json.loads(setup_json_string)
                og.setup = setup
                og.setup_filename = default_setup_file_path
                og.rewire()
                
except KeyError as e:
    logging.error('KeyError: {}'.format(e))
except:
    logging.error('ERRROR!!!! Something unspeakable happened! Traceback follows:')
    traceback.print_exc()

ogfx_ui.run(og)

logging.info('writing default setup...')
with open(default_setup_file_path, 'w') as f:
    f.write(json.dumps(og.setup, indent=4))

logging.info('stopping threads...')
og.stop_threads()
logging.info('clearing setup...')
og.create_setup()
logging.info('exiting...')
