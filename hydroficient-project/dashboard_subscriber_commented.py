import json  # JSON decoding
from datetime import datetime  # timestamp formatting

import paho.mqtt.client as mqtt  # MQTT client library

BROKER = "localhost"  # MQTT broker host
PORT = 1884  # MQTT broker port
TOPIC = "hydroficient/grandmarina/#"  # subscribe to all Grand Marina topics


def format_reading(reading):
    # Extract fields from the incoming JSON message
    location = reading.get("location", "unknown")
    device_id = reading.get("device_id", "unknown")
    timestamp = reading.get("timestamp", "unknown")
    counter = reading.get("counter", "?")
    pressure_up = reading.get("pressure_upstream", None)
    pressure_down = reading.get("pressure_downstream", None)
    flow_rate = reading.get("flow_rate", None)
    diff = None

    # Compute pressure differential if both pressure values are present
    if pressure_up is not None and pressure_down is not None:
        try:
            diff = round(float(pressure_up) - float(pressure_down), 1)
        except (ValueError, TypeError):
            diff = None

    lines = [
        "────────────────────────────────────────",
        f"  Location:  {location}",
        f"  Device ID: {device_id}",
        f"  Time:      {timestamp}",
        f"  Count:     #{counter}",
        "────────────────────────────────────────",
    ]

    # Add formatted pressure and flow lines
    if pressure_up is not None:
        lines.append(f"  Pressure (upstream):    {pressure_up} PSI")
    else:
        lines.append("  Pressure (upstream):    N/A")

    if pressure_down is not None:
        lines.append(f"  Pressure (downstream):  {pressure_down} PSI")
    else:
        lines.append("  Pressure (downstream):  N/A")

    if flow_rate is not None:
        lines.append(f"  Flow rate:              {flow_rate} gal/min")
    else:
        lines.append("  Flow rate:              N/A")

    if diff is not None:
        lines.append(f"  Pressure differential:   {diff} PSI")
    else:
        lines.append("  Pressure differential:   N/A")

    return "\n".join(lines)  # return the formatted block of text


def on_connect(client, userdata, flags, rc):
    # Called when the client connects to the broker
    if rc == 0:
        connected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("============================================================")
        print("  GRAND MARINA WATER MONITORING DASHBOARD")
        print(f"  Connected at: {connected_at}")
        print("============================================================\n")
        client.subscribe(TOPIC)  # subscribe to the wildcard topic
    else:
        print(f"Connection failed with result code {rc}")


def on_message(client, userdata, msg):
    # Called whenever a message is received on a subscribed topic
    payload = msg.payload.decode("utf-8", errors="replace")

    try:
        reading = json.loads(payload)  # parse JSON payload
    except json.JSONDecodeError:
        print(f"Received non-JSON message on {msg.topic}: {payload}")
        return

    print(format_reading(reading))  # print the formatted reading


if __name__ == "__main__":
    client = mqtt.Client()  # create MQTT client
    client.on_connect = on_connect  # set connect callback
    client.on_message = on_message  # set message callback

    client.connect(BROKER, PORT)  # connect to the broker
    client.loop_forever()  # process network events forever
