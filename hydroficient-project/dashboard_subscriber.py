import json  # JSON decoding for received messages
from datetime import datetime  # timestamp formatting for dashboard
from pathlib import Path
import ssl
import paho.mqtt.client as mqtt  # MQTT client library

# ============================================
# TLS CONFIGURATION - ADD THIS FOR TLS
# ============================================
TLS_CONFIG = {
    "ca_certs": "certs/ca.pem",
    "broker_host": "localhost",
    "broker_port": 8883,
}
# ============================================

TOPIC = "hydroficient/grandmarina/#"  # subscribe to all Grand Marina topics


def format_reading(reading):
    location = reading.get("location", "unknown")  # safe read for location
    device_id = reading.get("device_id", "unknown")  # safe read for device ID
    timestamp = reading.get("timestamp", "unknown")  # safe read for timestamp
    counter = reading.get("counter", "?")  # safe read for count
    pressure_up = reading.get("pressure_upstream", None)  # optional upstream pressure
    pressure_down = reading.get("pressure_downstream", None)  # optional downstream pressure
    flow_rate = reading.get("flow_rate", None)  # optional flow rate
    diff = None  # pressure differential initialization

    if pressure_up is not None and pressure_down is not None:
        try:
            diff = round(float(pressure_up) - float(pressure_down), 1)  # compute differential
        except (ValueError, TypeError):
            diff = None  # invalid values are handled gracefully

    lines = [
        "────────────────────────────────────────",
        f"  Location:  {location}",
        f"  Device ID: {device_id}",
        f"  Time:      {timestamp}",
        f"  Count:     #{counter}",
        "────────────────────────────────────────",
    ]

    if pressure_up is not None:
        lines.append(f"  Pressure (upstream):    {pressure_up} PSI")  # show upstream pressure
    else:
        lines.append("  Pressure (upstream):    N/A")  # missing value fallback

    if pressure_down is not None:
        lines.append(f"  Pressure (downstream):  {pressure_down} PSI")  # show downstream pressure
    else:
        lines.append("  Pressure (downstream):  N/A")  # missing value fallback

    if flow_rate is not None:
        lines.append(f"  Flow rate:              {flow_rate} gal/min")  # show flow rate
    else:
        lines.append("  Flow rate:              N/A")  # missing value fallback

    if diff is not None:
        lines.append(f"  Pressure differential:   {diff} PSI")  # show computed differential
    else:
        lines.append("  Pressure differential:   N/A")  # missing value fallback

    return "\n".join(lines)  # return the formatted display block


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        connected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # local connect time
        print("============================================================")
        print("  GRAND MARINA WATER MONITORING DASHBOARD")
        print(f"  Connected at: {connected_at}")
        print("============================================================\n")
        client.subscribe(TOPIC)  # subscribe when connected
    else:
        print(f"Connection failed with result code {rc}")  # report failure


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")  # decode message bytes

    try:
        reading = json.loads(payload)  # parse JSON payload
    except json.JSONDecodeError:
        print(f"Received non-JSON message on {msg.topic}: {payload}")  # handle bad payloads
        return

    print(format_reading(reading))  # print formatted reading block


if __name__ == "__main__":
    ca_path = Path(TLS_CONFIG["ca_certs"])
    if not ca_path.exists():
        print(f"CA certificate not found: {ca_path}")
        print("Run generate_certs.py first!")
        raise SystemExit(1)

    client = mqtt.Client()  # create MQTT client
    client.on_connect = on_connect  # assign connect callback
    client.on_message = on_message  # assign message callback

    client.tls_set(
        ca_certs=TLS_CONFIG["ca_certs"],
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
    )
    client.connect(TLS_CONFIG["broker_host"], TLS_CONFIG["broker_port"])  # connect to broker
    client.loop_forever()  # run forever processing network events
