"""This is the main script to run the experiment
"""
from os.path import expanduser, join
from datetime import datetime
from os import makedirs
from experiment.constants import Constants
from experiment.engine import PsychopyEngine
from experiment.labs import getLabConfiguration
const = Constants()  # load fixed parameters wrt timing, sizing etc


## this object represents drawing and interactions via psychopy
engine = PsychopyEngine()

## user input
config = getLabConfiguration()

sub = 'NONE'

## data directory and file paths
data_dir = expanduser(config['site']['directory'])
makedirs(data_dir, exist_ok=True) # ensure data directory exists
# current date+time to seconds, helps to generate unique files, prevent overwriting
dt_str = datetime.now().strftime(f'%Y%m%d%H%M%S')
# full file path to trials (structured) and log (unstructured) output 
trials_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_trials.csv')
log_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_log.txt')

## set log levels and log file location
engine.configureLog(log_fpath)

## setup psychopy monitor and window objects
engine.configureWindow(config)


## setup serial port or other trigger port
engine.connectTriggerInterface(config['triggers'])


# Welcome the participant
engine.showMessage(const.welcome_message, const.LARGE_FONT)


engine.promptIdentity('do soemthing', ('one', 'two'), 69)

engine.stop()
