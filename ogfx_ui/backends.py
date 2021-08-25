import logging
import subprocess
import json
import uuid
import time
import threading
import traceback

def unit_jack_client_name(unit):
    return '{}-{}'.format(unit['uuid'][0:8], unit['name'])

def switch_unit_jack_client_name(unit):
    return '{}-{}-{}'.format(unit['uuid'][0:8], 'switch', unit['name'])

class jalv:
    def __init__(self, lv2_world):
        self.lv2_world = lv2_world
        self.create_units_map()
        
        logging.info('creating subprocess map...')

        self.subprocess_map = dict()
        self.connections = []

        self.create_setup()

        self.quit_threads = False

    def connections_manager(self):
        while not self.quit_threads:
            time.sleep(1)
            continue
            logging.debug('managing connections...')
            for connection in self.connections:
                try:
                    logging.debug('connecting {} {}'.format(connection[0], connection[1]))
                    # jack_client.connect(connection[0], connection[1])
                    subprocess.check_call(['jack_connect', connection[0], connection[1]])
                except:
                    pass
        
    def start_threads(self):
        logging.info('running connections manager thread...')
        self.connections_manager_thread = threading.Thread(None, self.connections_manager)
        self.connections_manager_thread.start()

    def stop_threads(self):
        self.quit_threads = True

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
            logging.debug('{}', p)
            self.units_map[p['uri']] = {'name': p['name'], 'data': p }

        
    def create_setup(self):
        logging.info("creating (empty default) setup...")
        self.setup = {'name': 'new setup', 'racks': [], 'schema-version': 1 }
        self.rewire()

    
    def add_rack(self, rack_index):
        self.setup['racks'].insert(rack_index, {'enabled': True, 'units': [], 'cc': None, 'input_connections': [[],[]], 'output_connections': [[],[]]})
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
                control_port = { 'name': port['name'], 'symbol': port['symbol'], 'range': port['range'], 'value': port['range'][0], 'cc': None }
                input_control_ports.append(control_port)

        unit_uuid = str(uuid.uuid4())
        self.setup['racks'][rack_index]['units'].insert(unit_index, {'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'input_audio_ports': input_audio_ports, 'output_audio_ports': output_audio_ports, 'input_connections': extra_input_connections, 'output_connections': extra_output_connections, 'uuid': unit_uuid, 'direction': direction, 'enabled': True, 'cc': None })

        self.rewire()

    def delete_unit(self, rack_index, unit_index):
        unit = self.setup['racks'][rack_index]['units'][unit_index]
        del self.setup['racks'][rack_index]['units'][unit_index]
        self.rewire()

    def set_port_value(self, rack_index, unit_index, port_index, value):
        unit = self.setup['racks'][rack_index]['units'][unit_index]
        try:
            process = self.subprocess_map[unit['uuid']][1]
            symbol = unit['input_control_ports'][port_index]['symbol']
            logging.debug('setting {} to value {}...'.format(symbol, value))
            process.stdin.write('{} = {}\n'.format(symbol, value).encode('utf-8'))
            process.stdin.flush()
            unit['input_control_ports'][port_index]['value'] = value
        except:
            logging.error('failed to set port value...')
            traceback.print_exc()

    def toggle_unit_active(self, rack_index, unit_index, active):
        logging.debug('setting unit active: {} {} -> {}'.format(rack_index, unit_index, active))
        unit = self.setup['racks'][rack_index]['units'][unit_index]
        process = self.subprocess_map[unit['uuid']][0]
        process.stdin.write('{}\n'.format(1 if active else 0).encode('utf-8'))
        process.stdin.flush()
        unit['enabled'] = bool(active)
        
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

    def find_jack_audio_ports(self, direction):
        output = subprocess.check_output(['ogfx_jack_list_ports'])
        all_ports = json.loads(output)
        ports = []
        for port in all_ports:
            if port['type'] == '32 bit float mono audio' and direction == direction and port[direction] == 1:
                ports.append(port)
        return ports
    
    def connect_jack_ports(self, port1, port2):
        try:
            logging.debug('connecting {} -> {}'.format(port1, port2))
            subprocess.check_call(['jack_connect', port1, port2])
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

    def rewire_port_with_prefix_exists(self, s):
        ports_json_string = subprocess.check_output(['ogfx_jack_list_ports'])
        ports = json.loads(ports_json_string)
        for port in ports:
            if port['name'].find(s) == 0:
                return True
        
    def rewire_remove_leftover_subprocesses(self):
        for unit_uuid in list(self.subprocess_map.keys()):
            if not self.unit_in_setup(unit_uuid):
                logging.info('removing unit {}'.format(unit_uuid))
                for process in self.subprocess_map[unit_uuid]:
                    process.stdin.close()
                    time.sleep(0.01)
                    # while not process.returncode:
                    #     process.poll()
                    # process.terminate()
                    # FIXME Make sure the wait time is bounded!
                    process.wait()
                del self.subprocess_map[unit_uuid]

    def rewire_manage_subprocesses(self):
        logging.debug('managing subprocesses...')
        for rack in self.setup['racks']:
            # First let's do the process management
            for unit in rack['units']:
                if unit['uuid'] not in self.subprocess_map:
                    logging.debug('starting subprocess...')
                    # FIXME: investigate why sometimes the jack_switches do not meet their jack
                    # process deadline
                    time.sleep(0.01)
                    p1 = subprocess.Popen(
                            ['stdbuf', '-i0', '-o0', '-e0', 'ogfx_jack_switch', '-n', switch_unit_jack_client_name(unit)], 
                            stdin=subprocess.PIPE) 
                    time.sleep(0.01)
                    p2 = subprocess.Popen(
                            ['stdbuf', '-i0', '-o0', '-e0', 'jalv', '-n', unit_jack_client_name(unit), unit['uri']], 
                            stdin=subprocess.PIPE)
                    self.subprocess_map[unit['uuid']] = (p1, p2)
                    
                    while (not self.rewire_port_with_prefix_exists(switch_unit_jack_client_name(unit))) and (p1.returncode == None):
                        p1.poll()
                        time.sleep(0.01)
                    logging.debug('ogfx_jack_switch ports appeared...')
                    while (not self.rewire_port_with_prefix_exists(unit_jack_client_name(unit))) and (p2.returncode == None):
                        p2.poll()
                        time.sleep(0.01)
                    logging.debug('jalv ports appeared...') 
                    # self.subprocess_map[unit['uuid']][0].stdin.write('1\n'.encode('utf-8'))
                    # self.subprocess_map[unit['uuid']][0].stdin.flush()
        self.rewire_remove_leftover_subprocesses()

    def rewire_update_connections(self, old_connections, new_connections):
        # First remove old connections otherwise we get feedback in order changes :(
        for connection in old_connections:
            if not connection in new_connections:
                self.disconnect_jack_ports(connection[0], connection[1])
        for connection in new_connections:
            if not connection in old_connections:
                self.connect_jack_ports(connection[0], connection[1])
        
    def rewire(self):
        logging.info('rewire...')
        self.rewire_manage_subprocesses()
        old_connections = self.connections
        self.connections = []
        for rack_index in range(0, len(self.setup['racks'])):
            rack = self.setup['racks'][rack_index]
            logging.debug('rewiring rack...')
            units = rack['units']
            logging.debug('internal and extra connections...')
            for unit_index in range(0, len(units)):
                unit = units[unit_index]
                self.toggle_unit_active(rack_index, unit_index, unit['enabled'])
                logging.debug('connections for unit {}'.format(unit['name']))

                port_index = 0
                for port in unit['input_control_ports']:
                    self.set_port_value(rack_index, unit_index, port_index, port['value'])
                    port_index += 1
                # Extra connections
                port_index = 0
                for port in unit['input_connections']:
                    # logging.debug(port)
                    for connection in port:
                        c = [connection, '{}:{}'.format(switch_unit_jack_client_name(unit), 'in{}'.format(port_index))]
                        logging.debug(c)
                        self.connections.append(c)
                    port_index += 1
                    
                port_index = 0
                for port in unit['output_connections']:
                    for connection in port:
                        c = ['{}:{}'.format(unit_jack_client_name(unit), unit['output_audio_ports'][port_index]['symbol']), connection]
                        logging.debug(c)
                        self.connections.append(c)
                    port_index += 1
                    
                # Internal connections:
                if len(unit['input_audio_ports']) >= 1:
                    self.connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out10'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][0]['symbol']))) 
                if len(unit['input_audio_ports']) >= 2:
                    self.connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out11'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][1]['symbol'])))

            logging.debug('rack connections...')
            input_is_mono = (not not rack['input_connections'][0]) != (not not rack['input_connections'][1])
            output_is_mono = (not not rack['output_connections'][0]) != (not not rack['output_connections'][1])

            input_connections = []
            output_connections = []
            for channel in range(0,2):
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
                            self.connections.append((inp, '{}:in{}'.format(switch_unit_jack_client_name(unit), (channel % len(unit['input_audio_ports'])))))
                    
                    logging.debug('output')
                    unit = units[-1]
                    for channel in range(0,2):
                        outputs = output_connections[channel % len(output_connections)]
                        for outp in outputs:
                            self.connections.append(('{}:out0{}'.format(switch_unit_jack_client_name(unit), (channel % len(unit['output_audio_ports']))), outp))
                            self.connections.append(('{}:{}'.format(unit_jack_client_name(unit), unit['output_audio_ports'][channel % len(unit['output_audio_ports'])]['symbol']), outp))

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
                        '{}:{}'.format(switch_unit_jack_client_name(prev_unit), 'out0{}'.format(previous_port)),
                        '{}:{}'.format(switch_unit_jack_client_name(unit), 'in{}'.format(current_port)))) 
                    self.connections.append((
                        '{}:{}'.format(unit_jack_client_name(prev_unit), prev_unit['output_audio_ports'][previous_port]['symbol']),
                        '{}:{}'.format(switch_unit_jack_client_name(unit), 'in{}'.format(current_port)))) 
                       
        self.rewire_update_connections(old_connections, self.connections)




