#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Selector Command class
#===============================================================================

"""
*****
Dials
*****

.. autoclass:: SelectorCommands()


General
-------

.. automethod:: SelectorCommands.set_value
.. automethod:: SelectorCommands.position
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
# Selector Command generator
#===============================================================================

class SelectorCommands(ComponentCommand):

    """Selector Command Object"""

    def __init__(self, canvas, *iid):

        super().__init__(canvas, "Selector", *iid)


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Selector[{}]".format(self._id)

    def __repr__(self):
        return "Selector[{}]".format(self._id)


    #===========================================================================
    # set control value
    #===========================================================================

    def set_value(self, **parameters):
        """set_value(name=value [,...])
        Set the Selector control values.

        .. table:: Selector Control Values

            ========= ===== ==================================================
            Parameter Type  Description
            ========= ===== ==================================================
            Name      str   Title of the button
            Group     str   Group name
            Display   int   Display title on button (1=Yes, 0=No)
            LabelType int   Value Display (0=Index, 1=Value, 2=Both)
            NDP       int   Number of dial positions (3-10)
            Value     int   Initial dial position (1-NDP)
            conv      int   Convert output to integer (1=Yes, 0=No)
            F1        str   Output value for Dial position #1
            F2        str   Output value for Dial position #2
            F3        str   Output value for Dial position #3
            F4        str   Output value for Dial position #4
            F5        str   Output value for Dial position #5
            F6        str   Output value for Dial position #6
            F7        str   Output value for Dial position #7
            F8        str   Output value for Dial position #8
            F9        str   Output value for Dial position #9
            F10       str   Output value for Dial position #10
            ========= ===== ==================================================
        """

        return self._set_control_value(parameters)


    def position(self, position):
        """
        Set the selector to the given position

        Parameters:
            position (int): New position for the dial (1-NDP)
        """

        self.set_value(Value=position)
