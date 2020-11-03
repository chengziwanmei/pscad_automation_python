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

"""Microsoft Word Document Helper"""


#---------------------------------------------------------------------
# Imports
#---------------------------------------------------------------------

from win32com.client import Dispatch
import pywintypes

#---------------------------------------------------------------------
# Microsoft Word Document class
#---------------------------------------------------------------------

class Word:

    """Microsoft Word Document helper"""

    def __init__(self):
        self._word = None
        self._doc = None
        self._paragraphs = 0
##        self._word = Dispatch("Word.Application")
##        self._word.Visible = True
##        self._word.Documents.Add()
##        self._doc = self._word.Documents(1)
##        self._paragraphs = 0

    #---------------------------------------------------------------------
    # _add_paragraph
    #---------------------------------------------------------------------

    def _add_paragraph(self):
        """Create a new paragraph"""

        if self._paragraphs > 0:
            self._doc.Paragraphs.Add()
        #self._paragraphs += 1;
        self._paragraphs = self._doc.Paragraphs.Count
        return self._doc.Paragraphs(self._paragraphs)

    #---------------------------------------------------------------------
    # addPageBreak
    #---------------------------------------------------------------------

    def addPageBreak(self): # pylint: disable=invalid-name
        """Adds a Page Break to the current document"""

        paragraph = self._add_paragraph()
        #np.Range.Collapse()
        paragraph.Range.InsertBreak()

    #---------------------------------------------------------------------
    # textParagraph
    #---------------------------------------------------------------------

    def textParagraph(self, text, size=None, bold=None): # pylint: disable=invalid-name
        """Adds a paragraph to the current document"""

        paragraph = self._add_paragraph()
##        old_size = p.Range.Font.Size
##        old_bold = p.Range.Font.Bold
        if size:
            paragraph.Range.Font.Size = size
        if bold or bold == False:
            paragraph.Range.Font.Bold = bold
        paragraph.Range.InsertAfter(text)

    #---------------------------------------------------------------------
    # pasteImage
    #---------------------------------------------------------------------

    def pasteImage(self): # pylint: disable=invalid-name
        """Adds an image from the clipboard to the current document"""

        paragraph = self._add_paragraph()
        paragraph.Range.Paste()

    #---------------------------------------------------------------------
    # save
    #---------------------------------------------------------------------

    def save(self, filename=None, close=False):
        """Save (and possibly close) the current document"""

        if filename:
            self._doc.SaveAs(filename)
        else:
            self._doc.Save()
        if close:
            self.close()

    #---------------------------------------------------------------------
    # close
    #---------------------------------------------------------------------

    def close(self):
        """Close the current document"""

        self._doc.Close()
        self._doc = None
        if self._word.Documents.Count == 0:
            self._word.Quit()
            self._word = None

    #---------------------------------------------------------------------
    # open_document
    #---------------------------------------------------------------------

    def open_document(self, document):
        """Opens the given document"""

        self._word = Dispatch("Word.Application")
        self._word.Visible = True
        self._word.Documents.Open(document)
        self._doc = self._word.Documents(1)
        self._paragraphs = 0

    #---------------------------------------------------------------------
    # new_document
    #---------------------------------------------------------------------

    def new_document(self):
        """Creates a new document"""

        self._word = Dispatch("Word.Application")
        self._word.Visible = True
        self._word.Documents.Add()
        self._doc = self._word.Documents(1)
        self._paragraphs = 0

#---------------------------------------------------------------------
# Unit Testing
#---------------------------------------------------------------------

if __name__ == '__main__':

    word = Word() # pylint: disable=invalid-name
    #word_doc.open_document(r"C:\Users\georgew\Desktop\test.docx")
    word.new_document()
    word.textParagraph("Hello world", 20)
    word.pasteImage()

    word.addPageBreak()
    word.addPageBreak()

    word.textParagraph("Another image follows")
    word.textParagraph("Another image follows")
    word.pasteImage()

    try:
        word.save("C:\\test", False)
    except pywintypes.com_error as ex:
        print("Unable to save")

