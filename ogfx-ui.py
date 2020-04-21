#!/usr/bin/python3

# External dependencies imports
import bottle

# python3 imports
import json
import xdg
import os
import copy
import io
import subprocess
import uuid
import logging
import argparse
import socket
import threading
import time
import sys
import traceback

import ogfx

arguments_parser = argparse.ArgumentParser(description='ogfx-ui - a web interface for OGFX')
arguments_parser.add_argument('--log-level', type=int, dest='log_level', help='5: DEBUG, 4: INFO, 3: WARNING, 2: ERROR, 1: CRITICAL, default: %(default)s', action='store', default=4)
arguments_parser.add_argument('--setup', dest='setup', action='store', help='A file containing a setup to load at startup')
arguments_parser.add_argument('--default-input', dest='default_input', action='append', help='A default input port to connect to')
arguments_parser.add_argument('--default-output', dest='default_output', action='append', help='A default output port to connect to')
arguments = arguments_parser.parse_args()

log_levels_map = {5: logging.DEBUG, 4: logging.INFO, 3: logging.WARNING, 2: logging.ERROR, 1: logging.CRITICAL}

logging.basicConfig(level=log_levels_map[arguments.log_level], format='%(asctime)s %(message)s')

logging.info('default_inputs: {}'.format(arguments.default_input))
logging.info('default_outputs: {}'.format(arguments.default_output))

setups_path = os.path.join(xdg.XDG_DATA_HOME, 'ogfx', 'setups')

if not os.path.exists(setups_path):
    logging.info('creating setups path {}'.format(setups_path))
    os.makedirs(setups_path)

logging.info('using setups path {}'.format(setups_path))
default_setup_file_path = os.path.join(setups_path, 'default_setup.json')

logging.info('scanning for lv2 plugins...')
lv2_world_json_string = subprocess.check_output(['./lv2lsjson'])
lv2_world = json.loads(lv2_world_json_string)
logging.info('number of plugins: {}'.format(len(lv2_world)))


og = ogfx.ogfx(lv2_world)
og.start_threads()

logging.info('setting up routes...')
@bottle.route('/connect2/<rack_index:int>/<unit_index:int>/<channel_index:int>/<port_index:int>')
def connect2(rack_index, unit_index, channel_index, port_index):
    og.setup['racks'][rack_index]['units'][unit_index]['connections'][channel_index].insert(0,  ports[port_index].name)
    rewire()
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/connect/<rack_index:int>/<unit_index:int>/<channel_index:int>/<direction:path>')
@bottle.view('connect')
def connect(rack_index, unit_index, channel_index, direction):
    if direction == 'output':
        ports = og.find_jack_audio_port_names('input')
        return dict({'ports': ports, 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })
    else:
        ports = og.find_jack_audio_port_names('output')
        return dict({'ports': ports, 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })

@bottle.route('/disconnect/<rack_index:int>/<unit_index:int>/<channel_index:int>/<connection_index:int>')
def disconnect(rack_index, unit_index, channel_index, connection_index):
    og.disconnect(rack_index, unit_index, channel_index, connection_index)
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

# UNITS 

@bottle.route('/add/<rack_index:int>/<unit_index:int>/<uri>')
def add_unit(rack_index, unit_index, uri):
    og.add_unit(rack_index, unit_index, uri)
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/add2/<rack_index:int>/<unit_index:int>/<units_map_index:int>')
def add_unit2(rack_index, unit_index, units_map_index):
    keys_list = list(og.units_map)
    og.add_unit(rack_index, unit_index, keys_list[units_map_index])
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/add/<rack_index:int>/<unit_index:int>')
@bottle.view('add_unit')
def add_unit(rack_index, unit_index):
    return dict({'units': og.units_map, 'remaining_path': '/{}/{}'.format(rack_index, unit_index)})

@bottle.route('/delete/<rack_index:int>/<unit_index:int>')
def delete_unit(rack_index, unit_index):
    og.delete_unit(rack_index, unit_index)
    bottle.redirect('/#rack-{}'.format(rack_index))


# RACKS

@bottle.route('/add/<rack_index:int>')
def add_rack(rack_index):
    og.add_rack(rack_index)
    bottle.redirect('/#rack-{}'.format(rack_index))

@bottle.route('/delete/<rack_index:int>')
def delete_rack(rack_index):
    og.delete_rack(rack_index)
    bottle.redirect('/')
    

# DOWNLOADS

@bottle.route('/download')
def download_setup():
    bottle.response.content_type = 'text/json'
    return json.dumps(og.setup, indent=2)

@bottle.route('/download/<rack_index:int>')
def download_rack(rack_index):
    bottle.response.content_type = 'text/json'
    return json.dumps(og.setup['racks'][rack_index], indent=2)

@bottle.route('/download/<rack_index:int>/<unit_index:int>')
def download_rack(rack_index, unit_index):
    bottle.response.content_type = 'text/json'
    return json.dumps(og.setup['racks'][rack_index]['units'][unit_index], indent=2)


# UPLOADS

@bottle.route('/upload2', method='POST')
def upload_setup2():
    upload = bottle.request.files.get('upload')
    upload_contents = io.BytesIO()
    upload.save(upload_contents)
    logging.info(upload_contents.getvalue())
    og.setup = json.loads(upload_contents.getvalue())
    og.rewire()
    bottle.redirect('/')

@bottle.route('/upload')
@bottle.view('upload')
def upload_setup():
    return dict({'remaining_path': ''})


def checkbox_to_bool(value):
    if value == 'on':
        return True
    else:
        return False

@bottle.route('/', method='POST')
def index_post():
    rack_index = 0
    for rack in og.setup['racks']:
        param_name = 'rack_enabled_{}'.format(rack_index)
        logging.debug(param_name)
        og.toggle_rack_active(rack_index, checkbox_to_bool(bottle.request.forms.get(param_name)))
        unit_index = 0
        for unit in rack['units']:
            param_name = 'unit_enabled_{}_{}'.format(rack_index, unit_index)
            logging.debug(param_name)
            og.toggle_unit_active(rack_index, unit_index, checkbox_to_bool(bottle.request.forms.get(param_name)))
            port_index = 0
            for port in unit['input_control_ports']:
                param_name = 'input_control_port_value_text_{}_{}_{}'.format(rack_index, unit_index, port_index)
                logging.debug('port value for: {} {} {} - {}'.format(rack_index, unit_index, port_index, param_name ))
                og.set_port_value(rack_index, unit_index, port_index, float(bottle.request.forms.get(param_name)))
                port_index += 1
            unit_index += 1
        rack_index += 1
    bottle.redirect('/')

@bottle.route('/')
@bottle.view('index')
def index():
    return dict({'setup': og.setup})

@bottle.route('/reset')
def resetet():
    og.create_setup()
    bottle.redirect('/')


@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

midi_in_quit = False
def midi_in():
    global midi_in_quit
    
    while not midi_in_quit:
        time.sleep(0.01)
        pass


try:
    if arguments.setup:
        logging.info('loading setup {}...'.format(arguments.setup))
        with open(arguments.setup) as f:
            json_content = f.read()
            setup = json.loads(json_content)
            og.setup = setup
            og.rewire()
    if False:
        logging.info('adding example data...')
        
        og.add_rack(0)
    
        og.append_unit(0, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
        og.set_port_value(0, 0, 0, 0)
        
        og.append_unit(0, 'http://guitarix.sourceforge.net/plugins/gx_cabinet#CABINET')
        # append_unit0(0, 'http://gareus.org/oss/lv2/convoLV2#Mono')
        # og.append_unit(0, 'http://calf.sourceforge.net/plugins/Equalizer5Band')
        og.append_unit(0, 'http://drobilla.net/plugins/mda/DubDelay')
        og.set_port_value(0, 2, 0, 0.2)

        og.append_unit(0, 'http://calf.sourceforge.net/plugins/Reverb')
        
        og.setup['racks'][0]['units'][0]['extra_input_connections'][0].append('system:capture_2')


        og.append_unit(0, 'http://plugin.org.uk/swh-plugins/sc4')
        og.setup['racks'][0]['units'][-1]['extra_output_connections'][0].append('system:playback_1')
        og.setup['racks'][0]['units'][-1]['extra_output_connections'][1].append('system:playback_2')
        
        og.rewire()
        
except KeyError as e:
    logging.error('KeyError: {}'.format(e))
except:
    logging.error('ERRROR!!!!')
    logging.error('Something unspeakable happened!')
    traceback.print_exc()

logging.info('starting bottle server...')
bottle.run(host='0.0.0.0', port='8080', debug=True)

logging.info('stopping threads...')
og.stop_threads()
logging.info('clearing setup...')
og.create_setup()
logging.info('exiting...')
