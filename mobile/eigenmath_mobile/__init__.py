"""Prebuilt Jupyter mobile controls. No server authentication changes."""
from importlib.metadata import version

__version__ = version('eigenmath-mobile')

def _jupyter_labextension_paths():
    return [{'src': 'labextension', 'dest': '@querygraph/eigenmath-mobile'}]
