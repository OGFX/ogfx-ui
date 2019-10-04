#!/usr/bin/python3


import lilv
# import ingen
import bottle
import json
import xdg
import os
import copy
import io

print(os.path.join(xdg.XDG_DATA_HOME, 'ogfx', 'setups'))

lilv_world = lilv.World()
lilv_world.load_all()
lilv_plugins = lilv_world.get_all_plugins()

units_map = dict()
for p in lilv_plugins:
        units_map[str(p.get_uri())] = {'type': 'lv2', 'data': p }


special_units = dict()

# Some special names:
input_uri = 'http://ogfx.fps.io/lv2/ns/input'
units_map[input_uri] = {'type': 'special', 'data': { 'name': 'input', 'connections': [] } }

output_uri = 'http://ogfx.fps.io/lv2/ns/outut'
units_map[output_uri] = {'type': 'special', 'data': { 'name': 'output', 'connections': [] } }

send_uri = 'http://ogfx.fps.io/lv2/ns/send'
units_map[send_uri] = {'type': 'special', 'data': { 'name': 'send', 'connections': [] } }

return_uri = 'http://ogfx.fps.io/lv2/ns/send'
units_map[return_uri] = {'type': 'special', 'data': { 'name': 'return', 'connections': [] } }

unit_type_lv2 = 'lv2'
unit_type_special = 'special'

def create_setup():
    return {'name': 'new setup', 'racks': [] }

setup = create_setup()


# UNITS 

def add_unit0(rack_index, unit_index, uri):
    unit = units_map[uri]
    unit_type = unit['type']
    input_control_ports = []
    connections = []
    unit_name = ''
    if unit_type == unit_type_special:
        unit_name = unit['data']['name']
        connections = unit['data']['connections']

    if unit_type == unit_type_lv2:
        unit_name = str(unit['data'].get_name())
        for port_index in range(unit['data'].get_num_ports()):
            port = unit['data'].get_port_by_index(port_index)
            if port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/ext/atom#InputPort')) or port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/lv2core#ControlPort')):
                lilv_port_range = port.get_range()
                port_range1 = tuple(map(str, lilv_port_range))
                port_range = tuple(map(float, port_range1))
                default_value = port_range[0]
                control_port = { 'name': str(port.get_name()), 'symbol': str(port.get_symbol()), 'range': port_range, 'value': default_value }
                input_control_ports.append(control_port)

    setup['racks'][rack_index].insert(unit_index, {'type': unit_type, 'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'connections': connections })

@bottle.route('/add/<rack_index:int>/<unit_index:int>/<uri>')
def add_unit(rack_index, unit_index, uri):
    add_unit0(rack_index, unit_index, uri)
    bottle.redirect('/#rack-{}-unit-{}'.format(rack_index, unit_index))

@bottle.route('/add/<rack_index:int>/<unit_index:int>')
def add_unit(rack_index, unit_index):
    add_unit0(rack_index, unit_index, input_uri)
    bottle.redirect('/#rack-{}-unit-{}'.format(rack_index, unit_index))

def delete_unit0(rack_index, unit_index):
    global setup
    del setup['racks'][rack_index][unit_index]

@bottle.route('/delete/<rack_index:int>/<unit_index:int>')
def delete_unit(rack_index, unit_index):
    delete_unit0(rack_index, unit_index)
    bottle.redirect('/#rack-{}'.format(rack_index))


# RACKS

def add_rack0(rack_index):
    global setup
    setup['racks'].insert(int(rack_index), [])

@bottle.route('/add/<rack_index>')
def add_rack(rack_index):
    add_rack0(rack_index)
    bottle.redirect('/#rack-{}'.format(rack_index))

@bottle.route('/delete/<rack_index>')
def delete_rack(rack_index):
    global setup
    del setup['racks'][int(rack_index)]
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
    print(upload_contents.getvalue())
    global setup
    setup = json.loads(upload_contents.getvalue())
    bottle.redirect('/')

@bottle.route('/upload')
@bottle.view('upload')
def upload_setup():
    return dict({'remaining_path': ''})
    


@bottle.route('/plugins')
def plugins():
    return '\n'.join(['<p>{}</p>'.format(str(plugin.get_uri())) for plugin in lilv_plugins])

@bottle.route('/')
@bottle.view('index')
def index():
    global setup
    return dict({'setup': setup})


def resetet0():
    global setup
    setup = create_setup()

@bottle.route('/reset')
def resetet():
    resetet0()
    bottle.redirect('/')


@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

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
    
    print(json.dumps(setup))
    
bottle.run(host='0.0.0.0', port='8080', debug=True)

