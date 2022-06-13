"""Abstracts access to the various ways to send triggers to the EEG
"""
from __future__ import annotations
from typing import Union, TYPE_CHECKING
from numpy import int0
from serial import Serial
from psychopy.parallel import ParallelPort
from psychopy.core import wait
from psychopy.visual.line import Line
if TYPE_CHECKING:
    from psychopy.visual import Window as PsychopyWindow


class FakeTriggerPort:

    def trigger(self, val: int) -> None:
        print(f'TRIGGER: {val}')


class SerialTriggerPort:

    def __init__(self, win: PsychopyWindow, address: str, baud: int):
        self.sport = Serial(port=address, baudrate=baud)
        self.win = win

    def trigger(self, val: int) -> None:
        self.win.callOnFlip(self.sport.write, bytes([val]))


class ParallelTriggerPort:

    def __init__(self, address: str):
        """
        Psychopy parallel port documentation uses address examples
        in hexadecimal literal notation which compiles to integer.
        So we also convert our string hex addresses to integers.
        """
        raise NotImplemented('Parallel port disabled because of critical timing issue')
        address_int = int(address, 16)
        self.pport = ParallelPort(address_int)

    def trigger(self, val: int) -> None:
        self.pport.setData(val)
        wait(0.01)
        self.pport.setData(0)

class ViewPixxTriggerPort:

    def __init__(self, win: PsychopyWindow, scale: float, viewPixBulbSize: float):
        self.win = win
        halfWidth, halfHeight = self.win.size[0]*scale/2, self.win.size[1]*scale/2
        self.line = Line(
            win=self.win,
            units = 'pix',
            lineWidth=viewPixBulbSize+0.5,
            start=[-halfWidth, halfHeight],
            end=[-halfWidth+viewPixBulbSize, halfHeight-viewPixBulbSize],
            interpolate = False,
            colorSpace = 'rgb255',
            lineColor = (200, 200, 200)
        )

    def trigger(self, val: int) -> None:
        val = 200
        self.line.setLineColor((val, val, val))
        self.line.draw()


TriggerPort = Union[SerialTriggerPort, ParallelTriggerPort, FakeTriggerPort,
    ViewPixxTriggerPort]

def openTriggerPort(typ: str, win: PsychopyWindow, scale: float, address: str='', rate: int=0, viewPixBulbSize: float=7.0) -> TriggerPort:
    if typ == 'dummy':
        return FakeTriggerPort()
    elif typ == 'parallel':
        return ParallelTriggerPort(address)
    elif typ == 'serial':
        return SerialTriggerPort(win, address, rate)
    elif typ == 'viewpixx':
        return ViewPixxTriggerPort(win, scale, viewPixBulbSize)
    else:
        raise ValueError('Unknown port type in lab settings.')
