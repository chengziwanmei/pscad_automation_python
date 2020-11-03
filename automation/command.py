#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD command class
#===============================================================================

"""PSCAD Command objects.  Creates XML command nodes, for transmission over
a socket to a PSCAD process."""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging, time
import xml.etree.ElementTree as ET


#===============================================================================
# Constants
#===============================================================================

# XML Transmit Tags

# <command name='..' sequence-id='..' scope='...'> ... </command>
COMMAND_TAG = "command"
COMMAND_NAME = "name"
COMMAND_SEQ_ID = "sequence-id"
COMMAND_SCOPE = "scope"

# <param name='..' value='..'/>
PARAM_TAG = "param"
PARAM_NAME = "name"
PARAM_VALUE = "value"

# <scope> ... </scope>
SCOPE_TAG = "scope"


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)

#===============================================================================
# Command Processor
#===============================================================================

class CmdProcessor:

    #===========================================================================
    # Constructor
    #===========================================================================

    def __init__(self):
        super().__init__()
        self._sock = None
        self._cmd_seq = 0
        self._handlers = []


    #===========================================================================
    # Close
    #===========================================================================

    def close_and_cleanup(self):
        for handler in self._handlers:
            handler.close()
        self._handlers = None
        self._sock.close()


    #===========================================================================
    # Handler
    #===========================================================================

    #---------------------------------------------------------------------------
    # Add / Remove Handlers
    #---------------------------------------------------------------------------

    def add_handler(self, handler):
        if handler not in self._handlers:
            handlers = self._handlers[:]    # Copy on write
            handlers.insert(0, handler)
            self._handlers = handlers

    def remove_handler(self, handler):
        if handler in self._handlers:
            handlers = self._handlers[:]    # Copy on write
            handlers.remove(handler)
            self._handlers = handlers


    #---------------------------------------------------------------------------
    # Dispatcher
    #---------------------------------------------------------------------------

    def _dispatch(self, msg):
        for handler in self._handlers:
            remove = False
            try:
                handled = handler.send(msg)
                if handled is StopIteration:
                    remove = True
                elif handled:
                    break
            except StopIteration:
                remove = True

            if remove:
                LOG.info("Handler: StopIteration: Removing handler")
                self.remove_handler(handler)


    #===========================================================================
    # Response Waiters
    #===========================================================================

    #---------------------------------------------------------------------------
    # Wait for message
    #---------------------------------------------------------------------------

    def _recv(self):
        return self._sock.recv()


    #---------------------------------------------------------------------------
    # Wait for consumer to collect result
    #---------------------------------------------------------------------------

    def _wait_for_consumer(self, consumer):

        while self._sock.rx_open():
            msg = self._recv()
            try:
                handled = consumer.send(msg)
                if handled is StopIteration:
                    break
                if not handled:
                    self._dispatch(msg)
            except StopIteration:
                break


    #---------------------------------------------------------------------------
    # Wait for response to specific command
    #---------------------------------------------------------------------------

    def wait_for(self, xpath, timeout=0):
        start = time.time()

        while self._sock.rx_open():
            msg = self._recv()
            self._dispatch(msg)

            if msg is not None:
                found = msg.find(xpath) is not None
                if found:
                    break
            elif timeout > 0:
                elapsed = time.time() - start
                if elapsed > timeout:
                    break

        if not self._sock.rx_open():
            LOG.warning("PSCAD unexpectedly disconnected")
            raise Exception("PSCAD unexpectedly disconnected")

        return msg


    #---------------------------------------------------------------------------
    # Wait for response to specific command
    #---------------------------------------------------------------------------

    def _wait_for_response(self, cmd):
        if isinstance(cmd, Command):
            seq_no = cmd.get_id()
        else:
            seq_no = cmd.get(COMMAND_SEQ_ID)

        xpath = "[@sequence-id='{}']".format(seq_no)

        return self.wait_for(xpath)


    #===========================================================================
    # Command Generator
    #===========================================================================

    def command(self, cmd_name, scope=None):
        cmd = Command(self, cmd_name, scope)
        return cmd

    def cmd_seq(self):
        self._cmd_seq += 1
        return str(self._cmd_seq)


    #===========================================================================
    # Send Command
    #===========================================================================

    def _send(self, cmd):
        xml = cmd.root if isinstance(cmd, Command) else cmd
        self._sock.send(xml)


    #===========================================================================
    # Command Executor
    #===========================================================================

    #---------------------------------------------------------------------------
    # Send a command
    #---------------------------------------------------------------------------

    def send(self, cmd):
        self._send(cmd)


    #---------------------------------------------------------------------------
    # Send a command, wait for consumer to collect result
    #---------------------------------------------------------------------------

    def submit(self, cmd, consumer):
        self._send(cmd)
        self._wait_for_consumer(consumer)


    def wait_for_consumer(self, consumer):
        self._wait_for_consumer(consumer)


    #---------------------------------------------------------------------------
    # Send a command, wait for response
    #---------------------------------------------------------------------------

    def execute(self, cmd):
        self._send(cmd)
        return self._wait_for_response(cmd)


    #---------------------------------------------------------------------------
    # Migration help
    #---------------------------------------------------------------------------

    def send_command(self, cmd, wait_for_response=True):
        resp = None
        if wait_for_response:
            resp = self.execute(cmd)
        else:
            self._send(cmd)

        return resp

    #===========================================================================
    # Post Command
    #===========================================================================

    def post_command(self, cmd, func, *args, **kwargs):

        xpath = "[@sequence-id='{}']".format(cmd.get_id())

        def consumer():
            LOG.debug("Handler started: xpath = %s", xpath)
            while True:
                try:
                    msg = yield False
                    if msg is not None  and  msg.find(xpath) is not None:
                        func(msg, *args, **kwargs)
                        break
                except GeneratorExit:
                    break
            LOG.debug("Handler exited: xpath = %s", xpath)

        LOG.debug("post_command: %s", cmd)
        handler = consumer()
        next(handler)
        self.add_handler(handler)
        self._send(cmd)


#===============================================================================
# Command (sending commands from ATS to PSCAD over socket
#===============================================================================

class Command:

    """Command (wrapper for an XML node containing a command)"""

    def __init__(self, pscad, cmd_name, scope=None):
        self.pscad = pscad
        self._scope = None

        self.root = ET.Element(COMMAND_TAG)
        self.root.set(COMMAND_SEQ_ID, pscad.cmd_seq())
        self.root.set(COMMAND_NAME, cmd_name)

        if scope is not None:
            self.root.set(COMMAND_SCOPE, scope)

    def get_id(self):
        return self.root.get(COMMAND_SEQ_ID)

    def dump(self):
        ET.dump(self.root)

    def __str__(self):
        return str(ET.tostring(self.root), "utf-8")

    def __repr__(self):
        return str(ET.tostring(self.root), "utf-8")


    #---------------------------------------------------------------------------
    # Create Scope Tag
    #---------------------------------------------------------------------------

    def scope(self, scope_name):
        self.root.set(COMMAND_SCOPE, scope_name)
        self._scope = ET.SubElement(self.root, SCOPE_TAG)
        return self._scope


    #---------------------------------------------------------------------------
    # Param Tag
    #---------------------------------------------------------------------------

    @staticmethod
    def param(root, name, value):
        param = ET.SubElement(root, PARAM_TAG)
        param.set(PARAM_NAME, name)
        param.set(PARAM_VALUE, value)
        return param

    #---------------------------------------------------------------------------
    # Other subtags
    #---------------------------------------------------------------------------

    def tag(self, tag_name):
        return ET.SubElement(self.root, tag_name)


    #---------------------------------------------------------------------------
    # "Execute" the command (sending it to PSCAD)
    #---------------------------------------------------------------------------

    def execute(self, wait_for_response=True):
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("execute %s", self)

        resp = self.pscad.send_command(self.root, wait_for_response)

        if resp is not None and resp.get("success") != "true":
            LOG.error("execute %s failed", self)
            LOG.error("  resp %s", str(ET.tostring(resp), "utf-8"))

        elif LOG.isEnabledFor(logging.DEBUG):
            if resp is not None:
                LOG.debug("  resp %s", str(ET.tostring(resp), "utf-8"))
            else:
                LOG.debug("  resp %s", resp)

        return resp

    def submit(self, consumer):
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("submit: %s", str(ET.tostring(self.root), "utf-8"))

        return self.pscad.submit(self.root, consumer)


#===============================================================================
# ScopedCommand
#===============================================================================

class CommandScope:

    def __init__(self, pscad, scope_name, **scope):

        self._pscad = pscad
        self._scope_name = scope_name
        self._scope = scope

    def command(self, cmd_name):
        if self._scope:
            cmd = Command(self._pscad, cmd_name)
            scope = cmd.scope(self._scope_name)
            for key, val in self._scope.items():
                ET.SubElement(scope, key).set('name', val)
        else:
            cmd = Command(self._pscad, cmd_name, self._scope_name)

        return cmd

    def _set_value(self, name, value):
        cmd = self.command('set-' + name)
        cmd.tag(name).set('value', str(value))
        resp = cmd.execute()
        success = resp.get('success') == 'true'
        if not success:
            LOG.error("Command failed: %s", str(cmd))
        return resp

    def _get_value(self, name):
        cmd = self.command('get-' + name)
        resp = cmd.execute()
        value = None
        if resp.get('success') == 'true':
            tag = resp.find(name)
            if tag is not None:
                value = tag.get('value')

        return value

    def _parameters(self, name=None, parameters=None):
        if parameters:
            cmd = self.command('set-parameters')
            if name:
                cmd.tag('name').set('value', name)
            for key, value in parameters.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                cmd.param(cmd.root, key, str(value))
            cmd.execute()
        else:
            cmd = self.command('list-parameters')
            if name:
                cmd.tag('name').set('value', name)
            resp = cmd.execute()
            parameters = {}
            for param in resp.findall('paramlist/param'):
                parameters[param.get('name')] = param.get('value')

        return parameters

    def _set_control_value(self, parameters=None):
        if parameters:
            cmd = self.command('set-value')
            for key, value in parameters.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                cmd.param(cmd.root, key, str(value))
            cmd.execute()

        return parameters
