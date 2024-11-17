# Software-in-the-Loop

## Setup
1. Create Python virtual environment

`$ python -m venv .venv`

2. Activate virtual environment

`$ source .venv/bin/activate`

3. Install Python dependencies

`$ pip install -r requirements.txt`

## Utilities

### Mosquitto Docker Container
Hosts a Mosquitto MQTT broker configured to serve websocket clients.

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
$ python sitl.py
```

### MQTT Echo
Prints all MQTT messages from any topic to the terminal.

Running:
```bash
$ python mqtt_echo.py
```
