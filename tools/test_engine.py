"""Test the psychopy wrapper
"""
#from experiment.engine import PsychopyEngine
from experiment.fake_engine import FakeEngine
engine = FakeEngine()


# engine.connectTriggerInterface(port_type: str, port_address: str, port_baudrate: int)
engine.configureLog('')
engine.configureWindow(dict())
engine.loadStimuli(0, 0, 0)
engine.createLine()
engine.showMessage('Hello World!', text_height=0.6, wait=True)
engine.displayEmptyScreen(11)
engine.displayT1('OIIO', 99, 12)
engine.displayT2('QUOI', 99, 13)
engine.displayMask('XXX', 14)
engine.displayFixCross(15)
engine.promptIdentity('ID question', ('start', 'end'), 99)
engine.promptVisibility('Viz question', ('start', 'end'), 77, 0, 99)
