"""Wrapper around SerialPort to provide same interface
"""
from __future__ import annotations
from serial import Serial


class SerialPort(object):

    def __init__(self, address: str, baud: int):
        self.sport = Serial(port=address, baudrate=baud)

    def setData(self, val: int):
        self.sport.write(bytes([val]))
