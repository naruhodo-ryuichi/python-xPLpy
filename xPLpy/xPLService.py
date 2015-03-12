# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import random
import time
import socket
from threading import Timer, Thread

from .xPLConfig import localVendor
from .xPLListener import Listener
from .xPLNet import Net
from .xPLMessage import Message, MsgType, Source


__author__ = "naruhodo-ryuichi"


class XPLService(Thread):
    """
    A xPL service. Manages hbeat sending, startup-keep up-closing and message sending-receiving,
    A service instantiates a listener to receive messages and a message object to send them.
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args)
            Thread.__init__(cls.instance)
            cls.instance.running = True
        return cls.instance

    def __init__(self, src=None):
        super(XPLService, self).__init__()
        self.running = None
        self.lsn = None
        self.net = Net()
        if src:
            self.source = Source(src)
        else:
            self.source = "%s-%s.%s" % (
            localVendor, self.__class__.__name__.lower(), socket.gethostname().lower().replace("-", ""))
        self.hb = Message(MsgType.xPL_STATUS, self.source, "*", "hbeat.app")
        self.hb.interval = 5 * 60  # seconds

    def run(self):
        pass

    def start(self):
        self.net.connect()
        # send heartbeat
        self.hb.setvalue("interval", self.hb.interval)
        self.hb.setvalue("port", self.net.port)
        self.hb.setvalue("remote-ip", self.net.address)
        self.sendhb()
        self.addlistener()
        logging.info("service: listener added")
        self.run()

    def rcv(self, msg):
        pass

    def receive(self, msg):
        if (msg.type is MsgType.xPL_COMMAND) and str(msg.schema) == "hbeat.request":
            time.sleep(random.uniform(2, 6))
            self.hb.send()
        else:
            self.rcv(msg)

    def stop(self):
        self.hb.schema.stype = "end"
        self.hb.send()
        logging.info("service: hb end sent")
        self.net.disconnect()
        self.running = False
        self.close()

    def addlistener(self, matchMessageType=None, matchSchemaClass=None, matchSchemaType=None):
        logging.info("service: listener started")
        self.lsn = Listener(self, matchMessageType=matchMessageType, matchSchemaClass=matchSchemaClass,
                            matchSchemaType=matchSchemaType)
        self.lsn.start()

    def sendhb(self):
        self.hb.send()
        logging.info("service: heartbeat sent")
        tshb = Timer(self.hb.interval, self.sendhb)
        tshb.start()