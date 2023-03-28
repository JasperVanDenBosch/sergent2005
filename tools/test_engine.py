"""Test the psychopy wrapper
"""
from experiment.engine import PsychopyEngine
engine = PsychopyEngine()

engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)
target1 = engine.createTextStim(SCREEN, height=string_height, units='deg')
target2_square1 = engine.createRect(SCREEN, size=(square_size, square_size), units='deg', pos=(-5,-5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))
mask = engine.createTextStim(SCREEN, text='INIT', height=string_height, units='deg')