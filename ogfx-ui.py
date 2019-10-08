#!/usr/bin/python3


import lilv
import bottle
import json
import xdg
import os
import copy
import io
import subprocess
import uuid
import jack
import logging
import rtmidi
import argparse

arguments_parser = argparse.ArgumentParser(description='ogfx-ui - a web interface for OGFX')
arguments_parser.add_argument('--log-level', type=int, dest='log_level', help='5: DEBUG, 4: INFO, 3: WARNING, 2: ERROR, 1: CRITICAL, default: %(default)s', action='store', default=3)
arguments_parser.add_argument('--setup', dest='setup', action='store', help='A file containing a setup to load at startup')


arguments = arguments_parser.parse_args()


log_levels_map = {1: logging.DEBUG, 2: logging.INFO, 3: logging.WARNING, 4: logging.ERROR, 5: logging.CRITICAL}

logging.basicConfig(level=log_levels_map[arguments.log_level], format='%(asctime)s %(message)s')

logging.info(os.path.join(xdg.XDG_DATA_HOME, 'ogfx', 'setups'))


logging.info('-> creating jack client...')
jack_client = jack.Client('OGFX')

units_map = dict()

logging.info('-> registering special units...')
special_units = dict()

# Some special names:
mono_input_uri = 'http://ogfx.fps.io/lv2/ns/mono_input'
units_map[mono_input_uri] = {'type': 'special', 'name': 'mono_input', 'direction': 'input', 'data': { 'connections': [[]] } }

mono_output_uri = 'http://ogfx.fps.io/lv2/ns/mono_output'
units_map[mono_output_uri] = {'type': 'special', 'name': 'mono_output', 'direction': 'output', 'data': { 'connections': [[]] } }

stereo_input_uri = 'http://ogfx.fps.io/lv2/ns/stereo_input'
units_map[stereo_input_uri] = {'type': 'special', 'name': 'stereo_input', 'direction': 'input', 'data': { 'connections': [[], []] } }

stereo_output_uri = 'http://ogfx.fps.io/lv2/ns/stereo_outut'
units_map[stereo_output_uri] = {'type': 'special', 'name': 'stereo_output', 'direction': 'output', 'data': { 'connections': [[], []] } }

mono_send_uri = 'http://ogfx.fps.io/lv2/ns/mono_send'
units_map[mono_send_uri] = {'type': 'special', 'name': 'mono_send', 'direction': 'output', 'data': { 'connections': [[]] } }

mono_return_uri = 'http://ogfx.fps.io/lv2/ns/mono_return'
units_map[mono_return_uri] = {'type': 'special', 'name': 'mono_return', 'direction': 'input', 'data': { 'connections': [[]] } }

stereo_send_uri = 'http://ogfx.fps.io/lv2/ns/stereo_send'
units_map[stereo_send_uri] = {'type': 'special', 'name': 'stereo_send', 'direction': 'output', 'data': { 'connections': [[], []] } }

stereo_return_uri = 'http://ogfx.fps.io/lv2/ns/stereo_return'
units_map[stereo_return_uri] = {'type': 'special', 'name': 'stereo_return', 'direction': 'input', 'data': { 'connections': [[], []] } }

unit_type_lv2 = 'lv2'
unit_type_special = 'special'

logging.info('-> creating lilv world...')
lilv_world = lilv.World()
logging.info('-> load_all...')
lilv_world.load_all()
logging.info('-> get_all_plugins...')
lilv_plugins = lilv_world.get_all_plugins()

logging.info('-> registering lv2 plugins...')
for p in lilv_plugins:
    # logging.info(str(p.get_uri()))
    logging.debug(str(p.get_uri()))
    units_map[str(p.get_uri())] = {'type': 'lv2', 'name': str(p.get_name()), 'data': p }

logging.info('-> creating subprocess map...')

subprocess_map = dict()


def create_setup():
    return {'name': 'new setup', 'racks': [] }


logging.info('-> creating setup...')
setup = create_setup()


# WIRING
def rewire():
    logging.info('-> rewire')
    global setup

logging.info('-> setting up routes...')
@bottle.route('/connect2/<rack_index:int>/<unit_index:int>/<channel_index:int>', method='POST')
def connect2(rack_index, unit_index, channel_index):
    global setup
    setup['racks'][rack_index][unit_index]['connections'][channel_index].insert(0,  bottle.request.forms.get('port'))
    rewire()
    bottle.redirect('/#unit-{}-{}'.format(rack_index, unit_index))

@bottle.route('/connect/<rack_index:int>/<unit_index:int>/<channel_index:int>/<direction:path>')
@bottle.view('connect')
def connect(rack_index, unit_index, channel_index, direction):
    if direction == 'output':
        return dict({'ports': jack_client.get_ports(is_input=True, is_audio=True), 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })
    else:
        return dict({'ports': jack_client.get_ports(is_output=True, is_audio=True), 'remaining_path': '/{}/{}/{}'.format(rack_index, unit_index, channel_index) })

def disconnect0(rack_index, unit_index, channel_index, connection_index):
    global setup
    del setup['racks'][rack_index][unit_index]['connections'][channel_index][connection_index]
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
    connections = []
    direction = ''
    unit_name = unit['name']
    if unit_type == unit_type_special:
        connections = copy.copy(unit['data']['connections'])
        direction = unit['direction']

    if unit_type == unit_type_lv2:
        for port_index in range(unit['data'].get_num_ports()):
            port = unit['data'].get_port_by_index(port_index)
            if port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/ext/atom#InputPort')) or port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/lv2core#ControlPort')):
                logging.debug('port {} {}'.format(str(port.get_name()), str(port.get_symbol())))
                port_range = [0, -1, 1]
                lilv_port_range = port.get_range()
                if lilv_port_range[0] is not None:
                    port_range[0] = float(str(lilv_port_range[0]))
                if lilv_port_range[1] is not None:
                    port_range[1] = float(str(lilv_port_range[1]))
                if lilv_port_range[2] is not None:
                    port_range[2] = float(str(lilv_port_range[2]))
                default_value = port_range[0]
                control_port = { 'name': str(port.get_name()), 'symbol': str(port.get_symbol()), 'range': port_range, 'value': default_value }
                input_control_ports.append(control_port)

    unit_uuid = str(uuid.uuid4())
    # subprocess_map[unit_uuid] = subprocess.Popen(['jalv', '-n', '{}-{}'.format(unit_uuid[0:8], unit_name), uri], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    setup['racks'][rack_index].insert(unit_index, {'type': unit_type, 'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'connections': connections, 'uuid': unit_uuid, 'direction': direction })

    rewire()

def append_unit0(rack_index, uri):
    add_unit0(rack_index, len(setup['racks'][rack_index]), uri)

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
    unit = setup['racks'][rack_index][unit_index]
    #if unit['type'] == 'special':
    #    pass
    #else:
    #    subprocess_map[unit['uuid']].stdin.close()
    #    del subprocess_map[unit['uuid']]
    del setup['racks'][rack_index][unit_index]
    rewire()

@bottle.route('/delete/<rack_index:int>/<unit_index:int>')
def delete_unit(rack_index, unit_index):
    global setup
    delete_unit0(rack_index, unit_index)
    bottle.redirect('/#rack-{}'.format(rack_index))


# RACKS

def add_rack0(rack_index):
    global setup
    setup['racks'].insert(int(rack_index), [])
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
    return json.dumps(setup['racks'][rack_index][unit_index], indent=2)


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

logging.info('-> adding example data...')

add_rack0(0)

append_unit0(0, mono_input_uri)
append_unit0(0, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
append_unit0(0, 'http://guitarix.sourceforge.net/plugins/gx_cabinet#CABINET')
append_unit0(0, 'http://gareus.org/oss/lv2/convoLV2#Mono')
append_unit0(0, 'http://calf.sourceforge.net/plugins/Equalizer5Band')
append_unit0(0, 'http://drobilla.net/plugins/mda/DubDelay')
append_unit0(0, 'http://calf.sourceforge.net/plugins/Reverb')
append_unit0(0, 'http://plugin.org.uk/swh-plugins/sc4')
append_unit0(0, 'http://plugin.org.uk/swh-plugins/amp')
append_unit0(0, stereo_output_uri)

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
    

logging.info('-> starting bottle server...')
bottle.run(host='0.0.0.0', port='8080', debug=True)


for key, value in subprocess_map.items():
    logging.info('terminating subprocess {}'.format(key))
    value.stdin.close()
    value.terminate()
    value.wait()

