# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RenameDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RenameDialog(object):
    def setupUi(self, RenameDialog):
        RenameDialog.setObjectName("RenameDialog")
        RenameDialog.resize(316, 251)
        self.label = QtWidgets.QLabel(RenameDialog)
        self.label.setGeometry(QtCore.QRect(90, 40, 149, 18))
        self.label.setMaximumSize(QtCore.QSize(149, 18))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.splitter = QtWidgets.QSplitter(RenameDialog)
        self.splitter.setGeometry(QtCore.QRect(70, 190, 186, 28))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.setButton = QtWidgets.QPushButton(self.splitter)
        self.setButton.setMaximumSize(QtCore.QSize(90, 28))
        self.setButton.setObjectName("setButton")
        self.cancelButton = QtWidgets.QPushButton(self.splitter)
        self.cancelButton.setMaximumSize(QtCore.QSize(90, 28))
        self.cancelButton.setObjectName("cancelButton")
        self.labelFileName = QtWidgets.QLabel(RenameDialog)
        self.labelFileName.setGeometry(QtCore.QRect(110, 80, 85, 18))
        self.labelFileName.setMaximumSize(QtCore.QSize(16777215, 18))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelFileName.setFont(font)
        self.labelFileName.setObjectName("labelFileName")
        self.textEdit = QtWidgets.QTextEdit(RenameDialog)
        self.textEdit.setGeometry(QtCore.QRect(30, 130, 261, 31))
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(RenameDialog)
        self.cancelButton.clicked.connect(RenameDialog.close)
        QtCore.QMetaObject.connectSlotsByName(RenameDialog)

    def retranslateUi(self, RenameDialog):
        _translate = QtCore.QCoreApplication.translate
        RenameDialog.setWindowTitle(_translate("RenameDialog", "Rename File/Folder"))
        self.label.setText(_translate("RenameDialog", "Rename File/Folder:-"))
        self.setButton.setText(_translate("RenameDialog", "Set"))
        self.cancelButton.setText(_translate("RenameDialog", "Cancel"))
        self.labelFileName.setText(_translate("RenameDialog", "Filename. txt"))
