#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Slider Command class
#===============================================================================

"""
*******
Sliders
*******

.. autoclass:: SliderCommands()


General
-------

.. automethod:: SliderCommands.set_value
.. automethod:: SliderCommands.value
.. automethod:: SliderCommands.limits
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
# Slider Command generator
#===============================================================================

class SliderCommands(ComponentCommand):

    """Slider Command Object"""

    def __init__(self, canvas, *iid):

        """Construct a command component for a Slider, identified by an id"""

        super().__init__(canvas, "Slider", *iid)


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Slider[{}]".format(self._id)

    def __repr__(self):
        return "Slider[{}]".format(self._id)


    #===========================================================================
    # set control value
    #===========================================================================

    def set_value(self, **parameters):

        """set_value(name=value [,...])
        Set the Slider control values.

        .. table:: Slider Control Values

            ========= ===== ==================================================
            Parameter Type  Description
            ========= ===== ==================================================
            Name      str   Title of the button
            Group     str   Group name
            Display   int   Display title on button (1=Yes, 0=No)
            Max       float Slider's upper limit
            Min       float Slider's lower limit
            Value     float Slider's initial value
            Units     str   Units to display in control panel
            Collect   int   Data collection (1=continuous, 0=on release)
            ========= ===== ==================================================
        """

        return self._set_control_value(parameters)


    def value(self, value):
        """
        Set slider to the given value

        Parameters:
            value (float): Value to move slider to.
        """

        self.set_value(Value=value)

    def limits(self, lower, upper):
        """
        Set slider minumum and maximum limits

        Parameters:
            lower (float): Lower slider limit
            upper (float): Upper slider limit
        """

        self.set_value(Min=lower, Max=upper)
