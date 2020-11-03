#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Cable Component Command class
#===============================================================================

"""
******
Cables
******

.. autoclass:: CableComponent()


Configuration
-------------

.. automethod:: CableComponent.canvas
.. automethod:: CableComponent.set_parameters
.. automethod:: CableComponent.get_parameters
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .component import ComponentCommand


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Cable Component Command generator
#===============================================================================

class CableComponent(ComponentCommand):

    """Cable Component Command Object"""

    def __init__(self, canvas, iid, defn=None):

        """Construct a command component for a Cable, identified by an id"""

        super().__init__(canvas, "Cable", iid)

        self._defn = defn

    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Cable[{}]".format(self._id)

    def __repr__(self):
        return "Cable[{}]".format(self._id)


    #===========================================================================
    # canvas
    #===========================================================================

    def canvas(self):
        if self._defn and ':' in self._defn:
            prj_name, canvas_name = self._defn.split(':')
            prj = self._pscad.project(prj_name)
            canvas = prj.user_canvas(canvas_name)
            return canvas

        raise ValueError("Don't know canvas definition name")

    #===========================================================================
    # parameters
    #===========================================================================

    def set_parameters(self, scenario=None, **parameters):

        """Set Cable component parameters

        set_parameters(param1=value1, param2=value2, ...) - sets param1, param2
        set_parameters('xxx', ...) - set parameters for scenario 'xxx'.
        """

        return self._parameters(scenario, parameters)

    def get_parameters(self, scenario=None):

        """Get Cable component parameters

        get_parameters('xxx') - set parameters for scenario 'xxx'.
        """

        return self._parameters(scenario)

