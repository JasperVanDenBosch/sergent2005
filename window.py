from __future__ import annotations
from typing import Dict
from psychopy.monitors import Monitor
from psychopy.visual import Window


def configureWindow(settings: Dict, fullscr: bool):
    my_monitor = Monitor(name='EMLSergent2005', distance=settings['mon_dist'])
    my_monitor.setSizePix(settings['mon_resolution'])
    my_monitor.setWidth(settings['mon_width'])
    my_monitor.saveMon()
    return Window(
        monitor='EMLSergent2005',
        color=(-1,-1,-1),
        fullscr=fullscr,
        units='deg'
    )
