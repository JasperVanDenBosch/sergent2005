"""
https://psychopy.org/coder/codeStimuli.html
https://psychopy.org/general/timing/detectingFrameDrops.html#warn-me-if-i-drop-a-frame
"""
from __future__ import annotations
from typing import List
from typing import Tuple, Dict
from psychopy.monitors import Monitor
from psychopy.event import waitKeys
from psychopy.core import wait
from psychopy.visual import Window, TextStim
from psychopy.visual.line import Line
from psychopy.visual.rect import Rect
from psychopy.visual.shape import ShapeStim
from experiment.ports import TriggerInterface, FakeTriggerPort, createTriggerPort


class PsychopyEngine(object):

    win: Window
    port: TriggerInterface

    ## stimuli
    target1: TextStim
    target2: TextStim
    target2_squares: List[Rect]
    mask: TextStim
    fixCross: ShapeStim

    def __init__(self) -> None:
        self.port = FakeTriggerPort()

    def configureLog(self, fpath: str):
        pass
        # logging.console.setLevel(logging.WARNING)
        # logging.LogFile(log_fpath, logging.EXP)

        ## timer
        # clock = core.Clock()
        # logging.setDefaultClock(clock)
        # logging.exp(f'time={clock.getTime(applyZero=False)}')

        #logFile = logging.LogFile(log_fpath, level=logging.EXP)
        #logging.console.setLevel(logging.INFO)

    def configureWindow(self, settings: Dict) -> None:
        my_monitor = Monitor(name='EMLSergent2005', distance=settings['mon_dist'])
        my_monitor.setSizePix(settings['mon_resolution'])
        my_monitor.setWidth(settings['mon_width'])
        my_monitor.saveMon()
        self.win = Window(
            size=settings['mon_resolution'],
            monitor='EMLSergent2005',
            color=(-1,-1,-1),
            fullscr=True,
            units='deg'
        )
        scaling = settings['mon_resolution'][0] / self.win.size[0]
        if scaling == 0.5: 
            print('Looks like a retina display')
        elif scaling != 0.0:
            print('Weird scaling. Is your configured monitor resolution correct?')

    def loadStimuli(self, squareSize: float, squareOffset: int, fixSize: float):
        self.target1 = TextStim(self.win, height=1, units='deg')
        self.target2 = TextStim(self.win, height=1, units='deg')
        self.mask = TextStim(self.win, height=1, units='deg')
        square_size = (squareSize, squareSize)
        o = squareOffset
        positions = [(-o, -o), (o, -o), (-o, o), (o, o)]
        self.target2_squares = []
        for pos in positions:
            self.target2_squares.append(Rect(
                self.win,
                size=(square_size, square_size),
                units='deg',
                pos=pos,
                lineColor=(1, 1, 1),
                fillColor=(1, 1, 1)
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
            lineColor = (1, 1, 1)
        )

    def createLine(self, **kwargs):
        """Paint a line of pixels

        Used by viewpixx triggers
        """
        return Line(**kwargs)

    def showMessage(self, message: str, height=0.6, confirm=True):
        self.msg = TextStim(self.win, text=message, height=height, units='deg')
        self.msg.draw()
        self.win.flip()
        if confirm:
            waitKeys(keyList='space')
        else:
            wait(1.5)

    ## display duration, custom text, trigger on flip
    def connectTriggerInterface(self, port_type: str, port_address: str,
                                port_baudrate: int) -> None:
        self.port = createTriggerPort(
            typ=port_type,
            engine=self,
            scale=1.0,
            address=port_address,
            rate=port_baudrate,
            viewPixBulbSize=7.0
        )

    def displayEmptyScreen(self, duration: int) -> None:
        for _ in range(duration):
            self.win.flip()

    def displayT1(self, val: str, triggerNr: int, duration: int) -> None:
        '''
        Displays the first target (T1) consisting of either the string 'OXXO' or 'XOOX'
        '''
        self.target1.text = val
        self.target1.draw()
        self.port.trigger(triggerNr)
        for _ in range(duration):
            self.win.flip()

    def displayT2(self, val: str, triggerNr: int, duration: int) -> None:
        '''
        Displays the second target (T2) constisting of 4 white squares and (if present
        condition is active) of a number word in capital letters.
        Parameters:
            T2_present bool: True for present or False for absent
        '''
        for square in self.target2_squares:
            square.draw()

        if len(val):
            self.target2.text = val #random.choice(constants.target2_strings)
            self.target2.draw()
        else:
            self.target2.text = ''

        self.port.trigger(triggerNr)
        for _ in range(duration):
            self.win.flip()

    def displayMask(self, val: str, duration: int) -> None:
        '''
        Displays a mask consisting of 4 consonants. The mask appears after the targets.
        The selection and order of consonants is ramdomly chosen at every execution.
        '''
        self.mask.text = val
        self.mask.draw()
        for _ in range(duration):
            self.win.flip()

    def displayFixCross(self, duration: int):
        self.fixCross.draw()
        for _ in range(duration):
            self.win.flip()

    def promptIdentity(self, prompt: str, options: Tuple[str, str], trigger: int) -> Tuple[int, int]:
        while True:
            ## This loop is a trick to force a choice; if the dummy middle choice is chosen,
            ## we simply create a new RatingScale
            rating_scaleT1 = RatingScale(SCREEN, noMouse=True,
                choices=['OO', '', 'XX'], markerStart=1, #labels=['OO', '', 'XX'],
                scale=task1_text, acceptKeys='space', lineColor='DarkGrey',
                markerColor='DarkGrey', pos=(0.0, 0.0), showAccept=False)
            rating_scaleT1.draw()
            SCREEN.flip()
            while rating_scaleT1.noResponse:
                rating_scaleT1.draw()
                SCREEN.flip()
            if rating_scaleT1.getRating() != '':
                ## valid choice; continue
                break

        # get and return the rating int, int
        return [rating_scaleT1.getRating(), rating_scaleT1.getRT()]
    
    def promptVisibility(self, prompt: str, labels: Tuple[str, str], scale_length: int, init: int, trigger: int) -> Tuple[int, int]:
    # the rating scale has to be re-initialized in every function call, because
    # the marker start can't be randomized and updated when using the same rating
    # scale object again and again.
    # The marker start needs to be defined randomly beforehand
        scale_length = 21 # the maximum visibiliy rating
        task2_text = 'Please indicate the visibility of the number word \n by choosing a rating on the scale below.\n' \
                    'Press \'space\' to confirm.\n\n'
        random_init = random.choice(range(scale_length))
        rating_scaleT2 = RatingScale(SCREEN, low=0, high=scale_length-1, labels=['nothing', 'maximal visibility'],
                                            acceptKeys='space', scale=task2_text, noMouse=True, lineColor='DarkGrey',
                                            markerColor='LightGrey', pos=(0.0, 0.0), showAccept=False, markerStart=random_init)

        rating_scaleT2.draw()
        p.trigger(Triggers.taskT2visibility)
        SCREEN.flip()

        # Show scale and instruction und confirmation of rating is done
        while rating_scaleT2.noResponse:
            rating_scaleT2.draw()
            SCREEN.flip()

        # get and return the rating
        return [rating_scaleT2.getRating(), rating_scaleT2.getRT()]
