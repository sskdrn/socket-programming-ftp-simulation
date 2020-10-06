from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
from RenameDialog import Ui_RenameDialog

class RenameDialogBox(QDialog):
    def __init__(self,main_window_object,file_name,*args,**kwargs):
        super(RenameDialogBox,self).__init__(*args, **kwargs)
        self.ui=Ui_RenameDialog()
        self.ui.setupUi(self)
        self.textEdit=self.ui.textEdit
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.setButton.clicked.connect(self.get_new_name)
        self.ui.labelFileName.setText(file_name)
        self.ui.labelFileName.adjustSize()
        self.main_window_object=main_window_object
        self.main_window_object.new_file_name="null"

    def get_new_name(self):
    		self.main_window_object.new_file_name=self.textEdit.toPlainText()
    		self.close()

