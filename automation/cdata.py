# Adapted from http://stackoverflow.com/a/8915039/3690024

import xml.etree.ElementTree as ET

if not hasattr(ET, 'CDATA'):
    _original_serialize_xml = ET._serialize_xml

    def _cdata(node, text):
        element = ET.Element('![CDATA[')
        element.text = text
        node.append(element)

    def _serialize_xml(write, elem, qnames, namespaces,
                       *args, **kwargs):
        if elem.tag == '![CDATA[':
            write("<%s%s]]>" % (
                    elem.tag, elem.text))
            return

        return _original_serialize_xml(write, elem, qnames, namespaces,
                                       *args, **kwargs)

    ET._serialize_xml = ET._serialize['xml'] = _serialize_xml
    ET.CDATA = _cdata

