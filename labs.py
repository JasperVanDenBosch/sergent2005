"""A lookup table of lab-specific configuration

mon_width: width of the monitor in cm
mon_dist: distance of the participant to the monitor in cm
port_address: The address of the port used to send triggers.
    The value 'parallel' means the default parallel port will be used.
    Another value will be interpreted to be the address of a serial port.
port_baudrate: Only used for serial ports.
"""

lab_settings = dict(
    jasper=dict(
        mon_width=62.23,
        mon_dist=60,
        port_address='/dev/ttyUSB0',
        port_baudrate=115200,
    )
)