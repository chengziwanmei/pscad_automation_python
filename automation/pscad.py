#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD command/control/communication class
#===============================================================================

"""
*********************
The PSCAD Application
*********************

.. autoclass:: PSCAD()


Configuration
-------------

.. automethod:: PSCAD.settings


Application Flags
-----------------
The following flags are supported:

.. table::
    :widths: 15 80

    =============== ===========================================================
    Flag Name       Description
    =============== ===========================================================
    silence         Suppress popup dialogs which may interfere with automation.
    load-meta-files Controls loading of additional project state information,\
                    such as build messages from a previous session.
    =============== ===========================================================

.. automethod:: PSCAD.set_flags
.. automethod:: PSCAD.get_flags


Licensing
---------

.. automethod:: PSCAD.logged_in
.. automethod:: PSCAD.licensed
.. automethod:: PSCAD.get_available_certificates
.. automethod:: PSCAD.get_current_certificate
.. automethod:: PSCAD.get_certificate
.. automethod:: PSCAD.release_certificate


Workspace Commands
------------------

.. automethod:: PSCAD.new_workspace
.. automethod:: PSCAD.workspace
.. automethod:: PSCAD.load
.. automethod:: PSCAD.list_projects
.. automethod:: PSCAD.project


Build & Run Commands
--------------------

.. automethod:: PSCAD.build_all
.. automethod:: PSCAD.build_current
.. automethod:: PSCAD.simulation_set
.. automethod:: PSCAD.run_all_simulation_sets
.. automethod:: PSCAD.pause_run
.. automethod:: PSCAD.stop_run
.. automethod:: PSCAD.clean_all


Navigation
----------

.. automethod:: PSCAD.navigate_up


Subscriptions
-------------

These methods are used to get asynchronous events from the PSCAD application.

.. automethod:: PSCAD.subscribe
.. automethod:: PSCAD.unsubscribe
.. automethod:: PSCAD.subscribed


Termination
-----------

.. automethod:: PSCAD.quit

"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging, socket, subprocess
import ctypes, win32con, win32gui, win32process

import xml.etree.ElementTree as ET

# Automation imports
from .command import CmdProcessor, Command
from .certificate import Certificate
from .handler import BuildEvent
from .keystroke import KeyStrokes
from .mouse import MouseEvents
from .project import ProjectCommands
from .resource import RES_ID
from .simulation import SimulationSet
from .workspace import Workspace
from .xml_sock import XmlSocket

# Patch to ET to include CDATA
from . import cdata


#===============================================================================
# Constants
#===============================================================================

# XML Transmit Tags

# Wrapper for entire ATS->PSCAD conversation
CONTENT = b"<content>"
CONTENT_END = b"</content>"

# Default command scope
COMMAND_SCOPE_PSCAD = "PSCAD"


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD class
#===============================================================================

class PSCAD(CmdProcessor):

    """
    This class is responsible for command and control of the PSCAD application.

    An instance of this class would be created by the
    :meth:`launch_pscad() <mhrc.automation.launch_pscad>` command::

        pscad = mhrc.automation.launch_pscad()
    """

    def __init__(self, rxtx_logger, options):

        super().__init__()

        self._proc = None   # PSCAD process handle
        self._subscription = {}
        self._cache = {}

        # Manager cache
        self._workspace = None

        try:
            # Launch PSCAD
            self._launch_pscad(options, rxtx_logger)

            # Send open tag, for PSCAD's xml parser
            self._sock.send_raw(CONTENT)

        except Exception as exception:
            LOG.exception("Failed to launch due to %s", exception)
            self._kill()
            raise


    #===========================================================================
    # Create Server Socket, Launch PSCAD, and wait for connection
    #===========================================================================

    def _launch_pscad(self, options, rxtx_logger):
        serversock, port = self._open_listener()
        self._launch(port, options)
        self._wait_for_connection(serversock, rxtx_logger)


    #---------------------------------------------------------------------------

    @staticmethod
    def _open_listener(host='', port=0):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.bind((host, port))
        ipaddr, port = serversock.getsockname()

        LOG.info("Server socket bound to %s port %d", ipaddr, port)

        return serversock, port


    #---------------------------------------------------------------------------

    def _launch(self, port, options):
        """
        Launch PSCAD with automation command-line options, and instruct it
        to connect back to the automated test suite on the given port.
        """

        path = options['path']

        args = [path, '/startup:au', '/host:localhost', '/port:'+str(port),
                '/nologo']
        if '/silence' in options:
            args.append('/silence:{}'.format(options['/silence']))

        LOG.debug("Execute: %r", args)

        # Suppress the "<Application> has stopped responding" Dialog.
        # Child processes (PSCAD) and grand-child processes (EMTDC) will
        # inherit this Error Mode, exiting immediately if they crash.
        ctypes.windll.kernel32.SetErrorMode(win32con.SEM_NOGPFAULTERRORBOX)

        # Start the PSCAD child process.
        sui = subprocess.STARTUPINFO()
        if 'launch-minimized' in options:
            if options['launch-minimized']:
                sui.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                sui.wShowWindow = win32con.SW_SHOWMINNOACTIVE
            else:
                sui.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                sui.wShowWindow = win32con.SW_SHOWNOACTIVATE

        self._proc = subprocess.Popen(args, close_fds=True, startupinfo=sui)
        LOG.info("Process ID = %d", self._proc.pid)


    #---------------------------------------------------------------------------

    def _wait_for_connection(self, serversock, rxtx_logger, timeout=30.0):
        try:
            serversock.settimeout(timeout)
            serversock.listen(1)
            LOG.info("Waiting for connection on %s",
                     repr(serversock.getsockname()))

            sock, addr = serversock.accept()
            LOG.info("Connected to %r", addr)
            serversock.close()
            serversock = None

            self._sock = XmlSocket(sock)
            self._sock.logger(rxtx_logger)

        except socket.timeout:
            LOG.error("Connection timeout (listen)")
            raise RuntimeError("Failed to get connection from PSCAD")


    #---------------------------------------------------------------------------

    def _kill(self):
        if self._proc is not None:
            self._proc.terminate()
            self._proc.communicate()
        self._proc = None


    #---------------------------------------------------------------------------

    def is_alive(self):
        return self._proc  and  self._sock.is_open()


    #---------------------------------------------------------------------------

    def hwnd(self):

        process_id = self._proc.pid

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd)  and \
               win32gui.IsWindowEnabled(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == process_id:
                    hwnds.append(hwnd)

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)

        hwindow = None
        LOG.debug("Proc %d, hwnds = %r", process_id, hwnds)
        for hwnd in hwnds:
            title = win32gui.GetWindowText(hwnd)
            LOG.debug("hwnd %d: %r", hwnd, title)
            if title:
                hwindow = hwnd
        return hwindow


    #===========================================================================
    # Read Responses from PSCAD
    #===========================================================================

    def _read_next(self):
        """Read the next <xml/> packet on the communication socket.
        Raises a 'StopInteration' exception if the socket is closed.
        """

        return self._recv()

    #---------------------------------------------------------------------------

    def _read_available(self):
        responses = []

        while self._sock.rx_open():
            resp = self._read_next()
            if resp == None:
                break
            responses.append(resp)

        return responses


    #===========================================================================
    # Close connection
    #===========================================================================

    def close_connection(self):
        try:
            # Send closing tag '</content>'
            self._sock.send_raw(CONTENT_END)
        except ConnectionAbortedError as ex:
            LOG.warning("Exception sending </content>: %s", ex)

        self._sock.tx_close()
        self._read_available()
        self.close_and_cleanup()


    #===========================================================================
    # Command Generator
    #===========================================================================

    def command(self, cmd_name, scope=COMMAND_SCOPE_PSCAD):
        return Command(self, cmd_name, scope)


    #===========================================================================
    # Subscriptions
    #===========================================================================

    #---------------------------------------------------------------------------
    # Subscribe
    #---------------------------------------------------------------------------

    def subscribe(self, name, handler=None):
        """
        Start receiving `name` events.

        Parameters:
            name (str): Name of event being subscribed to, such as
                        `"load-events"` or `"build-events"`
            handler: Function to call when event is received.
        """

        if handler is not None:
            self.add_handler(handler)

        cmd = self.command(name, scope='Subscription')
        cmd.execute()

        self._subscription[name] = (cmd.get_id(), handler)


    #---------------------------------------------------------------------------
    # Unsubscribe
    #---------------------------------------------------------------------------

    def unsubscribe(self, name):
        """
        Stop receiving and processing `name` events.

        Parameters:
            name (str): Name of event being unsubscribed from.
        """

        if self.subscribed(name):
            seq_id, handler = self._subscription[name]
            del self._subscription[name]

            cmd = self.command('unsubscribe', scope='Subscription')
            cmd.root.set('sequence-id', seq_id)
            cmd.execute()

            if handler is not None:
                self.remove_handler(handler)


    #---------------------------------------------------------------------------
    # Are we subscribed?
    #---------------------------------------------------------------------------

    def subscribed(self, name):

        """
        Determine if the given event is being subscribed to.

        Returns:
            `True` if the given events is subscribed to, `False` otherwise.
        """

        return name in self._subscription


    #===========================================================================
    # Settings
    #===========================================================================

    def settings(self, settings=None, **kwargs):

        """
        Set or retrieve PSCAD's settings.

        Parameters:
            settings (dict): A dictionary of setting key-values pairs
            **kwargs: individual setting key-value pairs

        If called without providing any key-value pairs, the current settings
        are returned.  Otherwise, the given key-value pairs are set in the
        application's settings.

        Any unknown keys are silently ignored.  The effect of setting an known
        key to an invalid value is undefined.
        """

        # Combined **kwargs into settings dictionary
        settings = dict(settings, **kwargs) if settings else kwargs

        if settings:
            cmd = self.command('set-settings')
            for key, value in settings.items():
                cmd.param(cmd.root, key, str(value))
            cmd.execute()
        else:
            resp = self.command('list-settings').execute()
            settings = {}
            for param in resp.findall('paramlist/param'):
                settings[param.get('name')] = param.get('value')

        return settings


    #===========================================================================
    # Licensing
    #===========================================================================

    @staticmethod
    def _get_param(root, xpath, param):
        value = None
        if root is not None:
            node = root.find(xpath)
            if node is not None:
                value = node.get(param)
        return value

    def _get_bool(self, root, xpath, param='value'):
        value = self._get_param(root, xpath, param)
        return value.lower() == 'true' if value is not None else None

    def logged_in(self):
        """
        Returns whether or not the user is "Logged in"

        Returns:
            `True` if the user is logged in, `False` otherwise.

        Example:
            >>> pscad.logged_in()
            True
        """

        resp = self.command('is-logged-in').execute()
        return self._get_bool(resp, 'loggedin')

    def licensed(self):
        """
        Determine whether a valid license is being held.

        Returns:
            `True` if the a license is held, `False` otherwise.

        Example:
            >>> pscad.licensed()
            True
        """

        resp = self.command('is-licensed').execute()
        return self._get_bool(resp, 'licensed')

    def get_available_certificates(self):
        """
        Retrieve a list of license certificates available to the user.

        Returns:
            A dictionary of :class:`certificates <.Certificate>`,
            keyed by :meth:`.Certificate.id`.
        """

        if 'certificates' in self._cache:
            certificates = self._cache['certificates']
        else:
            resp = self.command('get-available-certificates').execute()
            certificates = Certificate.parse(resp)
            self._cache['certificates'] = certificates
        return certificates

    def get_current_certificate(self):
        """
        Retrieve the Certificate currently being held.

        Returns:
            The :class:`.Certificate` being held, or `None`
        """

        resp = self.command('get-current-certificate').execute()
        certificate = None
        current = resp.find('License')
        if current is not None:
            group_id_param = current.find("param[@name='groupID']")
            if group_id_param is not None:
                group_id = group_id_param.get('value')
                certificates = self.get_available_certificates()
                if group_id in certificates:
                    certificate = certificates[group_id]
        return certificate

    def get_certificate(self, certificate):
        """
        Attempt to acquire the given license certificate.

        Parameters:
            certificate: the :class:`.Certificate` to be acquired.
        """

        cmd = self.command('get-certificate')
        ET.SubElement(cmd.root, 'group').set('value', str(certificate.id()))
        return cmd.execute()

    def release_certificate(self):
        """
        Releases the the currently held certificate.
        """

        return self.command('release-certificate').execute()


    #===========================================================================
    # Load commands
    #===========================================================================

    #---------------------------------------------------------------------------
    # Load Project(s)/Workspace
    #---------------------------------------------------------------------------

    def load(self, *filenames, handler=None):
        """
        Load a workspace, or one or more projects into the current workspace.

        Parameters:
            *filenames (str): a list of filenames to load.
            handler: If provided, the given handler is automatically added for\
                the duration of the load operation.  Defaults to `None`.

        If a workspace file (`*.pswx`) is given, it must be the only file.
        Otherwise, more than one library (`*.pslx`) and/or case (`*.pscx`) may
        be given.

        >>> pscad.load( os.path.join(examples_dir, r'tutorial\\vdiv.pscx') )
        >>> vdiv = pscad.project('vdiv')
        >>> vdiv.parameters()['description']
        'Single Phase Voltage Divider'
        """

        if len(filenames) == 1  and  isinstance(filenames[0], list):
            filenames = filenames[0]

        LOG.info("Loading %s", filenames)

        auto_subscribe = not self.subscribed('load-events')
        if auto_subscribe:
            self.subscribe('load-events')

        if handler is not None:
            self.add_handler(handler)

        cmd = self.command('load')
        for filename in filenames:
            file = ET.SubElement(cmd.root, 'file')
            file.text = filename
        cmd.execute(wait_for_response=False)

        self.wait_for("./event[@type='LoadEvent']/"
                      "type[@file-type='files'][@status='END']")

        if handler is not None:
            self.remove_handler(handler)

        if auto_subscribe:
            self.unsubscribe('load-events')

    def new_workspace(self):

        """
        Unload the current workspace, and create a new one.

        Warning:
            If popup dialogs are being silenced,
            **all unsaved changes will be unconditionally lost**.
        """

        LOG.info("New Workspace")
        cmd = self._command_id_cmd('ID_RIBBON_MAIN_NEW_WORKSPACE')
        return cmd.execute()


    #===========================================================================
    # List Projects
    #===========================================================================

    def list_projects(self):
        """
        List all :class:`projects <.ProjectCommands>` (libraries & cases) loaded
        in the current workspace.

        Returns:
            List[dict]: The `name`, `type` and `description` of each project.

        >>> pscad.load( os.path.join(examples_dir, r'tutorial\\Tutorial.pswx') )
        >>> for prj in pscad.list_projects():
        ...    print(prj)
        {'name': 'master', 'type': 'Library', 'description': 'Master Library'}
        {'name': 'chatter', 'type': 'Case', 'description': 'Simple case with chatter elimination'}
        {'name': 'fft', 'type': 'Case', 'description': 'Harmonic Impedance and FFT'}
        {'name': 'inputctrl', 'type': 'Case', 'description': 'Input Control Components'}
        {'name': 'interpolation', 'type': 'Case', 'description': 'Simple case illustrating interpolation'}
        {'name': 'legend', 'type': 'Case', 'description': 'Use of macros'}
        {'name': 'vdiv', 'type': 'Case', 'description': 'Single Phase Voltage Divider'}
        {'name': 'simpleac', 'type': 'Case', 'description': 'A Simple AC Power System'}
        {'name': 'multirun', 'type': 'Case', 'description': 'A Simple Multiple Run Example'}
        {'name': 'pagearray', 'type': 'Case', 'description': 'Page Inside a Page, Arrays'}
        """

        cases = []
        resp = self.command('list-cases').execute()
        for node in resp.findall('project'):
            case = {'name': node.get('name'), 'type': node.get('type'),
                    'description': node.get('Description')}
            cases.append(case)

        return cases

    list_cases = list_projects

    #===========================================================================
    # Build/Run Pause/Stop commands
    #===========================================================================

    #---------------------------------------------------------------------------
    # Execute Build/Run command, wait for all Build Events
    #---------------------------------------------------------------------------

    def execute_build_run_cmd(self, cmd, handler=None):

        if handler is None:
            handler = BuildEvent()

        auto_subscribe = not self.subscribed('build-events')
        if auto_subscribe:
            self.subscribe('build-events')

        cmd.submit(handler)

        if auto_subscribe:
            self.unsubscribe('build-events')

        return None


    #---------------------------------------------------------------------------
    # Build All
    #---------------------------------------------------------------------------

    def build_all(self, handler=None):
        """
        Build all projects
        """

        LOG.info("Build all")
        cmd = self._command_id_cmd("ID_RIBBON_HOME_COMPILE_BUILD_ALL")
        return self.execute_build_run_cmd(cmd, handler)


    #---------------------------------------------------------------------------
    # Build Current
    #---------------------------------------------------------------------------

    def build_current(self, handler=None):
        """
        Build only the current project
        """

        LOG.info("Build current")
        cmd = self._command_id_cmd("ID_RIBBON_HOME_COMPILE_BUILD")
        return self.execute_build_run_cmd(cmd, handler)


    #---------------------------------------------------------------------------
    # Run All Simulation Sets
    #---------------------------------------------------------------------------

    def run_all_simulation_sets(self, handler=None):
        """
        Run all simulations sets.

        Any modified projects will be built as necessary.
        """

        LOG.info("Run all simulation sets")
        cmd = self._command_id_cmd('ID_RIBBON_HOME_RUN_RUNALLSIMS')
        return self.execute_build_run_cmd(cmd, handler)

    #---------------------------------------------------------------------------
    # Pause
    #---------------------------------------------------------------------------

    def pause_run(self):
        """
        Pause the currently running projects.
        """

        LOG.info("Pause Run")
        cmd = self._command_id_cmd('ID_RIBBON_HOME_RUN_PAUSE')
        print("Pause")
        return cmd.execute()

    #---------------------------------------------------------------------------
    # Stop
    #---------------------------------------------------------------------------

    def stop_run(self):
        """
        End the currently running projects.
        """

        LOG.info("Stop Run")
        cmd = self._command_id_cmd('ID_RIBBON_HOME_RUN_STOP')
        return cmd.execute()


    #===========================================================================
    # Other commands
    #===========================================================================

    #---------------------------------------------------------------------------
    # Quit command
    #---------------------------------------------------------------------------

    def quit(self):
        """
        Send the EXIT command to PSCAD.

        The command will wait for at most 5 seconds for the PSCAD process
        to terminate.  If the process is still running after 5 seconds,
        the operating system is asked to terminate the process.
        """

        LOG.info("Quiting PSCAD")

        try:

            resp = self.command_id("ID_RIBBON_MAIN_EXIT")

            # Send closing tag '</content>' and shut down socket
            self.close_connection()

        finally:

            if self._proc is not None:
                try:
                    self._proc.wait(5) # pylint: disable=too-many-function-args
                except Exception as ex:
                    LOG.error("Quit PSCAD: %s: Force quiting process", ex)
                    self._kill()
                self._proc = None

        return resp


    #---------------------------------------------------------------------------
    # Generic commands
    #---------------------------------------------------------------------------

    def _command_id_cmd(self, cmd_name):
        #define IDENTIFIER --> #

        cmd_id = cmd_name
        if cmd_name in RES_ID:
            cmd_id = RES_ID[cmd_name]

        cmd = self.command('generic')
        cmd.param(cmd.root, 'command-id', str(cmd_id))
        cmd.root.set('ident', str(cmd_name))

        return cmd

    # Commands sent by ID_xxxx codes never have useful responses
    def command_id(self, cmd_name):
        cmd = self._command_id_cmd(cmd_name)
        cmd.execute(wait_for_response=False)
        return None


    #---------------------------------------------------------------------------
    # Navigate commands
    #---------------------------------------------------------------------------

    def navigate(self, message):
        cmd = self.command('navigate-message')

        msg = ET.SubElement(cmd.root, 'message')
        msg.set('status', message.get('status'))
        msg.set('label', 'build')
        msg.set('groupid', '0')

        ET.CDATA(msg, message.get('data'))

        user = ET.SubElement(msg, 'User')
        for key in ('scope', 'name', 'status', 'link'):
            user.set(key, message.get(key))

        # Backwards compatibility (pre-461)
        msg.set('table_namespace', message.get('scope'))
        for key in ('scope', 'name', 'link', 'data'):
            msg.set(key, message.get(key))

        return cmd.execute(False)

    def navigate_up(self):

        """
        Navigate Up

        Return to the page which contains the object currently
        being viewed.
        """

        LOG.info("Navigate Up")
        cmd = self._command_id_cmd('ID_RIBBON_HOME_NAVIGATION_UP')
        return cmd.execute()


    #---------------------------------------------------------------------------
    # Common commands
    #---------------------------------------------------------------------------

    def clean_all(self):

        """
        Remove all temporary files used to build the case.
        """

        return self.command_id("ID_RIBBON_HOME_COMPILE_CLEAN_ALL")


    #---------------------------------------------------------------------------
    # Flags
    #---------------------------------------------------------------------------

    def set_flags(self, flags):

        """
        Set or clear one or more application flags

        Parameters:
            flags (dict): The flags to set or clear.

        Example::

            pscad.set_flags({"silence": True, "load-meta-files": False})
        """

        cmd = self.command("set-flags")
        for name, value in flags.items():
            flag = ET.SubElement(cmd.root, 'flag')
            flag.set('name', name)
            flag.set('value', str(value))

        return cmd.execute()

    def get_flags(self):

        """
        Retrieve the current application flags

        Returns:
            A dictionary of the current application flags.

        Example:

            >>> pscad.get_flags()
            {'silence': True, 'load-meta-files': True}

        """

        resp = self.command("get-flags").execute()
        flags = {}
        for flag in resp.findall('flag'):
            flags[flag.get('name')] = flag.get('value') == 'true'

        return flags

    #---------------------------------------------------------------------------
    # Key Commands
    #---------------------------------------------------------------------------

    def keystroke(self):
        return KeyStrokes(self)

    def keystrokes(self, *strokes):
        ks_cmd = self.keystroke()
        for stroke in strokes:
            if isinstance(stroke, int):
                ks_cmd.stroke(stroke)
            elif isinstance(stroke, str):
                ks_cmd.typing(stroke)
            else:
                LOG.error("Invalid keystrokes: %r", stroke)
        return ks_cmd.execute()


    #---------------------------------------------------------------------------
    # Mouse Commands
    #---------------------------------------------------------------------------

    def mouse(self):
        return MouseEvents(self)


    #---------------------------------------------------------------------------
    # Project commands
    #---------------------------------------------------------------------------

    def project(self, project_name):

        """
        Retrieve a controller for a named
        :class:`project <.ProjectCommands>` (library or case) in the workspace.

        Parameters:
            project_name (str): Name of the library or case. \
                The directory and filename extension must not be included.

        Returns:
            A :class:`project <.ProjectCommands>` controller

        >>> master = pscad.project('master')
        >>> master.parameters()['description']
        'Master Library'
        """

        return ProjectCommands(self, project_name)


    #---------------------------------------------------------------------------
    # Get workspace manager
    #---------------------------------------------------------------------------

    def workspace(self):

        """
        Retrieve a proxy controller for the PSCAD :class:`.Workspace`.

        Returns:
            A :class:`.Workspace` controller
        """

        if self._workspace is None:
            self._workspace = Workspace(self)
        return self._workspace


    #---------------------------------------------------------------------------
    # Get simulation set manager
    #---------------------------------------------------------------------------

    def simulation_set(self, set_name):

        """
        Retrieve a proxy controller for a
        :class:`simulation set <.SimulationSet>`.

        Parameters:
            set_name (str): Name of the simulation set

        Returns:
            A :class:`simulation set <.SimulationSet>` controller
        """

        return SimulationSet(self, set_name)

