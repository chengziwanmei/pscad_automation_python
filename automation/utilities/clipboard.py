# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Power Systems Computer Aided Design (PSCAD)
# ------------------------------------------------------------------------------
#  PSCAD is a powerful graphical user interface that integrates seamlessly
#  with EMTDC, a general purpose time domain program for simulating power
#  system transients and controls in power quality studies, power electronics
#  design, distributed generation, and transmission planning.
#
#  This Python script is a utility class that can be used by end users
#
#
#     PSCAD Support Team <support@pscad.com>
#     Manitoba HVDC Research Centre Inc.
#     Winnipeg, Manitoba. CANADA
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""Clipboard Utilities"""

#---------------------------------------------------------------------
# Imports
#---------------------------------------------------------------------

import sys, win32clipboard

#---------------------------------------------------------------------
# Clipboard
#---------------------------------------------------------------------

class Clipboard:
    """This Clipboard class allows saving Device Independent Bitmaps (DIBs)
    to a file"""

    FORMATS = {val: name for name, val in vars(win32clipboard).items()
               if name.startswith('CF_')}

    #---------------------------------------------------------------------
    # getFormatName
    #---------------------------------------------------------------------

    @classmethod
    def getFormatName(cls, fmt): # pylint: disable=invalid-name
        """Convert a format identifier (integer) to a readable name"""

        if fmt in cls.FORMATS:
            return cls.FORMATS[fmt]
        try:
            return win32clipboard.GetClipboardFormatName(fmt)
        except:
            return "???"

    #---------------------------------------------------------------------
    # getFormats
    #---------------------------------------------------------------------

    @classmethod
    def _getFormats(cls): # pylint: disable=invalid-name
        """Get format identifiers for contents currently on clipboard"""

        formats = []
        fmt = 0

        while 1:
            fmt = win32clipboard.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            formats.append(fmt)

        return formats

    #---------------------------------------------------------------------
    # _getFormatNames
    #---------------------------------------------------------------------

    @classmethod
    def _getFormatNames(cls): # pylint: disable=invalid-name
        """Get format names for contents currently on clipboard"""

        return [cls.getFormatName(fmt) for fmt in cls._getFormats()]

    #---------------------------------------------------------------------
    # saveBitmap
    #---------------------------------------------------------------------

    @classmethod
    def saveBitmap(cls, filename): # pylint: disable=invalid-name
        """Save the clipboard contents as a Device Independent Bitmap (DIB)

        Returns True if successful, or False if the clipboard does not
        contain DIB content."""

        success = False

        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)

            dib_header_len = int.from_bytes(data[0:4], byteorder='little')
            pixel_offset = 14 + dib_header_len
            size = len(data)+14

            header = (b'BM'
                      + size.to_bytes(4, byteorder='little')
                      + (0).to_bytes(4, byteorder='little')
                      + pixel_offset.to_bytes(4, byteorder='little'))

            with open(filename, 'wb') as bmp:
                bmp.write(header)
                bmp.write(data)

            success = True

        except TypeError:
            print("Clipboard does not contain a bitmap", file=sys.stderr)
            print("Clipboard formats:", cls._getFormatNames(), file=sys.stderr)

        win32clipboard.CloseClipboard()

        return success

#---------------------------------------------------------------------
# Unit Test - requires image stored in clipboard
#---------------------------------------------------------------------

if __name__ == '__main__':
    print("Saving to img2.bmp")
    Clipboard.saveBitmap('img2.bmp')
    print("Saved")
