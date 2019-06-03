#!/usr/bin/python3

import logging
import _thread
#from fs.memoryfs import MemoryFS
from fs import open_fs

import webserver

import config
import constants
from ServerHandlers import ReportServerHandler, ControlServerHandler

def main():
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Starting deGarden Server %s', constants.VERSION)
    fileSystem = open_fs('./deGardenServer/database/')

    reportServer = ReportServerHandler(fileSystem, config.REPORT_PORT)
    controlServer = ControlServerHandler(fileSystem, config.CONTROL_PORT)

    _thread.start_new_thread(reportServer.loop)
    _thread.start_new_thread(controlServer.loop)
    webserver.start(fileSystem, controlServer)

    while True:
        pass

    logging.info('bye bye...')

if __name__== "__main__":
  main()