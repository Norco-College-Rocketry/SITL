# Software-in-the-Loop

## Utilities

### Mosquitto Docker Container
Hosts a Mosquitto MQTT broker.

Running: 
```
$ cd docker/mosquitto
$ sudo docker compose up -d
$ cd ../../
```

### Simulated Telemetry MQTT Publisher
Publishes a telemetry replay of data recorded during a static fire test of Valkyrie.

Running:
``` bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python sitl.py
```
