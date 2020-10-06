from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
from AboutDialog import Ui_AboutDialog

class AboutDialogBox(QDialog):
    def __init__(self,*args,**kwargs):
        super(AboutDialogBox,self).__init__(*args, **kwargs)
        self.ui=Ui_AboutDialog()
        self.ui.setupUi(self)
    