#!/usr/bin/python3


import lilv
# import ingen
import bottle
import json

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

setup = {'name': 'new setup', 'racks': [] }

@bottle.route('/insert_unit/<rack_index>/<unit_index>/<uri>')
def insert_unit(rack_index, unit_index, uri):
    unit = units_map[uri]
    unit_type = unit['type']
    input_control_ports = []
    unit_name = ''
    if unit_type == unit_type_special:
        unit_name = unit['data']['name']

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

    setup['racks'][rack_index].insert(unit_index, {'type': unit_type, 'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports })

# Add a rack BEFORE the index
@bottle.route('/insert_rack/<rack_index')
def insert_rack(rack_index):
    setup['racks'].insert(rack_index, [])


@bottle.route('/plugins')
def plugins():
    return '\n'.join(['<p>{}</p>'.format(str(plugin.get_uri())) for plugin in lilv_plugins])

@bottle.route('/')
@bottle.view('index')
def index():
    return dict({'setup': setup})

@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

insert_rack(0)
insert_unit(0, 0, input_uri)
insert_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
insert_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
insert_unit(0, len(setup['racks'][0]), output_uri)

insert_rack(0)
insert_unit(0, 0, input_uri)
insert_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
insert_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
insert_unit(0, len(setup['racks'][0]), output_uri)

print(json.dumps(setup, indent=2))

bottle.run(host='0.0.0.0', port='8080', debug=True)

