import machine
from imu import MPU6050
import network
import socket
from time import sleep

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))
mpu =MPU6050(i2c)

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('SSID', 'PASSWORD')

while not wifi.isconnected():
    pass

# Create UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('IP',PORT)  # Replace with your PC's IP address and port

while True:
    # Read data
    gyrox = mpu.gyro.x/100
    gyroy = mpu.gyro.y/100
    gyroz = mpu.gyro.z/1000  # Replace with the actual method to read gyroscope data
    data = "{},{},{}\n".format(gyrox,gyroy,gyroz)
    udp_socket.sendto(data.encode(), server_address)
    print(data)
    sleep(0.1)

  
    