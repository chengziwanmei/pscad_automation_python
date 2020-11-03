#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Simulation Set command/control/communication class
#===============================================================================

"""
**************
Simulation Set
**************

.. autoclass:: SimulationSet


Management
----------

.. automethod:: SimulationSet.name
.. automethod:: SimulationSet.depends_on


Tasks
-----

.. automethod:: SimulationSet.list_tasks
.. automethod:: SimulationSet.add_tasks
.. automethod:: SimulationSet.remove_tasks
.. automethod:: SimulationSet.task


Build & Run
-----------

.. automethod:: SimulationSet.run

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging

# ATS imports
from .command import CommandScope
from .task import Task


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Simulation Set class
#===============================================================================

class SimulationSet(CommandScope):

    """Simulation Set command object"""

    def __init__(self, pscad, simset_name):

        super().__init__(pscad, "Simulation", simulation=simset_name)


    #===========================================================================
    # Name
    #===========================================================================

    def name(self, name=None):
        """
        Get or set the name of the simulation set

        Parameters:
            name (str): New name of simulation set (optional)

        Returns:
            The name of the simulation set.
        """

        if name is not None:
            self._set_value('name', name)
        else:
            name = self._get_value('name')

        return name


    #===========================================================================
    # Depends on
    #===========================================================================

    def depends_on(self, name=None):
        """
        Get or set the simulation set dependency

        Parameters:
            name (str): Name of simulation set dependency (optional)

        Returns:
            The name of the simulation set dependency.
        """

        if name is not None:
            if name == '':
                name = 'None'
            self._set_value('dependson', name)
        else:
            name = self._get_value('dependson')

        return name


    #===========================================================================
    # Tasks
    #===========================================================================

    def list_tasks(self):
        """
        List projects included in the simulation set.

        Returns:
            A list of the tasks (projects) included in the simulation set.
        """

        resp = self.command('list-tasks').execute()
        tasks = [task.get('name') for task in resp.findall('tasks/task')]
        return tasks

    def add_tasks(self, *task_names):
        """
        Add one or more tasks (projects) to the simulation set.

        Parameters:
            *name (str): Names of tasks (projects) to add to the simulation set
        """

        cmd = self.command('add-tasks')
        for task_name in task_names:
            cmd.tag('task').set('name', task_name)

        return cmd.execute()

    def remove_tasks(self, *task_names):
        """
        Remove one or more tasks (projects) from the simulation set.

        Parameters:
            *name (str): Names of tasks (projects) to remove.
        """

        cmd = self.command('remove-tasks')
        for task_name in task_names:
            cmd.tag('task').set('name', task_name)

        return cmd.execute()


    def task(self, task_name):
        """
        Retrieve a controller proxy for an individual simulation set task.

        Parameters:
            task_name (str): Name of task
        """

        return Task(self._pscad, self._scope['simulation'], task_name)


    #===========================================================================
    # Simulations Sets
    #===========================================================================

    def run(self, consumer=None):
        """
        Run the simulation set.

        Parameters:
           consumer: handler for events generated by the build/run (optional).
         """

        cmd = self.command('run')
        return self._pscad.execute_build_run_cmd(cmd, consumer)