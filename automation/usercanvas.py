#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD User Canvas Command class
#===============================================================================

"""
***********
User Canvas
***********

.. autoclass:: UserCanvas


Finding Components
------------------

The :meth:`.find()`, :meth:`.find_first()` and :meth:`.find_all()` methods are
improvements over the original methods which found components by Id attribute.
These methods automatically detect the type of the found component(s),
and return a control proxy of the correct type.

.. automethod:: UserCanvas.find
.. automethod:: UserCanvas.find_first
.. automethod:: UserCanvas.find_all


Finding By Id
-------------

These methods are the original methods which find components by Id attribute.
Care must be taken to ensure the correct method is used for the type
of component, or an incorrect control proxy will be returned.

In almost every case, it is simplier to use the newer `find()`, `find_first()`,
or `find_all()` methods.

.. automethod:: UserCanvas.user_cmp
.. automethod:: UserCanvas.bus
.. automethod:: UserCanvas.tline
.. automethod:: UserCanvas.cable
.. automethod:: UserCanvas.graph_frame
.. automethod:: UserCanvas.overlay_graph
.. automethod:: UserCanvas.slider
.. automethod:: UserCanvas.switch
.. automethod:: UserCanvas.button
.. automethod:: UserCanvas.selector

.. automethod:: UserCanvas.list_components


Creating Components
-------------------

.. automethod:: UserCanvas.add_component
.. automethod:: UserCanvas.add_wire


Clipboard Operations
--------------------

.. automethod:: UserCanvas.select_components
.. automethod:: UserCanvas.clear_selection
.. automethod:: UserCanvas.copy
.. automethod:: UserCanvas.cut
.. automethod:: UserCanvas.paste
.. automethod:: UserCanvas.delete
.. automethod:: UserCanvas.paste_transfer
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import logging
import xml.etree.ElementTree as ET

# ATS imports
from .button import ButtonCommands
from .canvas import CanvasComponent
from .graph_frame import GraphFrame
from .overlay_graph import OverlayGraph
from .selector import SelectorCommands
from .slider import SliderCommands
from .switch import SwitchCommands
from .usercmp import UserComponent
from .wire import Wire, WireOrthogonal
from .tline import TLineComponent
from .cable import CableComponent
from .bus import BusComponent

#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# User Canvas Command generator
#===============================================================================

class UserCanvas(CanvasComponent):

    """UserCanvas
    User Canvas

    A canvas is a surface when components can be placed and arranged.
    A "user canvas" is the most general version of a canvas.
    (T-Line and Cable canvases are more restrictive, which permit only certain
    types of components.)


    The main page of a project is typically retrieved with::

        main = project.user_canvas('Main')
    """

    def __init__(self, project, name, *iid):

        """Construct a command component for a User Canvas"""

        super().__init__(project, "UserCanvas", name, *iid)
        self._scope['definition'] = name
        self.name = name


    #===========================================================================
    # Debugging
    #===========================================================================

    def __str__(self):
        return "UserCanvas[{}]".format(self.name)

    def __repr__(self):
        return "UserCanvas[{}]".format(self.name)


    #===========================================================================
    # Canvas entities
    #===========================================================================

    #---------------------------------------------------------------------------
    # UserCmp
    #---------------------------------------------------------------------------

    def user_cmp(self, iid):
        """
        Retrieve by its Id attribute a controller for a user component.

        Note:
            A "user component" is the term used to describe a component which
            is not built-in to the PSCAD application, but rather has a
            definition which is read from a component library.  In this sense,
            most components in the "Master Library" are user components.

            A user component may be identified by a colon (:) in the definition
            name.

        Parameters:
            iid (int): The Id attribute of the user component.

        Returns:
            A user component proxy object.
        """

        return UserComponent(self, iid)

    #---------------------------------------------------------------------------
    # Bus
    #---------------------------------------------------------------------------

    def bus(self, iid):
        """
        Retrieve by its Id attribute a controller for a Bus.

        Parameters:
            iid (int): The Id attribute of the Bus.

        Returns:
            A Bus proxy object.
        """

        return BusComponent(self, iid)

    #---------------------------------------------------------------------------
    # TLine
    #---------------------------------------------------------------------------

    def tline(self, iid, defn=None):
        """
        Retrieve by its Id attribute a controller for a T-Line.

        Parameters:
            iid (int): The Id attribute of the T-Line.

        Returns:
            A T-Line proxy object.
        """

        return TLineComponent(self, iid, defn)

    #---------------------------------------------------------------------------
    # Cable
    #---------------------------------------------------------------------------

    def cable(self, iid, defn=None):
        """
        Retrieve by its Id attribute a controller for a Cable.

        Parameters:
            iid (int): The Id attribute of the Cable.

        Returns:
            A Cable proxy object.
        """

        return CableComponent(self, iid)

    #---------------------------------------------------------------------------
    # Graph Frame
    #---------------------------------------------------------------------------

    def graph_frame(self, iid):
        """
        Retrieve by its Id attribute a controller for a Graph Frame.

        Parameters:
            iid (int): The Id attribute of the Graph Frame.

        Returns:
            A Graph Frame proxy object.
        """

        return GraphFrame(self, iid)

    #---------------------------------------------------------------------------
    # Overlay Graph
    #---------------------------------------------------------------------------

    def overlay_graph(self, *iid):
        """overlay_graph(frame_id, id)
        Retrieve by its Id attribute a controller for an Overlay Graph.

        Parameters:
            frame_id (int): The Id attribute of the Graph Frame.
            id (int): The Id attribute of the Overlay Graph.

        Returns:
            An Overlay Graph proxy object.
        """

        return OverlayGraph(self, *iid)

    #---------------------------------------------------------------------------
    # Slider
    #---------------------------------------------------------------------------

    def slider(self, *iid):
        """slider(frame_id, id)
        Retrieve by its Id attribute a controller for a Slider, nested
        in a control frame.

        Parameters:
            frame_id (int): The Id attribute of the Control Frame.
            id (int): The Id attribute of the Slider.

        Returns:
            A Slider proxy object.
        """

        return SliderCommands(self, *iid)

    #---------------------------------------------------------------------------
    # Switch
    #---------------------------------------------------------------------------

    def switch(self, *iid):
        """switch(frame_id, id)
        Retrieve by its Id attribute a controller for a Switch, nested
        in a control frame.

        Parameters:
            frame_id (int): The Id attribute of the Control Frame.
            id (int): The Id attribute of the Switch.

        Returns:
            A Switch proxy object.
        """

        return SwitchCommands(self, *iid)

    #---------------------------------------------------------------------------
    # Button
    #---------------------------------------------------------------------------

    def button(self, *iid):
        """button(frame_id, id)
        Retrieve by its Id attribute a controller for a Button, nested
        in a control frame.

        Parameters:
            frame_id (int): The Id attribute of the Control Frame.
            id (int): The Id attribute of the Button.

        Returns:
            A Button proxy object.
        """

        return ButtonCommands(self, *iid)

    #---------------------------------------------------------------------------
    # Selector
    #---------------------------------------------------------------------------

    def selector(self, *iid):
        """button(frame_id, id)
        Retrieve by its Id attribute a controller for a Selector, nested
        in a control frame.

        Parameters:
            frame_id (int): The Id attribute of the Control Frame.
            id (int): The Id attribute of the Selector.

        Returns:
            A Selector proxy object.
        """

        return SelectorCommands(self, *iid)


    #===========================================================================
    # select_components
    #===========================================================================

    def select_components(self, x1, y1, x2=None, y2=None, # pylint: disable=invalid-name, too-many-arguments
                          width=None, height=None):
        """
        Select components in a rectangular area.

        If width and height are used, the x1,y1 values are interpreted as the
        lower-left corner of the region.  If both x1,y1 and x2,y2 are given,
        any opposite corners may be used and the rectangle will be normalized
        for the user automatically.

        Parameters:
            x1 (int): lower left corner of the selection region
            y1 (int): lower left corner of the selection region
            x2 (int): upper right corner of the selection region (optional)
            y2 (int): upper right corner of the selection region (optional)
            width (int): width of the selection region (optional)
            height (int): height of the selection region (optional)
        """

        if (x2 is None) == (width is None):
            raise ValueError("Specify either x2 or width (but not both)")
        if (y2 is None) == (height is None):
            raise ValueError("Specify either y2 or height (but not both)")

        if x2 is None:
            x2 = x1 + width
        if y2 is None:
            y2 = y1 - height

        cmd = self.command('select-components')

        point1 = cmd.tag('point')
        point1.set('x', str(x1))
        point1.set('y', str(y1))

        point2 = cmd.tag('point')
        point2.set('x', str(x2))
        point2.set('y', str(y2))

        return cmd.execute()


    #===========================================================================
    # clear_selection
    #===========================================================================

    def clear_selection(self):
        """
        Reset the selection so that no components are selected.
        """

        cmd = self.command('clear-selection')

        return cmd.execute()

    #===========================================================================
    # copy
    #===========================================================================

    def copy(self):
        """
        Copy the currently selected components to the clipboard.
        """

        self._generic('IDM_COPY')

    #===========================================================================
    # cut
    #===========================================================================

    def cut(self):
        """
        Cut the currently selected components to the clipboard.
        """

        self._generic('IDM_CUT')

    #===========================================================================
    # paste
    #===========================================================================

    def paste(self):
        """
        Paste the contents of the clipboard into this canvas
        """

        self._generic('IDM_PASTE')

    #===========================================================================
    # delete
    #===========================================================================

    def delete(self):
        """
        Delete the currently selected components.
        """

        self._generic('IDM_DELETE')


    #===========================================================================
    # add_component
    #===========================================================================

    def add_component(self, library, name, x=0, y=0):
        """
        Create a new user component and add it to the canvas.

        Parameters:
            library (str): Library the definition may be found in.
            name (str): Name of the component definition in the library.
            x (int): X location on the canvas for the component.
            y (int): Y location on the canvas for the component.

        Returns:
            The created :class:`.UserComponent`.
        """

        cmd = self.command('add-components')

        component = cmd.tag('component')
        component.set('classid', 'UserCmp')

        scope = ET.SubElement(component, 'scope')

        project = ET.SubElement(scope, 'project')
        project.set('name', library)

        definition = ET.SubElement(scope, 'definition')
        definition.set('name', name)

        resp = cmd.execute()

        component = resp.find('components/component')
        if component is not None:
            component_id = int(component.get('id'))
            component = UserComponent(self, component_id)
            component.set_location(x, y)

        return component


    #===========================================================================
    # add_wire
    #===========================================================================

    def add_wire(self, *vertices):

        """add_wire( (x1,y1), (x2,y2), [... (xn,yn) ...])
        Create a new wire and add it to the canvas.

        If more than two vertices are given, a multi-vertex wire will be
        created.
        If any segment is neither horizontal or vertical, additional vertices
        will be inserted.

        Returns:
            A created :class:`.Wire`.

        Note:
            Use :meth:`.UserComponent.get_port_location()` to determine
            the locations to connect the wires to.
        """

        cmd = self.command('add-components')

        component = cmd.tag('component')
        component.set('classid', 'WireOrthogonal')

        resp = cmd.execute()

        wire = None
        component = resp.find('components/component')
        if component is not None:
            component_id = int(component.get('id'))

            wire = WireOrthogonal(self, component_id)

            # Normalize vertices with first coordinate as (0,0)
            x0, y0 = vertices[0]
            vertices = [(x-x0,y-y0) for x,y in vertices]

            wire.vertices = vertices
            wire.location = (x0,y0)

        return wire


    #===========================================================================
    # Paste Transfer
    #===========================================================================

    def paste_transfer(self):

        """
        Paste a component and its definition from the clipboard,
        so it can be used in this project.

        See:
            :meth:`.UserComponent.copy_transfer()`
        """

        self._generic('IDM_PASTE_COPYTRANSFER')


    #===========================================================================
    # list_components
    #===========================================================================

    def list_components(self):
        """
        List all components on canvas.

        Returns:
            An XML fragment containing the the contents of the canvas.

        For a friendlier way of getting the entire canvas contents, use::

            contents = canvas.find_all()
        """

        cmd = self.command('list-components')

        return cmd.execute()


    #===========================================================================
    # find, find_first, find_all
    #
    # ...
    # These function searches the canvas for one or more components, which
    # are of a particular type (Bus, TLine, Cable, master:source3, ...) and
    # perhaps have a particular set of parameter values.  In particular, they
    # may be used to find a component with a specific name.
    #===========================================================================

    def find(self, *names, **params):
        """find( [[definition,] name,] [key=value, ...])

        Find the (singular) component that matches the given criteria, or None
        if no matching component can be found.  Raises an exception if more
        than one components match the given criteria.

        Parameters:
            definition (str): One of "Bus", "TLine", "Cable", "GraphFrame",
                "Sticky", or a colon-seperated definition name, such as
                "master:source3" (optional)
            name (str): the component's name, as given by a parameter
                called "name", "Name", or "NAME".
                If no definition was given, and if the provided name is
                "Bus", "TLine", "Cable", "GraphFrame", "Sticky", or
                contains a colon, it is treated as the definition name.
                (optional)
            key=value: A keyword list specifying additional parameters
               which must be matched.  Parameter names and values must match
               exactly. For example, Voltage="230 [kV]" will not match
               components with a Voltage parameter value of "230.0 [kV]".
               (optional)

        Returns:
            A component controller object for the found component,
            or `None` if no matching component can be found.

        Raises:
            ValueError: if more than 1 components match the criteria.

        Examples::

           c = find('Bus'                # the one and only Bus component
           c = find('Bus10')             # the component named "Bus10"
           c = find('Bus', 'Bus10')      # the Bus component named "Bus10"
           c = find('Bus', BaseKV='138') # the Bus with BaseKV="138"
           c = find(BaseKV='138')        # the only component with BaseKV="138"
        """

        components = self.find_all(*names, **params)
        if len(components) > 1:
            raise Exception("Multiple components found")

        return components[0] if components else None


    def find_first(self, *names, **params):
        """find_first( [[definition,] name,] [key=value, ...])

        Find the first component that matches the given criteria, or None
        if no matching component can be found.

        Parameters:
            definition (str): One of "Bus", "TLine", "Cable", "GraphFrame",
                "Sticky", or a colon-seperated definition name, such as
                "master:source3" (optional)
            name (str): the component's name, as given by a parameter
                called "name", "Name", or "NAME".
                If no definition was given, and if the provided name is
                "Bus", "TLine", "Cable", "GraphFrame", "Sticky", or
                contains a colon, it is treated as the definition name.
                (optional)
            key=value: A keyword list specifying additional parameters
               which must be matched.  Parameter names and values must match
               exactly. For example, Voltage="230 [kV]" will not match
               components with a Voltage parameter value of "230.0 [kV]".
               (optional)

        Returns:
            A component controller object for the found component,
            or `None` if no matching component can be found.

        Examples::

           c = find_first('Bus'                # a Bus component
           c = find_first('Bus10')             # a named "Bus10"
           c = find_first('Bus', 'Bus10')      # a Bus component named "Bus10"
           c = find_first('Bus', BaseKV='138') # a Bus with BaseKV="138"
           c = find_first(BaseKV='138')        # a component with BaseKV="138"
        """

        components = self.find_all(*names, **params)

        return components[0] if components else None


    def find_all(self, *names, **params):
        """find_all( [[definition,] name,] [key=value, ...])

        Find all component that matches the given criteria.
        If no criteria is given, all components on the canvas are returned.

        Parameters:
            definition (str): One of "Bus", "TLine", "Cable", "GraphFrame",
                "Sticky", or a colon-seperated definition name, such as
                "master:source3" (optional)
            name (str): the component's name, as given by a parameter
                called "name", "Name", or "NAME".
                If no definition was given, and if the provided name is
                "Bus", "TLine", "Cable", "GraphFrame", "Sticky", or
                contains a colon, it is treated as the definition name.
                (optional)
            key=value: A keyword list specifying additional parameters
               which must be matched.  Parameter names and values must match
               exactly. For example, Voltage="230 [kV]" will not match
               components with a Voltage parameter value of "230.0 [kV]".
               (optional)

        Returns:
            A list of component controller objects for the matching components.
            If no matching components can be found, an empty list is returned.

        Examples::

           c = find_all('Bus'                # all Bus components
           c = find_all('Bus10')             # all components named "Bus10"
           c = find_all('Bus', 'Bus10')      # all Bus component named "Bus10"
           c = find_all('Bus', BaseKV='138') # all Buses with BaseKV="138"
           c = find_all(BaseKV='138')        # all components with BaseKV="138"
        """

        if len(names) > 2:
            raise ValueError("Too many name arguments")

        defn = names[0] if len(names) > 0 else None
        is_named = names[1] if len(names) > 1 else None

        nodetype = "*"
        classid = None
        definition = None

        if defn:
            if defn in ('Bus', 'TLine', 'Cable', 'WireOrthogonal'):
                nodetype = "Wire"
                classid = defn
            elif defn in ('GraphFrame', 'PlotFrame', 'ControlFrame'):
                nodetype = "Frame"
                classid = defn
            elif defn in ('Sticky', 'FileCmp'):
                nodetype = defn
                classid = defn
            elif ':' in defn:
                nodetype = "User"
                classid = "UserCmp"
                definition = defn
            elif not is_named:
                is_named = defn
                defn = None
            else:
                raise ValueError("Unrecognized definition: "+defn)

        resp = self.list_components()
        xpath = "components/"+nodetype
        if classid:
            xpath += "[@classid='%s']" % classid

        nodes = []
##        if definition:
##            xpath2 = xpath + "[@name='%s']" % definition
##            nodes = resp.findall(xpath2)
        if not nodes:
            nodes = resp.findall(xpath)

        components = [self._to_component(node) for node in nodes]
        components = [cmp for cmp in components if cmp is not None]

        # Filter based on definition name
        if definition:
            components = [cmp for cmp in components
                          if cmp.get_definition().scoped_name == definition]

        # Filter based on parameters
        if is_named or params:
            components = [cmp for cmp in components
                          if self._find_match(cmp, is_named, params)]

        return components


    def _to_component(self, xml):

        """Convert XML node to a Component"""

        iid = xml.get('id')
        tag = xml.tag
        classid = xml.get('classid')
        name = xml.get('name')

        if tag == 'User':
            return self.user_cmp(iid)

        elif tag == 'Wire':
            if classid == 'Bus':
                return self.bus(iid)
            elif classid == 'TLine':
                return self.tline(iid, name)
            elif classid == 'Cable':
                return self.cable(iid, name)
            elif classid == 'WireOrthogonal':
                return WireOrthogonal(self, iid)

        elif tag == 'Frame':
            if classid == 'GraphFrame':
                return self.graph_frame(iid)
            elif classid == 'PlotFrame':
                pass
            elif classid == 'ControlFrame':
                pass

        elif tag == 'FileCmp':
            pass

        return None

    @staticmethod
    def _find_match(cmp, is_named, props):

        """Match component name/parameters"""

        params = cmp.get_parameters()

        match = all(params.get(key) == val for key, val in props.items())

        if match and is_named:
            match = any(key.casefold() == "name" and params[key] == is_named
                        for key in params)
        return match

