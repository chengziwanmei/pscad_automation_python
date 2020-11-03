#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD Canvas Command class
#===============================================================================

"""Canvas Component Command Object"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
#import xml.etree.ElementTree as ET

# ATS imports
from .component import ComponentCommand


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Canvas Command generator
#===============================================================================

class CanvasComponent(ComponentCommand):

    """Canvas Component Command Object"""

    def __init__(self, project, scope_name, *iid):

        """Construct a command component for a Canvas/Frame"""

        super().__init__(project, scope_name, *iid)

    #===========================================================================
    # copy as bitmap
    #===========================================================================

    def copy_as_bitmap(self):

        """Copy the selected entity to the clipboard as a bitmap"""

        return self._generic('701')

    #===========================================================================
    # copy as metafile
    #===========================================================================

    def copy_as_metafile(self):

        """Copy the selected entity to the clipboard as a metafile"""

        return self._generic('700')

