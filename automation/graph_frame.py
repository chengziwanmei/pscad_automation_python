#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Graph Frame Command class
#===============================================================================

"""
***********
Graph Frame
***********

.. autoclass:: GraphFrame


Properties
----------

The Graph Frame parameters holds two sets of properties.
The first set of properties is the properties for the frame itself.

.. table:: Graph Frame Properties

   ============ ===== ============================================
   Param Name   Type  Description
   ============ ===== ============================================
   title        str   Caption of Graph Frame
   markers      bool  Show Markers
   glyphs       bool  Show Glyphs
   ticks        bool  Show Ticks (obsolete)
   grid         bool  Show Grid
   yinter       bool  Show Y-Intercept
   xinter       bool  Show X-Intercept
   Pan          str   "Auto-Pan X-Axis": a string containing an
                      enable flag (true/false), a comma, and the
                      pan percentage as an integer.
   ============ ===== ============================================

The second set of properties is for the horizontal axis.

.. table:: Horizontal Axis Properties

   ============ ===== ============================================
   Param Name   Type  Description
   ============ ===== ============================================
   XLabel       str   Title
   snapaperture bool  Snap Aperture to the Grid
   dynaperture  bool  Dynamic Time Aperture Adjustment
   minorgrids   bool  Enable Minor Grids
   markers      bool  Show Markers
   lockmarkers  bool  Lock Markers
   deltareadout bool  Show Delta Readout
   xmarker      float X-Marker position
   omarker      float Y-Marker position
   ============ ===== ============================================

.. automethod:: GraphFrame.set_parameters
.. automethod:: GraphFrame.get_parameters


Axis
----

.. automethod:: GraphFrame.reset_x_axis
.. automethod:: GraphFrame.reset_y_axis


Contents
--------

.. automethod:: GraphFrame.overlay_graph

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .canvas import CanvasComponent
from .overlay_graph import OverlayGraph


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Graph Frame Command generator
#===============================================================================

class GraphFrame(CanvasComponent):

    """
    This class is responsible for interacting with a PSCAD Graph Frame.

    The Graph Frame object must be retrieved from a PSCAD Project using
    the :meth:`ProjectCommands.graph_frame` method (or equivalent). ::

        prj = pscad.project('vdiv')
        graph_frame = prj.graph_frame('Main', 653718116)

    """

    def __init__(self, canvas, *iid):

        """Construct a command component for a Graph Frame"""

        super().__init__(canvas, "GraphFrame", *iid)
        self._canvas = canvas

    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "GraphFrame[{}]".format(self._id)

    def __repr__(self):
        return "GraphFrame[{}]".format(self._id)


    #===========================================================================
    # parameters
    #===========================================================================

    def set_parameters(self, scenario=None, **kwargs):

        """
        Set the parameters of a graph frame and/or its horizontal axis.

        Parameters:
            scenario (str): Name of scenario to set parameters for. (optional)
            **kwargs: One or more name=value keyword parameters
        """

        return self._parameters(scenario, kwargs)

    def get_parameters(self, scenario=None):

        """
        Get the parameters of a graph frame and its horiztonal axis.

        Parameters:
            scenario (str): Name of scenario to get parameters from. (optional)

        Returns:
            A dictionary of property name=value pairs.
        """

        return self._parameters(scenario)

    #---------------------------------------------------------------------------
    # Reset graph frame x axis
    #---------------------------------------------------------------------------

    def reset_x_axis(self):
        """
        Reset graph frame X-Axis to the extents of the data
        """

        self._generic('150')

    #---------------------------------------------------------------------------
    # Reset graph frame y axis
    #---------------------------------------------------------------------------

    def reset_y_axis(self):
        """
        Reset the Y-Axis for all graphs individually to the extents of the data
        in each plot.
        """

        self._generic('160')


    #===========================================================================
    # GraphFrame entities
    #===========================================================================

    #---------------------------------------------------------------------------
    # Overlay Graph
    #---------------------------------------------------------------------------

    def overlay_graph(self, iid):
        """
        Retrieve a controller for on overlay graph in a graph frame.

        Parameters:
            iid (int): The id attribute of the overlay graph.

        Returns:
            An overlay graph controller proxy object.
        """

        return OverlayGraph(self._canvas, *(self._id+(iid,)))
