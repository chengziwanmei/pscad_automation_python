#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Definition Command class
#===============================================================================

"""
====================
Component Definition
====================

.. autoclass:: Definition()
    :members:
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .command import CommandScope


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Definition Command generator
#===============================================================================

class Definition(CommandScope):

    """
    A Component Definition

    All :class:`User Components <.UserComponent>` have a component definition,
    which specifies what parameters the component has, and whether or not
    the component is a module, with its own canvas containing other components.
    """

    def __init__(self, parent, project_name, defn_name):

        """Construct a command component for a Definition, identified by name"""

        pscad = parent._pscad               # pylint: disable=protected-access

        super().__init__(pscad, "Definition", project=project_name,
                         definition=defn_name)

    #===========================================================================
    # Properties
    #===========================================================================

    @property
    def scope(self):
        """
        Project the definition is defined in
        """

        return self._scope['project']

    @property
    def name(self):
        """
        Name of the definition
        """

        return self._scope['definition']

    @property
    def scoped_name(self):
        """
        The scoped definition name is the project and definition names,
        separated by a colon.
        """

        return "{}:{}".format(self.scope, self.name)


    #===========================================================================
    # Is Module
    #===========================================================================

    def is_module(self):
        """
        Check to see if this definition is a module.

        A `module` will have a canvas, which can contain other components.
        """

        flag = False

        resp = self.command('is-module').execute()
        if resp is not None:
            module = resp.find('module')
            if module is not None:
                flag = module.get('value') == 'true'

        return flag


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return self.scoped_name

    def __repr__(self):
        return "Definition[{}:{}]".format(self.scope, self.name)

