#!/usr/bin/env python3

from .xdg import *

# External dependencies imports
import bottle

# python3 imports
import json
import os
import pathlib
import copy
import io
import logging
import urllib
import uuid

import time
import subprocess
import sys
import traceback

setups_path = os.path.join(XDG_DATA_HOME, 'ogfx', 'setups')
racks_path = os.path.join(XDG_DATA_HOME, 'ogfx', 'racks')
units_path = os.path.join(XDG_DATA_HOME, 'ogfx', 'units')
default_setup_file_path = os.path.join(setups_path, 'default')

og = None

bottle.TEMPLATE_PATH.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), 'views')))

logging.info('setting up routes...')


# UNIT CONNECTIONS

@bottle.route('/connect2/<rack_index:int>/<unit_index:int>/<direction>/<channel_index:int>/<port_name>')
def connect2(rack_index, unit_index, channel_index, direction, port_name):
    og.setup['racks'][rack_index]['units'][unit_index][direction + '_connections'][channel_index].append(port_name)
    og.rewire()
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/connect/<rack_index:int>/<unit_index:int>/<direction>/<channel_index:int>')
@bottle.view('connect')
def connect(rack_index, unit_index, channel_index, direction):
    jack_port_direction = 'input'
    if direction == 'input':
        jack_port_direction = 'output'

    ports = og.find_jack_audio_ports(jack_port_direction)
    logging.debug('{}'.format(ports))
    return dict({'ports': ports, 'remaining_path': '/{}/{}/{}/{}'.format(rack_index, unit_index, direction, channel_index) })

@bottle.route('/disconnect/<rack_index:int>/<unit_index:int>/<direction>/<channel_index:int>/<connection_index:int>')
def disconnect(rack_index, unit_index, channel_index, direction, connection_index):
    del og.setup['racks'][rack_index]['units'][unit_index][direction + '_connections'][channel_index][connection_index]
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))
    og.rewire()


# RACK CONNECTIONS

@bottle.route('/connect2/<rack_index:int>/<direction>/<channel_index:int>/<port_name>')
def connect2(rack_index, channel_index, direction, port_name):
    og.setup['racks'][rack_index][direction + '_connections'][channel_index].append(port_name)
    og.rewire()
    bottle.redirect('/#rack-{}'.format(rack_index))

@bottle.route('/connect/<rack_index:int>/<direction>/<channel_index:int>')
@bottle.view('connect')
def connect(rack_index, channel_index, direction):
    jack_port_direction = 'input'
    if direction == 'input':
        jack_port_direction = 'output'

    ports = og.find_jack_audio_ports(jack_port_direction)
    logging.debug('{}'.format(ports))
    return dict({'ports': ports, 'remaining_path': '/{}/{}/{}'.format(rack_index, direction, channel_index) })

@bottle.route('/disconnect/<rack_index:int>/<direction>/<channel_index:int>/<connection_index:int>')
def disconnect(rack_index, channel_index, direction, connection_index):
    del og.setup['racks'][rack_index][direction + '_connections'][channel_index][connection_index]
    og.rewire()
    bottle.redirect('/#rack-{}'.format(rack_index))

# MIDI input connections

@bottle.route('/connect2/midi-input/<port_name>')
def connect2(port_name):
    og.setup['input_midi_connections'].append(port_name)
    og.rewire()
    bottle.redirect('/')

@bottle.route('/connect/midi-input')
@bottle.view('connect')
def connect():
    ports = og.find_jack_midi_ports('output')
    logging.debug('{}'.format(ports))
    return dict({'ports': ports, 'remaining_path': '/midi-input'})

@bottle.route('/disconnect/midi-input/<connection_index:int>')
def disconnect(connection_index):
    del og.setup['input_midi_connections'][connection_index]
    og.rewire()
    bottle.redirect('/')

# UNITS

@bottle.route('/set_unit_midi_cc/<rack_index:int>/<unit_index:int>/<enabled:int>/<channel:int>/<cc:int>')
def set_unit_midi_cc(rack_index, unit_index, enabled, channel, cc):
    logging.debug('set_midi_cc {} {} {} {} {}'.format(rack_index, unit_index, enabled, channel, cc))
    og.set_unit_midi_cc(rack_index, unit_index, (True if enabled > 0 else False), channel, cc)

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


@bottle.route('/enable_unit/<rack_index:int>/<unit_index:int>/<enabled:int>')
def enable_unit(rack_index, unit_index, enabled):
    logging.debug('enable unit')
    og.toggle_unit_active(rack_index, unit_index, enabled != 0)

@bottle.route('/move_unit_down/<rack_index:int>/<unit_index:int>')
def move_unit_down(rack_index, unit_index):
    og.move_unit_down(rack_index, unit_index)
    bottle.redirect('/')

@bottle.route('/move_unit_up/<rack_index:int>/<unit_index:int>')
def move_unit_up(rack_index, unit_index):
    og.move_unit_up(rack_index, unit_index)
    bottle.redirect('/')

# PORTS

@bottle.route('/set_port_value/<rack_index:int>/<unit_index:int>/<port_index:int>/<value:float>')
def set_port_value(rack_index, unit_index, port_index, value):
    logging.debug('set port value')
    og.set_port_value(rack_index, unit_index, port_index, value)


# RACKS

@bottle.route('/add/<rack_index:int>')
def add_rack(rack_index):
    og.add_rack(rack_index)
    bottle.redirect('/#rack-{}'.format(rack_index))

@bottle.route('/delete/<rack_index:int>')
def delete_rack(rack_index):
    og.delete_rack(rack_index)
    bottle.redirect('/')
    
@bottle.route('/move_rack_down/<rack_index:int>')
def move_rack_down(rack_index, unit_index):
    og.move_rack_down(rack_index)
    bottle.redirect('/')

@bottle.route('/move_rack_up/<rack_index:int>')
def move_rack_up(rack_index, unit_index):
    og.move_rack_up(rack_index)
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

@bottle.route('/upload2/<rack_index:int>/<unit_index:int>', method='POST')
def upload_unit2(rack_index, unit_index):
    upload = bottle.request.files.get('upload')
    upload_contents = io.BytesIO()
    upload.save(upload_contents)
    logging.info(upload_contents.getvalue())
    og.setup['racks'][rack_index]['units'][unit_index] = json.loads(upload_contents.getvalue())
    og.rewire()
    bottle.redirect('/')

@bottle.route('/upload/<rack_index:int>/<unit_index:int>')
@bottle.view('upload')
def upload_unit(rack_index, unit_index):
    return dict({'remaining_path': '/{}/{}'.format(rack_index, unit_index)})

@bottle.route('/upload2/<rack_index:int>', method='POST')
def upload_rack2(rack_index):
    upload = bottle.request.files.get('upload')
    upload_contents = io.BytesIO()
    upload.save(upload_contents)
    logging.info(upload_contents.getvalue())
    og.setup['racks'][rack_index] = json.loads(upload_contents.getvalue())
    og.rewire()
    bottle.redirect('/')

@bottle.route('/upload/<rack_index:int>')
@bottle.view('upload')
def upload_rack(rack_index):
    return dict({'remaining_path': '/{}'.format(rack_index)})

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


# SAVING FILES

def save_default_setup():
    logging.info('writing default setup...')
    with open(default_setup_file_path, 'w') as f:
        f.write(json.dumps(og.setup, indent=4))

@bottle.route('/saveas2/<rack_index:int>/<unit_index:int>')
def saveas2(rack_index, unit_index):
    path = bottle.request.query.get('filename')
    logging.debug('saveas2: path: {}'.format(path))
    with open(pathlib.Path(units_path, path), 'w') as file:
        json.dump(og.setup['racks'][rack_index]['units'][unit_index], file, indent=4)

    bottle.redirect('/')

@bottle.route('/saveas2/<rack_index:int>')
def saveas2(rack_index):
    path = bottle.request.query.get('filename')
    logging.debug('saveas2: path: {}'.format(path))
    with open(pathlib.Path(racks_path, path), 'w') as file:
        json.dump(og.setup['racks'][rack_index], file, indent=4)

    bottle.redirect('/')

@bottle.route('/saveas2')
def saveas2():
    path = bottle.request.query.get('filename')
    logging.debug('saveas2: path: {}'.format(path))
    with open(pathlib.Path(setups_path, path), 'w') as file:
        json.dump(og.setup, file, indent=4)

    bottle.redirect('/')

@bottle.route('/saveas')
@bottle.view('file_chooser')
def load_setup():
    return {'save': True, 'files': list(map(lambda x: x.name, pathlib.Path(setups_path).iterdir())), 'remaining_path': ''}

@bottle.route('/saveas/<rack_index:int>')
@bottle.view('file_chooser')
def load_setup(rack_index):
    return {'save':  True, 'files': list(map(lambda x: x.name, pathlib.Path(racks_path).iterdir())), 'remaining_path': '/{}'.format(rack_index)}

@bottle.route('/saveas/<rack_index:int>/<unit_index:int>')
@bottle.view('file_chooser')
def load_setup(rack_index, unit_index):
    return {'save': True, 'files': list(map(lambda x: x.name, pathlib.Path(units_path).iterdir())), 'remaining_path': '/{}/{}'.format(rack_index, unit_index)}


# LOADING FILES


@bottle.route('/load2/<rack_index:int>/<unit_index:int>')
def load2(rack_index, unit_index):
    path = bottle.request.query.get('filename')
    logging.debug('load2: path: {}'.format(path))
    with open(pathlib.Path(units_path, path), 'r') as file:
        data = json.loads(file.read())
        data['uuid'] = str(uuid.uuid4())
        og.setup['racks'][rack_index]['units'][unit_index] = data
        og.rewire()

    bottle.redirect('/')

@bottle.route('/load2/<rack_index:int>')
def load2(rack_index):
    path = bottle.request.query.get('filename')
    logging.debug('load2: path: {}'.format(path))
    with open(pathlib.Path(racks_path, path), 'r') as file:
        data = json.loads(file.read())
        for unit in data['units']:
            unit['uuid'] = str(uuid.uuid4())
        og.setup['racks'][rack_index] = data
        og.rewire()

    bottle.redirect('/')

@bottle.route('/load2')
def load2():
    path = bottle.request.query.get('filename')
    logging.debug('load2: path: {}'.format(path))
    with open(pathlib.Path(setups_path, path), 'r') as file:
        data = json.loads(file.read())
        og.setup = data
        og.rewire()

    bottle.redirect('/')

@bottle.route('/load')
@bottle.view('file_chooser')
def load_setup():
    return {'save': False, 'files': list(map(lambda x: x.name, pathlib.Path(setups_path).iterdir())), 'remaining_path': ''}

@bottle.route('/load/<rack_index:int>')
@bottle.view('file_chooser')
def load_setup(rack_index):
    return {'save':  False, 'files': list(map(lambda x: x.name, pathlib.Path(racks_path).iterdir())), 'remaining_path': '/{}'.format(rack_index)}

@bottle.route('/load/<rack_index:int>/<unit_index:int>')
@bottle.view('file_chooser')
def load_setup(rack_index, unit_index):
    return {'save': False, 'files': list(map(lambda x: x.name, pathlib.Path(units_path).iterdir())), 'remaining_path': '/{}/{}'.format(rack_index, unit_index)}

# FORM SUBMISSION

@bottle.route('/', method='POST')
def index_post():
    og.set_tempotap_midi_cc(bool(bottle.request.forms.get('tempotap_midi_cc_enabled')), int(bottle.request.forms.get('tempotap_midi_cc_channel')), int(bottle.request.forms.get('tempotap_midi_cc_cc')))
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

                enabled_param_name = 'input_control_port_cc_enabled_checkbox_{}_{}_{}'.format(rack_index, unit_index, port_index)
                channel_param_name = 'port_midi_cc_channel_{}_{}_{}'.format(rack_index, unit_index, port_index)
                cc_param_name = 'port_midi_cc_cc_{}_{}_{}'.format(rack_index, unit_index, port_index)
                minimum_param_name = 'port_midi_cc_min_{}_{}_{}'.format(rack_index, unit_index, port_index)
                maximum_param_name = 'port_midi_cc_max_{}_{}_{}'.format(rack_index, unit_index, port_index)
                og.set_port_midi_cc(rack_index, unit_index, port_index, bool(bottle.request.forms.get(enabled_param_name)), int(bottle.request.forms.get(channel_param_name)), int(bottle.request.forms.get(cc_param_name)), float(bottle.request.forms.get(minimum_param_name)), float(bottle.request.forms.get(maximum_param_name)))
                port_index += 1
            unit_index += 1
        rack_index += 1
    og.setup_midi_maps()
    bottle.redirect('/')

@bottle.route('/')
@bottle.view('index')
def index():
    return dict({'setup': og.setup,'filename': og.setup_filename})

@bottle.route('/reset')
def resetet():
    og.create_setup()
    bottle.redirect('/')

    
# STATIC FILES
    
@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static/')))

midi_in_quit = False
def midi_in():
    global midi_in_quit
    
    while not midi_in_quit:
        time.sleep(0.01)
        pass


def run(o):
    global og;
    og = o
    logging.info('starting bottle server...')
    bottle.run(host='0.0.0.0', port='8080', debug=False, quiet=True)
