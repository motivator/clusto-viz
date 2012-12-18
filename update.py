#!/usr/bin/env python
import sqlite3
import time
from clusto import script_helper
import clusto
import json
import sys

class Update(script_helper.Script):
    def __init__(self):
        script_helper.Script.__init__(self)

    def update_racks(self):
        result = {}
    
        for datacenter in clusto.get_entities(clusto_types=['datacenter']):
            for cage in datacenter.contents(clusto_types=['cage']):
                for rack in cage.contents(clusto_types=['rack']):
                    devices = []
                    for ru in range(45, 0, -1):
                        device = rack.get_device_in(ru)
                        if device:
                            devices.append((ru, device.name, device.type, ' '.join([x.name for x in device.parents(clusto_types=['pool'])])))
                        else:
                            devices.append((ru, None, None, ''))
    
                    if not datacenter.name in result:
                        result[datacenter.name] = []
                    result[datacenter.name].append((rack.name, devices))
                result[datacenter.name].sort(key=lambda x: x[0])
    
        result = json.dumps(result)
        file('/home/synack/src/clusto-viz/result.json', 'w').write(result)
    
    def update_count(self):
        conn = sqlite3.connect('/Users/mike/tmp/clusto-viz/pools.db')
        c = conn.cursor()
        now = int(time.time())
    
        for pool in clusto.get_entities(clusto_types=['pool']):
            c.execute('INSERT INTO counts(name, ts, count) VALUES (?, ?, ?)', (pool.name, now, len(pool.contents())))
        conn.commit()
        c.close()
   
    def run(self):
        self.update_racks()
        self.update_count()

def main():
    update, args = script_helper.init_arguments(Update)
    return(update.run(args))

if __name__ == '__main__':
    sys.exit(main())
