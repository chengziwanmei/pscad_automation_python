#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Switch Command class
#===============================================================================

"""
********
Switches
********

.. autoclass:: SwitchCommands()


General
-------

.. automethod:: SwitchCommands.set_value
.. automethod:: SwitchCommands.set_state
.. automethod:: SwitchCommands.on
.. automethod:: SwitchCommands.off
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
# Switch Command generator
#===============================================================================

class SwitchCommands(ComponentCommand):

    """Switch Command Object"""

    def __init__(self, canvas, *iid):

        super().__init__(canvas, "Switch", *iid)


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Switch[{}]".format(self._id)

    def __repr__(self):
        return "Switch[{}]".format(self._id)


    #===========================================================================
    # set control value
    #===========================================================================

    def set_value(self, **parameters):
        """set_value(name=value [,...])
        Set the Switch control values.

        .. table:: Switch Control Values

            ========= ===== ==================================================
            Parameter Type  Description
            ========= ===== ==================================================
            Name      str   Title of the button
            Group     str   Group name
            Display   int   Display title on button (1=Yes, 0=No)
            Value     int   Initial state (1=On, 0=Off)
            Max       float Switch's output value when On
            Min       float Switch's output value when Off
            Ton       str   Text for On position
            Toff      str   Text for Off position
            ========= ===== ==================================================
        """

        return self._set_control_value(parameters)

    def set_state(self, state):
        """
        Set the switch to the given state

        Parameters:
            state (int): New state: 1=On, 0=Off
        """

        self.set_value(Value=state)

    def on(self): # pylint: disable=invalid-name
        """Turn the switch to the On state"""

        self.set_state(1)

    def off(self):
        """Turn the switch to the Off state"""

        self.set_state(0)
