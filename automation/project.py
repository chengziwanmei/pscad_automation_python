#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Project Command class
#===============================================================================

"""
========
Projects
========

In PSCAD, a `Project` may refer to a `Library` (*.pslx) or a `Case` (*.pscx).
A `Library` will contain component definitions and/or code which may be used in
other libraries and cases.
A `Case` is a runnable simulation that may reference other libraries.

The `Master Library` is a library which is automatically loaded into every
:class:`workspace <.Workspace>`.

.. autoclass:: ProjectCommands


Management
----------

.. automethod:: ProjectCommands.focus
.. automethod:: ProjectCommands.parameters
.. automethod:: ProjectCommands.set_parameters
.. automethod:: ProjectCommands.save
.. automethod:: ProjectCommands.save_as
.. automethod:: ProjectCommands.is_dirty


Build & Run
-----------

.. automethod:: ProjectCommands.build
.. automethod:: ProjectCommands.run
.. .. automethod:: ProjectCommands.get_run_status
.. automethod:: ProjectCommands.pause
.. automethod:: ProjectCommands.stop
.. .. automethod:: ProjectCommands.list_messages
.. automethod:: ProjectCommands.messages
.. .. automethod:: ProjectCommands.get_output
.. automethod:: ProjectCommands.get_output_text
.. automethod:: ProjectCommands.clean


Scenarios
---------

.. automethod:: ProjectCommands.list_scenarios
.. automethod:: ProjectCommands.scenario
.. automethod:: ProjectCommands.save_as_scenario


Layers
------

.. automethod:: ProjectCommands.set_layer
.. automethod:: ProjectCommands.create_layer
.. automethod:: ProjectCommands.delete_layer


Definitions
-----------

.. automethod:: ProjectCommands.list_definitions
.. automethod:: ProjectCommands.get_definition
.. .. automethod:: ProjectCommands.create_definition
.. automethod:: ProjectCommands.delete_definition
.. automethod:: ProjectCommands.delete_definition_instances


Parameter Grid
--------------

.. automethod:: ProjectCommands.export_parameter_grid
.. automethod:: ProjectCommands.import_parameter_grid


Finding Canvases
----------------

.. automethod:: ProjectCommands.user_canvas


Finding Components
------------------

.. note::

    After using :meth:`~ProjectCommands.user_canvas` to obtain the relevant
    canvas, it is usually simplier to use :meth:`.UserCanvas.find`,
    :meth:`.UserCanvas.find_first` or :meth:`.UserCanvas.find_all` methods to
    find a component of interest, rather than use a component Id for locate
    the component.

.. automethod:: ProjectCommands.user_cmp
.. automethod:: ProjectCommands.slider
.. automethod:: ProjectCommands.switch
.. automethod:: ProjectCommands.button
.. automethod:: ProjectCommands.selector
.. automethod:: ProjectCommands.overlay_graph
.. automethod:: ProjectCommands.graph_frame

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
from collections import namedtuple

# ATS imports
from .command import CommandScope
from .usercanvas import UserCanvas
from .definition import Definition


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Project Command generator
#===============================================================================

class ProjectCommands(CommandScope):

    """ProjectCommands()
    A Project Controller

    Once loaded into the :class:`.Workspace`, a project must be referenced
    through a project controller object by calling
    :meth:`.PSCAD.project` passing in the appropriate project name::

    >>> master_library = pscad.project('master')  # Get master library project
    """

    def __init__(self, pscad, project_name):

        super().__init__(pscad, "Project", project=project_name)
        self.name = project_name


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "Project[{}]".format(self.name)

    def __repr__(self):
        return "Project[{}]".format(self.name)


    #===========================================================================
    # Save/Save As
    #===========================================================================

    def save(self):
        """
        Save changes made to this project
        """

        return self.command('save').execute()

    def save_as(self, name):
        """
        Save this project to a new name or location.

        Parameters:
            name (str): The filename to store project to.
        """

        cmd = self.command('save-as')
        cmd.tag('file_name').set('name', name)
        resp = cmd.execute()
        return resp


    #===========================================================================
    # Focus
    #===========================================================================

    def focus(self):
        """
        Switch PSCAD's focus to this project.
        """

        return self.command('focus').execute()


    #===========================================================================
    # Build/Clean
    #===========================================================================

    def build(self):
        """
        Build the current project
        """

        self.focus()
        self._pscad.build_current()


    def clean(self):
        """
        Clean the current project
        """

        return self.command('clean-files').execute()


    #===========================================================================
    # Run/Pause/Stop
    #===========================================================================

    def run(self, consumer=None):

        """
        Build and run this project.

        Parameters:
            consumer: handler for events generated by the build/run (optional).

        Note:
            A library cannot be run; only a case can be run.
        """

        cmd = self.command('run')
        return self._pscad.execute_build_run_cmd(cmd, consumer)

    #---------------------------------------------------------------------------

    def get_run_status(self, func, *args, **kwargs):
        """
        .. todo::

            Documentation required
        """

        cmd = self.command('get-run-status')
        self._pscad.post_command(cmd, func, *args, **kwargs)

    def pause(self):
        """
        Pause the currently running projects.

        Note:
            All projects being run will be paused, not just this project.
        """

        return self._pscad.pause_run()

    def stop(self):
        """
        End the currently running projects.

        Note:
            All projects being run will be terminated, not just this project.
        """

        return self._pscad.stop_run()


    #===========================================================================
    # Messages
    #===========================================================================

    def list_messages(self):
        """
        Retrieve the load/build messages

        Returns:
            An ElementTree node containing the messages in an internal format.
        """

        return self.command('list-messages').execute()

    def messages(self):
        """
        Retrieve the load/build messages

        Returns:
            List[tuple]: A list of messages associated with the project.

        Each message is a named tuple composed of:

        ====== ====================================================
        text   The message text
        label  Kind of message, such as build or load
        status Type of messages, such as normal, warning, or error.
        scope  Project to which the message applies
        name   Component which caused the message
        link   Id of the component which caused the message
        group  Group id of the message
        ====== ====================================================

        ::

            pscad.load( os.path.join(examples_dir, r'tutorial\\vdiv.pscx') )
            vdiv = pscad.project('vdiv')
            vdiv.build()
            for msg in vdiv.messages():
                print(msg.text)
        """

        resp = self.list_messages()
        nodes = resp.findall('messagelist/message')
        msgs = [ self._build_msg(node) for node in nodes ]
        return msgs

    _Message = namedtuple('Message', 'text label status scope name link group')

    @classmethod
    def _build_msg(cls, node):
        """
        Turn the following XML ...

            <message groupid="100006" label="build" status="normal">
              <User link="2131920914" name="pagearray" scope="pagearray"
                status="normal" />
              Text here
            </message>

        ... into a Named `Message` Tuple
        """

        text = "".join(node.itertext())
        label = node.get('label')
        status = node.get('status')
        scope = node.get('scope')
        name = None
        link = None
        group = int(node.get('groupid'))

        user = node.find('User')
        if user is not None:
            scope = user.get('scope')
            name = user.get('name')
            link = int(user.get('link'))

        return cls._Message(text, label, status, scope, name, link, group)


    #===========================================================================
    # Definitions
    #===========================================================================

    def list_definitions(self):
        """
        Retrieve a list of all definitions contained in the project.

        Returns:
            List[str]: A list of all of the :class:`.Definition` names.
        """

        definitions = []
        resp = self.command('list-definitions').execute()

        for node in resp.findall('definitions/definition'):
            definitions.append(node.get('name'))

        return definitions

    def get_definition(self, name):
        """
        Retrieve the given named definition from the project.

        Parameters:
            name (str): The name of the definition.

        Returns:
            The named :class:`.Definition`.
        """

        if ':' in name:
            name = name[name.find(':')+1:]

        return Definition(self, self.name, name)


    def create_definition(self, structure):
        """
        .. todo::

            Documentation required
        """

        cmd = self.command('create-definition')
        cmd.tag('definition_xml').set('xmlstruct', structure)
        resp = cmd.execute()

        return resp

    def delete_definition(self, name):
        """
        Delete the given named :class:`.Definition`.

        Parameters:
            name (str): The name of the definition to delete.
        """

        cmd = self.command('delete-definition')
        cmd.tag('definition_name').set('name', name)
        resp = cmd.execute()

        return resp

    def delete_definition_instances(self, name):
        """
        Delete all instances of the given :class:`.Definition`.

        Parameters:
            name (str): The name of the :class:`.Definition` whose instances\
                are to be deleted.
        """

        cmd = self.command('delete-definition-instances')
        cmd.tag('definition_name').set('name', name)
        resp = cmd.execute()

        return resp


    #===========================================================================
    # Output
    #===========================================================================

    def get_output(self):
        """
        Retrieve the output (run messages) for the project

        Returns:
            An ElementTree node containing the messages in an internal format.
        """

        return self.command('get-output').execute()

    def get_output_text(self):
        """
        Retrieve the output (run messages) for the project

        Returns:
            str: The output messages

        ::

            pscad.load( os.path.join(examples_dir, r'tutorial\\vdiv.pscx') )
            vdiv = pscad.project('vdiv')
            vdiv.run()
            print(vdiv.get_output_text())

        """

        output = None
        resp = self.get_output()
        msgs = resp.find('output')
        if msgs is not None:
            output = "".join(msgs.itertext())

        return output


    #===========================================================================
    # Dirty?
    #===========================================================================

    def is_dirty(self):
        """
        Check if the project contains unsaved changes

        Returns:
            `True`, if unsaved changes exist, `False` otherwise.
        """

        resp = self.command('is-dirty').execute()
        return resp.find('dirty').get('value') == 'true'


    #===========================================================================
    # Scenarios
    #===========================================================================

    def list_scenarios(self):
        """
        List the scenarios which exist in the project.

        Returns:
            List[str]: List of scenario names.
        """

        resp = self.command('list-scenarios').execute()
        scenarios = []
        for scenario in resp.findall('scenarios/scenario'):
            scenarios.append(scenario.get('name'))

        return scenarios

    def scenario(self, name=None):
        """
        Get or set the current scenario.

        Parameters:
            name (str): Name of scenario to switch to (optional).

        Returns:
            str: The name of the (now) current scenario.
        """

        if name:
            cmd = self.command('set-scenario')
            cmd.tag('scenario').set('name', name)
            cmd.execute()
        else:
            resp = self.command('current-scenario').execute()
            name = resp.find('scenario').get('name')

        return name

    def delete_scenario(self, name):
        """
        Delete the named scenario.

        Parameters:
            name (str): Name of scenario to delete.
        """

        if name:
            cmd = self.command('delete-scenario')
            cmd.tag('scenario').set('name', name)
            cmd.execute()
        else:
            print("Can not delete default base scenario")

        return name

    def save_as_scenario(self, name):
        """
        Save the current configuration under the given scenario name.

        Parameters:
            name (str): Name of scenario to create or overwrite.
        """

        cmd = self.command('save-as-scenario')
        cmd.tag('scenario').set('name', name)
        resp = cmd.execute()
        return resp


    #===========================================================================
    # Parameters
    #===========================================================================

    def parameters(self, parameters=None, **kwargs):
        """
        Get or set project parameters

        Parameters:
            parameters (dict): A dictionary of name=value parameters
            **kwargs: Zero or more name=value keyword parameters

        Returns:
            A dictionary of current parameters, if no parameters were given.


        .. table:: Project Parameters

            ================= ===== ============================================
            Param Name        Type  Description
            ================= ===== ============================================
            time_duration     float Duration of run
            description       str   Description
            MrunType          int   Run config 0=Standalone, 1=Master, 2=Slave
            startup_filename  str   Start up snapshot file name
            PlotType          int   Save Channels to disk 0=No, 1=Yes
            snapshot_filename str   Save snapshot as text
            SnapTime          float Snapshot time as a real number
            SnapType          int   Timed Snapshot: 0=None, 1=Single,\
                                    2=Incremental (same file),\
                                    3=Incremental (multiple file)
            StartType         int   Start simulation: 0=Standard,\
                                    1=From Snapshot File
            Source            str   Additional Source files
            Mruns             int   Number of multiple runs
            output_filename   str   Name of data file, with .out extension
            sample_step       float Channel plot step
            time_step         float Solution time step
            ================= ===== ============================================
        """

        # Combined **kwargs in parameters dictionary
        parameters = dict(parameters, **kwargs) if parameters else kwargs

        return self._parameters('Settings', parameters)

    def set_parameters(self, parameters=None, **kwargs):
        """
        Set project parameters

        The names of the parameters which are to be changed are tested
        against the set of existing parameters.  If an unknown parameter
        is found, no action is performed and `False` is returned.

        Parameters:
            parameters (dict): A dictionary of name=value parameters
            **kwargs: Zero or more name=value keyword parameters

        Returns:
            `True` if all parameter names are valid, `False` otherwise.
        """

        # Combined **kwargs in parameters dictionary
        parameters = dict(parameters, **kwargs) if parameters else kwargs

        # get a current list from the project
        settings_list = self.parameters()

        # check if user is trying to set an invalid setting
        valid = True

        for name in parameters:
            match = name in settings_list
            if match == False:
                LOG.error("Unknown parameter: set_parameters(%s=...)", name)
                valid = False

        if valid:
            # all parameters are valid, let's set them
            self.parameters(parameters)

        return valid

    #===========================================================================
    # Layers
    #===========================================================================

    # states (invisible, disabled, enabled)
    def set_layer(self, name, state):
        """
        Set the state of a layer

        Parameters:
            name (str): Name of the layer to alter.
            state (str): One of "enabled", "disabled" or "invisible".
        """

        cmd = self.command('set-layer')
        cmd.tag('layer').set('name', name)
        cmd.tag('state').set('value', state)
        resp = cmd.execute()
        return resp

    def create_layer(self, name):
        """
        Create a new layer

        Parameters:
            name (str): Name of the layer to create.
        """

        cmd = self.command('create-layer')
        cmd.tag('layer').set('name', name)
        resp = cmd.execute()
        return resp

    def delete_layer(self, name):
        """
        Delete an existing layer

        Parameters:
            name (str): Name of the layer to delete.
        """

        cmd = self.command('delete-layer')
        cmd.tag('layer').set('name', name)
        resp = cmd.execute()
        return resp

    #===========================================================================
    # Import and Export from Parameter Grid
    #===========================================================================

    def export_parameter_grid(self, name):
        """
        Export parameters to a CSV file.

        Parameters:
            name (str): Filename of the CSV file to write.
        """

        cmd = self.command('export-parameters')
        cmd.tag('csv_file').set('name', name)
        resp = cmd.execute()
        return resp

    def import_parameter_grid(self, name):
        """
        Import parameters from a CSV file.

        Parameters:
            name (str): Filename of the CSV file to read.
        """

        cmd = self.command('import-parameters')
        cmd.tag('csv_file').set('name', name)
        resp = cmd.execute()
        return resp


    #===========================================================================
    # Project command entities
    #===========================================================================

    #---------------------------------------------------------------------------
    # User Canvas
    #---------------------------------------------------------------------------

    def user_canvas(self, name):
        """
        Retrieve a controller for the canvas of a user component.

        Parameters:
            name (str): Definition name of the user component.

        Returns:
            A user canvas controller proxy object.

        Getting the main page of a project::

            main = project.user_canvas('Main')

        """

        return UserCanvas(self, name)


    #===========================================================================
    # Project canvas command entities
    #===========================================================================

    #---------------------------------------------------------------------------
    # UserCmp
    #---------------------------------------------------------------------------

    def user_cmp(self, defn, iid):
        """
        Retrieve a controller for a user component

        Parameters:
            defn (str): Name of user component to find the component inside.
            iid (int): Id attribute of the component.
        """

        return self.user_canvas(defn).user_cmp(iid)

    #---------------------------------------------------------------------------
    # Slider
    #---------------------------------------------------------------------------

    def slider(self, defn, *iid):
        """
        Retrieve a controller for a Slider

        Since this component can exist inside a control panel, the `*iid` list
        must include the entire chain of Id attributes.

        Parameters:
            defn (str): Name of user component to find the component inside.
            *iid (int): Id attributes of the control panel and slider.
        """

        return self.user_canvas(defn).slider(*iid)

    #---------------------------------------------------------------------------
    # Switch
    #---------------------------------------------------------------------------

    def switch(self, defn, *iid):
        """
        Retrieve a controller for a Switch

        Since this component can exist inside a control panel, the `*iid` list
        must include the entire chain of Id attributes.

        Parameters:
            defn (str): Name of user component to find the component inside.
            *iid (int): Id attributes of the control panel and Switch.
        """

        return self.user_canvas(defn).switch(*iid)

    #---------------------------------------------------------------------------
    # Button
    #---------------------------------------------------------------------------

    def button(self, defn, *iid):
        """
        Retrieve a controller for a Button

        Since this component can exist inside a control panel, the `*iid` list
        must include the entire chain of Id attributes.

        Parameters:
            defn (str): Name of user component to find the component inside.
            *iid (int): Id attributes of the control panel and Button.
        """

        return self.user_canvas(defn).button(*iid)

    #---------------------------------------------------------------------------
    # Selector
    #---------------------------------------------------------------------------

    def selector(self, defn, *iid):
        """
        Retrieve a controller for a Selector

        Since this component can exist inside a control panel, the `*iid` list
        must include the entire chain of Id attributes.

        Parameters:
            defn (str): Name of user component to find the component inside.
            *iid (int): Id attributes of the control panel and Selector.
        """

        return self.user_canvas(defn).selector(*iid)


    #---------------------------------------------------------------------------
    # Overlay Graph
    #---------------------------------------------------------------------------

    def overlay_graph(self, defn, *iid):
        """
        Retrieve a controller for an Overlay Graph

        Since this component can exist inside a Graph Frame, the `*iid` list
        must include the entire chain of Id attributes.

        Parameters:
            defn (str): Name of user component to find the component inside.
            *iid (int): Id attributes of the Graph Frame and Overlay Graph.
        """

        return self.user_canvas(defn).overlay_graph(*iid)


    #---------------------------------------------------------------------------
    # Graph Frame
    #---------------------------------------------------------------------------

    def graph_frame(self, defn, iid):
        """
        Retrieve a controller for a Graph Frame

        Parameters:
            defn (str): Name of user component to find the component inside.
            iid (int): Id attribute of the Graph Frame.
        """

        return self.user_canvas(defn).graph_frame(iid)

