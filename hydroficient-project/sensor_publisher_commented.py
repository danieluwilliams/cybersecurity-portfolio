import paho.mqtt.client as mqtt  # MQTT client library
import json  # JSON encoding/decoding
import random  # random variation for sensor values
import time  # sleep between readings
from datetime import datetime, timezone  # timestamp generation

class WaterSensorMQTT:
    """
    A water sensor that publishes readings to MQTT.
    """

    def __init__(self, device_id, location, broker="127.0.0.1", port=1884):
        self.device_id = device_id  # unique sensor/device identifier
        self.location = location  # physical location of the sensor
        self.counter = 0  # reading counter

        # MQTT setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # create MQTT client
        try:
            self.client.connect(broker, port)  # connect to the MQTT broker
        except ConnectionRefusedError as exc:
            raise ConnectionRefusedError(
                f"Unable to connect to MQTT broker at {broker}:{port}. "
                "Make sure a broker is running and the host/port are correct."
            ) from exc
        self.client.loop_start()  # start the network loop in the background

        # Topic for this sensor
        self.topic = f"hydroficient/grandmarina/sensors/{self.location}/readings"

        # Base values for realistic variation
        self.base_pressure_up = 82  # base upstream pressure
        self.base_pressure_down = 76  # base downstream pressure
        self.base_flow = 40  # base flow rate

    def get_reading(self):
        """Generate a sensor reading with realistic variation."""
        self.counter += 1  # increment the reading counter
        return {
            "device_id": self.device_id,  # identity
            "location": self.location,  # location key/value
            "timestamp": datetime.now(timezone.utc).isoformat(),  # UTC ISO timestamp
            "counter": self.counter,  # count of readings
            "pressure_upstream": round(self.base_pressure_up + random.uniform(-2, 2), 1),  # random upstream pressure
            "pressure_downstream": round(self.base_pressure_down + random.uniform(-2, 2), 1),  # random downstream pressure
            "flow_rate": round(self.base_flow + random.uniform(-3, 3), 1),  # random flow rate
        }

    def publish_reading(self):
        """Generate a reading and publish it to MQTT."""
        reading = self.get_reading()  # create payload
        self.client.publish(self.topic, json.dumps(reading))  # publish JSON to MQTT topic
        return reading

    def run_continuous(self, interval=2):
        """Publish readings continuously at the specified interval."""
        print(f"Starting device: {self.device_id}")
        print(f"Location: {self.location}")
        print(f"Publishing to: {self.topic}")
        print(f"Interval: {interval} seconds")
        print("-" * 40)

        try:
            while True:
                reading = self.publish_reading()  # publish one reading
                print(
                    f"[{reading['counter']}] Pressure: {reading['pressure_upstream']}/{reading['pressure_downstream']} PSI, Flow: {reading['flow_rate']} gal/min"
                )
                time.sleep(interval)  # wait before next reading
        except KeyboardInterrupt:
            print("\nSensor stopped.")
            self.client.loop_stop()  # stop MQTT network loop
            self.client.disconnect()  # disconnect from broker

if __name__ == "__main__":
    sensor = WaterSensorMQTT("GM-HYDROLOGIC-01", "main-building", port=1884)  # create sensor instance
    sensor.run_continuous(2)  # start publishing every 2 seconds
