#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# Automation Controller module
#===============================================================================

"""PSCAD Automation Controller.  Manages valid PSCAD, Fortran and Matlab
versions."""


#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import os, logging, time
import xml.etree.ElementTree as ET
import win32api, win32con

# ATS imports
from .pscad import PSCAD


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Controller
#===============================================================================

class Controller:

    """PSCAD Automation Controller.  Manages valid PSCAD, Fortran and Matlab
    versions.  Launches PSCAD"""

    def __init__(self, product_list=''):

        if product_list == '':
            product_list = self._default_product_list()

        # What versions of PSCAD, Fortran, and Matlab are installed?
        if product_list:
            self._product_list = self._read_product_list(product_list)
        else:
            self._product_list = self._empty_product_list()


    #===========================================================================
    # Launch PSCAD instance
    #===========================================================================

    def launch(self, pscad_ver=None, rxtx_logger=None, options=None, *,
               settings=None, timeout=15):

        if options is None:
            options = {}

        if settings is None:
            settings = { 'cl_use_advanced': True }

        options['path'] = self.get_param('pscad', pscad_ver)
        if options['path']:
            LOG.info("Launching %s: %s", pscad_ver, options['path'])
            try:
                app = PSCAD(rxtx_logger, options)
                if settings:
                    app.settings(**settings)
                if not app.licensed() and timeout > 0:
                    LOG.warning("Waiting to acquire license ...")
                    start = time.perf_counter()
                    while not app.licensed():
                        time.sleep(0.2)
                        elapsed = time.perf_counter() - start
                        if elapsed > timeout:
                            LOG.error("No license found")
                            app._kill()
                            return None
                if 'silence' in options:
                    app.set_flags({"silence": str(options['silence']).lower()})
                return app
            except Exception as exception:
                LOG.error("Failed to launch PSCAD: %s", exception)
                return None
        else:
            LOG.error("Failed to launch %s. Product missing from the required ProductList.xml configuration file.", pscad_ver)
            LOG.error("Ensure the product is installed, then select Tools | Run Fortran Medic to update this file")
            return None


    #===========================================================================
    # Configuration
    #===========================================================================

    #---------------------------------------------------------------------------
    # Default configuration location
    #---------------------------------------------------------------------------

    @staticmethod
    def _default_product_list():
        # Default Public documents location
        public_docs = r'C:\Users\Public\Documents'

        # Try and read from Registry
        try:
            path = ('SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\'
                    'Shell Folders')
            name = 'Common Documents'
            rkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, path)
            val = win32api.RegQueryValueEx(rkey, name)
            public_docs = str(val[0])
        finally:
            win32api.RegCloseKey(rkey)

        product_list = os.path.join(public_docs,
                                    "Manitoba HVDC Research Centre\\ATS",
                                    "ProductList.xml")
        return product_list


    #---------------------------------------------------------------------------
    # Read configuration
    #---------------------------------------------------------------------------

    @staticmethod
    def _read_product_list(product_list):
        LOG.debug("Read ProductList: %s", product_list)
        tree = ET.parse(product_list)
        return tree.getroot()

    #---------------------------------------------------------------------------
    # Default configuration
    #---------------------------------------------------------------------------

    @staticmethod
    def _empty_product_list():
        root = ET.Element("Main")
        for name in ['pscad', 'fortran', 'matlab']:
            paramlist = ET.SubElement(root, 'paramlist')
            paramlist.set('name', name)

        return root

    #---------------------------------------------------------------------------
    # Get list of product versions
    #   eg) get_paramlist_names('fortran')
    #           ->['GFortran 4.2.1', 'GFortran 4.6.2']
    #---------------------------------------------------------------------------

    def get_paramlist_names(self, paramlist_name):
        names = []
        xpath = "./paramlist[@name='{0}']/param[@name]".format(paramlist_name)
        for node in self._product_list.findall(xpath):
            names.append(node.attrib['name'])

        return names

    #---------------------------------------------------------------------------
    # Get param detail for a given product version
    #---------------------------------------------------------------------------

    def get_param(self, paramlist_name, param_name):
        """Retrieve the value of a parameter from a parameter list.
        For example, the parameter list "pscad" stores the executable pathname
        as the value for a parameter, such as "PSCAD Beta (x64)".
        """

        if not param_name:
            return None

        value = None

        xpath = "./paramlist[@name='{0}']/param[@name='{1}']".format(
            paramlist_name, param_name)
        node = self._product_list.find(xpath)
        if node != None:
            value = node.attrib['value']
        else:
            xpath = "./paramlist[@name='{0}']/param[@value='{1}']".format(
                paramlist_name, param_name)
            node = self._product_list.find(xpath)
            if node != None:
                value = param_name
            else:
                raise KeyError("{1!r} not found in {0} parameter list".format(
                    paramlist_name, param_name))

        LOG.debug("paramlist('%s', '%s') -> '%s'", paramlist_name, param_name,
                  value)
        return value

    #---------------------------------------------------------------------------
    # Add/modify the parameter detail for a product version
    #---------------------------------------------------------------------------

    def add_param(self, paramlist_name, param_name, value):
        """Add a new parameter name/value pair to a parameter list.  This
        is used to add new entries or override existing ones, such as for
        private developer versions of PSCAD.
        """

        xpath = "paramlist[@name='{0}']".format(paramlist_name)
        LOG.debug("add_param(): %s", xpath)
        section = self._product_list.find(xpath)

        # Find existing node
        node = section.find("param[@name='{0}']".format(param_name))

        # Create a new node, if not found
        if node is None:
            node = ET.SubElement(section, "param")
            node.attrib['name'] = param_name

        node.attrib['value'] = value

    #---------------------------------------------------------------------------
    # Select a PSCAD version
    #---------------------------------------------------------------------------

    def select_pscad_version(self):

        versions = self.get_paramlist_names('pscad')

        # Skip 'Alpha' versions if other possibilities exist
        vers = [ver for ver in versions if not 'Alpha' in ver]
        if len(vers) > 0:
            versions = vers

        # Skip 'Beta' versions if other possibilities exist
        vers = [ver for ver in versions if not 'Beta' in ver]
        if len(vers) > 0:
            versions = vers

        # Also, skip any (x86) versions, if other possibilities exist
        vers = [ver for ver in versions if not '(x86)' in ver]
        if len(vers) > 0:
            versions = vers

        # Return the highest version available, which should be the last
        # entry in the sorted list.
        return sorted(versions)[-1]
