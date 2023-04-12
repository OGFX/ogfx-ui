#!/usr/bin/python3

import logging
import argparse
import os
import subprocess
import json
import uuid

arguments_parser = argparse.ArgumentParser(description='ogfx_ui - a web interface for OGFX')
arguments_parser.add_argument('--log-level', type=int, dest='log_level', help='5: DEBUG, 4: INFO, 3: WARNING, 2: ERROR, 1: CRITICAL, default: %(default)s', action='store', default=4)
arguments_parser.add_argument('--setup', dest='setup', action='store', help='A file containing a setup to load at startup')
arguments_parser.add_argument('--lv2-cache', dest='lv2_cache', action='store', help='A file containing the output of ogfx_lv2ls. If missing a scan will be performed at startup')
arguments = arguments_parser.parse_args()

log_levels_map = {5: logging.DEBUG, 4: logging.INFO, 3: logging.WARNING, 2: logging.ERROR, 1: logging.CRITICAL}

logging.basicConfig(level=log_levels_map[arguments.log_level], format='ogfx: %(asctime)s %(message)s')

import ogfx_ui

logging.info('we are here: {}'.format((os.path.dirname(__file__))))

for path in [ogfx_ui.setups_path, ogfx_ui.racks_path, ogfx_ui.units_path]:
    if not os.path.exists(path):
        logging.info('creating path {}'.format(path))
        os.makedirs(path)

logging.info('using setups path {}'.format(ogfx_ui.setups_path))
logging.info('using racks path {}'.format(ogfx_ui.racks_path))
logging.info('using units path {}'.format(ogfx_ui.units_path))

if arguments.lv2_cache:
  with open(arguments.lv2_cache, 'r') as f:
    lv2_world = json.load(f)
else:
  logging.info('scanning for lv2 plugins...')
  lv2_world_json_string = subprocess.check_output(['ogfx_lv2ls'])
  logging.debug('parsing json')
  lv2_world = json.loads(lv2_world_json_string)
  logging.info('number of plugins: {}'.format(len(lv2_world)))

# og = ogfx_ui.backends.jalv(lv2_world)
logging.info('starting backend...')
og = ogfx_ui.backends.mod_host(lv2_world)
og.start_threads()
logging.info('done.')

def fixup_setup(setup):
    for rack in og.setup['racks']:
        for unit in rack['units']:
            unit['uuid'] = str(uuid.uuid4())


try:
    if arguments.setup:
        logging.info('loading setup {}...'.format(arguments.setup))
        with open(arguments.setup) as f:
            json_content = f.read()
            setup = json.loads(json_content)
            og.setup = setup
            fixup_setup(og.setup)
            og.setup_filename = arguments.setup
            og.rewire()
    else:
        if os.path.exists(ogfx_ui.default_setup_file_path):
            with open(ogfx_ui.default_setup_file_path) as f:
                setup_json_string = f.read()
                setup = json.loads(setup_json_string)
                og.setup = setup
                fixup_setup(og.setup)
                og.setup_filename = ogfx_ui.default_setup_file_path
                og.rewire()
                
except KeyError as e:
    logging.error('KeyError: {}'.format(e))
except:
    logging.error('ERRROR!!!! Something unspeakable happened! Traceback follows:')
    traceback.print_exc()

ogfx_ui.run(og)

ogfx_ui.save_default_setup()


logging.info('stopping threads...')
og.stop_threads()
logging.info('clearing setup...')
og.create_setup()
logging.info('exiting...')
