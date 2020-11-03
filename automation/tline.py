#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD TLine Component Command class
#===============================================================================

"""
*******
T-Lines
*******

.. autoclass:: TLineComponent()


Configuration
-------------

.. automethod:: TLineComponent.canvas
.. automethod:: TLineComponent.set_parameters
.. automethod:: TLineComponent.get_parameters
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
# TLine Component Command generator
#===============================================================================

class TLineComponent(ComponentCommand):

    """TLine Component Command Object"""

    def __init__(self, canvas, iid, defn=None):

        """Construct a command component for a TLine, identified by an id"""

        super().__init__(canvas, "TLine", iid)

        self._defn = defn

    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "TLine[{}]".format(self._id)

    def __repr__(self):
        return "TLine[{}]".format(self._id)


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

        """set_parameters([scenario], name=value [, ...])
        Set the TLine component parameters.

        The valid parameters for the component are determined by the component
        definition.

        Parameters:
            scenario (str): Name of scenario to set parameters for. (optional)
            **kwargs: One or more name=value keyword parameters
        """

        return self._parameters(scenario, parameters)

    def get_parameters(self, scenario=None):

        """Get TLine component parameters

        get_parameters('xxx') - set parameters for scenario 'xxx'.
        """

        return self._parameters(scenario)

