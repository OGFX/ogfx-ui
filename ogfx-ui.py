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

units_map = dict()

logging.info('registering special units...')
special_units = dict()

unit_type_lv2 = 'lv2'
unit_type_special = 'special'

logging.info('scanning for lv2 plugins...')
lv2_world_json_string = subprocess.check_output(['./lv2lsjson'])
lv2_world = json.loads(lv2_world_json_string)
logging.info('number of plugins: {}'.format(len(lv2_world)))

logging.info('registering lv2 plugins...')
for p in lv2_world:
    # logging.info(str(p.get_uri()))
    logging.debug('{} ({})'.format(p['name'], p['uri']))
    units_map[p['uri']] = {'type': 'lv2', 'name': p['name'], 'data': p }

logging.info('creating subprocess map...')

subprocess_map = dict()
connections = []


def create_setup():
    return {'name': 'new setup', 'racks': [] }


logging.info('creating setup...')
setup = create_setup()


# WIRING
def unit_in_setup(unit_uuid):
    global setup
    global subprocess_map
    for rack in setup['racks']:
        for unit in rack['units']:
            if unit['uuid'] == unit_uuid:
                return True
    return False

def remove_leftover_subprocesses():
    global subprocess_map
    global setup
    for unit_uuid in list(subprocess_map.keys()):
        if not unit_in_setup(unit_uuid):
            logging.info('removing unit {}'.format(unit_uuid))
            for process in subprocess_map[unit_uuid]:
                process.stdin.close()
                process.terminate()
                # FIXME Make sure the wait time is bounded!
                process.wait()
            del subprocess_map[unit_uuid]

def unit_jack_client_name(unit):
    return '{}-{}'.format(unit['uuid'][0:8], unit['name'])

def switch_unit_jack_client_name(unit):
    return '{}-{}'.format(unit['uuid'][0:8], 'switch')

def manage_subprocesses():
    global setup
    global subprocess_map
    
    for rack in setup['racks']:
        # First let's do the process management
        for unit in rack['units']:
            if unit['type'] == 'lv2':
                if unit['uuid'] not in subprocess_map:
                    subprocess_map[unit['uuid']] = (
                        subprocess.Popen(
                            ['./jack_switch', '-n', switch_unit_jack_client_name(unit)], 
                            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), 
                        subprocess.Popen(
                            ['jalv', '-n', unit_jack_client_name(unit), unit['uri']], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            if unit['type'] == 'special':
                pass
    
    remove_leftover_subprocesses()

def rewire():
    logging.info('rewire')
    global setup
    manage_subprocesses()
    global connections
    connections = []
    for rack in setup['racks']:
        units = rack['units']
        for unit_index in range(0, len(units)):
            unit = units[unit_index]
            if unit['type'] == 'lv2':
                # Internal connections:
                if len(unit['input_audio_ports']) >= 1:
                    connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out00'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][0]['symbol']))) 
                if len(unit['input_audio_ports']) >= 2:
                    connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out01'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][1]['symbol']))) 
        for unit_index in range(1, len(units)):
            logging.debug('unit index {}'.format(unit_index))
            unit = units[unit_index]
            prev_unit = units[unit_index - 1]
            if unit['type'] == 'lv2' and prev_unit['type'] == 'lv2':
                if len(unit['input_audio_ports']) == len(prev_unit['output_audio_ports']):
                    if len(unit['input_audio_ports']) >= 1:
                        connections.append((
                            '{}:{}'.format(switch_unit_jack_client_name(prev_unit), 'out10'),
                            '{}:{}'.format(switch_unit_jack_client_name(unit), 'in0'))) 
                        connections.append((
                            '{}:{}'.format(unit_jack_client_name(prev_unit), prev_unit['output_audio_ports'][0]['symbol']),
                            '{}:{}'.format(switch_unit_jack_client_name(unit), 'in0'))) 
                    if len(unit['input_audio_ports']) >= 2:
                        connections.append((
                            '{}:{}'.format(switch_unit_jack_client_name(prev_unit), 'out11'),
                            '{}:{}'.format(switch_unit_jack_client_name(unit), 'in1'))) 
                        connections.append((
                            '{}:{}'.format(unit_jack_client_name(prev_unit), prev_unit['output_audio_ports'][1]['symbol']),
                            '{}:{}'.format(switch_unit_jack_client_name(unit), 'in1'))) 
                
                
    

ports = []

logging.info('setting up routes...')
@bottle.route('/connect2/<rack_index:int>/<unit_index:int>/<channel_index:int>/<port_index:int>')
def connect2(rack_index, unit_index, channel_index, port_index):
    global setup
    setup['racks'][rack_index]['units'][unit_index]['connections'][channel_index].insert(0,  ports[port_index].name)
    rewire()
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/connect/<rack_index:int>/<unit_index:int>/<channel_index:int>/<direction:path>')
@bottle.view('connect')
def connect(rack_index, unit_index, channel_index, direction):
    global ports
    if direction == 'output':
        ports = jack_client.get_ports(is_input=True, is_audio=True)
        return dict({'ports': ports, 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })
    else:
        ports = jack_client.get_ports(is_output=True, is_audio=True)
        return dict({'ports': ports, 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })

def disconnect0(rack_index, unit_index, channel_index, connection_index):
    global setup
    del setup['racks'][rack_index]['units'][unit_index]['connections'][channel_index][connection_index]
    rewire()

@bottle.route('/disconnect/<rack_index:int>/<unit_index:int>/<channel_index:int>/<connection_index:int>')
def disconnect(rack_index, unit_index, channel_index, connection_index):
    disconnect0(rack_index, unit_index, channel_index, connection_index)
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

# UNITS 

def add_unit0(rack_index, unit_index, uri):
    logging.info('adding unit {}:{} uri {}'.format(rack_index, unit_index, uri))
    unit = units_map[uri]
    unit_type = unit['type']
    input_control_ports = []
    input_audio_ports = []
    output_audio_ports = []
    extra_input_connections = []
    extra_output_connections = []
    direction = ''
    unit_name = unit['name']
    
    if unit_type == unit_type_lv2:
        for port_index in range(len(unit['data']['ports'])):
            port = unit['data']['ports'][port_index]
            if port['http://lv2plug.in/ns/lv2core#InputPort'] and port['http://lv2plug.in/ns/lv2core#AudioPort']:
                logging.debug('input audio port {} {}'.format(port['name'], port['symbol']))
                input_audio_ports.append({ 'name': port['name'], 'symbol': port['symbol']})
                extra_input_connections.append([])

            if port['http://lv2plug.in/ns/lv2core#OutputPort'] and port['http://lv2plug.in/ns/lv2core#AudioPort']:
                logging.debug('output audio port {} {}'.format(port['name'], port['symbol']))
                output_audio_ports.append({ 'name': port['name'], 'symbol': port['symbol']})
                extra_output_connections.append([])

            if port['http://lv2plug.in/ns/lv2core#InputPort'] and port['http://lv2plug.in/ns/lv2core#ControlPort']:
                logging.debug('input control port {} {}'.format(port['name'], port['symbol']))
                control_port = { 'name': port['name'], 'symbol': port['symbol'], 'range': port['range'], 'value': port['range'][0], 'cc': None }
                input_control_ports.append(control_port)

    unit_uuid = str(uuid.uuid4())
    setup['racks'][rack_index]['units'].insert(unit_index, {'type': unit_type, 'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'input_audio_ports': input_audio_ports, 'output_audio_ports': output_audio_ports, 'extra_input_connections': extra_input_connections, 'extra_output_connections': extra_output_connections, 'uuid': unit_uuid, 'direction': direction, 'enabled': True, 'cc': None })

    rewire()

def append_unit0(rack_index, uri):
    add_unit0(rack_index, len(setup['racks'][rack_index]['units']), uri)

@bottle.route('/add/<rack_index:int>/<unit_index:int>/<uri>')
def add_unit(rack_index, unit_index, uri):
    add_unit0(rack_index, unit_index, uri)
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/add2/<rack_index:int>/<unit_index:int>/<units_map_index:int>')
def add_unit2(rack_index, unit_index, units_map_index):
    keys_list = list(units_map)
    add_unit0(rack_index, unit_index, keys_list[units_map_index])
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/add/<rack_index:int>/<unit_index:int>')
@bottle.view('add_unit')
def add_unit(rack_index, unit_index):
    return dict({'units': units_map, 'remaining_path': '/{}/{}'.format(rack_index, unit_index)})

def delete_unit0(rack_index, unit_index):
    global setup
    unit = setup['racks'][rack_index]['units'][unit_index]
    #if unit['type'] == 'special':
    #    pass
    #else:
    #    subprocess_map[unit['uuid']].stdin.close()
    #    del subprocess_map[unit['uuid']]
    del setup['racks'][rack_index]['units'][unit_index]
    rewire()

@bottle.route('/delete/<rack_index:int>/<unit_index:int>')
def delete_unit(rack_index, unit_index):
    global setup
    delete_unit0(rack_index, unit_index)
    bottle.redirect('/#rack-{}'.format(rack_index))


# RACKS

def add_rack0(rack_index):
    global setup
    setup['racks'].insert(int(rack_index), {'enabled': True, 'units': [], 'cc': None})
    rewire()

@bottle.route('/add/<rack_index>')
def add_rack(rack_index):
    add_rack0(rack_index)
    bottle.redirect('/#rack-{}'.format(rack_index))

@bottle.route('/delete/<rack_index>')
def delete_rack(rack_index):
    global setup
    del setup['racks'][int(rack_index)]
    rewire()
    bottle.redirect('/')
    

# DOWNLOADS

@bottle.route('/download')
def download_setup():
    bottle.response.content_type = 'text/json'
    return json.dumps(setup, indent=2)

@bottle.route('/download/<rack_index:int>')
def download_rack(rack_index):
    bottle.response.content_type = 'text/json'
    return json.dumps(setup['racks'][rack_index], indent=2)

@bottle.route('/download/<rack_index:int>/<unit_index:int>')
def download_rack(rack_index, unit_index):
    bottle.response.content_type = 'text/json'
    return json.dumps(setup['racks'][rack_index]['units'][unit_index], indent=2)


# UPLOADS

@bottle.route('/upload2', method='POST')
def upload_setup2():
    upload = bottle.request.files.get('upload')
    upload_contents = io.BytesIO()
    upload.save(upload_contents)
    logging.info(upload_contents.getvalue())
    global setup
    setup = json.loads(upload_contents.getvalue())
    rewire()
    bottle.redirect('/')

@bottle.route('/upload')
@bottle.view('upload')
def upload_setup():
    return dict({'remaining_path': ''})
    


@bottle.route('/')
@bottle.view('index')
def index():
    global setup
    return dict({'setup': setup})


def resetet0():
    global setup
    setup = create_setup()
    rewire()

@bottle.route('/reset')
def resetet():
    resetet0()
    bottle.redirect('/')


@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

midi_in_quit = False
def midi_in():
    global midi_in_quit


    
    while not midi_in_quit:
        pass

connections_manager_quit = False
def connections_manager():
    global connections_manager_quit
    while not connections_manager_quit:
        # logging.info('managing connections...')
        for connection in connections:
            try:
                # jack_client.connect(connection[0], connection[1])
                subprocess.check_call(['jack_connect', connection[0], connection[1]])
            except:
                pass
        time.sleep(1)

logging.info('running connections manager thread...')
connections_manager_thread = threading.Thread(None, connections_manager)
connections_manager_thread.start()

try:
    if True:
        logging.info('adding example data...')
        
        add_rack0(0)
    
        append_unit0(0, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
        append_unit0(0, 'http://guitarix.sourceforge.net/plugins/gx_cabinet#CABINET')
        # append_unit0(0, 'http://gareus.org/oss/lv2/convoLV2#Mono')
        append_unit0(0, 'http://calf.sourceforge.net/plugins/Equalizer5Band')
        # append_unit0(0, 'http://drobilla.net/plugins/mda/DubDelay')
        append_unit0(0, 'http://calf.sourceforge.net/plugins/Reverb')
        append_unit0(0, 'http://plugin.org.uk/swh-plugins/sc4')

        setup['racks'][0]['units'][0]['extra_input_connections'][0].append('system:capture_1')
        
        if False:
            add_rack(0)
            add_unit(0, 0, input_uri)
            setup['racks'][0][0]['connections'].add(0, 'jack#system:capture_1')
            add_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
            add_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
            add_unit(0, len(setup['racks'][0]), output_uri)
            
            add_rack(0)
            add_unit(0, 0, input_uri)
            add_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
            add_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
            add_unit(0, 3, 'http://guitarix.sourceforge.net/plugins/gx_voodoo_#_voodoo_')
            add_unit(0, len(setup['racks'][0]), output_uri)
            
            logging.info(json.dumps(setup))
except KeyError as e:
    logging.error('KeyError: {}'.format(e))
except:
    logging.error('ERRROR!!!!')
    logging.error('Something unspeakable happened!')
    traceback.print_exc()

logging.info('starting bottle server...')
bottle.run(host='0.0.0.0', port='8080', debug=True)

logging.info('shutting down...')

connections_manager_quit = True
setup = create_setup()
rewire()

