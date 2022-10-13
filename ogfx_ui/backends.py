import logging
import subprocess
import json
import uuid
import time
import threading
import traceback
import signal

def ignore_sigint():
  signal.signal(signal.SIGINT, signal.SIG_IGN)

class backend:
    def __init__(self, lv2_world):
        self.lv2_world = lv2_world
        self.create_units_map()
        self.setup_filename = 'unnamed.ogfx-setup'
        self.connections = []
        self.lazy_connections = []
        self.unit_cc_bindings = {}
        self.port_cc_bindings = {}
        self.quit_threads = False
        self.create_setup()

    def create_setup(self):
        logging.info("creating (empty default) setup...")
        self.setup = {'racks': [], 'schema-version': 1, 'input_midi_connections': []}
        self.rewire()

    def create_units_map(self):
        self.units_map = dict()

        logging.info('registering lv2 plugins...')
        for p in self.lv2_world:
            num_input_ports = 0
            num_output_ports = 0
            for port in p['ports']:
                if port['http://lv2plug.in/ns/lv2core#InputPort'] and port['http://lv2plug.in/ns/lv2core#AudioPort']:
                    num_input_ports += 1
                if port['http://lv2plug.in/ns/lv2core#OutputPort'] and port['http://lv2plug.in/ns/lv2core#AudioPort']:
                    num_output_ports += 1
            if num_input_ports == 0 or num_output_ports == 0:
                continue
            logging.debug('{} ({}): in: {}, out: {}'.format(p['name'], p['uri'], num_input_ports, num_output_ports))
            # logging.debug('{}'.format(p))
            self.units_map[p['uri']] = {'name': p['name'], 'data': p }

    def add_rack(self, rack_index):
        self.setup['racks'].insert(rack_index, {'enabled': True, 'autoconnect': True, 'units': [], 'cc': None, 'input_connections': [[],[]], 'output_connections': [[],[]]})
        self.rewire()

    def delete_rack(self, rack_index):
        del self.setup['racks'][int(rack_index)]
        self.rewire()

    def unit_in_setup(self, unit_uuid):
        for rack in self.setup['racks']:
            for unit in rack['units']:
                if unit['uuid'] == unit_uuid:
                    return True
        return False

    def add_unit(self, rack_index, unit_index, uri):
        logging.info('adding unit {}:{} uri {}'.format(rack_index, unit_index, uri))
        unit = self.units_map[uri]
        input_control_ports = []
        input_audio_ports = []
        output_audio_ports = []
        extra_input_connections = []
        extra_output_connections = []
        direction = ''
        unit_name = unit['name']

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
                control_port = { 'name': port['name'], 'symbol': port['symbol'], 'range': port['range'], 'value': port['range'][0], 'cc': { 'enabled': False, 'channel': 0, 'cc': 0, 'cc_minimum': 0, 'cc_maximum': 127, 'target_minimum': port['range'][1], 'target_maximum': port['range'][2], 'mode': 'linear'}}
                input_control_ports.append(control_port)

        unit_uuid = str(uuid.uuid4())
        self.setup['racks'][rack_index]['units'].insert(unit_index, {'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'input_audio_ports': input_audio_ports, 'output_audio_ports': output_audio_ports, 'input_connections': extra_input_connections, 'output_connections': extra_output_connections, 'uuid': unit_uuid, 'direction': direction, 'enabled': True, 'cc': { 'enabled': False, 'channel': 0, 'cc': 0}})

        self.rewire()

    def delete_unit(self, rack_index, unit_index):
        unit = self.setup['racks'][rack_index]['units'][unit_index]
        del self.setup['racks'][rack_index]['units'][unit_index]
        self.rewire()

    def setup_midi_maps(self):
        self.unit_cc_bindings = {}

        rack_index = 0
        for rack in self.setup['racks']:
            unit_index = 0
            for unit in rack['units']:
                if unit['cc']['enabled']:
                    channel = unit['cc']['channel']
                    cc = unit['cc']['cc']
                    if not (channel, cc) in self.unit_cc_bindings:
                        self.unit_cc_bindings[(channel, cc)] = []
                    self.unit_cc_bindings[(unit['cc']['channel'], unit['cc']['cc'])].append((rack_index, unit_index))

                unit_index += 1
            rack_index += 1

        self.port_cc_bindings = {}

    def set_unit_midi_cc(self, rack_index, unit_index, enabled, channel, cc):
        logging.debug('set_unit_midi_cc {} {} {} {} {}'.format(rack_index, unit_index, enabled, channel, cc))

        self.setup['racks'][rack_index]['units'][unit_index]['cc']['enabled'] = enabled
        self.setup['racks'][rack_index]['units'][unit_index]['cc']['channel'] = channel
        self.setup['racks'][rack_index]['units'][unit_index]['cc']['cc'] = cc

        # self.setup_midi_maps()

    def set_port_midi_cc(self, rack_index, unit_index, port_index, enabled, channel, cc, minimum, maximum):
        logging.debug('set_port_midi_cc {} {} {} {} {} {}'.format(rack_index, unit_index, port_index, enabled, channel, cc))

        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['cc']['enabled'] = enabled
        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['cc']['channel'] = channel
        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['cc']['cc'] = cc
        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['cc']['target_minimum'] = minimum
        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['cc']['target_maximum'] = maximum

        # self.setup_midi_maps()

    def move_rack_down(self, rack_index):
        racks = self.setup['racks']
        if rack_index >= (len(racks) - 1):
            return

        racks[rack_index + 1], racks[rack_index] = racks[rack_index], racks[rack_index + 1]
        self.rewire()

    def move_rack_up(self, rack_index):
        racks = self.setup['racks']
        if rack_index < 1:
            return

        racks[rack_index - 1], racks[rack_index] = racks[rack_index], racks[rack_index - 1]
        self.rewire()

    def move_unit_down(self, rack_index, unit_index):
        units = self.setup['racks'][rack_index]['units']
        if unit_index >= (len(units) - 1):
            return

        units[unit_index + 1], units[unit_index] = units[unit_index], units[unit_index + 1]
        self.rewire()

    def move_unit_up(self, rack_index, unit_index):
        units = self.setup['racks'][rack_index]['units']
        if unit_index < 1:
            return

        units[unit_index - 1], units[unit_index] = units[unit_index], units[unit_index - 1]
        self.rewire()

    def toggle_rack_active(self, rack_index, active):
        pass
            
    def append_unit(self, rack_index, uri):
        self.add_unit(rack_index, len(self.setup['racks'][rack_index]['units']), uri)
        # add_unit calls rewire()

    def find_jack_ports(self, port_type, direction):
        output = subprocess.check_output(['ogfx_jack_list_ports'])
        all_ports = json.loads(output)
        ports = []
        for port in all_ports:
            if port['type'] == port_type and direction == direction and port[direction] == 1:
                ports.append(port)
        return ports

    def find_jack_audio_ports(self, direction):
        return self.find_jack_ports('32 bit float mono audio', direction)
    
    def find_jack_midi_ports(self, direction):
        return self.find_jack_ports('8 bit raw midi', direction)

    def connect_jack_ports(self, port1, port2):
        try:
            logging.debug('connecting {} -> {}'.format(port1, port2))
            subprocess.check_call(['ogfx_jack_batch_connect', '-c', '[[\"{}\", \"{}\"]]'.format(port1, port2)])
        except:
            logging.debug('failed to connect {} -> {}'.format(port1, port2))
            
    def disconnect_jack_ports(self, port1, port2):
        try:
            logging.debug('discconnecting {} -> {}'.format(port1, port2))
            subprocess.check_call(['jack_disconnect', port1, port2])
        except:
            logging.debug('failed to disconnect {} -> {}'.format(port1, port2))
    
    def disconnect(self, rack_index, unit_index, channel_index, direction, connection_index):
        del self.setup['racks'][rack_index]['units'][unit_index][direction + '_connections'][channel_index][connection_index]
        self.rewire()

    def rewire_update_connections(self, old_connections, new_connections):
        # First remove old connections otherwise we get feedback in order changes :(
        connections_to_be_removed = []
        for connection in old_connections:
            if not connection in new_connections:
                connections_to_be_removed.append(connection)
                # self.disconnect_jack_ports(connection[0], connection[1])

        subprocess.check_call(['ogfx_jack_batch_connect', '-d', '1', '-c', json.dumps(connections_to_be_removed)])

        connections_to_be_made = []
        for connection in new_connections:
            if not connection in old_connections:
                connections_to_be_made.append(connection)
                # self.connect_jack_ports(connection[0], connection[1])

        subprocess.check_call(['ogfx_jack_batch_connect', '-d', '0', '-c', json.dumps(connections_to_be_made)])
 
    def start_threads(self):
        logging.info('running connections manager thread...')
        self.connections_manager_thread = threading.Thread(None, self.connections_manager)
        self.connections_manager_thread.start()

    def stop_threads(self):
        logging.info('telling threads to quit...')
        self.quit_threads = True
        self.connections_manager_thread.join()
        logging.info('threads joined. done.')

    def connections_manager(self):
        while not self.quit_threads:
            time.sleep(1)
            # continue
            # logging.debug('managing connections...')
            for connection in self.lazy_connections:
                try:
                    # logging.debug('connections_manager connecting {} {}'.format(connection[0], connection[1]))
                    # jack_client.connect(connection[0], connection[1])
                    subprocess.check_output(['ogfx_jack_batch_connect', '-c', '[[\"{}\", \"{}\"]]'.format(connection[0], connection[1])], stderr=subprocess.STDOUT)
                except:
                    pass        

    def rewire_port_with_prefix_exists(self, s):
        ports_json_string = subprocess.check_output(['ogfx_jack_list_ports'])
        ports = json.loads(ports_json_string)
        for port in ports:
            if port['name'].find(s) == 0:
                return True

    def rewire(self):
        logging.info('rewire...')
        self.rewire_manage_units()
        old_connections = self.connections
        self.connections = []
        self.lazy_connections = []

        for connection in self.setup['input_midi_connections']:
            self.lazy_connections.append((self.midi_input_port, connection))
            # self.lazy_connections.append(('ogfx_jack_midi_tool:in0', connection))

        for rack_index in range(0, len(self.setup['racks'])):
            rack = self.setup['racks'][rack_index]

            logging.debug('rewiring rack...')
            units = rack['units']
            logging.debug('unit extra connections...')
            for unit_index in range(0, len(units)):
                unit = units[unit_index]
                self.toggle_unit_active(rack_index, unit_index, unit['enabled'])
                logging.debug('connections for unit {}'.format(unit['name']))

                # Initial port values. FIXME: This might reset state modified by MIDI controllers
                port_index = 0
                for port in unit['input_control_ports']:
                    self.set_port_value(rack_index, unit_index, port_index, port['value'])
                    port_index += 1

                # Extra connections
                port_index = 0
                for port_connections in unit['input_connections']:
                    # logging.debug(port)
                    for connection in port_connections:
                        c = [connection, '{}:{}'.format(self.unit_jack_client_name(unit), unit['input_audio_ports'][port_index]['symbol'])]
                        logging.debug(c)
                        self.connections.append(c)
                    port_index += 1
                    
                port_index = 0
                for port_connections in unit['output_connections']:
                    for connection in port_connections:
                        c = ['{}:{}'.format(self.unit_jack_client_name(unit), unit['output_audio_ports'][port_index]['symbol']), connection]
                        logging.debug(c)
                        self.connections.append(c)
                    port_index += 1
                    
                # Internal connections:
                # if len(unit['input_audio_ports']) >= 1:
                #     self.connections.append(('{}:{}'.format(self.switch_unit_jack_client_name(unit), self.switch_output2_ports[0]), '{}:{}'.format(self.unit_jack_client_name(unit), unit['input_audio_ports'][0]['symbol']))) 
                # if len(unit['input_audio_ports']) >= 2:
                #     self.connections.append(('{}:{}'.format(self.switch_unit_jack_client_name(unit), self.switch_output2_ports[1]), '{}:{}'.format(self.unit_jack_client_name(unit), unit['input_audio_ports'][1]['symbol'])))

            logging.debug('rack connections...')
            # input_is_mono = (not not rack['input_connections'][0]) != (not not rack['input_connections'][1])
            # output_is_mono = (not not rack['output_connections'][0]) != (not not rack['output_connections'][1])

            input_connections = []
            output_connections = []
            for channel in range(0,2):
                # FIXME: Is this check necessary?
                if len(rack['input_connections'][channel]):
                    input_connections.append(rack['input_connections'][channel])
                if len(rack['output_connections'][channel]):
                    output_connections.append(rack['output_connections'][channel])

            if len(input_connections) and len(output_connections):
                if len(units) == 0:
                    logging.debug('empty rack')
                    for channel in range(0,2):
                        inputs = input_connections[channel % len(input_connections)]
                        outputs = output_connections[channel % len(output_connections)]
                        for inp in inputs:
                            for outp in outputs:
                                self.connections.append((inp, outp))
                else:
                    logging.debug('non empty rack')
                    logging.debug('input')
                    unit = units[0]
                    for channel in range(0,2):
                        inputs = input_connections[channel % len(input_connections)]
                        for inp in inputs:
                            self.connections.append((inp, '{}:{}'.format(self.unit_jack_client_name(unit), unit['input_audio_ports'][channel % len(unit['input_audio_ports'])]['symbol'])))
                    
                    logging.debug('output')
                    unit = units[-1]
                    for channel in range(0,2):
                        outputs = output_connections[channel % len(output_connections)]
                        for outp in outputs:
                            self.connections.append(('{}:{}'.format(self.switch_unit_jack_client_name(unit), self.switch_output1_ports[channel % len(unit['output_audio_ports'])]), outp))
                            self.connections.append(('{}:{}'.format(self.unit_jack_client_name(unit), unit['output_audio_ports'][channel % len(unit['output_audio_ports'])]['symbol']), outp))

            logging.debug('linear connections...')
            for unit_index in range(1, len(units)):
                logging.debug('unit index {}'.format(unit_index))
                unit = units[unit_index]
                prev_unit = units[unit_index - 1]

                current_ports = len(unit['input_audio_ports'])
                previous_ports = len(prev_unit['output_audio_ports'])
                
                maximum_ports = max(current_ports, previous_ports)
                maximum_ports = min(2, maximum_ports)
                logging.debug('maximum of number of ports of current and previous unit: {}'.format(maximum_ports))

                for port_index in range(0, maximum_ports):
                    current_port = port_index % current_ports
                    previous_port = port_index % previous_ports
                    self.connections.append((
                        '{}:{}'.format(self.unit_jack_client_name(prev_unit), prev_unit['output_audio_ports'][previous_port]['symbol']),
                        '{}:{}'.format(self.unit_jack_client_name(unit), unit['input_audio_ports'][current_port]['symbol']))) 
                       
        self.rewire_update_connections(old_connections, self.connections)
        self.setup_midi_maps()

     

class mod_host(backend):
    def __init__(self, lv2_world):
        self.midi_input_port = 'mod-host:midi_in'
        self.mod_units = []
        self.mod_start_index = 8000
        self.mod_process = subprocess.Popen(["mod-host", "-i"], stdin=subprocess.PIPE, preexec_fn=ignore_sigint)
        self.switch_input_ports = [ "InL", "InR" ]
        self.switch_output1_ports = [ "OUT1L", "OUT1R" ]
        self.switch_output2_ports = [ "Out2L", "Out2R" ]
        backend.__init__(self, lv2_world)

    def __del__(self):
        logging.debug('destructor...')
        self.mod_process.stdin.close()
        self.mod_process.wait()
    
    def setup_midi_maps(self):
        for rack in self.setup['racks']:
            for unit in rack['units']:
                index = 2 * self.mod_units.index(unit['uuid'])
                if unit['cc']['enabled']:
                    self.mod_process.stdin.write('midi_map {} :bypass {} {} 0 1\n'.format(index, unit['cc']['channel'], unit['cc']['cc']).encode('utf-8'))
                    self.mod_process.stdin.flush()
                else:
                    self.mod_process.stdin.write('midi_unmap {} :bypass\n'.format(index, unit['cc']['channel'], unit['cc']['cc']).encode('utf-8'))
                    self.mod_process.stdin.flush()
                for port in unit['input_control_ports']:
                    if port['cc']['enabled']:
                        self.mod_process.stdin.write('midi_map {} {} {} {} {} {}\n'.format(index, port['symbol'], port['cc']['channel'], port['cc']['cc'], port['cc']['target_minimum'], port['cc']['target_maximum']).encode('utf-8'))
                        self.mod_process.stdin.flush()
                    else:
                        self.mod_process.stdin.write('midi_unmap {} {}\n'.format(index, port['symbol']).encode('utf-8'))
                        self.mod_process.stdin.flush()
            
    def set_port_value(self, rack_index, unit_index, port_index, value):
        logging.debug("set port value {} {} {} {}".format(rack_index, unit_index, port_index, value))
        self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['value'] = value
        index = self.mod_units.index(self.setup['racks'][rack_index]['units'][unit_index]['uuid']) * 2
        self.mod_process.stdin.write('param_set {} {} {}\n'.format(index, self.setup['racks'][rack_index]['units'][unit_index]['input_control_ports'][port_index]['symbol'], value).encode('utf-8'))
        self.mod_process.stdin.flush()

    def toggle_unit_active(self, rack_index, unit_index, active):
        logging.debug("toggle unit active {} {} {}".format(rack_index, unit_index, active))
        index = self.mod_units.index(self.setup['racks'][rack_index]['units'][unit_index]['uuid']) * 2
        self.mod_process.stdin.write('bypass {} {}\n'.format(index, (0 if active else 1)).encode('utf-8'))
        # self.mod_process.stdin.write('param_set {} Switch {}\n'.format(index, (1 if active else 0)).encode('utf-8'))
        self.mod_process.stdin.flush()
        self.setup['racks'][rack_index]['units'][unit_index]['enabled'] = bool(active)	
        
       
    def rewire_remove_leftover_units(self):
        logging.debug("removing leftover units...")
        for unit_uuid in self.mod_units:
            if not self.unit_in_setup(unit_uuid):
                index = self.mod_units.index(unit_uuid)
                self.mod_process.stdin.write('remove {}\n'.format(2*index).encode('utf-8'))
                self.mod_process.stdin.write('remove {}\n'.format(2*index+1).encode('utf-8'))
                self.mod_process.stdin.flush()
                self.mod_units[index] = ''

    def rewire_manage_units(self):
        logging.debug('managing subprocesses...')
        for rack in self.setup['racks']:
            # First let's do the process management
            for unit in rack['units']:
                if not unit['uuid'] in self.mod_units:
                    logging.debug("adding plugin: {}".format(unit['uri']))
                    self.mod_process.stdin.write("add {} {} {}\n".format(unit['uri'], 2*len(self.mod_units), self.unit_jack_client_name(unit)).encode('utf-8')) 
                    # self.mod_process.stdin.write("add http://moddevices.com/plugins/mod-devel/switchbox_1-2_st {} {}\n".format(2*len(self.mod_units)+1, self.switch_unit_jack_client_name(unit)).encode('utf-8')) 
                    self.mod_process.stdin.flush()
                    self.mod_units.append(unit['uuid'])

        if len(self.setup['racks']) and len(self.setup['racks'][0]['units']):
            delta_t = 0.1
            t = 0
            while (not self.rewire_port_with_prefix_exists(self.unit_jack_client_name(self.setup['racks'][0]['units'][-2]))) and delta_t < 1:
                time.sleep(delta_t)
                t = t + delta_t
                
            logging.debug('switch ports appeared...')
        self.rewire_remove_leftover_units()

    def unit_jack_client_name(self, unit):
        return '{}-{}'.format(unit['uuid'][0:8], unit['uri'][-54:])

    def switch_unit_jack_client_name(self, unit):
        return '{}-{}-{}'.format(unit['uuid'][0:8], 'switch', unit['uri'][-47:])

    # def unit_jack_client_name(self, unit):
    #     return '{}-{}'.format(unit['uuid'][0:8], unit['uri'])

    # def switch_unit_jack_client_name(self, unit):
    #     return '{}-{}-{}'.format(unit['uuid'][0:8], 'switch', unit['uri'])


    # def unit_jack_client_name(self, unit):
    #     index = self.mod_units.index(unit['uuid'])     
    #     return 'effect_{}'.format(2*index)

    # def switch_unit_jack_client_name(self, unit):
    #     index = self.mod_units.index(unit['uuid'])    
    #     return 'effect_{}'.format(2*index+1)
    #    


