"""Test the psychopy wrapper
"""
from experiment.engine import PsychopyEngine
engine = PsychopyEngine()
#from experiment.fake_engine import FakeEngine
#engine = FakeEngine()


# engine.connectTriggerInterface(port_type: str, port_address: str, port_baudrate: int)
engine.askForString('HELLO WORLD')
engine.configureLog('')
engine.configureWindow(dict(
    mon_dist=50,
    mon_width=50,
    mon_resolution=(1920, 1080)
))
engine.loadStimuli(0.5, 5, 0.5)
engine.showMessage('Hello World! Press SPACE', height=2, confirm=True)
engine.displayEmptyScreen(60)
engine.displayT1('OIIO', 99, 60)
engine.displayT2('QUOI', 99, 60)
engine.displayMask('XXX', 60)
engine.displayFixCross(60)
engine.promptIdentity('ID question', ('start', 'end'), 99)
engine.promptVisibility('Viz question', ('start', 'end'), 21, 7, 99)
engine.flush()
engine.stop()
