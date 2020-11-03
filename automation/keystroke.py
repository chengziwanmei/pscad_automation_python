#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Keystroke Command class
#===============================================================================

"""Keystroke Commands"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging, string
import xml.etree.ElementTree as ET

# ATS imports
from .command import Command


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Keystroke Command generator
#===============================================================================

class KeyStrokes(Command):

    """KeyStroke XML Commands"""

    def __init__(self, pscad):
        super().__init__(pscad, 'keystroke', 'PSCAD')

    def key(self, vktype, vkcode):
        key = ET.SubElement(self.root, 'key')
        key.set('type', vktype)
        key.set('vk-code', str(vkcode))
        return key

    #---------------------------------------------------------------------------
    # Key presses (down, up, stroke)
    #---------------------------------------------------------------------------

    def key_down(self, vkcode):
        self.key('down', vkcode)
        return self

    def stroke(self, vkcode):
        self.key('stroke', vkcode)
        return self

    def key_up(self, vkcode):
        self.key('up', vkcode)
        return self

    #---------------------------------------------------------------------------
    # Typing keys
    #   Cooked data:
    #       ! - Hold shift key down for next character
    #               !t -> T    !5 -> %    !' -> "
    #       @ - Hold alt down
    #               @a -> <Alt-A>
    #       # - Hold control down
    #               #c -> <Ctrl-C>
    #
    #   typing(text):
    #       automatically cooks uncooked strings
    #         keys.typing("He said, 'Why?'")  ->  !He said, '!Why!?'
    #---------------------------------------------------------------------------

    def typing(self, data, cooked=False):
        key = ET.SubElement(self.root, 'key')
        key.set('type', 'typing')
        if not cooked:
            data = self.cook(data)
        key.text = data
        return self

    @staticmethod
    def cook(data):
        """Translate generic ASCII into magic keystroke string"""

        cooked = ''
        for char in data:
            if char in "abcdefghijklmnopqrstuvwxyz 0123456789`-=[]\\;',./":
                cooked += char
            elif char in string.ascii_uppercase:
                cooked += '!'
                cooked += char     # Send uppercase letter, just because
            else:
                # Translate from:
                #       ~!@#$%^&*()_+{}|:"<>?
                # To:
                #       `1234567890-=[]\;',./
                pos = "~!@#$%^&*()_+{}|:\"<>?".find(char)
                if pos >= 0:
                    cooked += '!'
                    cooked += "`1234567890-=[]\\;',./"[pos]
                else:
                    LOG.error("Unknown character: %s", char)

        return cooked

