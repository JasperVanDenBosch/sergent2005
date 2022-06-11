"""A lookup table of lab-specific configuration

mon_width: width of the monitor in cm
mon_dist: distance of the participant to the monitor in cm
port_type: use serial or parallel port for triggers
port_address: The address of the port used to send triggers.
    The value 'parallel' means the default parallel port will be used.
    Another value will be interpreted to be the address of a serial port.
port_baudrate: Only used for serial ports.
"""

lab_settings = dict(
    jasper=dict(
        mon_width=62.23,
        mon_dist=50,
        mon_resolution=(1920, 1080),
        port_type='serial',
        port_address='/dev/pts/2', # '/dev/ttyUSB0',
        port_baudrate=9600, # 115200,
    ),
    maria=dict(
        mon_width=54.37,
        mon_dist=50,
        mon_resolution=(1920, 1080),
        port_type='parallel',
        port_address='EFF0',
        port_baudrate=0,
    ),
    karine=dict(
        mon_width=53,
        mon_dist=60,
        mon_resolution=(1920, 1080),
        port_type='parallel',
        port_address='C010',
        port_baudrate=0,
    ),
    example=dict(
        mon_width=55, ## width in cm of the experiment screen
        mon_dist=60, ## distance in cm between participant eyes and screen
        mon_resolution=(3456, 2234), ## horizontal, vertical resolution of the monitor
        port_type='dummy', ## serial, parallel, viewpixx or dummy
        ## most systems have only one parallel port, so we can use the default
        port_address='', ## use default address
        port_baudrate=0, ## parallel ports dont require a baudrate
    )
)
