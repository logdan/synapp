""" Get the right tqdm for the environment.
tqdm has a different library for interactive mode. This
file automatically detects interactive mode (Jupyter or IPython)
in order to correctly display progress bars.

Usage:
`from synapp.misc.tqdm_provider import tqdm`
"""

try:
    from tqdm.notebook import tqdm as tqdm_notebook
    from tqdm import tqdm as tqdm_cli
    from IPython.core.getipython import get_ipython

    # Check if the get_ipython exists and whether it's in an interactive environment
    if 'IPKernelApp' not in get_ipython().config:  # Terminal running IPython
        tqdm = tqdm_cli
    else:  # Jupyter notebook
        tqdm = tqdm_notebook
except ImportError as e:  # If IPython is not installed at all
    from tqdm import tqdm as tqdm_cli
    tqdm = tqdm_cli
