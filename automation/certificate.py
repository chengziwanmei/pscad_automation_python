#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# PSCAD License Certificates
#===============================================================================

"""
********************
License Certificates
********************

.. autoclass:: Certificate()


Identification
--------------

.. automethod:: Certificate.id
.. automethod:: Certificate.name
.. automethod:: Certificate.account
.. automethod:: Certificate.available
.. automethod:: Certificate.total


Features
--------

.. automethod:: Certificate.features
.. automethod:: Certificate.feature


Requirements
------------

.. automethod:: Certificate.meets
.. automethod:: Certificate.meet
.. automethod:: Certificate.cost

****************
License Features
****************

.. autoclass:: Feature()

Identification
--------------

.. automethod:: Feature.id
.. automethod:: Feature.name
.. automethod:: Feature.value
.. automethod:: Feature.cost
"""

#===============================================================================
# Imports
#===============================================================================

# Standard Python imports
import re, sys

#===============================================================================
# Certificate
#===============================================================================

class Certificate:
    """
    PSCAD License Certificate
    """

    #---------------------------------------------------------------------------
    # Parse
    #---------------------------------------------------------------------------

    @staticmethod
    def parse(msg):
        """Parses a <NewDataSet> XML node containing a list of <LicenseGroups/>
        and <Features/> nodes, and returns a dictionary containing all of the
        LicenseGroups, keyed by the Certificate.id()
        """

        certificates = {}

        for lg_node in msg.findall('NewDataSet/LicenseGroups'):

            row_id = _content(lg_node, 'RowID')

            features = []
            xpath_fmt = "NewDataSet/Features[RowID='{}']"
            for feature in msg.findall(xpath_fmt.format(row_id)):
                features.append(Feature(feature))

            certificates[row_id] = Certificate(row_id, lg_node, features)

        return certificates


    #===========================================================================
    # Constructor
    #===========================================================================

    def __init__(self, row_id, node, features):
        """Parses the following XML Node:

        <LicenseGroups>
            <RowID>1971405233</RowID>
            <AccountID>13198</AccountID>
            <AccountName>Beta Account</AccountName>
            <FeatureSetID>2</FeatureSetID>
            <ProductID>13</ProductID>
            <ProductName>PSCAD 4.6.0 RC PRO</ProductName>
            <Count>1</Count>
            <Owned>2</Owned>
            <Notes />
        </LicenseGroups>"""

        self._id = row_id
        self._features = features
        self._data = {}

        for key in ('AccountID', 'FeatureSetID', 'ProductID', 'Count', 'Owned'):
            self._data[key] = _int_content(node, key)

        for key in ('AccountName', 'ProductName', 'Notes'):
            self._data[key] = _content(node, key)


    #===========================================================================
    # Data Accessors
    #===========================================================================

    def id(self): # pylint: disable=invalid-name
        """
        Returns the ID of the Certificate
        """

        return self._id

    def name(self):
        """
        Returns the 'Product Name' for the Certificate
        """

        return self._data['ProductName']

    def account(self):
        """
        Returns the 'Account Name' for the Certificate
        """

        return self._data['AccountName']

    def available(self):
        """
        Returns the # of available Certificates
        """

        return self._data['Count']

    def total(self):
        """
        Returns the total # of Certificates
        """

        return self._data['Owned']


    #===========================================================================
    # Features
    #===========================================================================

    def features(self):
        """
        Returns the list of all features associated with the Certificate.
        Note: This even includes Features where no instances of that feature
        are owned.
        """

        return self._features

    def feature(self, key):
        """
        Returns a `Feature` associated with the Certificate.  The feature may
        be specified by name (such as "Freq Dep Network Equivalent") or by
        an integer id (such as 17).
        """

        if isinstance(key, str):
            for feature in self._features:
                if feature.name() == key:
                    return feature
        elif isinstance(key, int):
            for feature in self._features:
                if feature.id() == key:
                    return feature
        return None


    #===========================================================================
    # certificate[key]
    #   key is an string:
    #       - returns feature where name=key
    #   key is an int:
    #       - returns feature where feature_id=key
    #   key is a tuple (feature_name_or_id, limit):
    #       - returns True if feature's value >= limit, False otherwise
    #       Since a feature will also evaluate as True/False in boolean context,
    #       This means self[feature_name] and self[(feature_name,10)] can both
    #       act as requirement tests, for the 'meets()' method.
    #===========================================================================

    def __getitem__(self, key):
        """If key is a string or an integer, returns the corresponding feature.
        If the key is a (feature_name_or_id, lower_limit) tuple, the feature's
        value is retrieved and tested against the specified lower_limit.
        """
        if key == 'account':
            return self.account()
        if key == 'product':
            return self.name()

        if isinstance(key, tuple):
            feature, lower_limit = key
            return self.feature(feature) >= lower_limit

        return self.feature(key)


    #===========================================================================
    # Does the certificate meet a set of requirements?
    #, where requirements are
    # givens as a sequence containing either:
    #    a feature_name,
    #    a (feature_name, lower_limit) tuple
    #===========================================================================

    def meets(self, requirements):
        """
        Tests if the certificate meets the given list of requirements.

        Parameters:
            requirements: A list of requirements.  Each requirement may be \
                given as:

                - a string or integer, in which case the certificate must
                  own the corresponding feature,
                - a (feature_name_or_id, lower_limit) tuple, in which case
                  the feature must have a value greater than or equal to the limit.

        Example::

            # Does `cert` allow black boxing and 20 or more EMTDC instances?
            cert.meets(["Blackboxing", ("EMTDC Instances", 20)])
        """

        if isinstance(requirements, dict):
            return all(self.meet(key, val) for key, val in requirements.items())
        else:
            return all(self[req] for req in requirements)

    def meet(self, key, req):
        """
        Tests if the certificate meets the given requirement.

        Parameters:
            key: a feature name or the corresponding integer value
            req: one of:

                - a string: exact match of feature value
                - a boolean: exact match of feature value
                - an int: exact match of feature value
                - a tuple: range of values [low,high] that can match the feature

        Example::

            # Does `cert` disallow black boxing?
            cert.meets("Blackboxing", False)
        """

        value = self[key]
        meets = True

        if value is None:
            meets = False
        elif isinstance(value, str):
            if len(req) > 2 and req.startswith("/") and req.endswith("/"):
                meets = re.search(req[1:-1], value) != None
            elif len(req) > 3 and  req.startswith("/") and req.endswith("/i"):
                meets = re.search(req[1:-2], value, re.IGNORECASE) != None
            else:
                meets = value == req
        elif isinstance(req, bool):
            meets = req == bool(value)
        elif isinstance(req, int):
            meets = value == req
        elif isinstance(req, tuple)  and len(req) <= 2:
            lower = req[0]
            upper = req[1] if len(req) == 2 else sys.maxsize
            meets = lower <= value and value <= upper
        else:
            meets = False

        return meets


    #===========================================================================
    # Certificate Cost
    #===========================================================================

    #---------------------------------------------------------------------------
    # Default Certificate Cost
    #---------------------------------------------------------------------------

    @classmethod
    def _default_cost(cls, certificate):
        """The cost of a certificate is calculated as the sum of the cost of the
        individual features, plus an additional premium for 'rare' (small values
        for cert.total()) certificates.

        The certificate cost is used by the license selection logic to determine
        which license to acquire from the set of all licenses which meet the
        list of requested features.  The 'cheapest' license is choosen.

        This function may be overridden to alter the certificate cost, altering
        the license selection logic.
        """

        cost = 5 / certificate.total()
        cost += sum(feature.cost() for feature in certificate.features())

        return cost


    COST = _default_cost

    #---------------------------------------------------------------------------
    # Certificate Cost
    #---------------------------------------------------------------------------

    def cost(self):
        """
        The certificate cost may be used by the license selection logic to
        determine which license to acquire from the set of all licenses which
        meet the list of requested features.  The 'cheapest' license would be
        choosen.

        This function returns a cost using a default heuristic.  The method may
        be overridden by setting the class member `Certificate.COST`.
        """

        return Certificate.COST(self)


    #===========================================================================
    # Debug
    #===========================================================================

    def __str__(self):
        return "Certificate[{} ({}), {}/{}]".format(
            self.name(), self.account(), self.available(), self.total())


#===============================================================================
# Feature
#===============================================================================

class Feature:

    """
    A feature of a license :class:`.Certificate`.
    """

    #===========================================================================
    # Constructor
    #===========================================================================

    def __init__(self, node):

        """Parses the following XML nodes:

        <Features>
            <RowID>1444555977</RowID>
            <FeatureID>12</FeatureID>
            <FeatureName>EMTDC Instances</FeatureName>
            <Owned>1</Owned>
            <FeatureValue>16</FeatureValue>
            <Notes />
        </Features>"""

        self._id = _int_content(node, 'FeatureID')
        self._name = _content(node, 'FeatureName')
        self._owned = _int_content(node, 'Owned')
        self._value = _int_content(node, 'FeatureValue')
        self._notes = _content(node, 'Notes')


    #===========================================================================
    # Data Accessors
    #===========================================================================

    def id(self): # pylint: disable=invalid-name
        """
        Returns the Feature's ID.
        """

        return self._id

    def name(self):
        """
        Returns the Feature's name.
        """

        return self._name

    def value(self):
        """
        Returns the Feature's value.
        """

        return self._value


    #===========================================================================
    # Feature Tests
    #===========================================================================

    def __bool__(self):
        """Is this feature 'owned'"""
        return self._owned > 0

    def __gt__(self, val):
        """Does this feature have a 'value' greater than ..."""
        return self._owned > 0  and  self._value > val

    def __ge__(self, val):
        """Does this feature have a 'value' greater than or equal to ..."""
        return self._owned > 0  and  self._value >= val

    def __lt__(self, val):
        """Does this feature have a 'value' less than ..."""
        return self._owned == 0  or  self._value < val

    def __le__(self, val):
        """Does this feature have a 'value' less than or equal to ..."""
        return self._owned == 0  or  self._value <= val

    def __eq__(self, val):
        value = self._value if self._owned > 0 else 0
        return val == value


    #===========================================================================
    # Feature 'Cost'
    #===========================================================================

    #---------------------------------------------------------------------------
    # Default feature costs
    #---------------------------------------------------------------------------

    COSTS = {
        "EMTDC Instances": (0, 0.1),
        "Workspace Level Control":  (1, 0),
        "Freq Dep Line Models":  (1.25, 0),
        "Xoreax Grid Engine":  (10, 0),
        "Blackboxing":  (7, 0),
        "Freq Dependent Network Equivalent":  (2.5, 0),
        "Electric Network Interface":  (3, 0)}


    #---------------------------------------------------------------------------
    # 'cost'
    #---------------------------------------------------------------------------

    def cost(self):
        """
        Computes the 'cost' of a feature.

        `Feature.COSTS` is a dictionary, indexed by feature name, of tuples
        containing the fixed and variable cost for a feature::

            fixed, variable = COSTS[feature.name()]
            cost = fixed + variable * feature.value()

        The certificate cost is used by the license selection logic to determine
        which license to acquire from the set of all licenses which meet the
        list of requested features.  The 'cheapest' license is choosen.

        The fixed and variable costs specified here are arbitrary, and may be
        changed to alter the license selection.
        """

        if self._owned > 0:
            costs = Feature.COSTS[self._name]
            cost = costs[0]
            if self._value is not None:
                cost += costs[1] * self._value
        else:
            cost = 0

        return cost


    #===========================================================================
    # Debug
    #===========================================================================

    def __str__(self):
        if self._value is not None:
            return "{} ({})".format(self._name, self._value)
        return self._name


#===============================================================================
# Helper functions
#===============================================================================

def _int_content(node, key):
    text = _content(node, key)
    return int(text) if text is not None else None

def _content(node, key):
    child = node.find(key)
    return child.text if child is not None else None
