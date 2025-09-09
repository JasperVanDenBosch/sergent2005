"""
This is an interface / wrapper around the psychopy functionality.
This makes it easier to work on the rest of the code without psychopy,
and to debug trial order, data formatting etc.

https://psychopy.org/coder/codeStimuli.html
https://psychopy.org/general/timing/detectingFrameDrops.html#warn-me-if-i-drop-a-frame
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Dict, List, Union, Any
import json
from psychopy.monitors import Monitor
from psychopy.event import waitKeys, getKeys
from psychopy.hardware.keyboard import Keyboard
from psychopy.core import wait
from psychopy import logging
from psychopy.visual import Window, TextStim
from psychopy.visual.slider import Slider
from psychopy.visual.line import Line
from psychopy.visual.rect import Rect
from psychopy.visual.shape import ShapeStim
from psychopy.info import RunTimeInfo
#from psychopy.gui import Dlg
from random import choice
from string import ascii_uppercase, digits
import numpy
from experiment.dummy import DummyStim
from experiment.ports import TriggerInterface, FakeTriggerPort, createTriggerPort
if TYPE_CHECKING:
    Stimulus = Union[TextStim, DummyStim, ShapeStim, Rect]


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class PsychopyEngine(object):

    win: Window
    port: TriggerInterface
    _exitNow: bool

    ## stimuli
    target1: TextStim
    target2: TextStim
    squares: List[Rect]
    target2_dummy: DummyStim
    mask: TextStim
    fixCross: ShapeStim

    def __init__(self) -> None:
        self.port = FakeTriggerPort()
        self._exitNow = False

    def askForParticipantId(self) -> str:
        DEFAULT = '9999'
        LABEL = 'Participant ID'
        try:
            from psychopy.gui import Dlg
            dlg = Dlg(title=LABEL)
            dlg.addField(LABEL, DEFAULT)
            data = dlg.show()
            string_id = data[LABEL]
            if not dlg.OK:
                raise ValueError('No participant ID given')
        except:
            from tkinter.simpledialog import askstring
            string_id = askstring(LABEL, LABEL, initialvalue=str(DEFAULT))
            if string_id is None:
                raise ValueError('No participant ID given')
        return string_id

    def configureLog(self, fpath: str):
        logging.console.setLevel(logging.WARN)
        logging.LogFile(fpath, level=logging.INFO, filemode='w')

    def logDictionary(self, label: str, content: Dict[str, Any]) -> None:
        logging.info(
            json.dumps({label: content}, sort_keys=True, indent=4, cls=NumpyEncoder)
        )

    def flush(self) -> None:
        logging.flush()

    def configureWindow(self, settings: Dict) -> None:
        mon_settings = settings['monitor']
        my_monitor = Monitor(
            name='EMLSergent2005',
            distance=mon_settings['distance'])
        my_monitor.setSizePix(mon_settings['resolution'])
        my_monitor.setWidth(mon_settings['width'])
        my_monitor.saveMon()
        self.win = Window(
            size=mon_settings['resolution'],
            monitor=my_monitor,
            color='black',
            fullscr=True,
            units='deg'
        )
        self.win.mouseVisible = False 
        scaling = mon_settings['resolution'][0] / self.win.size[0]
        if scaling == 0.5: 
            print('Looks like a retina display')
        if scaling != 1.0:
            print('Weird scaling. Is your configured monitor resolution correct?')

    def measureHardwarePerformance(self) -> Dict[str, Any]:
        return RunTimeInfo(win=self.win)

    def loadStimuli(self, squareSize: float, squareOffset: int, fixSize: float):
        self.target1 = TextStim(self.win, height=1, units='deg', name='target1')
        self.target1.autoLog = True
        self.target2 = TextStim(self.win, height=1, units='deg', name='target2')
        self.target2.autoLog = True
        self.target2_dummy = DummyStim()
        self.mask = TextStim(self.win, height=1, units='deg', name='mask')
        self.mask.autoLog = True
        o = squareOffset
        positions = [(-o, -o), (o, -o), (-o, o), (o, o)]
        self.squares = []
        for p, pos in enumerate(positions):
            self.squares.append(Rect(
                win=self.win,
                size=(squareSize, squareSize),
                units='deg',
                pos=pos,
                lineColor=(1, 1, 1),
                fillColor=(1, 1, 1),
                name=f'square{p}'
            ))
        self.fixCross = ShapeStim(
            self.win,
            pos=(0.0, 0.0),
            vertices=(
                (0,-fixSize),
                (0,fixSize),
                (0,0),
                (-fixSize,0),
                (fixSize,0)
            ),
            units = 'deg',
            lineWidth = fixSize,
            closeShape = False,
            lineColor=(1, 1, 1),
            name='fixCross'
        )
        self.fixCross.autoLog = True

    def createLine(self, **kwargs):
        """Paint a line of pixels

        Used by viewpixx triggers
        """
        return Line(**kwargs)

    def showMessage(self, message: str, height=0.6, confirm=True):
        msg = TextStim(self.win, text=message, height=height, units='deg',
                            name='message')
        msg.autoLog = True
        msg.draw()
        self.win.flip()
        if confirm:
            waitKeys(keyList='space')
        else:
            wait(1.5)

    def connectTriggerInterface(self, settings: Dict) -> None:
        self.port = createTriggerPort(
            typ=settings.get('type', '?'),
            engine=self,
            scale=1.0,
            address=settings.get('address', ''),
            rate=settings.get('baudrate', 0),
            viewPixBulbSize=7.0
        )

    def drawFlipAndTrigger(self, stims: List[Stimulus], duration: int, triggerNr: int) -> float:
        record = dict()
        for stim in stims:
            stim.draw()
        self.win.logOnFlip(level=logging.DATA, msg=f'flip {triggerNr}')
        self.win.timeOnFlip(record, 'flipTime')
        self.win.callOnFlip(self.port.trigger, triggerNr)
        self.win.flip()
        for _ in range(duration-1):
            for stim in stims:
                stim.draw()
            self.win.flip()
            self.port.reset()
        return record.get('flipTime', -99.99)

    def displayEmptyScreen(self, duration: int) -> float:
        record = dict()
        self.win.logOnFlip(level=logging.DATA, msg=f'flip blank')
        self.win.timeOnFlip(record, 'flipTime')
        for _ in range(duration):
            self.win.flip()
        return record.get('flipTime', -99.99)

    def displayT1(self, val: str, triggerNr: int, duration: int) -> float:
        '''
        Displays the first target (T1) consisting of either the string 'OXXO' or 'XOOX'
        '''
        self.target1.text = val
        return self.drawFlipAndTrigger([self.target1], duration, triggerNr)

    def displayT2(self, val: str, triggerNr: int, duration: int) -> float:
        '''
        Displays the second target (T2) constisting of 4 white squares and (if present
        condition is active) of a number word in capital letters.
        Parameters:
            T2_present bool: True for present or False for absent
        '''
        if len(val):
            target2 = self.target2
        else:
            target2 = self.target2_dummy
        target2.text = val
        return self.drawFlipAndTrigger([target2]+self.squares, duration, triggerNr)

    def displayMask(self, val: str, duration: int) -> None:
        '''
        Displays a mask consisting of 4 consonants. The mask appears after the targets.
        The selection and order of consonants is ramdomly chosen at every execution.
        '''
        self.mask.text = val
        for _ in range(duration):
            self.mask.draw()
            self.win.flip()

    def displayFixCross(self, duration: int):
        for _ in range(duration):
            self.fixCross.draw()
            self.win.flip()

    def promptIdentity(self, prompt: str, options: Tuple[str, str], triggerNr: int) -> Tuple[int, float, int]:
        """Display a slider for the participant to identify the stimulus

        Args:
            prompt (str): instruction
            options (Tuple[str, str]): tuple with the labels of the two options
            triggerNr (int): integer number to send as trigger when slider first displayed

        Returns:
            Tuple[int, float, int]: rating, onset, rt (in milliseconds)
        """
        instruction = TextStim(
            self.win,
            text=prompt,
            height=1.5,
            pos=(0.0, 5.0),
            units='deg',
            name='promptIdentity instruction'
        )
        choices = [options[0], '', options[1]]
        record = dict()
        self.win.timeOnFlip(record, 'flipTime')
        self.win.callOnFlip(self.port.trigger, triggerNr)
        slider = Slider(
            win=self.win,
            name='promptId',
            size=(16.0, 2.0),
            units='deg',
            pos=(0.0, -2.0),
            labels=choices,
            granularity=1,
            ticks=[0, 1, 2],
            style=['rating'], # ['slider', 'rating', 'radio', 'scrollbar', 'choice']¶
            lineColor='DarkGrey',
            markerColor='DarkGrey',
        )
        slider.setRating(1)
        keyboard = Keyboard()
        n_moves = 0
        while True:
            slider.draw()
            instruction.draw()
            self.win.flip()

            keys = keyboard.getKeys()
            if len(keys):
                if 'left' in keys:
                    n_moves += 1
                    slider.setRating(0)
                elif 'right' in keys:
                    n_moves += 1
                    slider.setRating(2)
                elif ('space' in keys) and (n_moves > 0):
                    break
                elif 'escape' in keys:
                    self._exitNow = True
                    break
            self.port.reset()

        choice = choices[slider.getRating()]
        onset = record.get('flipTime', -99.99)
        rt = round((slider.getRT() or 9999)*1000)
        return choice, onset, rt
    
    def promptVisibility(self, prompt: str, labels: Tuple[str, str], scale_length: int, init: int, triggerNr: int) -> Tuple[int, float, int]:
        """Display a slider for the participant to rate the visibility of the stimulus

        Args:
            prompt (str): instruction
            labels (Tuple[str, str]): tuple with the labels of the two extremes
            triggerNr (int): integer number to send as trigger when slider first displayed

        Returns:
            Tuple[int, float, int]: rating, onset, rt (in milliseconds)
        """
        instruction = TextStim(
            self.win,
            text=prompt,
            pos=(0.0, 5.0),
            height=1.5,
            units='deg',
            name='promptVisibility instruction'
        )
        record = dict()
        self.win.timeOnFlip(record, 'flipTime')
        self.win.callOnFlip(self.port.trigger, triggerNr)
        values = list(range(scale_length))
        slider = Slider(
            win=self.win,
            name='promptVis',
            size=(30.0, 1.0),
            units='deg',
            startValue=init,
            pos=(0.0, -2.0),
            labels=labels,
            granularity=1,
            ticks=values,
            style=['rating'], # ['slider', 'rating', 'radio', 'scrollbar', 'choice']¶
            lineColor='DarkGrey',
            markerColor='DarkGrey',
            labelWrapWidth=None,
        )
        slider.setRating(init)
        keyboard = Keyboard()
        n_moves = 0
        while True:
            slider.draw()
            instruction.draw()
            self.win.flip()

            keys = keyboard.getKeys()
            if len(keys):
                if 'left' in keys:
                    n_moves += 1
                    slider.setRating(max(0, slider.getRating()-1)) ## todo
                elif 'right' in keys:
                    n_moves += 1
                    slider.setRating(min(max(values), slider.getRating()+1))
                elif ('space' in keys) and (n_moves > 0):
                    break
                elif 'escape' in keys:
                    self._exitNow = True
                    break
            self.port.reset()

        choice = slider.getRating()
        onset = record.get('flipTime', -99.99)
        rt = round((slider.getRT() or 9999)*1000)
        return choice, onset, rt
    
    def exitRequested(self) -> bool:
        if self._exitNow:
            return True
        if getKeys(keyList=['escape']):
            self._exitNow = True
            logging.warn('EXIT REQUESTED (ESC pressed)')
            return True
        return False
    
    def stop(self) -> None:
        self.win.close()


