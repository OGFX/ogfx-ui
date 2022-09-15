import logging
import subprocess
import json
import uuid
import time
import threading
import traceback
import signal

class jalv(backend):
    def __init__(self, lv2_world):
        logging.info('creating subprocess map...')
        self.midi_input_port = 'ogfx_jack_midi_tool:in0'
        self.subprocess_map = dict()
        backend.__init__(self, lv2_world)

    def midi_manager(self):
        logging.debug('running ogfx_jack_midi_tool process...')
        with subprocess.Popen(['ogfx_jack_midi_tool'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=ignore_sigint) as p1:
            while not self.quit_threads:
                time.sleep(0.001)
                # continue
                p1.stdin.write('\n'.encode('utf-8'))
                p1.stdin.flush()
                line = p1.stdout.readline().decode('utf-8')
                if len(line) > 0 and line != '\n':
                    # logging.debug('got a line: {}'.format(line))
                    # continue
                    parts = line.split()
                    # logging.debug('parts {} {}'.format(parts, len(parts)))
                    if not (len(parts) == 3):
                        # logging.debug('not len == 3 ????')
                        continue
                    # logging.debug('getting the bytes...')
                    the_bytes = [int(parts[0]), int(parts[1]), int(parts[2])]
                    # logging.debug('the bytes: {}'.format(the_bytes))
                    if not (the_bytes[0] & 176 == 176):
                        continue
                    channel = the_bytes[0] - 176
                    cc = the_bytes[1]
                    value = the_bytes[2]
                    logging.debug('cc: {} {} {}'.format(channel, cc, value))
                    if not (channel, cc) in self.unit_cc_bindings:
                        continue

                    bindings = self.unit_cc_bindings[(channel, cc)]
                    for binding in bindings:
                        logging.debug('binding {} {}'.format(binding[0], binding[1]))
                        self.toggle_unit_active(binding[0], binding[1], True if (value > 0) else False)

            logging.debug('telling ogfx_jack_midi_tool process to quit...')
            p1.stdin.write('quit\n'.encode('utf-8'))
            p1.stdin.flush()
            logging.debug('waiting for ogfx_jack_midi_tool to exit...')
            while p1.poll() == None:
                logging.debug('still waiting...')
                time.sleep(0.1)
            p1.kill()
            logging.debug('midi_manager done.')
    
    def start_threads(self):
        logging.info('running midi manager thread...')
        self.midi_manager_thread = threading.Thread(None, self.midi_manager)
        self.midi_manager_thread.start()
        backend.start_threads(self)

    def stop_threads(self):
        backend.stop_threads(self)
        self.midi_manager_thread.join()
        logging.info('threads joined. done.')
        
   
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
        
    def rewire_port_with_prefix_exists(self, s):
        ports_json_string = subprocess.check_output(['ogfx_jack_list_ports'])
        ports = json.loads(ports_json_string)
        for port in ports:
            if port['name'].find(s) == 0:
                return True
        
    def rewire_remove_leftover_units(self):
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

    def rewire_manage_units(self):
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
                            ['stdbuf', '-i0', '-o0', '-e0', 'ogfx_jack_switch', '-n', self.switch_unit_jack_client_name(unit)], 
                            stdin=subprocess.PIPE, preexec_fn=ignore_sigint) 
                    time.sleep(0.01)
                    p2 = subprocess.Popen(
                            ['stdbuf', '-i0', '-o0', '-e0', 'jalv', '-n', self.unit_jack_client_name(unit), unit['uri']], 
                            stdin=subprocess.PIPE, preexec_fn=ignore_sigint)
                    self.subprocess_map[unit['uuid']] = (p1, p2)
                    
                    while (not self.rewire_port_with_prefix_exists(self.switch_unit_jack_client_name(unit))) and (p1.returncode == None):
                        p1.poll()
                        time.sleep(0.01)
                    logging.debug('ogfx_jack_switch ports appeared...')
                    while (not self.rewire_port_with_prefix_exists(self.unit_jack_client_name(unit))) and (p2.returncode == None):
                        p2.poll()
                        time.sleep(0.01)
                    logging.debug('jalv ports appeared...') 
                    # self.subprocess_map[unit['uuid']][0].stdin.write('1\n'.encode('utf-8'))
                    # self.subprocess_map[unit['uuid']][0].stdin.flush()
        self.rewire_remove_leftover_subprocesses()

       

    def unit_jack_client_name(self, unit):
        return '{}-{}'.format(unit['uuid'][0:8], unit['name'])

    def switch_unit_jack_client_name(self, unit):
        return '{}-{}-{}'.format(unit['uuid'][0:8], 'switch', unit['name'])



