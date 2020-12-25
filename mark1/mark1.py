#just got the values from the mobile

from sensordroid import Client
import time
from pynput.keyboard import Key, Controller


def devicesDiscoveredEventHandler(devices):
    print(devices)
    if len(devices) > 0:
        client = Client(devices[0])

        client.connectionUpdated = connectionUpdatedEventHandler
        client.sensorsReceived = sensorsReceivedEventHandler
        client.imageReceived = cameraReceivedEventHandler

        client.sensorsSampleRate = 100
        client.cameraResolution = 13

        client.connect()
        

def connectionUpdatedEventHandler(sender, msg):
    if sender is not None:
        if sender.connected:
            print("Connected")
        else:
            print("Disonnected") 

def sensorsReceivedEventHandler(sender, dataCurrent):
    print((dataCurrent.Acceleration.Values.AsString.split(','+'\t')))

def cameraReceivedEventHandler(sender, image):
    #Process image data bytes
    pass

Client.devicesDiscovered = devicesDiscoveredEventHandler
Client.startDiscovery()

key = input("Press ENTER to exit\n") 

Client.closeAll()
