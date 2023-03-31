"""Drop-in replacement for the PsychopyEngine for testing
when psychopy is not available
"""
from __future__ import annotations
from typing import Tuple, Dict
from experiment.ports import TriggerInterface, FakeTriggerPort


class FakeEngine(object):

    port: TriggerInterface

    flips = 0
    secs = 0

    def __init__(self) -> None:
        self.port = FakeTriggerPort()

    def configureLog(self, fpath: str):
        pass

    def connectTriggerInterface(self, port_type: str, port_address: str,
                                port_baudrate: int) -> None:
        print('[ENGINE] connectTriggerInterface()')

    def configureWindow(self, settings: Dict):
        print('[ENGINE] configureWindow()')
    
    def loadStimuli(self, squareSize: float, squareOffset: int, fixSize: float):
        print('[ENGINE] loadStimuli()')

    def createLine(self, **kwargs):
        """Paint a line of pixels

        Used by viewpixx triggers
        """
        print('[ENGINE] createLine()')

    def showMessage(self, message: str, height=0.6, confirm=True):
        print(f'[ENGINE] Message: {"WAIT" if confirm else ""} {message}')
        self.secs += 20

    def displayEmptyScreen(self, duration: int) -> None:
        print(f'[ENGINE] EmptyScreen ({duration} x flip)')
        self.flips += duration

    def displayT1(self, val: str, trigger: int, duration: int) -> None:
        print(f'[ENGINE] Target 1 "{val}" ({duration} x flip)')
        self.port.trigger(trigger)
        self.flips += duration

    def displayT2(self, val: str, trigger: int, duration: int) -> None:
        print(f'[ENGINE] Target 2 "{val}" ({duration} x flip)')
        self.port.trigger(trigger)
        self.flips += duration

    def displayMask(self, val: str, duration: int) -> None:
        print(f'[ENGINE] Mask "{val}" ({duration} x flip)')
        self.flips += duration

    def displayFixCross(self, duration: int):
        print(f'[ENGINE] Fixation ({duration} x flip)')
        self.flips += duration

    def promptIdentity(self, prompt: str, options: Tuple[str, str], trigger: int) -> Tuple[int, int]:
        print(f'[ENGINE] Identity Task')
        self.port.trigger(trigger)
        self.secs += 3
        return (0, 0)
    
    def promptVisibility(self, prompt: str, labels: Tuple[str, str], scale_length: int, init: int, trigger: int) -> Tuple[int, int]:
        print(f'[ENGINE] Identity Task')
        self.port.trigger(trigger)
        self.secs += 4
        return (0, 0)
    
    def estimateDuration(self) -> int:
        """Simulated duration in seconds
        """
        return self.secs + round(self.flips * (1/60))
