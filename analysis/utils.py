from colorama import init as colorama_init, Fore, Style
colorama_init()

def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')

def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')