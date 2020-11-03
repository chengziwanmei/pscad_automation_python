#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Mouse Command class
#===============================================================================

"""Mouse Event Commands"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
import xml.etree.ElementTree as ET

# ATS imports
from .command import Command


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Mouse Events generator
#===============================================================================

class MouseEvents(Command):

    """Mouse Event Commands"""

    def __init__(self, pscad):
        super().__init__(pscad, 'mouse-event', 'PSCAD')

    def mouse(self, kind, _dx, _dy):
        mouse = ET.SubElement(self.root, 'mouse')
        mouse.set('type', kind)
        mouse.set('dx', str(_dx))
        mouse.set('dy', str(_dy))
        return mouse


    #---------------------------------------------------------------------------
    # Mouse movement
    #---------------------------------------------------------------------------

    def move(self, _dx, _dy):
        self.mouse('move', _dx, _dy)
        return self

    #---------------------------------------------------------------------------
    # Left mouse button down/up/click
    #---------------------------------------------------------------------------

    def leftdown(self, _dx, _dy):
        self.mouse('leftdown', _dx, _dy)
        return self

    def leftup(self, _dx, _dy):
        self.mouse('leftup', _dx, _dy)
        return self

    def leftclick(self, _dx, _dy):
        self.mouse('leftclick', _dx, _dy)
        return self

    #---------------------------------------------------------------------------
    # Middle mouse button down/up/click
    #---------------------------------------------------------------------------

    def middledown(self, _dx, _dy):
        self.mouse('middledown', _dx, _dy)
        return self

    def middleup(self, _dx, _dy):
        self.mouse('middleup', _dx, _dy)
        return self

    def middleclick(self, _dx, _dy):
        self.mouse('middleclick', _dx, _dy)
        return self

    #---------------------------------------------------------------------------
    # Right mouse button down/up/click
    #---------------------------------------------------------------------------

    def rightdown(self, _dx, _dy):
        self.mouse('rightdown', _dx, _dy)
        return self

    def rightup(self, _dx, _dy):
        self.mouse('rightup', _dx, _dy)
        return self

    def rightclick(self, _dx, _dy):
        self.mouse('rightclick', _dx, _dy)
        return self

    #---------------------------------------------------------------------------
    # Scroll wheel
    #---------------------------------------------------------------------------

    def wheel(self, delta):
        mouse = ET.SubElement(self.root, 'mouse')
        mouse.set('type', 'wheel')
        mouse.set('delta', str(delta))
        return self

