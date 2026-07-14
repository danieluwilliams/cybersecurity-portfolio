import paho.mqtt.client as mqtt  # MQTT client library
import json  # JSON encoding for published payloads
import random  # random variations for sensor values
import time  # sleep between publish intervals
from datetime import datetime, timezone  # UTC timestamp generation
from pathlib import Path
import ssl

# ============================================
# TLS CONFIGURATION - ADD THIS FOR TLS
# ============================================
TLS_CONFIG = {
    "ca_certs": "certs/ca.pem",
    "broker_host": "localhost",
    "broker_port": 8883,
}
# ============================================


class WaterSensorMQTT:
    """
    A water sensor that publishes readings to MQTT.
    """

    def __init__(self, device_id, location, broker=TLS_CONFIG["broker_host"], port=TLS_CONFIG["broker_port"]):
        self.device_id = device_id  # unique device identifier
        self.location = location  # sensor location used in topic and payload
        self.counter = 0  # reading counter

        ca_path = Path(TLS_CONFIG["ca_certs"])
        if not ca_path.exists():
            print(f"CA certificate not found: {ca_path}")
            print("Run generate_certs.py first!")
            raise FileNotFoundError(f"CA certificate not found: {ca_path}")

        # MQTT setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # create MQTT client
        self.client.tls_set(
            ca_certs=TLS_CONFIG["ca_certs"],
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
        )
        try:
            self.client.connect(broker, port)  # connect to the MQTT broker
        except ConnectionRefusedError as exc:
            raise ConnectionRefusedError(
                f"Unable to connect to MQTT broker at {broker}:{port}. "
                "Make sure a broker is running and the host/port are correct."
            ) from exc
        self.client.loop_start()  # start the MQTT network loop in the background

        # Topic for this sensor
        self.topic = f"hydroficient/grandmarina/sensors/{self.location}/readings"  # publish topic

        # Base values for realistic variation
        self.base_pressure_up = 82  # baseline upstream pressure
        self.base_pressure_down = 76  # baseline downstream pressure
        self.base_flow = 40  # baseline flow rate

    def get_reading(self):
        """Generate a sensor reading with realistic variation."""
        self.counter += 1  # increment counter for each reading
        return {
            "device_id": self.device_id,  # identity field
            "location": self.location,  # sensor location
            "timestamp": datetime.now(timezone.utc).isoformat(),  # UTC ISO timestamp
            "counter": self.counter,  # sequential reading number
            "pressure_upstream": round(self.base_pressure_up + random.uniform(-2, 2), 1),  # random upstream pressure
            "pressure_downstream": round(self.base_pressure_down + random.uniform(-2, 2), 1),  # random downstream pressure
            "flow_rate": round(self.base_flow + random.uniform(-3, 3), 1),  # random flow rate
        }

    def publish_reading(self):
        """Generate a reading and publish it to MQTT."""
        reading = self.get_reading()  # produce one reading payload
        self.client.publish(self.topic, json.dumps(reading))  # publish JSON payload
        return reading  # return the reading for local output

    def run_continuous(self, interval=2):
        """Publish readings continuously at the specified interval."""
        print(f"Starting device: {self.device_id}")  # print startup info
        print(f"Location: {self.location}")  # print location info
        print(f"Publishing to: {self.topic}")  # print topic info
        print(f"Interval: {interval} seconds")  # print interval info
        print("-" * 40)

        try:
            while True:
                reading = self.publish_reading()  # publish and receive reading
                print(f"[{reading['counter']}] Pressure: {reading['pressure_upstream']}/{reading['pressure_downstream']} PSI, Flow: {reading['flow_rate']} gal/min")  # print summary line
                time.sleep(interval)  # wait before next reading
        except KeyboardInterrupt:
            print("\nSensor stopped.")  # handle Ctrl+C
            self.client.loop_stop()  # stop MQTT network loop
            self.client.disconnect()  # disconnect cleanly

if __name__ == "__main__":
    sensor = WaterSensorMQTT("GM-HYDROLOGIC-01", "main-building", port=8883)  # create sensor instance
    sensor.run_continuous(2)  # start publishing every 2 seconds