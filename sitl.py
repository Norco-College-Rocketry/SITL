import csv
from datetime import datetime
import itertools
import json
import paho.mqtt.publish as publish
import time
import os


def simulate_valkyrie():

    def parse_date(datestr):
        s = (datestr[:-4]+datestr[-3:])
        return datetime.strptime(s, "%H:%M:%S:%f")

    topics = [['telemetry/injector/temperature', 'F'],
              ['telemetry/vent/temperature', 'F'],
              ['telemetry/chamber/temperature', 'F'],
              ['', ''],
              ['telemetry/injector/pressure', 'psi'],
              ['telemetry/tank/pressure', 'psi'],
              ['telemetry/feed/pressure', 'psi'],
              ['telemetry/weight/1', 'kg'],
              ['telemetry/weight/2', 'kg']]

    source_dir = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(source_dir, 'data', 'Datafile_1.csv')
    with open(filename) as data_file:
        reader = csv.reader(data_file)
        next(reader)
        sim_ts = datetime.now()
        for (row, next_row) in itertools.pairwise(reader):
            ts = parse_date(row[0])
            print(sim_ts)
            msgs = []
            for i in range(0, len(row)-1):
                topic = topics[i][0]
                units = topics[i][1]
                if topic != '':
                    value = float(row[i+1])
                    if (topic[:-2] == 'telemetry/weight'):
                        # Convert to kg
                        value /= 1000
                    msgs.append({
                        'topic': topic,
                        'payload': json.dumps({
                            'timestamp': sim_ts.timestamp()*1000, 
                            'value': value,
                            'unit': units 
                            })
                        })

            publish.multiple(msgs)
            delta = parse_date(next_row[0])-ts
            sim_ts += delta
            time.sleep(delta.total_seconds())

if __name__ == '__main__':
    simulate_valkyrie()
