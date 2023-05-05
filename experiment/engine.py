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
from psychopy.event import waitKeys
from psychopy.core import wait
from psychopy import logging
from psychopy.visual import Window, TextStim
from psychopy.visual.ratingscale import RatingScale
from psychopy.visual.line import Line
from psychopy.visual.rect import Rect
from psychopy.visual.shape import ShapeStim
from psychopy.info import RunTimeInfo
from psychopy.gui import Dlg
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

    ## stimuli
    target1: TextStim
    target2: TextStim
    squares: List[Rect]
    target2_dummy: DummyStim
    mask: TextStim
    fixCross: ShapeStim

    def __init__(self) -> None:
        self.port = FakeTriggerPort()

    def askForString(self, question: str) -> str:
        myDlg = Dlg()
        myDlg.addField(question)
        ok_data = myDlg.show()
        if not myDlg.OK:
            raise ValueError('Dialog was cancelled')
        return ok_data[0]

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
        choices = [options[0], '', options[1]]
        record = dict()
        self.win.timeOnFlip(record, 'flipTime')
        self.win.callOnFlip(self.port.trigger, triggerNr)
        total_rt = 0
        while True:
            ## This loop is a trick to force a choice; if the dummy middle choice is chosen,
            ## we simply create a new RatingScale
            scale = RatingScale(
                self.win,
                noMouse=True,
                choices=choices,
                markerStart=1,
                scale=prompt,
                acceptKeys='space',
                lineColor='DarkGrey',
                markerColor='DarkGrey',
                pos=(0.0, 0.0),
                showAccept=False,
                name='promptId'
            )
            scale.draw()
            self.win.flip()
            while scale.noResponse:
                scale.draw()
                self.win.flip()
            ## in case we have to restart the prompt, store RT
            total_rt += round((scale.getRT() or -999)*1000)
            if scale.getRating() != '':
                ## valid choice; continue
                break
        choice_index = options.index(scale.getRating()) # index of response wrt labels
        return choice_index, record.get('flipTime', -99.99), total_rt
    
    def promptVisibility(self, prompt: str, labels: Tuple[str, str], scale_length: int, init: int, triggerNr: int) -> Tuple[int, float, int]:
        # the rating scale has to be re-initialized in every function call, because
        # the marker start can't be randomized and updated when using the same rating
        # scale object again and again.
        # The marker start needs to be defined randomly beforehand
        scale = RatingScale(
            self.win, low=0,
            high=scale_length-1,
            labels=['nothing', 'maximal visibility'],
            acceptKeys='space',
            scale=prompt,
            noMouse=True,
            lineColor='DarkGrey',
            markerColor='LightGrey',
            pos=(0.0, 0.0),
            showAccept=False,
            markerStart=init,
            name='promptVis'
        )

        scale.draw()
        record = dict()
        self.win.timeOnFlip(record, 'flipTime')
        self.win.callOnFlip(self.port.trigger, triggerNr)
        self.win.flip()

        # Show scale and instruction und confirmation of rating is done
        while scale.noResponse:
            scale.draw()
            self.win.flip()

        choice_index = int(scale.getRating() or -999) # index of response wrt scale
        rt = round((scale.getRT() or -999)*1000) # return RT in milliseconds
        return choice_index, record.get('flipTime', -99.99), rt
    
    def stop(self) -> None:
        self.win.close()


