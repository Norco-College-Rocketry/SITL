import csv
from datetime import datetime, UTC
import itertools
import json
import paho.mqtt.publish as publish
import time
import os
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

def simulate_valkyrie(write_api):

    def parse_date(datestr):
        s = (datestr[:-4]+datestr[-3:])
        return datetime.strptime(s, "%H:%M:%S:%f")

    points = [influxdb_client.Point(measurement).tag('location', 'injector'),
              influxdb_client.Point(measurement).tag('location', 'vent'),
              influxdb_client.Point(measurement).tag('location', 'chamber'),
              influxdb_client.Point(measurement),
              influxdb_client.Point(measurement).tag('location', 'injector'),
              influxdb_client.Point(measurement).tag('location', 'tank'),
              influxdb_client.Point(measurement).tag('location', 'feed'),
              influxdb_client.Point(measurement).tag('location', '1'),
              influxdb_client.Point(measurement).tag('location', '2')]

    fields = ['temperature', 
              'temperature',
              'temperature',
              '',
              'pressure',
              'pressure',
              'pressure',
              'weight',
              'weight']

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
        sim_ts = datetime.now(UTC)
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

                    # Write to InfluxDB
                    p = points[i].field(fields[i], value).time(sim_ts)
                    write_api.write(bucket=bucket, org=org, record=p)

                    # Create MQTT message
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

    load_dotenv()

    url = os.getenv('INFLUX_URL')
    bucket = os.getenv('INFLUX_BUCKET')
    org = os.getenv('INFLUX_ORG')
    token = os.getenv('INFLUX_TOKEN')
    measurement = 'sitl'

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    simulate_valkyrie(client.write_api(write_options=SYNCHRONOUS))
