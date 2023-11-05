import utime
start_time = utime.ticks_us()
from machine import Pin, Timer, SPI
import time
from DHT22 import DHT22
import onewire
import ds18x20
from umqttsimple import MQTTClient
from usocket import socket
import network


#W5x00 chip init
def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    #This enalbles DHCP
    nic.ifconfig()
    print("Connecting...")
    nic.active(True)
    
    while not nic.isconnected():
        time.sleep(1)
        print(nic.regs())

#MQTT connect
def mqtt_connect():
    client_id = 'SPM1'
    mqtt_server = '192.168.0.100'
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

#reconnect & reset
def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    #machine.reset()




def DHT_read(dht_sensor):
    global T,H
    T,H = dht_sensor.read()
    if T is None:
        return -1, -1
    else:
        return T,H
        
def temp_read(ds, devices):
    if len(devices) != 0:
        ds.convert_temp()
        for device in devices:
            return ds.read_temp(device)
        


# Loop forever
def get_moisture(moisture_sensor): 
    # Read the analog value from the soil moisture sensor
    moisture_value = moisture_sensor.read_u16()

    # Convert the analog value to a percentage
    moisture_percentage = moisture_value / 65535 * 100
    
    
    #print("Soil Moisture = %.2f%%" % (moisture_percentage))
    
    return moisture_percentage

    
def uv_read(uv_sensor):
    uv_value = uv_sensor.read_u16()
    
    
    
    return uv_value

    

    
def main():
    global start_time

    ow = onewire.OneWire(Pin(28))
    ds = ds18x20.DS18X20(ow)
    devices = ds.scan()
    
    # Set up the analog input pin for the soil moisture sensor
    moisture_sensor = machine.ADC(0)
    
    uv_sensor = machine.ADC(1)
    
    dht_data = Pin(2,Pin.IN,Pin.PULL_UP)
    dht_sensor=DHT22(dht_data,Pin(2,Pin.OUT),dht11=False)
    
    
    topic_soilTemp = b'SPM1_soilTemp'
    topic_humidity = b'SPM1_airHumidity'
    topic_UV = b'SPM1_UV'
    topic_soilMoisture = b'SPM1_soilMoisture'
    topic_airTemp = b'SPM1_airTemp'
    
    w5x00_init()
    client = mqtt_connect()
 
    
    while True:
        #led.toggle()
        
        
        
        #moisture = get_moisture(moisture_sensor)
        #client.publish(topic_soilMoisture, "{:3.1f}".format(moisture))

        #print("M %.2f" % (moisture))
        
        
        
        #T, H = DHT_read(dht_sensor)
        #client.publish(topic_airTemp, "{:3.1f}".format(T))
        #client.publish(topic_humidity, "{:3.1f}".format(H))
        #print("A {:3.1f}\nH {:3.1f}".format(T,H))
        
        
        #temp = temp_read(ds, devices)
        #client.publish(topic_soilTemp, "{:3.1f}".format(temp))
        #print("S {}".format(temp))
        
        
        uv = uv_read(uv_sensor)
        print("U %.2f" % (uv))
        #client.publish(topic_UV, "{:3.1f}".format(uv)) 
        
        
        #end_time = utime.ticks_us()
        #time_elapsed = utime.ticks_diff(end_time, start_time)
        #print(time_elapsed)
        #start_time = utime.ticks_us()
        
        
        
        
        
    
if __name__ == "__main__":
    main()




