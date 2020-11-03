#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD User Component Command class
#===============================================================================

"""
**************
User Component
**************

.. autoclass:: UserComponent


Location
--------

.. automethod:: UserComponent.set_location
.. automethod:: UserComponent.get_location
.. automethod:: UserComponent.get_port_location

Properties
----------

.. automethod:: UserComponent.set_parameters
.. automethod:: UserComponent.get_parameters
.. automethod:: UserComponent.view_ParameterGrid

Modules
-------

.. automethod:: UserComponent.get_definition
.. automethod:: UserComponent.is_module
.. automethod:: UserComponent.navigate_in

Layers
------

.. automethod:: UserComponent.add_to_layer
.. automethod:: UserComponent.remove_from_layer

Clipboard
---------

.. automethod:: UserComponent.copy
.. automethod:: UserComponent.cut
.. automethod:: UserComponent.delete
.. automethod:: UserComponent.copy_transfer


"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .component import ComponentCommand
from .definition import Definition


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# User Component Command generator
#===============================================================================

class UserComponent(ComponentCommand):

    """User Component Command Object"""

    def __init__(self, canvas, iid):

        """Construct a command component for a UserCmp, identified by an id"""

        super().__init__(canvas, "UserCmp", iid)

    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "UserCmp[{}]".format(self._id)

    def __repr__(self):
        return "UserCmp[{}]".format(self._id)


    #===========================================================================
    # parameters
    #===========================================================================

    def set_parameters(self, scenario=None, **kwargs):

        """set_parameters([scenario], name=value [, ...])
        Set the component parameters.

        The valid parameters for the component are determined by the component
        definition.

        Parameters:
            scenario (str): Name of scenario to set parameters for. (optional)
            **kwargs: One or more name=value keyword parameters
        """

        return self._parameters(scenario, kwargs)

    def get_parameters(self, scenario=None):

        """
        Get the component parameters.

        The parameters contained in the component are determined by the
        component definition.

        Parameters:
            scenario (str): Name of scenario to get parameters from. (optional)

        Returns:
            A dictionary of property name=value pairs.
        """

        return self._parameters(scenario)


    #===========================================================================
    # View ParameterGrid
    #===========================================================================

    def view_ParameterGrid(self):

        """
        View the parameter grid for this component
        """

        self._generic('IDM_VIEW_PARAMETERSGRID')

    #===========================================================================
    # Get/Set location
    #===========================================================================

    def set_location(self, x, y):

        """
        Set the component's (x,y) location

        Parameters:
            x (int): The new x location for this component
            y (int): The new y location for this component
        """

        return self._set_location(x, y)

    def get_location(self):

        """
        Get this component's (x,y) location

        Returns:
            tuple(int,int): The x,y location of the component.
        """

        return self._get_location()


    #===========================================================================
    # Get Definition
    #===========================================================================

    def get_definition(self):

        """
        Retrieve a controller for this component definition.

        Returns:
            A definition controller proxy object.
        """

        cmd = self.command('get-definition')
        resp = cmd.execute()

        defn = None
        scope = resp.find('scope') if resp is not None else None
        if scope is not None:
            prj_name = scope.find('project').get('name')
            defn_name = scope.find('definition').get('name')
            defn = Definition(self, prj_name, defn_name)

        return defn


    #===========================================================================
    # Is Module
    #===========================================================================

    def is_module(self):
        """
        Check to see if this component has its own canvas, with in turn, can
        contain additional components.

        Returns:
            `True` if the component has an internal canvas, `False` otherwise.
        """

        definition = self.get_definition()
        return definition.is_module() if definition is not None else False


    #===========================================================================
    # Copy Transfer
    #===========================================================================

    def copy_transfer(self):

        """
        Copy the component as well as its definition to the clipboard,
        so it can be used in another project.

        See:
            :meth:`.UserCanvas.paste_transfer()`
        """

        self._generic('IDM_COPYSPECIAL_TRANSFER')


    #===========================================================================
    # Get Port Location
    #===========================================================================

    def get_port_location(self, name):

        """
        Based on the location and any rotation and/or mirroring of this
        component, return the location of the named port.

        Parameters:
            name (str): Name of port

        Returns:
            Location (x,y) of the port,
            or `None` if the port  is not enabled or does not exist.
        """

        cmd = self.command('get-port-location')
        cmd.tag('port').set('name', name)
        resp = cmd.execute()

        loc = resp.find('location')
        if loc is not None:
            x = int(loc.get('x'))
            y = int(loc.get('y'))
            return (x,y)
        else:
            return None
