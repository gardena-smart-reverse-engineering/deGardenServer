#!/usr/bin/python3

import socket
import _thread

import config
import constants
from ServerHandlers import ReportServerHandler, ControlServerHandler

def main():
    HOST = socket.gethostname()

    print('Starting deGarden Server', constants.VERSION)
    print('Report Port:\t', config.REPORT_PORT)
    print('Control Port:\t', config.CONTROL_PORT)

    reportSocket = socket.socket()
    controlSocket = socket.socket()

    reportSocket.bind((HOST, config.REPORT_PORT))
    controlSocket.bind((HOST, config.CONTROL_PORT))

    reportSocket.listen(5) #Max 5 clients
    controlSocket.listen(5) #Max 5 clients

    print('started, waiting for clients...')

    while True:
        c, addr = reportSocket.accept()
        _thread.start_new_thread(ReportServerHandler(c,addr).loop())

        c, addr = controlSocket.accept()
        _thread.start_new_thread(ControlServerHandler(c,addr).loop())
    reportSocket.close()
    controlSocket.close()

    print('server stopped, bye bye...')

if __name__== "__main__":
  main()