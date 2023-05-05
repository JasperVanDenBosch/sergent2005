"""Drop-in replacement for the PsychopyEngine for testing
when psychopy is not available
"""
from __future__ import annotations
from typing import Tuple, Dict, Any
import json
import random


class FakeTriggerPort:

    def trigger(self, val: int) -> None:
        print(f'[TRIGGER] {val}')


class FakeEngine(object):

    flips = 0
    secs = 0
    flip_dur = 0.016

    def __init__(self) -> None:
        self.port = FakeTriggerPort()

    def askForString(self, question: str) -> str:
        print(f'[ENGINE] askForString: {question}')
        return '999'

    def configureLog(self, fpath: str):
        pass

    def logDictionary(self, label: str, content: Dict[str, Any]) -> None:
        msg = json.dumps({label: content}, sort_keys=True, indent=4)
        print(f'[DICT] {msg}')

    def connectTriggerInterface(self, settings: Dict) -> None:
        print('[ENGINE] connectTriggerInterface()')

    def configureWindow(self, settings: Dict):
        print('[ENGINE] configureWindow()')

    def measureHardwarePerformance(self) -> Dict[str, Any]:
        return dict()
    
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

    def displayEmptyScreen(self, duration: int) -> float:
        print(f'[ENGINE] EmptyScreen ({duration} x flip)')
        self.flips += duration
        return (self.flips - duration) * self.flip_dur

    def displayT1(self, val: str, trigger: int, duration: int) -> float:
        print(f'[ENGINE] Target 1 "{val}" ({duration} x flip)')
        self.port.trigger(trigger)
        self.flips += duration
        return (self.flips - duration) * self.flip_dur

    def displayT2(self, val: str, trigger: int, duration: int) -> float:
        print(f'[ENGINE] Target 2 "{val}" ({duration} x flip)')
        self.port.trigger(trigger)
        self.flips += duration
        return (self.flips - duration) * self.flip_dur

    def displayMask(self, val: str, duration: int) -> None:
        print(f'[ENGINE] Mask "{val}" ({duration} x flip)')
        self.flips += duration

    def displayFixCross(self, duration: int):
        print(f'[ENGINE] Fixation ({duration} x flip)')
        self.flips += duration

    def promptIdentity(self, prompt: str, options: Tuple[str, str], trigger: int) -> Tuple[int, float, int]:
        print(f'[ENGINE] Identity Task')
        self.port.trigger(trigger)
        self.secs += 3
        onset = self.flips * self.flip_dur
        return (random.randint(0, 1), onset, random.randint(800, 1200))
    
    def promptVisibility(self, prompt: str, labels: Tuple[str, str], scale_length: int, init: int, trigger: int) -> Tuple[int, float, int]:
        print(f'[ENGINE] Identity Task')
        self.port.trigger(trigger)
        self.secs += 4
        onset = self.flips * self.flip_dur
        return (random.randint(0, scale_length-1), onset, random.randint(800, 1200))
    
    def estimateDuration(self) -> int:
        """Simulated duration in seconds
        """
        return self.secs + round(self.flips * (1/60))
    
    def flush(self) -> None:
        print(f'[ENGINE] Flushing')
    
    def stop(self) -> None:
        print(f'[ENGINE] Stopping')
