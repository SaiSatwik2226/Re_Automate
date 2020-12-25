#import asyncore
import socket
import threading
import time
import os

# SensorDroid Client Python.
class Client:

    @property
    def connected(self):
        return self._connected
    @connected.setter
    def connected(self, value):
        self._connected = value

    __portBaseDefault = 53121
    __sensorsPortDevice = 0

    @property
    def channel(self):
        return self._channel
    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            if value == -2:
                self.checkConnect();
            if value == -1:
                self._sensorsPort = 0;
                self.checkConnect();           
            elif value >= 0:
                self.connectSensors(sensorsPortT)

    @property
    def sensorsPort(self):
        return self.__sensorsPortDevice
    @sensorsPort.setter
    def sensorsPort(self, value):
        self._sensorsPort = value
        self.channel = -2


    @sensorsPort.setter
    def sensorsPort(self, value):
        self._sensorsPort = value
        self.channel = -2
  
    @property
    def sensorsSampleRate(self):
        return self._sensorsSampleRate
    @sensorsSampleRate.setter
    def sensorsSampleRate(self, value):
        self._sensorsSampleRate = value

    @property
    def discoveredDevices():
        return Client._discoveredDevices

    @property
    def devicesDiscovered():
        return Client._devicesDiscovered

    @devicesDiscovered.setter
    def devicesDiscovered(value):
        Client._devicesDiscovered.removeAt(0)
        Client._devicesDiscovered.append(value)

    @property
    def connectionUpdated(self):
        return self._connectionUpdated
    @connectionUpdated.setter
    def connectionUpdated(self, value):
        self._connectionUpdated.removeAt(0)
        self._connectionUpdated.append(value)

    @property
    def sensorsReceived(self):
        return self._sensorsReceived
    @sensorsReceived.setter
    def sensorsReceived(self, value):
        self._sensorsReceived.removeAt(0)
        self._sensorsReceived.append(value)

    @property
    def dataCurrent(self):
        return self._dataCurrent

    @property
    def image(self):
        return self._image

    _name = None
    _info = None
    _controlling = None
    _discoveredDevices = None
    _dataCurrent = None
    _image = None

    __udpDiscovery = None
    __udpMain = None
    __udpSensors = None

    __ipLocalDiscovery = None

    __clients = []


    def __init__(self, address):

        self.connected = False
        self.address = address
        self._ipLocal = Client.getLocalIP(address)
        
        self._channel = -1
        self._sensorsPort = 0;
        self.checkConnect()


        self._connectionUpdated = Event()
        self._connectionUpdated()

        self._sensorsReceived = Event()
        self._sensorsReceived()

        Client.__clients.append(self)

    @staticmethod
    def getLocalIP(address):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((address, 1))
            IP = s.getsockname()[0]
        except:
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except:
                IP = ''
        finally:
            s.close()
        return IP

    @staticmethod
    def devicesDiscoveredHandler(addr, data):     
        dataMain = data.decode('utf-8')
        if "SensorDroidDevice" in dataMain:
            if addr not in Client._discoveredDevices:
                 Client._discoveredDevices.append(addr)
                 Client.devicesDiscovered(Client._discoveredDevices)

        

    def getMainMsg(self):

        msg = ""
        msg += "@connect$" + str(1)
        msg += "@clientName$" + socket.gethostname()
        msg += "@clientIP$" + self.ipLocal
        msg += "@sensorsSampleRate$" + str(self.sensorsSampleRate)

        msg += "@sensorsPort$" + str(self._sensorsPort);

        return msg

    def connectionUpdatedHandler(self, addr, data):
        dataMain = data.decode('utf-8')
        if self.connected !=  self.__udpMain.connected:
            self.connected = self.__udpMain.connected
            self.connectionUpdated(self, dataMain)
        self.__udpMain.send(self.getMainMsg())

        self._info = ""

        dataMainM = dataMain.split("@")
        for i in range(0, len(dataMainM)): 
            try:
                dataMainA = dataMainM[i].split("$")

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceName":
                        self._info += dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceModel":
                        self._name = dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceOS":
                        self._info += " - " + dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "mainClient":
                        if self.address in dataMainA[1]:
                            self._controlling = True
                        else:
                            self._controlling = False

                if not self._controlling:                       
                    if len(dataMainA) > 1:
                        if dataMainA[0] == "sensorsPort":
                            self.__sensorsPortDevice = int(dataMainA[1])
                            if self._sensorsPort != self.__sensorsPortDevice:
                                self.connectSensors(self.__sensorsPortDevice)
                pass

            except Exception as e:
                pass

        pass

    def sensorsReceivedHandler(self, addr, data):
        self._dataCurrent = SensorsData(data.decode('utf-8'))
        self.sensorsReceived(self, self.dataCurrent)


    @staticmethod
    def startDiscovery(address="Any"):
        if (Client.__udpDiscovery == None):
            Client.__ipLocalDiscovery = Client.getLocalIP(address)
            Client.__udpDiscovery = AsyncoreSocketUDP(Client.__ipLocalDiscovery, "Any", 53120)
            Client.__udpDiscovery.isCheck = True
            Client.__udpDiscovery.dataRcvEvent.append(Client.devicesDiscoveredHandler)

            Client._discoveredDevices =[]

            loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
            loop_thread.daemon = True
            loop_thread.start()

    def connect(self):
        isAsync = True

        if isAsync:
            self.__udpMain = AsyncoreSocketUDP(self.ipLocal, self.address, self.__portBaseDefault)
            self.__udpMain.isCheck = True
            self.__udpMain.dataRcvEvent.append(self.connectionUpdatedHandler)

            self.checkConnect()

            loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
            loop_thread.daemon = True
            loop_thread.start()

        else:
            self.__udpMain = UDP(self.ipLocal, self.address, self.__portBaseDefault)
            self.__udpMain.start()

            while self.__udpMain.Connected:
                self.__udpMain.send(self.getMainMsg())
                self.__udpMain.receive()

            self.__udpSensors = UDP(self.ipLocal, self.address, self.sensorsPort)
            self.__udpSensors.start()


            while True:
                time.sleep(0.001)

                self.__udpMain.send(self.getMainMsg())
                self.__udpMain.receive()
                if self.__udpMain.data is not None:
                    self.__udpMain.data = None

                self.__udpSensors.send("1")
                self.__udpSensors.receive()
                if self.__udpSensors.data is not None:
                    dataCurrent = SensorsData(self.__udpSensors.data.decode('utf-8'))
                    self.sensorsReceived(dataCurrent)
                    self.__udpSensors.data = None


    def checkConnect(self):
            self.checkPortsAutomatic()

            if self._sensorsPort > 0:
                self.connectSensors(self._sensorsPort)


    def checkPortsAutomatic(self):
        if self.channel == -1 and self._sensorsPort == 0:
            for i in range(0, 999): 
                sensPort, camPort = self.getPorts(i)
                sensorsPortT, cameraPortT = self.getPorts(i);
                found = self.find(lambda x: x.port == sensorsPortT, AsyncoreSocketUDP.listSockets)
                if found == None:
                    self.connectSensors(sensorsPortT)
                    break             

    def find(self, pred, coll):
        for x in coll:
            if pred(x):
                return x

    def getPorts(self, channel):
        return (self.__portBaseDefault + 1) + 2 * (channel), (self.__portBaseDefault + 2) + 2 * (channel)

    def connectSensors(self, port):
        if port == 0:
            port = self.__portBaseDefault + 1

        if self.__udpSensors == None or (port > 0 and self._sensorsPort != port):
            if self.__udpSensors != None:
                self.__udpSensors.stop()
            self.__udpSensors = AsyncoreSocketUDP(self.ipLocal, self.address, port)
            self.__udpSensors.dataRcvEvent.append(self.sensorsReceivedHandler)
            self._sensorsPort = port


    def close(self):
        self.connected = False
        self.__udpMain.stop()
        self.__udpSensors.stop()

    def closeAll():
        for cli in Client.__clients:
            cli.close()
