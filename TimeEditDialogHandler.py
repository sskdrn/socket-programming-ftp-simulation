from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
from TimeEditDialog import Ui_TimeEditDialog
import datetime  # For date time operations
import time

class TimeEditDialogBox(QDialog):
    def __init__(self,main_window_object,file_name,*args,**kwargs):
        super(TimeEditDialogBox,self).__init__(*args, **kwargs)
        self.ui=Ui_TimeEditDialog()
        self.ui.setupUi(self)
        self.dateTimeEdit=self.ui.dateTimeEdit
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.setButton.clicked.connect(self.get_new_name)
        self.ui.labelFileName.setText(file_name)
        self.ui.labelFileName.adjustSize()
        self.main_window_object=main_window_object
        self.main_window_object.new_date="null"

    def get_new_name(self):
        date_time=self.dateTimeEdit.dateTime()
        to_secs=date_time.toSecsSinceEpoch()+19800
        self.main_window_object.new_date=time.strftime("%d-%m-%Y %I:%M:%S %p", time.gmtime(to_secs))
        self.close()