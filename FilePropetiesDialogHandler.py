from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
from FilePropetiesDialog import Ui_FilePropetiesDialog

class FilePropetiesDialogBox(QDialog):
    def __init__(self,*args,**kwargs):
        super(FilePropetiesDialogBox,self).__init__(*args, **kwargs)
        self.ui=Ui_FilePropetiesDialog()
        self.ui.setupUi(self)
        self.fileOrFolder=self.ui.labelFileOrFolder
        self.fileName=self.ui.labelFileName
        self.fileSize=self.ui.labelFileSize
        self.lastModified=self.ui.labelLastModified
        self.executableFileOrFolder=self.ui.label_6
        self.executableOrEmpty=self.ui.labelExecutableOrEmpty
        self.ui.buttonOK.clicked.connect(self.close)
    
    def setLabels(self,file_info):
        isfile=file_info[3]
        if isfile:
            self.fileOrFolder.setText("File name:")
        else:
            self.fileOrFolder.setText("Folder name:")
        
        self.fileName.setText(file_info[0])
        self.fileSize.setText("{:.4f}".format(float(file_info[1]))+" MB")
        self.lastModified.setText(file_info[2])
        if isfile:
            self.executableFileOrFolder.setText("Is Executable?:")
            if file_info[0].endswith(".exe") or file_info[0].endswith(".bat"):
                self.executableOrEmpty.setText("Yes")
            else:
                self.executableOrEmpty.setText("No")
        else:
            self.executableFileOrFolder.setText("Is Empty?:")
            if file_info[4]:
                self.executableOrEmpty.setText("Yes")
            else:
                self.executableOrEmpty.setText("No")
        

        
        
    