#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Button Command class
#===============================================================================

"""
*******
Buttons
*******

.. autoclass:: ButtonCommands()


General
-------

.. automethod:: ButtonCommands.set_value
.. automethod:: ButtonCommands.press
.. automethod:: ButtonCommands.release
.. automethod:: ButtonCommands.click
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging

# ATS imports
from .component import ComponentCommand

#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Button Command generator
#===============================================================================

class ButtonCommands(ComponentCommand):

    """Button Command Object"""

    def __init__(self, canvas, *iid):

        super().__init__(canvas, "Button", *iid)


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Button[{}]".format(self._id)

    def __repr__(self):
        return "Button[{}]".format(self._id)


    #===========================================================================
    # set control value
    #===========================================================================

    def set_value(self, **parameters):
        """set_value(name=value [,...])
        Set the Button control values.

        .. table:: Button Control Values

            ========= ===== ==================================================
            Parameter Type  Description
            ========= ===== ==================================================
            Name      str   Title of the button
            Group     str   Group name
            Display   int   Display title on button (1=Yes, 0=No)
            Min       float Button's output value when not pressed
            Max       float Button's output value when pressed
            ========= ===== ==================================================
        """

        return self._set_control_value(parameters)

    def press(self):
        """Press the button"""
        self.set_value(Value=1)

    def release(self):
        """Release the button"""
        self.set_value(Value=0)

    def click(self):
        """Press and release the button"""

        self.press()
        self.release()

