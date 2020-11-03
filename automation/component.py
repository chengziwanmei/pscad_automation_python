#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Component Command class
#===============================================================================

"""
PSCAD Component Command objects.  Creates XML command nodes, for transmission
over a socket to a PSCAD process.
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
import xml.etree.ElementTree as ET

# Automation imports
from .command import CommandScope
from .resource import RES_ID

#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)

#===============================================================================
# ComponentCommand
#===============================================================================

class ComponentCommand(CommandScope):

    """Component Command Object

    Create and submit commands with scope focused on a componnet id chain."""

    def __init__(self, parent, scope_name, *iid):

        """Create a command object for a component specified by an id chain."""

        pscad = parent._pscad               # pylint: disable=protected-access
        project = parent._scope['project']  # pylint: disable=protected-access
        defn = parent.name

        super().__init__(pscad, scope_name, project=project, definition=defn)
        self._id = iid
        self.name = project


    #===========================================================================
    # Command
    #===========================================================================

    def command(self, cmd_name):

        """Construct a command object for the component"""

        cmd = super().command(cmd_name)
        for iid in self._id:
            ET.SubElement(cmd._scope, 'component').set('id', str(iid))  # pylint: disable=protected-access

        return cmd


    #===========================================================================
    # generic
    #===========================================================================

    def _generic(self, cmd_name):

        """Send a 'generic command' to the component"""

        #define IDENTIFIER --> #
        cmd_id = cmd_name
        if cmd_name in RES_ID:
            cmd_id = RES_ID[cmd_name]

        cmd = self.command('generic')
        cmd.param(cmd.root, 'command-id', str(cmd_id))
        cmd.root.set('ident', str(cmd_name))

        return cmd.execute()

    #===========================================================================
    # copy
    #===========================================================================

    def copy(self):
        """
        Copy this component to the clipboard.
        """

        self._generic('IDM_COPY')

    #===========================================================================
    # cut
    #===========================================================================

    def cut(self):
        """
        Cut this component to the clipboard
        """

        self._generic('IDM_CUT')

    #===========================================================================
    # paste
    #===========================================================================

    def paste(self):
        """
        Paste the component on the clipboard to this canvas
        """

        self._generic('IDM_PASTE')

    #===========================================================================
    # delete
    #===========================================================================

    def delete(self):
        """
        Delete this component.
        """

        self._generic('IDM_DELETE')

    #===========================================================================
    # Base methods for Set/Get Location
    #===========================================================================

    def _set_location(self, x, y):

        cmd = self.command('set-location')
        tag = cmd.tag('location')
        tag.set('x', str(x))
        tag.set('y', str(y))

        resp = cmd.execute()

        return resp

    def _get_location(self):

        cmd = self.command('get-location')
        resp = cmd.execute()
        loc = resp.find('location')
        if loc is not None:
            x = int(loc.get('x'))
            y = int(loc.get('y'))
            return (x,y)
        else:
            return None

    #---------------------------------------------------------------------------
    # Allow attribute style access, e.g.)
    #    resistor.location = (10, 30)
    #    loc = resistor.location
    #---------------------------------------------------------------------------

    @property
    def location(self):
        """
        Set or get this component's (x,y) location

        Parameters:
            xy (List[int]): The x & y location of this component (optional)

        Returns:
            List[int]: The x,y location of the component if no new location was
                       given.
        """

        return self._get_location()

    @location.setter
    def location(self, xy):
        assert len(xy) == 2
        return self._set_location(xy[0], xy[1])

    #===========================================================================
    # Navigate into definition
    #===========================================================================

    def navigate_in(self):

        """
        Navigate into a page module or definition
        """

        self._generic('IDM_EDITDEFINITION')

    #===========================================================================
    # Layers
    #===========================================================================

    def add_to_layer(self, name):
        """
        Add this component to the given layer.

        The layer must exist, but need not be enabled or visible.

        Parameters:
            name (str): The layer to add the component to.
        """

        cmd = self.command('add-to-layer')
        cmd.tag('layer').set('name', name)
        resp = cmd.execute()
        return resp

    def remove_from_layer(self, name):
        """
        Remove this component from the given layer.

        The layer must exist, but need not be enabled or visible.

        Parameters:
            name (str): The layer to remove the component from.
        """

        cmd = self.command('remove-from-layer')
        cmd.tag('layer').set('name', name)
        resp = cmd.execute()
        return resp

