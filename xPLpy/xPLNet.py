# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .xPLConfig import bufferSize

__author__ = "naruhodo-ryuichi"

import socket
import logging


class Net(object):
    """
    A xpl net configuration object. Manages low level socket access
    """

    def __init__(self, address=None, port=3865):
        self.broadcast = ("255.255.255.255", 3865)
        if address:
            self.address = address
        else:
            self.address = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.buff = bufferSize
        self.UDPsk = None

    def connect(self):
        connected = False
        for self.port in [self.port] + list(range(50000, 50010)):
            try:
                self.UDPsk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.UDPsk.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                logging.debug("xplnet: Trying to connect to: %s:%s", self.address, self.port)
                self.UDPsk.bind((self.address, self.port))
                connected = True
                logging.info("xplnet: Successfully connected to: %s:%s", self.address, self.port)
            except socket.error as xxx_todo_changeme:
                (value, message) = xxx_todo_changeme.args
                self.disconnect()
                logging.error("xplnet: Error connecting to: %s", message)
            finally:
                if connected is True:
                    break
        if not connected:
            exit(1)

    def disconnect(self):
        if self.UDPsk:
            self.UDPsk.close()

    def send(self, msg):
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logging.debug("xplnet: Sending %s", msg)
        sk.sendto(bytes.decode(msg.__str__()), self.broadcast)
        sk.close()

    def read(self):
        data, address = self.UDPsk.recvfrom(self.buff)
        logging.debug("xplnet: From %s received %s " % (address, data))
        return data
