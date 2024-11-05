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

    topics = ['temperature/injector', 'temperature/vent', 'temperature/combustion', '', 'pressure/injector', 'pressure/tank', 'pressure/feed',  'load_cell/1', 'load_cell/2']

    with open('data/Datafile_1.csv') as data_file:
        reader = csv.reader(data_file)
        next(reader)
        sim_ts = datetime.now()
        for (row, next_row) in itertools.pairwise(reader):
            ts = parse_date(row[0])
            print(sim_ts)
            msgs = []
            for i in range(len(row)-1):
                if topics[i] != '':
                    msgs.append({'topic':topics[i], 'payload':json.dumps({'timestamp':sim_ts.timestamp(), 'value':row[i+1]})})

            publish.multiple(msgs)
            delta = parse_date(next_row[0])-ts
            sim_ts += delta
            time.sleep(delta.total_seconds())

if __name__ == '__main__':
    simulate_valkyrie()
