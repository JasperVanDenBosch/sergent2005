"""Simple experiment code to test setup in lab setting
"""
from psychopy.monitors import Monitor
from psychopy.event import getKeys
from psychopy.visual import Window
from psychopy.visual.rect import Rect
from psychopy.hardware.labjacks import U3
import time

port = U3()

def send_trigger(val: int):
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
    units='pix'
)
win.mouseVisible = False 

stimulus = Rect(
    win=win,
    size=(250, 250),
    units='pix',
    pos=(250, 250),
    lineColor=(1, 1, 1),
    fillColor=(1, 1, 1),
    name='stimulus'
)


for i in range(140):
    trigger = 1+i
    
    new_keys = getKeys(keyList=['q', 'esc'])
    if 'q' in new_keys or 'esc' in new_keys:
        break
        

    time.sleep(2)

    stimulus.draw()
    win.callOnFlip(send_trigger, trigger)
    win.flip()
    time.sleep(0.2)
    win.flip()


win.close()