"""A lookup table of lab-specific configuration

mon_width: width of the monitor in cm
mon_dist: distance of the participant to the monitor in cm
mon_resolution: tuple of the horizontal and vertical number of pixels
port_type: use serial or parallel port for triggers
port_address: The address of the port used to send triggers.
    'parallel' means the default parallel port will be used (currently doesn't work, please get in touch).
    'serial': Serial port
    'viewpixx': triggers sent through the monitor
    'dummy': print triggers to the command line, for development
port_baudrate: Only used for serial ports.
"""
from __future__ import annotations
from typing import Dict, Any

lab_settings = dict(
    damian=dict(
        mon_width=62.23,
        mon_dist=50,
        mon_resolution=(1920, 1080),
        port_type='labjack',
    ),
    maria=dict(
        mon_width=54.37,
        mon_dist=50,
        mon_resolution=(1920, 1080),
        port_type='viewpixx',
        port_address='0xEFF0',
        port_baudrate=0,
    ),
    karine=dict(
        mon_width=53,
        mon_dist=60,
        mon_resolution=(1920, 1080),
        port_type='viewpixx',
        port_address='0xC010',
        port_baudrate=0,
    ),
    example=dict(
        mon_width=55, ## width in cm of the experiment screen
        mon_dist=60, ## distance in cm between participant eyes and screen
        mon_resolution=(1728, 1117), ## horizontal, vertical resolution of the monitor
        port_type='viewpixx', ## serial, parallel, viewpixx or dummy
        port_address='0x378', ## a.k.a. LPT1
        port_baudrate=0, ## parallel ports dont require a baudrate
    )
)

def getLabConfiguration() -> Dict[str, Any]:
    labs_str = ''.join([f'[{l}] ' for l in lab_settings.keys()])
    lab_name = input(f'Please select your lab {labs_str}:')
    assert lab_name in lab_settings.keys(), 'Unknown lab'
    return lab_settings[lab_name]
