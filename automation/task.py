#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Task command/control/communication class
#===============================================================================

"""
*******************
Simulation Set Task
*******************

.. autoclass:: Task


Settings
----------

.. automethod:: Task.namespace
.. automethod:: Task.controlgroup
.. automethod:: Task.volley
.. automethod:: Task.affinity

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging

# ATS imports
from .command import CommandScope


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Simulation Set class
#===============================================================================

class Task(CommandScope):

    """Task command object"""

    def __init__(self, pscad, simset_name, task_name):

        super().__init__(pscad, "Task", simulation=simset_name, task=task_name)


    #===========================================================================
    # Namespace
    #===========================================================================

    def namespace(self):
        """
        Get the namespace

        Returns:
            str: The namespace.
        """
        return self._get_value('namespace')


    #===========================================================================
    # Controlgroup
    #===========================================================================

    def controlgroup(self, controlgroup=None):
        """
        Get or set the control group

        Parameters:
            controlgroup (str): The control group

        Returns:
            The control group.
        """

        if controlgroup is not None:
            self._set_value('controlgroup', controlgroup)
        else:
            controlgroup = self._get_value('controlgroup')
        return controlgroup


    #===========================================================================
    # Volley
    #===========================================================================

    def volley(self, volley=None):
        """
        Get or set the volley count

        Parameters:
            volley (int): The volley count

        Returns:
            The volley count.
        """

        if volley is not None:
            self._set_value('volley', volley)
        else:
            volley = self._get_value('volley')
            volley = int(volley) if volley else 1
        return volley


    #===========================================================================
    # Affinity
    #===========================================================================

    def affinity(self, affinity=None):
        """
        Get or set the trace affinity

        Parameters:
            affinity (int): The trace affinity

        Returns:
            The trace affinity.
        """

        if affinity is not None:
            self._set_value('affinity', affinity)
        else:
            affinity = self._get_value('affinity')
            affinity = int(affinity) if affinity else 1
        return affinity



