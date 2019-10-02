#!/usr/bin/python3


import lilv
# import ingen
import bottle

lilv_world = lilv.World()
lilv_world.load_all()
lilv_plugins = lilv_world.get_all_plugins()

plugins_map = dict()
for p in lilv_plugins:
        plugins_map[str(p.get_uri())] = p


special_units = dict()

# Some special names:
input_uri = 'http://ogfx.fps.io/lv2/ns/input'
special_units[input_uri] = {'name': 'input' }

output_uri = 'http://ogfx.fps.io/lv2/ns/outut'
special_units[output_uri] = {'name': 'output' }

send_uri = 'http://ogfx.fps.io/lv2/ns/send'
special_units[send_uri] = {'name': 'send'}

return_uri = 'http://ogfx.fps.io/lv2/ns/send'
special_units[return_uri] = {'name': 'return' }



# An array of racks, each rack being an array of plugins, each plugin being a list
# with a plugin URI as first element and then pairs of parameter/value pairs
# racks = [[[plugins_map['http://guitarix.sourceforge.net/plugins/gxts9#ts9sim'], ('fslider0_',  '-16')]]]
racks = []

@bottle.route('/insert_unit/<rack_index>/<unit_index>/<uri>')
def insert_unit(rack_index, unit_index, uri):
    if uri == input_uri or uri == output_uri or uri == send_uri or uri == return_uri:
        racks[rack_index].insert(unit_index, (uri, special_units[uri]['name'], []))
        return

    control_ports = []
    plugin = plugins_map[uri]
    for port_index in range(plugin.get_num_ports()):
        port = plugin.get_port_by_index(port_index)
        if port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/ext/atom#InputPort')) or port.is_a(lilv_world.new_uri('http://lv2plug.in/ns/lv2core#ControlPort')):
            port_range = port.get_range()
            control_ports.append((port.get_name(), port.get_symbol(), port_range, port.get_scale_points(), port_range[0]))

    racks[rack_index].insert(unit_index, (uri, plugins_map[uri].get_name(), control_ports))

# Add a rack BEFORE the index
@bottle.route('/insert_rack/<rack_index')
def insert_rack(rack_index):
    racks.insert(rack_index, [])

@bottle.route('/plugins')
def plugins():
    return '\n'.join(['<p>{}</p>'.format(str(plugin.get_uri())) for plugin in lilv_plugins])

@bottle.route('/')
@bottle.view('index')
def index():
    return dict({'racks': racks})

@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

insert_rack(0)
insert_unit(0, 0, input_uri)
insert_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
insert_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
insert_unit(0, len(racks[0]), output_uri)

insert_rack(0)
insert_unit(0, 0, input_uri)
insert_unit(0, 1, 'http://guitarix.sourceforge.net/plugins/gxts9#ts9sim')
insert_unit(0, 2, 'http://guitarix.sourceforge.net/plugins/gx_amp_stereo#GUITARIX_ST')
insert_unit(0, len(racks[0]), output_uri)

bottle.run(host='0.0.0.0', port='8080', debug=True)

