
from __future__ import annotations
from typing import Tuple


class PsychopyEngine(object):
    # create window
    # create stimulus
    # draw stimulus
    # flip
    # RatingScale
    # core.wait(stimulus_duration)
    # test message event.waitKeys

    def screen(self):

        my_monitor = monitors.Monitor(name='my_monitor', distance=dist_cm)
        my_monitor.setSizePix((width, height))
        my_monitor.setWidth(width_cm)
        my_monitor.saveMon()
        SCREEN = visual.Window(monitor='my_monitor',
                            color=(-1,-1,-1),
                            fullscr=True,
                            units='deg')
        
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