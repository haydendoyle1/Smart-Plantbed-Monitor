import influxdb_client, os, time, serial
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
def influxSend(data, num):
    # Create a data point with a measurement name "SPM" 
    # Field name is based on the letter given by the Node and which Node it came from
    # The float(data[2:-2]) is used as the field value, converting the data to a float.
    point = ( Point("SPM").field(data[0]+f"{num}", float(data[2:-2])))

    # Write the data point to the specified bucket and organization using the write API    
    write_api.write(bucket=bucket, org=org, record=point)

# Main Function
def main():
    # Initialise Baudrate for serial connection
    baudrate = "115200"

    # Serial Ports for Connection to each Node
    SPM1_port = "COM13"
    SPM2_port = "COM5"
    SPM3_port = "COM12"

    # Try connect to SPM1
    print("Attempting to connect to SPM1 on port " + SPM1_port + "\r\n")
    try:
        # Connect to Serial
        SPM1_serial = serial.Serial(SPM1_port, baudrate=int(baudrate), timeout=1)
        print("connected to " + SPM1_port + "\r\n")
    except:
        print("ERROR: Could not open serial port " + SPM1_port + "\r\n")
    
    
    # Try to connect to SPM2
    print("Attempting to connect to SPM2 on port " + SPM2_port + " at baudrate " + baudrate + "\r\n")
    try:
        # Connect to Serial
        SPM2_serial = serial.Serial(SPM2_port, baudrate=int(baudrate), timeout=1)
        print("connected to " + SPM2_port + "\r\n")
    except:
        print("ERROR: Could not open serial port " + SPM2_port + "\r\n")


    # Try to connect to SPM3
    print("Attempting to connect to SPM3 on port " + SPM3_port + " at baudrate " + baudrate + "\r\n")
    try:
        # Connect to Serial
        SPM3_serial = serial.Serial(SPM3_port, baudrate=int(baudrate), timeout=1)
        print("connected to " + SPM3_port + "\r\n")
    except:
        print("ERROR: Could not open serial port " + SPM3_port + "\r\n")
    


    # Main Loop - Reads data from each SPM - if there is data it  sends to the database 
    # If a data cannot be read, attempts to reconnect to SPM
    while True:

        # Try to read data from SPM1 
        try:

            SPM1_data = SPM1_serial.readline()

            # If data isn't empty send to the the INFLUXDB
            if len(SPM1_data) > 0:
                # Send data to InfluxDB for SPM1
                influxSend(SPM1_data.decode(), 1)

        except:
            # If data couldn't be read - try reconnecting to SPM1
            try:
                print("disconnected from " + SPM1_port + "\r\n")
                SPM1_serial = serial.Serial(SPM1_port, baudrate=int(baudrate), timeout=1)
                print("connected to " + SPM1_port + "\r\n")

            except:
                print("ERROR: Could not open serial port " + SPM1_port + "\r\n")

        # Try to read data from SPM2
        try:
            
            SPM2_data = SPM2_serial.readline()

            # If data isn't empty send to the the INFLUXDB
            if len(SPM2_data) > 0:
                # Send data to InfluxDB for SPM2
                influxSend(SPM2_data.decode(), 2)

        except:
            # If data couldn't be read - try reconnecting to SPM2
            try:
                print("disconnected from " + SPM2_port + "\r\n")
                SPM2_serial = serial.Serial(SPM2_port, baudrate=int(baudrate), timeout=1)
                print("connected to " + SPM2_port + "\r\n")

            except:
                print("ERROR: Could not open serial port " + SPM2_port + "\r\n")


        # Try to read data from SPM3
        try:   
            
            SPM3_data = SPM3_serial.readline()

            # If data isn't empty send to the the INFLUXDB
            if len(SPM3_data) > 0:
                # Send data to InfluxDB for SPM3
                influxSend(SPM3_data.decode(), 3) 

        except:
            # If data couldn't be read - try reconnecting to SPM1
            try:
                print("disconnected from " + SPM3_port + "\r\n")
                SPM3_serial = serial.Serial(SPM3_port, baudrate=int(baudrate), timeout=1)
                print("connected to " + SPM3_port + "\r\n")

            except:
                print("ERROR: Could not open serial port " + SPM3_port + "\r\n")
    
    
if __name__ == "__main__":
    main()