#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# Message Handlers
#===============================================================================

"""PSCAD Message Handlers"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Abstract Handler
#===============================================================================

class AbstractHandler:

    def __init__(self):
        pass

    def send(self, _msg): # pylint: disable=no-self-use
        return False

    def close(self):
        pass


#===============================================================================
# BuildEvent
#===============================================================================

class BuildEvent(AbstractHandler):

    def __init__(self):
        super().__init__()
        self._level = 0

    def send(self, msg):
        handled = False

        if msg is not None:
            event = msg.find("event[@type='BuildEvent']")
            if event is not None:
                handled = self._build_event(msg, event)

        return handled

    def _build_event(self, msg, event):
        elapsed = int(msg.get('elapsed'))
        etype = event.find('type')
        phase = etype.get('name')
        status = etype.get('status')
        project = event.find('project')
        prj_name = project.get('name') if project is not None else None

        LOG.debug("BuildEvt: [%s] %s/%s %d", prj_name, phase, status, elapsed)

        if status == 'BEGIN':
            self._level += 1
        elif status == 'END':
            self._level -= 1

        if self._level == 0:
            return StopIteration

        return False

