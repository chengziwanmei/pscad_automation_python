#===============================================================================
# PSCAD Automated Test Suite
#===============================================================================
# XML Socket
#===============================================================================

"""Communicate via XML over a socket"""


#===============================================================================
# Imports
#===============================================================================

import logging, socket
import xml.etree.ElementTree as ET


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# XML Socket
#===============================================================================

class XmlSocket:

    _HEARTBEAT = ET.fromstring(
        "<command name='keystroke' scope='PSCAD' sequence-id='0'>"
        "<key type='typing'></key></command>")

    #---------------------------------------------------------------------------
    # Constructor
    #---------------------------------------------------------------------------

    def __init__(self, sock, timeout=2.0, encoding='utf-8'):
        self._sock = sock
        self._sock.settimeout(timeout)

        self._tx_open = True
        self._rxbuf = ''
        self._end_tag = None
        self._rx = self._read_xml(sock, 1024, encoding)
        self._logger = None
        self._timeouts = 0

    #---------------------------------------------------------------------------
    # Logged
    #---------------------------------------------------------------------------

    def logger(self, logger):
        self._logger = logger


    #---------------------------------------------------------------------------
    # Open/Close
    #---------------------------------------------------------------------------

    def is_open(self):
        return self.tx_open()  and  self.rx_open()

    def is_closed(self):
        return self._sock is None

    def close(self):
        self.tx_close()
        self.rx_close()

        if self._sock is not None:
            if self._logger:
                self._logger.tx_log(ET.Element('socket-close'))
            try:
                self._sock.close()
            except Exception as ex:
                LOG.warning("Exception shutting down socket: %s", ex)

        self._sock = None


    #---------------------------------------------------------------------------
    # Transmit side
    #---------------------------------------------------------------------------

    def tx_open(self):
        return self._tx_open  and  self._sock is not None

    def send_raw(self, msg_text):
        if self.tx_open():
            try:
                self._sock.sendall(msg_text)
            except ConnectionResetError:
                self._tx_open = False
                self._sock = None
                self.tx_closed()

    def send(self, msg):
        if self.tx_open():
            self._timeouts = 0
            if self._logger:
                self._logger.tx_log(msg)
            self.send_raw(ET.tostring(msg))

    def tx_close(self):
        if self._tx_open  and  self._sock is not None:
            if self._logger:
                self._logger.tx_log(ET.Element('socket-tx-close'))
            try:
                self._sock.shutdown(socket.SHUT_WR)
            except Exception as ex:
                LOG.warning("Exception shutting down socket: %s", ex)
                self._sock = None
        self._tx_open = False

    def tx_closed(self):
        if self._logger:
            self._logger.tx_log(ET.Element('connection-reset'))
        LOG.warning("Socket: Connection Reset Error: send failed.")


    #---------------------------------------------------------------------------
    # Heartbeat?
    #---------------------------------------------------------------------------

    def _send_heartbeat(self):
        if XmlSocket._HEARTBEAT is not None:
            LOG.debug("HEARTBEAT: rxbuf=%r, endtag=%r",
                      self._rxbuf, self._end_tag)
            self.send(XmlSocket._HEARTBEAT)

    #---------------------------------------------------------------------------
    # Receive side
    #---------------------------------------------------------------------------

    def rx_open(self):
        return self._rx is not None

    def recv(self):
        xml = None

        if self.rx_open():
            try:
                xml = next(self._rx)
                if xml is None:
                    self._timeouts += 1
                    if self._timeouts >= 30:
                        self._send_heartbeat()
                elif self._logger:
                    self._logger.rx_log(xml)
            except StopIteration:
                self._rx = None
                self.rx_closed()

        return xml

    def rx_close(self):
        if self._rx is not None:
            if self._logger:
                self._logger.rx_log(ET.Element('socket-rx-close'))
            try:
                self._sock.shutdown(socket.SHUT_RD)
            except Exception as ex:
                LOG.warning("Exception shutting down socket: %s", ex)
                self._sock = None
        self._rx = None


    def rx_closed(self):
        if self._logger:
            conn_closed = ET.Element('connection-closed')
            conn_closed.append(ET.Comment(repr(self._rxbuf)))
            conn_closed.append(ET.Comment(repr(self._end_tag)))
            self._logger.rx_log(conn_closed)


    #---------------------------------------------------------------------------
    # XML Receive generator
    #---------------------------------------------------------------------------

    def _read_xml(self, sock, bufsize, encoding):

        LOG.debug("_read_xml generator started")

        while sock is not None:

            # The rxbuf at this point contains no more complete fragments;
            # wait for more data to arrive.
            # We expect Timeouts, handle them gracefully.  ConnectionResets are
            # not exactly expected, but we can handle them gracefully, too.
            try:
                # Check if we've received some data
                data = sock.recv(bufsize)

                # Did we receive any data?
                if data:
                    # Yes.  Accumulate most recently received data into buffer
                    self._rxbuf += data.decode(encoding)

                    # Extract and emit any complete messages
                    xml = self._extract_xml()
                    while xml is not None:
                        yield xml
                        xml = self._extract_xml()

                else:
                    # No, but we didn't timeout, either!
                    # The socket must have closed.
                    sock = None

            # If there is nothing to read at the moment, yield None, so that
            # other processing can continue, in parallel.
            except socket.timeout:
                yield None

            # If the connection is reset, we're done.
            except ConnectionResetError:
                LOG.warning("ConnectionResetError - Terminating Rx loop")
                sock = None

        LOG.debug("_read_xml generator exhausted: rxbuf=%r, endtag=%r",
                  self._rxbuf, self._end_tag)


    #---------------------------------------------------------------------------
    # XML Extractor
    #---------------------------------------------------------------------------

    def _extract_xml(self):

        rxbuf = self._rxbuf
        xml = None
        resp_len = 0

        # If we haven't determined what the end of the current message is...
        if self._end_tag is None:

            # Have we found the end of the first XML tag?
            end = rxbuf.find('>')
            if end < 0:
                # No!  We need more data in the buffer
                return None

            # Have we found a simple leaf-type "<name ... />"?
            if rxbuf[end-1:end+1] == '/>':
                # Yes, extract the entire tag
                resp_len = end+1
            else:
                # No, we need to find matching "</name> tag
                space = rxbuf.find(" ", 0, end)
                if space > 0:
                    end = space
                self._end_tag = "</" + rxbuf[1:end] + ">"

        # Are we looking for a </name> tag?
        if self._end_tag is not None:

            # If so, see if we've got it.
            pos = rxbuf.find(self._end_tag)
            if pos > 0:
                # Yes, extract up to and including this tag
                resp_len = pos + len(self._end_tag)
                self._end_tag = None


        # Do we have a complete XML fragment? <tag>...</tag>  or <tag.../>
        if resp_len > 0:
            # Yes!  Split the buffer at the end of the fragment,
            # and parse the first part as an XML string
            xml = ET.fromstring(rxbuf[:resp_len])

            # Remove first part from buffer.
            self._rxbuf = rxbuf[resp_len:]

        return xml

