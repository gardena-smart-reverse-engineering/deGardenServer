#!/usr/bin/python3

import logging
import socket
import _thread
#from fs.memoryfs import MemoryFS
from fs import open_fs

import config
import constants
from ServerHandlers import ReportServerHandler, ControlServerHandler

def main():
    HOST = socket.gethostname()

    logging.basicConfig(level=logging.DEBUG)

    logging.info('Starting deGarden Server %s', constants.VERSION)
    logging.info('Report Port:\t%i', config.REPORT_PORT)
    logging.info('Control Port:\t%i', config.CONTROL_PORT)

    reportSocket = socket.socket()
    controlSocket = socket.socket()

    reportSocket.bind((HOST, config.REPORT_PORT))
    controlSocket.bind((HOST, config.CONTROL_PORT))

    reportSocket.listen(5) #Max 5 clients
    controlSocket.listen(5) #Max 5 clients

    logging.info('started, waiting for clients...')

    fileSystem = open_fs('./deGardenServer/database/')

    while True:
        logging.debug('waiting for report socket')
        c, addr = reportSocket.accept()
        _thread.start_new_thread(ReportServerHandler(fileSystem,c,addr).loop)

        logging.debug('waiting for control socket')
        c, addr = controlSocket.accept()
        _thread.start_new_thread(ControlServerHandler(fileSystem,c,addr).loop)
    reportSocket.close()
    controlSocket.close()

    logging.info('server stopped, bye bye...')

if __name__== "__main__":
  main()