from os.path import join, expanduser, basename
from pandas import read_csv
from colorama import init as colorama_init, Fore, Style
colorama_init()

def read_events(data_dir: str, sub: str):
    return read_csv(
        join(data_dir, sub, 'eeg', f'{sub}_task-ab_events.tsv'),
        index_col=0,
        sep='\t',
    )

def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')

def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')