import logging
import subprocess
import json

class ogfx:
    def __init__(self, lv2_world):
        self.lv2_world = lv2_world
        
        self.units_map = dict()

        logging.info('registering special units...')
        self.special_units = dict()

        self.unit_type_lv2 = 'lv2'
        self.unit_type_special = 'special'

        logging.info('registering lv2 plugins...')
        for p in self.lv2_world:
            # logging.info(str(p.get_uri()))
            logging.debug('{} ({})'.format(p['name'], p['uri']))
            self.units_map[p['uri']] = {'type': 'lv2', 'name': p['name'], 'data': p }

        logging.info('creating subprocess map...')

        self.subprocess_map = dict()
        self.connections = []

        self.setup = self.create_setup()
        
    def create_setup(self):
        logging.info("creating setup...")
        return {'name': 'new setup', 'racks': [] }

    
