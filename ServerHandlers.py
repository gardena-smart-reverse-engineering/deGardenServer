import struct
import json

from abc import ABCMeta, abstractmethod

class BaseServerHandler(object):
    __metaclass__ = ABCMeta

    __BUFFER_SIZE = 8192

    __GATEWAY_HANDSHAKE_1 = "ff00000000000000257f".decode("hex")
    __SERVER_HANDSHAKE_1 = "ff00000000000000017f".decode("hex")

    __GATEWAY_HANDSHAKE_2 = "03".decode("hex")
    __SERVER_HANDSHAKE_2 = __GATEWAY_HANDSHAKE_2

    __GATEWAY_HANDSHAKE_3 = "004e554c4c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000".decode("hex")
    __SERVER_HANDSHAKE_3 = __GATEWAY_HANDSHAKE_3

    __GATEWAY_HELLO_ID = "044a0552454144590b536f636b65742d5479706500000003524551084964656e7469747900000024".decode("hex")
    __SERVER_HELLO = "04290552454144590b536f636b65742d5479706500000006524f55544552084964656e7469747900000000".decode("hex")

    __REQUEST_SHORT_INIT = "010000".decode("hex")
    __REQUEST_LONG_INIT = "0100020000".decode("hex")

    def __init__(self, client, address):
        self.__client = client
        self.__address = address

        self.__messageBuffer = ""
        self.__messageTargetLength = 0
    
    def loop(self):
        while True:
            message = b''
            while True:
                part = self.__client.recv(self.__BUFFER_SIZE)
                message += part
                if len(part) < self.__BUFFER_SIZE:
                    break

            if len(message) > 0:
                print self._name(), 'packet from', self.__address
                self.__handle_packet(message)
        self.__client.close()


    @abstractmethod
    def _name(self):
        pass

    #@abstractmethod
    def _handle_json_request(self, data):
        if data["id"] == "PONG_gateway" and data["method"] == "PING":
            response = self.__get_result(data["id"], "PONG")
        else: 
            #TODO Work with the data
            response = self.__get_simple_result(data["id"])
        self.__send_json(response)
    
    #@abstractmethod
    def _handle_data_request(self, data):
        print "Recieved", self.__client.getpeername(), self.__client.getsockname(), data

    def __handle_packet(self, message):
        if message == self.__GATEWAY_HANDSHAKE_1:
            self.__client.sendall(self.__SERVER_HANDSHAKE_1)
            print "Handshake 1"
        elif message == self.__GATEWAY_HANDSHAKE_2:
            self.__client.sendall(self.__SERVER_HANDSHAKE_2)
            print "Handshake 2"
        elif message == self.__GATEWAY_HANDSHAKE_3:
            self.__client.sendall(self.__SERVER_HANDSHAKE_3)
            print "Handshake 3"
        elif message.startswith(self.__GATEWAY_HELLO_ID):
            gatewayId = message[len(self.__GATEWAY_HELLO_ID):]
            self.__client.sendall(self.__SERVER_HELLO)
            print "Hello from Gateway", gatewayId
        elif message.startswith(self.__REQUEST_SHORT_INIT):
            self.__messageTargetLength = struct.unpack('B', message[len(self.__REQUEST_SHORT_INIT):len(self.__REQUEST_SHORT_INIT)+1])[0]
            self.__message = message[len(self.__REQUEST_SHORT_INIT)+1:]
            self.__handle_packet(self.__message)
        elif message.startswith(self.__REQUEST_LONG_INIT):
            self.__messageTargetLength = struct.unpack('>I', message[len(self.__REQUEST_LONG_INIT)+2:len(self.__REQUEST_LONG_INIT)+6])[0]
            self.__message = message[len(self.__REQUEST_LONG_INIT)+6:]
            self.__handle_packet(self.__message)
        elif self.__messageTargetLength > 0 and self.__messageTargetLength > len(self.__messageBuffer):
            self.__messageBuffer += message
            if self.__messageTargetLength <= len(self.__messageBuffer):
                self.__handle_data(self.__messageBuffer, self.__messageTargetLength)
                self.__messageBuffer = ""
                self.__messageTargetLength = 0
        else:
            for i in message:
                print hex(ord(i))

    def __handle_data(self, message, responseLength):
        #print json
        if len(message) == responseLength:
            try:
                dataSet = json.loads(message)
                if isinstance(dataSet, list) == False:
                    dataSet = [dataSet]
                for data in dataSet:
                    print self.__client.getpeername(), self.__client.getsockname(), "Received JSON", data #json.dumps(data)
                    self._handle_json_request(data)
            except ValueError, e:
                self._handle_data_request(message)
        else:
            print self.__client.getpeername(), self.__client.getsockname(), "Expected length was", responseLength, "bytes, but received", len(message), "bytes", message

    def __get_result(self, id, result):
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }

    def __get_simple_result(self, id):
        return self.__get_result(id, True)

    def __send_raw(self, data):
        dataLength = len(data)
        if dataLength <= 0xFF:
            prefix = b"".join([self.__REQUEST_SHORT_INIT, struct.pack("B", dataLength)])
        elif dataLength <= 0xFFFFFF:
            prefix = b"".join([self.__REQUEST_LONG_INIT, struct.pack(">I", dataLength)])

        print "Send response", data
        fullData = prefix + data
        self.__client.sendall(fullData)

    def __send_json(self, dictonary):
        self.__send_raw(json.dumps(dictonary, separators=(',', ':')))

class ControlServerHandler(BaseServerHandler):
    #def __init__(self, client, address):
        #super(ControlServerHandler, self).__init__(client, address)

    def _name(self):
        return "Control"
        
class ReportServerHandler(BaseServerHandler):
    #def __init__(self, client, address):
        #super(ControlServerHandler, self).__init__(client, address)

    def _name(self):
        return "Report"