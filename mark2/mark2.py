#cleaned the data

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
    value = (dataCurrent.Acceleration.Values.AsString.split(','+'\t'))
    for i,j in enumerate(value):
        value[i] = float(j)

    if value[1] <= -2:
        print('W')
    if value[1] >= 2:
        print('S')
    if value[0] >= 5:
        print('A')
    if value[0] <= -5:
        print('D')
    if value[0] <= 0.5 and value[0] >= 0 and value[1] <= -1 and value[1] >= -1.5:
        print('Space')
    


def cameraReceivedEventHandler(sender, image):
    #Process image data bytes
    pass


Client.devicesDiscovered = devicesDiscoveredEventHandler
Client.startDiscovery()

key = input("Press ENTER to exit\n")

Client.closeAll()
