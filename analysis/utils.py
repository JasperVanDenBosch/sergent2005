from os.path import join, expanduser, basename
from pandas import read_csv
from colorama import init as colorama_init, Fore, Style
import matplotlib.pyplot as plt
colorama_init()

def read_events(data_dir: str, sub: str):
    return read_csv(
        join(data_dir, sub, 'eeg', f'{sub}_task-ab_events.tsv'),
        index_col=False,
        sep='\t',
    )

def read_selected_events(deriv_dir: str, sub: str, mode: str, n_conds: int):
    return read_csv(
        join(deriv_dir, sub, f'{sub}_mode-{mode}_conds-{n_conds}_events.tsv'),
        index_col=False,
        sep='\t',
    )

def read_channels(data_dir: str, sub: str):
    return read_csv(
        join(data_dir, sub, 'eeg', f'{sub}_task-ab_channels.tsv'),
        index_col=False,
        sep='\t',
    )

def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')

def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')

def log_to(report, text, title=None):
    """Add a text page to the PDF report
    
    Args:
        report: matplotlib.backends.backend_pdf.PdfPages object
        text: Text content to display
        title: Optional title for the page
    """
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis('off')
    if title:
        ax.text(0.5, 0.95, title, ha='center', va='top', 
                fontsize=14, fontweight='bold', transform=ax.transAxes)
        ax.text(0.1, 0.85, text, ha='left', va='top', 
                fontsize=12, transform=ax.transAxes, family='monospace')
    else:
        ax.text(0.1, 0.9, text, ha='left', va='top', 
                fontsize=12, transform=ax.transAxes, family='monospace')
    report.savefig(fig, bbox_inches='tight')
    plt.close(fig)
