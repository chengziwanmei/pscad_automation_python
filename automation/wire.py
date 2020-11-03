#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Wire Component Command class
#===============================================================================

"""
*****
Wires
*****

.. autoclass:: Wire()


Identification
--------------

.. automethod:: Wire.vertices


****************
Orthogonal Wires
****************

.. autoclass:: WireOrthogonal()


Identification
--------------

.. automethod:: WireOrthogonal.vertices

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
# Wire Component Command generator
#===============================================================================

class Wire(ComponentCommand):

    """
    Wire Component Command Object

    Base class for WireOrthogonal, WireBranch, Bus, TLine and Cable components.

    To construct a new wire, use `UserCanvas.add_wire()`.
    """

    def __init__(self, canvas, scope_name, iid):

        """Construct a command component for a Wire, identified by an id"""

        super().__init__(canvas, scope_name, iid)

    #===========================================================================
    # Vertices
    #===========================================================================

    @property
    def vertices(self):
        """vertices( [vertices] )
        Set or get the vertices of the wire

        Parameters:
            vertices: a list of `(x,y)` coordinates (optional)

        Returns:
            A list of `(x,y)` coordinates.
        """

        cmd = self.command("list-vertices")
        resp = cmd.execute()

        vertices = []
        for point in resp.findall("points/point"):
            x = int(point.get('x'))
            y = int(point.get('y'))
            vertices.append((x,y))

        return vertices

    @vertices.setter
    def vertices(self, vertices):
        self._set_vertices(vertices)

    def _set_vertices(self, vertices):

        if len(vertices) < 2:
            raise ValueError("Wires need at least 2 vertices")

        cmd = self.command("set-vertices")

        for vertex in vertices:
            point = cmd.tag('point')
            point.set('x', str(vertex[0]))
            point.set('y', str(vertex[1]))

        resp = cmd.execute()
        return resp


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "{}[{}]".format(self._scope_name, self._id[0])

    def __repr__(self):
        return "{}[{}]".format(self._scope_name, self._id[0])


#===============================================================================
# WireOrthogonal Component Command generator
#===============================================================================

class WireOrthogonal(Wire):

    """
    Orthogonal Wire Component Command Object

    Each segment of the wire will be either horizontal or vertical.
    Diagonal segments are not allowed.
    """

    def __init__(self, canvas, iid):

        """Construct a cmd component for a WireOrthogonal, identified by id"""

        super().__init__(canvas, "WireOrthogonal", iid)


    def _set_vertices(self, vertices):

        new_vertices = []

        prev = None
        for curr in vertices:
            if prev is not None and prev[0] != curr[0] and prev[1] != curr[1]:
                new_vertices.append((curr[0], prev[1]))
            new_vertices.append(curr)
            prev = curr

        super()._set_vertices(new_vertices)

    def get_parameters(self, scenario=None):

        """Get Wire parameters

        Always returns an empty map.
        """

        return {}
