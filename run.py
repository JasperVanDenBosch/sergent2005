"""Simple experiment code to test setup in lab setting
"""
from psychopy.monitors import Monitor
from psychopy.event import getKeys
from psychopy.visual import Window
from psychopy.visual.rect import Rect
from psychopy.hardware.labjacks import U3

port = U3()
port.setData(val, address='FIO') # val: int


my_monitor = Monitor(
    name='latrec_mon',
    distance=50.0
)
my_monitor.setSizePix([1920, 1080])
my_monitor.setWidth(60.0)
my_monitor.saveMon()
win = Window(
    size=[1920, 1080],
    monitor=my_monitor,
    color='black',
    fullscr=True,
    units='deg'
)
win.mouseVisible = False 

stimulus = Rect(
    win=win,
    size=(100, 100),
    #units='deg',
    pos=(0, 0),
    lineColor=(1, 1, 1),
    fillColor=(1, 1, 1),
    name='stimulus'
)

for _ in range(4):
    trigger = 8

    new_keys = getKeys(keyList=['q', 'delete', 'esc'])
    if 'q' in new_keys and 'delete' in new_keys:
        break

    stimulus.draw()
    win.callOnFlip(port.trigger, trigger)
    win.flip()
    ## sleep for stim dur
    win.flip()


win.close()