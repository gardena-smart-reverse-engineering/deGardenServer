import logging
import struct
import socket
import json

from abc import ABC, abstractmethod
from uuid import UUID
from fs import path

import xml.etree.ElementTree as ET

class BaseServerHandler(ABC):
    __BUFFER_SIZE = 8192
    __MAX_CLIENTS = 1

    __GATEWAY_HANDSHAKE_1 = bytes.fromhex("ff00000000000000257f")
    __SERVER_HANDSHAKE_1 = bytes.fromhex("ff00000000000000017f")

    __GATEWAY_HANDSHAKE_2 = bytes.fromhex("03")
    __SERVER_HANDSHAKE_2 = __GATEWAY_HANDSHAKE_2

    __GATEWAY_HANDSHAKE_3 = bytes.fromhex("004e554c4c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
    __SERVER_HANDSHAKE_3 = __GATEWAY_HANDSHAKE_3

    __GATEWAY_HELLO_ID = bytes.fromhex("044a0552454144590b536f636b65742d5479706500000003524551084964656e7469747900000024")
    __SERVER_HELLO = bytes.fromhex("04290552454144590b536f636b65742d5479706500000006524f55544552084964656e7469747900000000")

    __REQUEST_SHORT_INIT = bytes.fromhex("010000")
    __REQUEST_LONG_INIT = bytes.fromhex("0100020000")

    def __init__(self, fs, port):
        self._fs = fs

        self.__messageBuffer = b''
        self.__messageTargetLength = 0

        self.log = logging.getLogger(self.__class__.__name__)

        self.__init_socket(port)
    
    def __init_socket(self, port):
        self.log.info('Starting server on port:\t%i', port)
        self._socket = socket.socket()
        self._socket.bind((socket.gethostname(), port))
        self._socket.listen(self.__MAX_CLIENTS)

    def loop(self):
        while True:
            self.__client, self.__address = self._socket.accept()
            self.log.info("Connection for %s established with %s %s", self._name(), self.__client.getpeername(), self.__client.getsockname())
            while True:
                message = b''
                while True:
                    part = self.__client.recv(self.__BUFFER_SIZE)
                    message += part
                    if len(part) < self.__BUFFER_SIZE:
                        break
                if len(message) > 0:
                    self.__handle_packet(message)
            self.__client.close()
            self.log.warning("Connection to %s lost", self._name())
        self._socket.close()
        self.log.info('Server stopped, bye bye...')

    @abstractmethod
    def _name(self):
        pass

    @abstractmethod
    def _handle_json_request(self, data):
        pass
    
    #@abstractmethod
    def _handle_data_request(self, data):
        self.log.warning("Recieved: %s", data)

    def __handle_packet(self, message):
        if message == self.__GATEWAY_HANDSHAKE_1:
            self.__client.sendall(self.__SERVER_HANDSHAKE_1)
            self.log.info("Handshake 1")
        elif message == self.__GATEWAY_HANDSHAKE_2:
            self.__client.sendall(self.__SERVER_HANDSHAKE_2)
            self.log.info("Handshake 2")
        elif message == self.__GATEWAY_HANDSHAKE_3:
            self.__client.sendall(self.__SERVER_HANDSHAKE_3)
            self.log.info("Handshake 3")
        elif message.startswith(self.__GATEWAY_HELLO_ID):
            gatewayId = message[len(self.__GATEWAY_HELLO_ID):]
            self.__client.sendall(self.__SERVER_HELLO)
            self.log.info("Hello from Gateway %s", gatewayId)
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
                self.__handle_data(self.__messageBuffer.decode("UTF-8"), self.__messageTargetLength)
                self.__messageBuffer = b''
                self.__messageTargetLength = 0
        else:
            for i in message:
                self.log.warning(hex(ord(i)))

    def __handle_data(self, message, responseLength):
        if len(message) == responseLength:
            try:
                dataSet = json.loads(message)
                if isinstance(dataSet, list) == False:
                    dataSet = [dataSet]
                for data in dataSet:
                    self.log.debug(data)
                    self._handle_json_request(data)
            except ValueError:
                self._handle_data_request(message)
        else:
            self.log.error("Expected length was %i bytes, but received %i bytes, message was %s", responseLength, len(message), message)

    def _send_raw(self, data):
        dataLength = len(data)
        if dataLength <= 0xFF:
            prefix = b''.join([self.__REQUEST_SHORT_INIT, struct.pack("B", dataLength)])
        elif dataLength <= 0xFFFFFF:
            prefix = b''.join([self.__REQUEST_LONG_INIT, struct.pack(">I", dataLength)])

        self.log.debug("Response: %s", data)
        fullData = prefix + data.encode("UTF-8")
        self.__client.sendall(fullData)

    def _send_json(self, dictonary):
        self._send_raw(json.dumps(dictonary, separators=(',', ':')))

    def _is_uuid(self, uuid):
        try:
            uuid_obj = UUID(uuid, version=version)
        except:
            return False
        return str(uuid_obj) == uuid

class ControlServerHandler(BaseServerHandler):
    def _name(self):
        return "Control"

    def _handle_json_request(self, data):
        pass
        
class ReportServerHandler(BaseServerHandler):
    def _name(self):
        return "Report"

    def _handle_json_request(self, data):
        id = data["id"]
        method = data["method"]
        urlPath = data["params"]["url"]
        if method == "PING":
            response = self.__get_result(id, "PONG") 
        elif method == "GET":
            xmlResponse = self.__json_get(urlPath)
            response = self.__get_result(id, xmlResponse)
        else:
            xmlData = data["params"]["data"]
            response = self.__get_simple_result(id)  
            if xmlData:
                if method == "POST":
                    self.__json_post(urlPath, xmlData)
                elif method == "PUT":
                    self.__json_put(urlPath, xmlData)
        self._send_json(response)

    def __get_result(self, id, result):
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
    def __get_simple_result(self, id):
        return self.__get_result(id, True)

    def __json_get(self, urlPath):
        if self.__ends_with_uuid(urlPath):
            return self._fs.readtext(urlPath + "/data.xml")
        else:
            return False

    def __json_post(self, urlPath, xmlData):
        if not self.__ends_with_uuid(urlPath):
            xmlDom = ET.fromstring(xmlData)
            id = xmlDom.attrib['id']
            urlPath = urlPath + "/" + id
            self._fs.makedirs(path=urlPath, recreate=True)
            self._fs.writetext(path=urlPath + "/data.xml", contents=xmlData)
        else:
            pass #error

    def __json_put(self, urlPath, xmlData):
        if self.__ends_with_uuid(urlPath):
            xmlData = self.__json_get(urlPath)
            pass
            #self._fs.writetext(path=urlPath+"/data.xml", contents=xmlData)
        else:
            pass #error

    def __ends_with_uuid(self, urlPath):
        return self._is_uuid(path.iteratepath(urlPath[-1]))