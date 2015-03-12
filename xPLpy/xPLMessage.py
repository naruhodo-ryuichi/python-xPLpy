# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from xPLpy.xPLNet import Net

__author__ = "naruhodo-ryuichi"

import logging


class MsgType:
    def __init__(self):
        pass

    xPL_ANY = 0
    xPL_COMMAND = 1
    xPL_STATUS = 2
    xPL_TRIGGER = 3


class Source(object):
    def __init__(self, src=None):
        if src:
            self.vendor, self.device, self.instance = src.replace("-", ".").split(".")
        else:
            self.vendor = self.device = self.instance = ""

    def __str__(self):
        return "%s-%s.%s" % (self.vendor, self.device, self.instance)


class Target(object):
    def __init__(self, tgt=None):
        if tgt:
            self.vendor, self.device, self.instance = tgt.replace("-", ".").split(".")
        else:
            self.vendor = self.device = self.instance = ""

    def __str__(self):
        return "%s-%s.%s" % (self.vendor, self.device, self.instance)


class Schema:
    def __init__(self, sch):
        if sch:
            self.sclass, self.stype = sch.split(".")
        else:
            self.sclass = ""
            self.stype = ""

    def __repr__(self):
        return "%s.%s" % (self.sclass, self.stype)


class Message(object):
    """
    Structure and code for message parsing
    """

    def __init__(self, msgtype=None, src=None, tgt=None, sch=None, vals=None, hop=1):
        self.type = msgtype
        self.hop = hop
        self.source = Source(src)
        self.broadcast = False
        self.interval = None
        if tgt is "*":
            self.broadcast = True
            self.target = Target()
        else:
            self.target = Target(tgt)
        self.schema = Schema(sch)
        if vals:
            self.values = dict(vals)
        else:
            self.values = dict()

    def setvalue(self, name, value):
        self.values[name] = str(value)

    def getvalue(self, name):
        return self.values[name]

    def send(self):
        Net().send(self)

    def parse(self, data):
        # first line, message type
        lines = iter(data.split("\n"))
        line = next(lines)
        if line.lower() == "xpl-cmnd":
            self.type = MsgType.xPL_COMMAND
        elif line.lower() == "xpl-trig":
            self.type = MsgType.xPL_TRIGGER
        elif line.lower() == "xpl-stat":
            self.type = MsgType.xPL_STATUS
        else:
            logging.error("Message: type not detected")
        # Header intro
        line = next(lines)
        if line != "{":
            logging.error("message: header not detected")
        # Hop value
        line = next(lines)
        hop, val = line.split("=")
        if hop.strip().lower() != "hop":
            logging.error("message: hop not found")
        self.hop = int(val.strip())
        #Source value
        line = next(lines)
        source, self.source.vendor, self.source.device, self.source.instance = line.strip().replace("=", ".").replace(
            "-", ".").split(".")
        if source.lower() != "source":
            logging.error("message: source not found")
        #target value
        line = next(lines)
        target, val = line.split("=")
        if target.strip().lower() != "target":
            logging.error("mensaje: target no encontrada")
        if val == "*":
            self.broadcast = True
        else:
            self.target.vendor, self.target.device, self.target.instance = val.replace("-", ".").split(".")

        #Header outtro
        line = next(lines)
        if line != "}":
            logging.error("message: header not detected")
        #schema value
        line = next(lines)
        self.schema.sclass, self.schema.stype = line.split(".")

        #schema intro
        line = next(lines)
        if line != "{":
            logging.error("message: schema header not detected")
        name = ""
        val = ""
        line = next(lines)
        while True:
            if line == "}":
                break
            elif line.split("="):
                name, part, val = line.partition("=")
                self.setvalue(name, val)
                line = next(lines)
        #schema outtro
        if line != "}":
            logging.error("message: schema header not detected")

    def __str__(self):
        mymsg = ""
        if self.type == MsgType.xPL_COMMAND:
            mymsg = "xpl-cmnd\n"
        elif self.type == MsgType.xPL_STATUS:
            mymsg = "xpl-stat\n"
        elif self.type == MsgType.xPL_TRIGGER:
            mymsg = "xpl-trig\n"
        mymsg += "{\n"
        mymsg += "hop=" + str(self.hop) + "\n"
        mymsg += "source=" + str(self.source) + "\n"
        if self.broadcast:
            mymsg += "target=*\n"
        else:
            mymsg += "target=" + str(self.target) + "\n"
        mymsg += "}\n"
        mymsg += str(self.schema) + "\n"
        mymsg += "{\n"
        for name, value in list(self.values.items()):
            mymsg += name + "=" + value + "\n"
        mymsg += "}\n"
        return str(mymsg)

    def __repr__(self):
        return self.__str__()

