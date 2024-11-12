import csv
from datetime import datetime
import itertools
import json
import paho.mqtt.publish as publish
import time


def simulate_valkyrie():

    def parse_date(datestr):
        s = (datestr[:-4]+datestr[-3:])
        return datetime.strptime(s, "%H:%M:%S:%f")

    topics = [['temperature/injector', 'F'],
              ['temperature/vent', 'F'],
              ['temperature/chamber', 'F'],
              ['', ''],
              ['pressure/injector', 'psi'],
              ['pressure/tank', 'psi'],
              ['pressure/feed', 'psi'],
              ['load_cell/1', 'g'],
              ['load_cell/2', 'g']]

    with open('data/Datafile_1.csv') as data_file:
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
                    msgs.append({
                        'topic': topic,
                        'payload': json.dumps({
                            'timestamp':sim_ts.timestamp(), 
                            'units': units, 
                            'value':row[i+1]
                            })
                        })

            publish.multiple(msgs)
            delta = parse_date(next_row[0])-ts
            sim_ts += delta
            time.sleep(delta.total_seconds())

if __name__ == '__main__':
    simulate_valkyrie()
