# ==============================================================================
# mhrc.automation package
# ==============================================================================

"""
Launch Methods
==============

The Automation Library provides two methods of starting PSCAD:
"Manual" and "Automatic".

The Automatic method, :meth:`launch_pscad() <mhrc.automation.launch_pscad>` is easier to use.
It will find the PSCAD application and launch it with the most common options
as defaults.
If more than one version of PSCAD is installed, it will choose one,
preferring offical releases over Beta versions, 64-bit versions over 32-bit
versions, and later releases over earlier ones.
Arguments may be specified to alter these defaults.

The Manual method involves obtaining a :meth:`controller()`, and querying it
for the installed version(s) of PSCAD, choosing the desired version from
the available choices, and passing that choice to the launch function.
After PSCAD launches, the
:meth:`PSCAD.settings() <mhrc.automation.pscad.PSCAD.settings>` command
must be invoked immediately to ensure the correct licensing option,
and a license is acquired.


Automatic
---------

.. autofunction:: launch_pscad


..

Manual
------

.. autofunction:: controller

"""

VERSION = "1.2.4"
VERSION_HEX = 0x010204f0


# ==============================================================================
# Retrieve a Controller object
# ==============================================================================

def controller(product_list=''):
    """controller()

    Retrieve an application controller object.

    Example Usage::

        import mhrc.automation

        controller = mhrc.automation.controller()

        # Select desired version from list of installed PSCAD versions.
        # For example, the first listed version:
        pscad_versions = controller.get_paramlist_names('pscad')
        pscad_version = pscad_versions[0]

        # Launch options
        opts = dict(silence=True, minimize=False)

        pscad = controller.launch(pscad_version, options=opts)

        # Select certificate licensing.  Must be done immediately after launch.
        pscad.settings(cl_use_advanced=True)

        # Select desired version from list of installed FORTRAN versions.
        # For example, the first listed version:

        fortran_versions = controller.get_paramlist_names('fortran')
        fortran_version = fortan_versions[0]

        # Convert human-readable version name to internal identifier.
        fortran_version = controller.get_param('fortran', fortran_version)

        # Select desired FORTRAN version.
        pscad.settings(fortran_version=fortran_version)

        ...

        pscad.quit()
    """

    from mhrc.automation.controller import Controller

    return Controller(product_list)


# ==============================================================================
# Launch PSCAD
# ==============================================================================

def launch_pscad(pscad_version=None, fortran_version=None, matlab_version=None,
                 silence=True, minimize=False, certificate=True):

    """launch_pscad([pscad_version=] [, fortran_version=] [, matlab_version=]\
        [, silence=] [, minimize=] [, certificate=])
    Launch PSCAD and return a controller proxy.

    All parameters are optional.

    Parameters:
        pscad_version (str) : The PSCAD version to launch.
        fortran_verion (str): The Fortran version to use.
        matlab_verion (str) : The MATLAB version to use.
        silence (bool)      : Supress pop-up dialogs, which block automation.
        minimize (bool)     : Minimize the application window when launched.
        certificate (bool)  : Select between legacy and certificate licensing.

    Returns:
        The PSCAD controller proxy.

    Example Usage::

        import mhrc.automation

        pscad = mhrc.automation.launch_pscad()
        ...
        pscad.quit()
    """

    from mhrc.automation.controller import Controller

    ctrl = Controller()

    if pscad_version is None:
        versions = ctrl.get_paramlist_names('pscad')

        # Prefer non 'Alpha', 'Beta' and 'x86' versions (if possible)
        for keyword in ('Alpha', 'Beta', 'x86'):
            vers = [ver for ver in versions if keyword not in ver]
            if vers:
                versions = vers

        pscad_version = sorted(versions)[-1]

    opts = { 'silence': silence, 'launch-minimized': minimize }

    settings = { 'cl_use_advanced': certificate }
    if fortran_version:
        fortran_version = ctrl.get_param('fortran', fortran_version)
        settings['fortran_version'] = fortran_version
    if matlab_version:
        matlab_version = ctrl.get_param('matlab', matlab_version)
        settings['matlab_version'] = matlab_version
    
    pscad = ctrl.launch(pscad_version, options=opts, settings=settings)

    return pscad

