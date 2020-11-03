# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Power Systems Computer Aided Design (PSCAD)
# ------------------------------------------------------------------------------
#  PSCAD is a powerful graphical user interface that integrates seamlessly
#  with EMTDC, a general purpose time domain program for simulating power
#  system transients and controls in power quality studies, power electronics
#  design, distributed generation, and transmission planning.
#
#  This Python script is a utiliy class.It has usefull functions that
#  can help you develop fully featured PSCAD scripts.
#
#     PSCAD Support Team <support@pscad.com>
#     Manitoba HVDC Research Centre Inc.
#     Winnipeg, Manitoba. CANADA
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""E-Mail Helper Utility"""

#---------------------------------------------------------------------
# Imports
#---------------------------------------------------------------------

import sys
import smtplib
import win32com.client
#from win32com.client import Dispatch
from os.path import basename
#from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

#===========================================================================
# Mail Class
#---------------------------------------------------------------------------
# Provides the ability to send emails
#---------------------------------------------------------------------------

class Mail:

    """E-Mail Helper Utility"""

    #----------------------------------------------------------------------
    # send_gmail() - Sends an email using any gmail account
    #----------------------------------------------------------------------
    @staticmethod
    def send_gmail(sender, password, recipients, subject, body, # pylint: disable=too-many-arguments
                   attachments=None):

        """Sends a document using a GMail account"""

        # Create the enclosing (outer) message
        outer_message = MIMEMultipart()
        outer_message.attach(MIMEText(body, 'plain'))
        outer_message['Subject'] = subject
        outer_message['To'] = recipients
        outer_message['From'] = 'pscad.script@gmail.com'
        outer_message.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        # Create a list of attachments
        #temp = attachments.replace(' ', '') # make sure no white space
        #attachment_list = temp.split(",")
        attachment_list = (fn.strip() for fn in attachments.split(","))


        # Add the attachments to the message
        for file in attachment_list:
            try:
                with open(file, "rb") as fil:
                    outer_message.attach(MIMEApplication(
                        fil.read(),
                        Content_Disposition='attachment; filename="%s"' % basename(file),
                        Name=basename(file)
                    ))
            except:
                print("Unable to open one of the attachments. Error: ",
                      sys.exc_info()[0])
                raise
        composed = outer_message.as_string()

        # Message is ready, send it!
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            # Convert 'recipients' into a list, as expected by sendmail()
            server.sendmail(sender, recipients.split(","), composed)
            server.close()
            print("Successfully sent the gmail")
        except:
            print("Failed to send gmail", sys.exc_info()[0])

    #----------------------------------------------------------------------
    # send_outlook_mail() - Sends an email using Microsoft Outlook
    #----------------------------------------------------------------------
    @staticmethod
    def send_outlook_mail(to, subject, body, attachments=None):

        """Sends a document using a Microsoft Outlook account"""

        try:
            olMailItem = 0x0
            obj = win32com.client.Dispatch("Outlook.Application")
            newMail = obj.CreateItem(olMailItem)
            newMail.Subject = subject
            newMail.Body = body
            newMail.To = to.replace(',', ';') # Outlook takes ; gmail uses ,

            # Create a list of attachments
            #temp = attachments.replace(' ', '') # make sure no white space
            #attachment_list = temp.split(",")
            attachment_list = (fn.strip() for fn in attachments.split(","))

            # Add the attachments to the message
            for file in attachment_list:
                newMail.Attachments.Add(file)
            newMail.Send()
            print("Successfully sent the Outlook Email")
        except:
            print("Failed to send Outlook Email", sys.exc_info()[0])


# Test Code, lets take this for a drive.
if __name__ == '__main__':

    sender = 'pscad.script@gmail.com'
    password = 'laliniscool'
    to = 'georgew@hvdc.ca'#'edillistone@pscad.com,georgew@hvdc.ca'
    subject = 'This email is being sent by a Python script'
    body = 'I am attaching files. \nPython is controlling Microsoft Outlook or GMail and is sending this email automatically !!!'
    attachments = r'C:\Users\Public\Documents\mlp\test.txt, C:\Users\Public\Documents\mlp\test.docx, C:\Users\Public\Documents\mlp\test.jpg, C:\Users\Public\Documents\mlp\test.xlsx'

    Mail.send_gmail(sender, password, to, subject, body, attachments)
    Mail.send_outlook_mail(to, subject, body, attachments)

# ------------------------------------------------------------------------------
#  End of script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
