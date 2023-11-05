import paho.mqtt.client as mqtt
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Set your InfluxDB token, organization, and InfluxDB URL, and bucket name - 
INFLUXDB_TOKEN="EXAMPLE"
org = "EXAMPLE"
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
bucket="EXAMPLE"

# Create an InfluxDB client with the provided URL, token, and organization
client = InfluxDBClient(url=url, token=INFLUXDB_TOKEN, org=org)
# Create a write API for writing data to InfluxDB with synchronous write options
write_api = client.write_api(write_options=SYNCHRONOUS)

# Function to sent data to InfluxDB
def influxSend(data, num, sensor):
    # Create a data point with a measurement name "SPM" 
    # Field name is based on the sensor given by the Node and which Node it came from
    # The float(data[2:-2]) is used as the field value, converting the data to a float.
    point = ( Point("SPM").field(sensor+f"{num}", float(data[2:-2])))

    # Write the data point to the specified bucket and organization using the write API    
    write_api.write(bucket=bucket, org=org, record=point)

# The callback when the MQTT client is connected
def on_connect(client, userdata, flags, rc):
    print("Connected with result code {0}".format(str(rc)))  

    # Subscribe to each of the TOPICS for each Smart Plantbed Monitor
    client.subscribe("SPM1_soilTemp")
    client.subscribe("SPM1_airTemp")
    client.subscribe("SPM1_airHumidity")
    client.subscribe("SPM1_UV")
    client.subscribe("SPM1_soilMoisture")

    client.subscribe("SPM2_soilTemp")
    client.subscribe("SPM2_airTemp")
    client.subscribe("SPM2_airHumidity")
    client.subscribe("SPM2_UV")
    client.subscribe("SPM2_soilMoisture")

    client.subscribe("SPM3_soilTemp")
    client.subscribe("SPM3_airTemp")
    client.subscribe("SPM3_airHumidity")
    client.subscribe("SPM3_UV")
    client.subscribe("SPM3_soilMoisture")


# The callback for when a message is received on the client
def on_message(client, userdata, msg):

    # Determine the Node Number of the message
    num = msg.topic[3]

    # Determine the Sensor the data is for
    if msg.topic[5:] == "soilTemp":
        sensor = 'S'
    if msg.topic[5:] == "airTemp":
        sensor = 'A'
    if msg.topic[5:] == "airHumidity":
        sensor = 'H'
    if msg.topic[5:] == "UV":
        sensor = 'U'
    if msg.topic[5:] == "soilMoisture":
        sensor = 'M'

    # Send the message to influx based on the node number and sensor
    influxSend(msg.payload.decode(), num, sensor)


# Initialise a MQTT Client for this HUB
client = mqtt.Client("HUB")

# Define callback function for successful connection
client.on_connect = on_connect 

 # Define callback function for receipt of a message
client.on_message = on_message 

# Establish a Client connection to the Broker with IP
client.connect('1.1.1.1.1')

# Start networking daemon
client.loop_forever()  