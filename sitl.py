import csv
from datetime import datetime, UTC
import itertools
import json
import paho.mqtt.client as mqtt
import time
import os
from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from dotenv import load_dotenv
import asyncio

async def simulate_valkyrie(mqttc, write_api, bucket, org, measurement):
    def parse_date(datestr):
        s = (datestr[:-4]+datestr[-3:])
        return datetime.strptime(s, "%H:%M:%S:%f")

    metadata = [{'location':'injector', 'field':'temperature', 'topic':'telemetry/injector/temperature', 'unit':'F'},
                {'location':'vent',     'field':'temperature', 'topic':'telemetry/vent/temperature',     'unit':'F'},
                {'location':'chamber',  'field':'temperature', 'topic':'telemetry/chamber/temperature',  'unit':'F'},
                {'location':'injector', 'field':'pressure',    'topic':'telemetry/injector/pressure',    'unit':'psi'},
                {'location':'tank',     'field':'pressure',    'topic':'telemetry/tank/pressure',        'unit':'psi'},
                {'location':'feed',     'field':'pressure',    'topic':'telemetry/feed/pressure',        'unit':'psi'},
                {'location':'1',        'field':'weight',      'topic':'telemetry/weight/1',             'unit':'kg'},
                {'location':'2',        'field':'weight',      'topic':'telemetry/weight/2',             'unit':'kg'}]

    source_dir = os.path.dirname(os.path.realpath(__file__)) # Find data file relative to script directory
    filename = os.path.join(source_dir, 'data', 'Datafile_1.csv')
    tasks = set()
    with open(filename) as data_file:
        reader = csv.reader(data_file)
        header = next(reader)
        elide = header.index(' N/A')
        sim_ts = datetime.now(UTC)
        for (row, next_row) in itertools.pairwise(reader):
            del row[elide] # Remove unused column
            ts = parse_date(row[0])
            print(sim_ts)

            msgs = []
            points = []
            for i in range(0, len(row)-1):
                topic = metadata[i]['topic']
                unit = metadata[i]['unit']
                value = float(row[i+1])
            
                if (metadata[i]['field'] == 'weight'):
                    # Convert to kg
                    value /= 1000

                # Create Influx point
                points.append(Point(measurement).tag('location', metadata[i]['location']).field(metadata[i]['field'], value).time(sim_ts))

                # Create MQTT message
                msgs.append({
                    'topic': topic,
                    'payload': json.dumps({
                        'timestamp': sim_ts.timestamp()*1000, 
                        'value': value,
                        'unit': unit
                        })
                    })

            # Write to InfluxDB
            task = asyncio.create_task(write_api.write(bucket=bucket, record=points))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
            # Publish to MQTT
            for msg in msgs:
                mqttc.publish(msg['topic'], msg['payload'])

            # Progress simulation time
            delta = parse_date(next_row[0])-ts
            sim_ts += delta
            time.sleep(delta.total_seconds())

    while len(tasks) != 0:
        await tasks.pop()

async def main():
    load_dotenv()

    url = os.getenv('INFLUX_URL')
    bucket = os.getenv('INFLUX_BUCKET')
    org = os.getenv('INFLUX_ORG')
    token = os.getenv('INFLUX_TOKEN')
    measurement = 'sitl'

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect('localhost')

    async with InfluxDBClientAsync(url=url, token=token, org=org) as client:
        await simulate_valkyrie(mqttc, client.write_api(), bucket, org, measurement)

if __name__ == '__main__':
    asyncio.run(main())
