# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = "naruhodo-ryuichi"

import logging
from threading import Thread

from .xPLMessage import Message, MsgType


class Listener(Thread):
    """
    Asynchronous listener. Sends filtered messages to parent service.
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args)
            Thread.__init__(cls.instance)
            cls.instance.running = True
        return cls.instance

    def __init__(self, service, matchMessageType=None, matchSchemaClass=None, matchSchemaType=None):
        Thread.__init__(self)
        self.service = service
        self.running = True
        self.matchMessageType = matchMessageType
        self.matchSchemaClass = matchSchemaClass
        self.matchSchemaType = matchSchemaType

    def run(self):
        logging.debug("xpllistener: thread started")
        while self.running:
            data = self.service.net.read()
            logging.debug("xpllistener: message received")
            msg = Message()
            msg.parse(data)
            if str(msg.source) != str(self.service.source):
                if ((msg.type == self.matchMessageType)
                    or (self.matchMessageType == MsgType.xPL_ANY)
                    or (self.matchMessageType is None)) \
                        and ((msg.schema.sclass == self.matchSchemaClass)
                             or (self.matchSchemaClass is None)) \
                        and ((msg.schema.stype == self.matchSchemaType)
                             or (self.matchSchemaType is None)):
                    self.service.receive(msg)

    def stop(self):
        self.running = False
        self.close()