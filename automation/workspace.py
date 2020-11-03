#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD workspace command/control/communication class
#===============================================================================

"""
=========
Workspace
=========

.. autoclass:: Workspace


Configuration
-------------

.. automethod:: Workspace.parameters
.. automethod:: Workspace.is_dirty


Projects
--------

In PSCAD, the term "Project" refers to both PSCAD Libraries (`*.pslx`)
as well as PSCAD Cases (`*.pscx`).

.. automethod:: Workspace.projects
.. automethod:: Workspace.project
.. automethod:: Workspace.create_project


Simulation Sets
---------------

.. automethod:: Workspace.list_simulation_sets
.. automethod:: Workspace.create_simulation_set
.. automethod:: Workspace.remove_simulation_set
.. automethod:: Workspace.simulation_set

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging

# ATS imports
from .command import CommandScope
from .project import ProjectCommands
from .simulation import SimulationSet


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD class
#===============================================================================

class Workspace(CommandScope):

    """
    This class is responsible for interacting with the PSCAD "Workspace".

    The Workspace object must be retrieved from an instance of the PSCAD
    controller, using the :meth:`PSCAD.workspace` method. ::

        workspace = pscad.workspace()
    """

    def __init__(self, pscad):

        super().__init__(pscad, "Workspace")

    #===========================================================================
    # Parameters
    #===========================================================================

    def parameters(self, parameters=None, **kwargs):
        """
        Get or set the current workspace's options

        Workspace options are usually set through the "Workspace Options..."
        menu on the Workspace panel, but they can be retrieved or modified
        with this function.

        Parameters:
            parameters (dict): A dictionary of option name=value pairs
            **kwargs: One or more name=value keyword options

        While option values are always returned as strings, they may be given
        as string, integer or boolean values.

        Enable compile auto-save and set auto-save interval to 15 minutes::

            workspace.parameters(compile_save_enable=True, autosave_interval=15)

        To retrive all of the workspace options, pass in no arguments::

            >>> workspace.parameters()
            {'compile_save_enable': 'false', 'autosave_interval': '0', ... }

        Warning:

            It is possible to set options to invalid values.  Operation of
            PSCAD is undefined when illegal values have be used.

            For example, the legal values for ``autosave_interval`` are 0,
            5, 15, and 60.  If it is set to a different value, such as 10,
            PSCAD will show the autosave interval as ``Never``.
        """

        # Combined **kwargs in parameters dictionary
        parameters = dict(parameters, **kwargs) if parameters else kwargs

        return self._parameters('options', parameters)


    #===========================================================================
    # Dirty?
    #===========================================================================

    def is_dirty(self):
        """
        Determine whether the workspace has been modified since the last time
        it was saved.

        Returns:
            `True` if the workspace has unsaved changes, `False` otherwise.
        """

        resp = self.command('is-dirty').execute()
        return resp.find('dirty').get('value') == 'true'



    #===========================================================================
    # Projects
    #===========================================================================

    def projects(self):
        """
        List all currently loaded libraries and cases.

        Returns:
           List[dict]: The ``name``, ``type`` and ``description`` of each
           project in the workspace.

        With only the master library loaded:

        >>> workspace.projects()
        [{'name': 'master', 'type': 'Library', 'description': 'Master Library'}]
        """

        return self._pscad.list_projects()

    def project(self, project_name):
        """
        Retrieve a controller for a named project in the workspace.

        Parameters:
            project_name (str): The name of the library or case. \
                The directory and filename extension must not be included.

        Returns:
            A :class:`project <.ProjectCommands>` controller.

        >>> master = workspace.project('master')
        >>> master.parameters()['description']
        'Master Library'
        """

        return ProjectCommands(self._pscad, project_name)

    def create_project(self, prj_type, name, path ):

        """
        Create a new project in the workspace.

        Parameters:
           prj_type (int): Project type.  Use 1 -> case, 2 -> library
           name (str): Name of the project.
           path (str): Path to directory where project will be stored.

        Returns:
            A project controller for the newly created project.
        """

        if int(prj_type) != 1  and int(prj_type) != 2:
            raise ValueError("Invalid project type")
        if not name:
            raise ValueError("Invalid name argument")
        if not path:
            raise ValueError("Invalid path argument")

        full_path = path+'\\'+name

        cmd = self.command('create-project')
        cmd.tag('type').set('project_type', prj_type)
        cmd.tag('path').set('full_path', full_path)
        cmd.execute()

        return self.project(name)


    #===========================================================================
    # Simulations Sets
    #===========================================================================

    def list_simulation_sets(self):
        """
        List all simulations set names.

        Returns:
            List[str]: A names of all simulation sets in the workspace.
        """

        resp = self.command('list-simulation-sets').execute()
        simulations = []
        for simulation in resp.findall('simulations/simulation'):
            simulations.append(simulation.get('name'))

        return simulations

    def create_simulation_set(self, set_name):
        """
        Create a new simulation set.

        Parameters:
            set_name (str): Name of the new simulation set.
        """

        cmd = self.command('create-simulation-set')
        cmd.tag('simulation').set('name', set_name)
        return cmd.execute()

    def remove_simulation_set(self, set_name):
        """
        Remove an existing simulation set.

        Parameters:
            set_name (str): Name of the simulation set to remove.
        """

        cmd = self.command('remove-simulation-set')
        cmd.tag('simulation').set('name', set_name)
        return cmd.execute()


    #===========================================================================
    # Simulation Set
    #===========================================================================

    def simulation_set(self, set_name):
        """
        Retrieve a controller proxy for the given simulation set.

        Parameters:
            set_name (str): Name of the simulation set.

        Returns:
            A controller proxy for the simulation set.
        """

        return SimulationSet(self._pscad, set_name)



