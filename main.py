#!/usr/bin/python3


import lilv
# import ingen
import bottle

lilv_world = lilv.World()
lilv_world.load_all()
lilv_plugins = lilv_world.get_all_plugins()

# An array of racks, each rack being an array of plugins, each plugin being a list
# with a plugin URI as first element and then pairs of parameter/value pairs
state = [[['http://guitarix.sourceforge.net/plugins/gxts9#ts9sim', ('fslider0_',  '-16')]]]

@bottle.route('/plugins')
def plugins():
    return '\n'.join(['<p>{}</p>'.format(str(plugin.get_uri())) for plugin in lilv_plugins])

@bottle.route('/')
@bottle.view('index')
def index():
    return dict()

@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

bottle.run(host='0.0.0.0', port='8080')

