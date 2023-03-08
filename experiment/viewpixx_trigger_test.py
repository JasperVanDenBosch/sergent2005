"""Quick test to see if ViewPixx configured triggers will arrive in the data.
Run this and check if the triggers reported on the command line are in your data.
"""
from psychopy.visual.text import TextStim
from psychopy import core
from psychopy.event import waitKeys
from window import configureWindow
from labs import getLabConfiguration
from ports import openTriggerPort


settings = getLabConfiguration()
win, scale = configureWindow(settings, fullscr=True)
win.recordFrameIntervals = True
port = openTriggerPort('viewpixx', win, scale=scale, viewPixBulbSize=7)
stimKwargs = dict(height=0.6)


values = [29, 250, 37, 37, 44, 52, 65]
stims = [TextStim(win, text=str(v), **stimKwargs) for v in values]
print()
msg = TextStim(win, text='Press space to start once recording..', height=0.5)
msg.draw()
win.flip()
waitKeys(keyList='space')
win.flip()
core.wait(2)
for val, stim in zip(values, stims):
    stim.draw()
    port.trigger(val)
    win.flip()
    print(val)
    core.wait(0.200)
    win.flip()
    core.wait(2) #ISI
    
print(f'\n\nSent {len(values)} triggers. Check your EEG data to see if they are as above.\n')
print(f'Number of frames dropped: {win.nDroppedFrames}')
