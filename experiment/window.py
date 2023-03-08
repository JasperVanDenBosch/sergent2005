from __future__ import annotations
from typing import Dict, Tuple
from psychopy.monitors import Monitor
from psychopy.visual import Window


def configureWindow(settings: Dict) -> Tuple[Window, float]:
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

