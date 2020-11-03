#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Bus Component Command class
#===============================================================================

"""
*****
Buses
*****

.. autoclass:: BusComponent()


Configuration
-------------

.. automethod:: BusComponent.vertices
.. automethod:: BusComponent.set_parameters
.. automethod:: BusComponent.get_parameters
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .wire import Wire


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Bus Component Command generator
#===============================================================================

class BusComponent(Wire):

    """
    Bus Component Command Object

    To construct a new wire, use `UserCanvas.add_bus()`.
    """

    def __init__(self, canvas, iid):

        """Construct a command component for a Bus, identified by an id"""

        super().__init__(canvas, "Bus", iid)

    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Bus[{}]".format(self._id)

    def __repr__(self):
        return "Bus[{}]".format(self._id)


    #===========================================================================
    # parameters
    #===========================================================================

    def set_parameters(self, scenario=None, **parameters):

        """set_parameters([scenario,] name=value [,...])
        Set the Bus component parameters.

        .. table:: Bus Parameters

            ========= ===== ==================================================
            Parameter Type  Description
            ========= ===== ==================================================
            Name      str   Name of the Bus
            BaseKV    str   Bus Base Voltage, in kV.  May be zero.
            ========= ===== ==================================================

        Parameters:
            scenario (str): Name of scenario to set parameters for. (optional)
            **kwargs: One or more name=value keyword parameters
        """

        return self._parameters(scenario, parameters)

    def get_parameters(self, scenario=None):

        """
        Get the Bus component parameters.

        Parameters:
            scenario (str): Name of scenario to get parameters from. (optional)

        Returns:
            A dictionary of property name=value pairs.
        """

        return self._parameters(scenario)

