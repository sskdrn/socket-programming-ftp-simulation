from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class MessageBox(QMessageBox):
    '''
    Creates a MessageBox to display error, inforamtion, or a question.
    exec() method invokes the dialog box
    Constructor parameters:
    MessageBox(title(str), message(str), icon(int), buttons(int) )
        values for buttons: MessageBox.BUTTONS_OK, MessageBox.BUTTONS_OK_CANCEL
        icons: MessageBox.ICON_INFORMATION, MessageBox.ICON_WARNING, MessageBox.ICON_ERROR, MessageBox.ICON_QUESTION, MessageBox.ICON_NONE
    '''
    BUTTONS_OK=QMessageBox.Ok #For only OK button
    BUTTONS_OK_CANCEL=QMessageBox.Ok | QMessageBox.Cancel #For both OK and Cancel buttons
    ICON_INFORMATION=QMessageBox.Information #Information Icon
    ICON_WARNING=QMessageBox.Warning #Warning icon
    ICON_ERROR=QMessageBox.Critical #Error Icon 
    ICON_QUESTION=QMessageBox.Question # Question icon
    ICON_NONE=QMessageBox.NoIcon #No icon
    def __init__(self,title,message,icon,buttons):
        super(MessageBox, self).__init__() #Invoke super class constructor
        super(MessageBox, self).setIcon(icon) #Set Icon 
        super(MessageBox, self).setText(message) #Set Message
        super(MessageBox, self).setStandardButtons(buttons) #Set buttons
        super(MessageBox, self).setWindowTitle(title) #Title

