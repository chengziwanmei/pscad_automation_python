#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Overlay Graph Command class
#===============================================================================

"""
*************
Overlay Graph
*************

.. autoclass:: OverlayGraph

General
=======

.. automethod:: OverlayGraph.set_zoom

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .canvas import CanvasComponent


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Overlay Graph Command generator
#===============================================================================

class OverlayGraph(CanvasComponent):

    """Overlay Graph Command Object"""

    def __init__(self, canvas, *iid):

        """Construct a command component for a Overlay Graph"""

        super().__init__(canvas, "OverlayGraph", *iid)


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "OverlayGraph[{}]".format(self._id)

    def __repr__(self):
        return "OverlayGraph[{}]".format(self._id)


    #===========================================================================
    # set_zoom
    #===========================================================================

    def set_zoom(self, xmin=None, xmax=None, ymin=None, ymax=None):
        """
        Set the horizontal and vertical limits of the overlay graph.

        Parameters:
            xmin (float): Lower X-Axis limit
            xmax (float): Upper X-Axis limit
            ymin (float): Lower Y-Axis limit
            ymax (float): Upper Y-Axis limit
        """

        cmd = self.command('set-zoom')
        bounds = cmd.tag('bounds')
        if xmin is not None:
            bounds.set('xmin', str(xmin))
        if xmax is not None:
            bounds.set('xmax', str(xmax))
        if ymin is not None:
            bounds.set('ymin', str(ymin))
        if ymax is not None:
            bounds.set('ymax', str(ymax))

        return cmd.execute()
