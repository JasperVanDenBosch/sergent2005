"""Abstracts access to the various ways to send triggers to the EEG
"""
from __future__ import annotations
from typing import Union
from serial import Serial
from psychopy.parallel import ParallelPort
from psychopy.core import wait


class FakeTriggerPort:

    def trigger(self, val: int) -> None:
        print(f'TRIGGER: {val}')


class SerialTriggerPort:

    def __init__(self, address: str, baud: int):
        self.sport = Serial(port=address, baudrate=baud)

    def trigger(self, val: int) -> None:
        self.sport.write(bytes([val]))


class ParallelTriggerPort:

    def __init__(self):
        self.pport = ParallelPort()

    def trigger(self, val: int) -> None:
        self.pport.setData(val)
        wait(0.01)
        self.pport.setData(0)

class ViewPixxTriggerPort:

    def __init__(self):
        # would also require the screen, address.
        raise NotImplementedError()

    def trigger(self, val: int) -> None:
        raise NotImplementedError()


TriggerPort = Union[SerialTriggerPort, ParallelTriggerPort, FakeTriggerPort]

def openTriggerPort(typ: str, address: str, rate: str) -> TriggerPort:
    if typ == 'dummy':
        return FakeTriggerPort()
    elif typ == 'parallel':
        return ParallelTriggerPort()
    elif typ == 'serial':
        return SerialTriggerPort(address, rate)
    elif typ == 'viewpixx':
        return ViewPixxTriggerPort(address)
    else:
        raise ValueError('Unknown port type in lab settings.')
