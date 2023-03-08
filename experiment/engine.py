from __future__ import annotations


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