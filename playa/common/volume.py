# OSX AppleScript
import warnings
from osax import OSAX

try:
    osax = OSAX()
except Exception, e:
    warnings.warn(e)
    osax = None

def get_volume():
    # OSX only currently
    assert osax

    return osax.get_volume()

def set_volume(value):
    # value should be between 0 and 100
    assert osax

    osax.set_volume(value)
