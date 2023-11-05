from machine import Pin, Timer, SPI
import time
from DHT22 import DHT22
import onewire
import ds18x20
from umqttsimple import MQTTClient
from usocket import socket
import network


# Intialise the Ethenet HAT - W5x00 chip
def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    # Enable DHCP
    nic.ifconfig()
    print("Connecting...")
    nic.active(True)
    
    while not nic.isconnected():
        time.sleep(1)
        print(nic.regs())

# MQTT connect
def mqtt_connect():
    # Set the ID for the MQTT client
    client_id = 'SPM3'

    # MQTT broker ip - change this
    mqtt_server = '1.1.1.1'

    # Connect to the MQTT broker
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))

    return client

# Callback when a connection cannot be established to the MQTT broker
def reconnect():
    print('Failed to connected to MQTT Broker.')
    time.sleep(5)

    # Restart the device - disable if using serial
    machine.reset() 

# Read Air Temperature and Humidity from the DHT22 sensor
def DHT_read(dht_sensor):
    global T,H
    T,H = dht_sensor.read()

    # If reading too fast, data will be empty
    if T is None:
        return -1, -1
    else:
        return T,H

# Read the Soil Temperature from DS18B20     
def temp_read(ds, devices):

    # Ensure there is a device connected
    if len(devices) != 0:
        ds.convert_temp()

        # Read Temp for each Sensor connected
        for device in devices:
            return ds.read_temp(device)
    
# Read the Soil Moisture from the Sensor
def get_moisture(moisture_sensor): 
    # Read the analog value
    moisture_value = moisture_sensor.read_u16()

    # Convert the analog value to a percentage
    moisture_percentage = moisture_value / 65535 * 100
    
    return moisture_percentage

# Read the Ambient Light from the TEM6000
def uv_read(uv_sensor):
    # Read analoge value and covert to percentage
    uv_value = uv_sensor.read_u16() / 65535 * 100
    
    return uv_value

    

# Main Function
def main():
    # Setup the Led pin for Toggle
    led = Pin(25, Pin.OUT)
    
    # Setup the Soil Temperature sensor on pin 28
    ow = onewire.OneWire(Pin(28))
    ds = ds18x20.DS18X20(ow)
    devices = ds.scan()
    
    # Set up the analog input pin for the soil moisture sensor
    moisture_sensor = machine.ADC(0)

    # Set up the analog input pin for the ambient light sensor
    uv_sensor = machine.ADC(1)
    
    # Set up the Air Temperature and Humidity Sensor on pin 2
    dht_data = Pin(2,Pin.IN,Pin.PULL_UP)
    dht_sensor=DHT22(dht_data,Pin(2,Pin.OUT),dht11=False)
    
    # Define MQTT topics to publish to
    topic_soilTemp = b'SPM3_soilTemp'
    topic_humidity = b'SPM3_airHumidity'
    topic_UV = b'SPM3_UV'
    topic_soilMoisture = b'SPM3_soilMoisture'
    topic_airTemp = b'SPM3_airTemp'
    
    # Try to establish a connection to the MQTT broker
    try:
        w5x00_init()
        client = mqtt_connect()
    except OSError as e:
        reconnect()
        client = 0
    

    # Main Loop
    while True:
        # Toggle the LED for Debugging purposes
        led.toggle()
        
        # Get the Moisture data
        moisture = get_moisture(moisture_sensor)
        # Send the Moisture data over serial
        print("M %.2f" % (moisture))
        # If MQTT connection established, publish to Moisure Topic
        if client != 0:
            client.publish(topic_soilMoisture, "{:3.1f}".format(moisture))
        
        # Get the Air Temp and Humidity data
        T, H = DHT_read(dht_sensor)
        # Send the Air Temp and Humidity data over serial
        print("A {:3.1f}\nH {:3.1f}".format(T,H))
        # If MQTT connection established, publish to Air Temp and Humidity Topics
        if client != 0:
            client.publish(topic_airTemp, "{:3.1f}".format(T))
            client.publish(topic_humidity, "{:3.1f}".format(H))
        
        # Get the Soil temp data
        temp = temp_read(ds, devices)
         # Send the Soil temp data over serial
        print("S {}".format(temp))
         # If MQTT connection established, publish to Soil temp Topic
        if client != 0:
            client.publish(topic_soilTemp, "{:3.1f}".format(temp))
        
        # Get the Ambient Light data
        uv = uv_read(uv_sensor)
        # Send the Ambient Light data over serial
        print("U %.2f" % (uv))
        # If MQTT connection established, publish to Ambient Light Topic
        if client != 0:
            client.publish(topic_UV, "{:3.1f}".format(uv)) 
        
        # Sleep to prevent spamming of data - don't need to sample every second
        time.sleep(10)
    
if __name__ == "__main__":
    main()



