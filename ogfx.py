import logging
import subprocess
import json
import uuid
import threading

def unit_jack_client_name(unit):
    return '{}-{}'.format(unit['uuid'][0:8], unit['name'])

def switch_unit_jack_client_name(unit):
    return '{}-{}'.format(unit['uuid'][0:8], 'switch')

class ogfx:
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
            # logging.info('managing connections...')
            for connection in self.connections:
                try:
                    # jack_client.connect(connection[0], connection[1])
                    subprocess.check_call(['jack_connect', connection[0], connection[1]])
                except:
                    pass
                time.sleep(1)
        
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
            logging.debug('{} ({})'.format(p['name'], p['uri']))
            self.units_map[p['uri']] = {'name': p['name'], 'data': p }

        
    def create_setup(self):
        logging.info("creating (empty default) setup...")
        self.setup = {'name': 'new setup', 'racks': [] }
        self.rewire()

    
    def add_rack(self, rack_index):
        self.setup['racks'].insert(rack_index, {'enabled': True, 'units': [], 'cc': None})
        self.rewire()

    def delete_rack(self, rack_index):
        del setup['racks'][int(rack_index)]
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
        self.setup['racks'][rack_index]['units'].insert(unit_index, {'uri': uri, 'name': unit_name, 'input_control_ports': input_control_ports, 'input_audio_ports': input_audio_ports, 'output_audio_ports': output_audio_ports, 'extra_input_connections': extra_input_connections, 'extra_output_connections': extra_output_connections, 'uuid': unit_uuid, 'direction': direction, 'enabled': True, 'cc': None })

        self.rewire()
        
    def append_unit(self, rack_index, uri):
        self.add_unit(rack_index, len(self.setup['racks'][rack_index]['units']), uri)

        
    def remove_leftover_subprocesses(self,):
        for unit_uuid in list(self.subprocess_map.keys()):
            if not self.unit_in_setup(unit_uuid):
                logging.info('removing unit {}'.format(unit_uuid))
                for process in self.subprocess_map[unit_uuid]:
                    process.stdin.close()
                    process.terminate()
                    # FIXME Make sure the wait time is bounded!
                    process.wait()
                del self.subprocess_map[unit_uuid]

    def manage_subprocesses(self):
        for rack in self.setup['racks']:
            # First let's do the process management
            for unit in rack['units']:
                if unit['uuid'] not in self.subprocess_map:
                    self.subprocess_map[unit['uuid']] = (
                        subprocess.Popen(
                            ['./jack_switch', '-n', switch_unit_jack_client_name(unit)], 
                            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), 
                        subprocess.Popen(
                            ['jalv', '-n', unit_jack_client_name(unit), unit['uri']], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        self.remove_leftover_subprocesses()

    def rewire(self):
        logging.info('rewire')
        self.manage_subprocesses()
        connections = []
        for rack in self.setup['racks']:
            units = rack['units']
            for unit_index in range(0, len(units)):
                unit = units[unit_index]
                # Internal connections:
                if len(unit['input_audio_ports']) >= 1:
                    connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out00'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][0]['symbol']))) 
                if len(unit['input_audio_ports']) >= 2:
                    connections.append(('{}:{}'.format(switch_unit_jack_client_name(unit), 'out01'), '{}:{}'.format(unit_jack_client_name(unit), unit['input_audio_ports'][1]['symbol']))) 
            for unit_index in range(1, len(units)):
                logging.debug('unit index {}'.format(unit_index))
                unit = units[unit_index]
                prev_unit = units[unit_index - 1]
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






