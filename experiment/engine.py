
from __future__ import annotations
from typing import Tuple, Dict
from psychopy.monitors import Monitor
from psychopy.visual import Window
from psychopy.visual.line import Line
from experiment.ports import TriggerInterface, FakeTriggerPort, createTriggerPort


class PsychopyEngine(object):

    port: TriggerInterface

    # create window
    # create stimulus
    # draw stimulus
    # flip
    # RatingScale
    # core.wait(stimulus_duration)
    # test message event.waitKeys

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

    def configureWindow(self, settings: Dict) -> Tuple[Window, float]:
        my_monitor = Monitor(name='EMLSergent2005', distance=settings['mon_dist'])
        my_monitor.setSizePix(settings['mon_resolution'])
        my_monitor.setWidth(settings['mon_width'])
        my_monitor.saveMon()
        win = Window(
            size=settings['mon_resolution'],
            monitor='EMLSergent2005',
            color=(-1,-1,-1),
            fullscr=True,
            units='deg'
        )
        scaling = settings['mon_resolution'][0] / win.size[0]
        if scaling == 0.5:
            print('Looks like a retina display')
        elif scaling != 0.0:
            print('Weird scaling. Is your configured monitor resolution correct?')
        return win, scaling
        
    def createTextStim(self, text: str):
        # target2 = visual.TextStim(SCREEN, height=string_height, units='deg')
        #mask = visual.TextStim(SCREEN, text='INIT', height=string_height, units='deg')


    def createRect(self, size: Tuple[float, float], pos: Tuple[int, int]):
        # target2_square1 = visual.Rect(SCREEN, size=(square_size, square_size), units='deg', pos=(-5,-5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))

    def createFixCross(self):
        fix_cross_arm_len = 0.4
        fix_cross = visual.ShapeStim(
            SCREEN,
            pos=(0.0, 0.0),
            vertices=(
                (0,-fix_cross_arm_len),
                (0,fix_cross_arm_len),
                (0,0),
                (-fix_cross_arm_len,0),
                (fix_cross_arm_len,0)
            ),
            units = 'deg',
            lineWidth = fix_cross_arm_len,
            closeShape = False,
            lineColor = (1, 1, 1)
        )

    def createLine(self, **kwargs):
        return Line(**kwargs)

    def showMessage(self, message: str, text_height=0.6, wait=True):
        print(f'[showMessage] {message}')
        return
        text_to_display = visual.TextStim(SCREEN, text=message, height=text_height)
        text_to_display.draw()
        SCREEN.flip()
        if wait:
            event.waitKeys(keyList='space')
        else:
            core.wait(1.5)

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
