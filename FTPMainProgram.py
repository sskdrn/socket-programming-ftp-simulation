from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from FTPMainWindow import Ui_FTPMainWindow
from ftpclient import FTPClient
from dialogbox import MessageBox
from AboutDialogHandler import AboutDialogBox
from RenameDialogHandler import RenameDialogBox
from FilePropetiesDialogHandler import FilePropetiesDialogBox
from TimeEditDialogHandler import TimeEditDialogBox
import pickle
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        self.ui=Ui_FTPMainWindow()
        self.ui.setupUi(self)
        self.client=FTPClient()
        self.connectButton=self.ui.connectButton
        #self.ui.textEdit_3.setText('192.168.1.5')  #for debugging purposes
        #self.ui.textEdit_4.setText('2001')
        self.connectButton.clicked.connect(self.connect_to_server)
        self.ui.goForServer.clicked.connect(self.populate_server_table)
        self.ui.goForClient.clicked.connect(self.populate_client_table)
        self.ui.actionAbout.triggered.connect(self.showAbout)
        self.ui.filePropetiesClientButton.clicked.connect(self.view_client_file_propeties)
        self.ui.filePropetiesServerButton.clicked.connect(self.view_server_file_propeties)
        self.ui.renameButton.clicked.connect(self.rename_server_file)
        self.ui.uploadbutton.clicked.connect(self.upload_file)
        self.ui.deleteButton.clicked.connect(self.delete_server_file)
        self.ui.downloadButton.clicked.connect(self.download_file)
        self.ui.setReadOnlyButton.clicked.connect(self.set_read_only)
        self.ui.actionExit.triggered.connect(self.exit_program)
        self.ui.setDateModifiedButton.clicked.connect(self.change_last_modified)
        self.ui.actionClear_All.triggered.connect(self.reset_program)

    def connect_to_server(self):
        self.addressBar=self.ui.textEdit_3
        self.portBar=self.ui.textEdit_4
        self.status_indicator_label=self.ui.connectionLabel
        host=self.addressBar.toPlainText()
        try:
            if host == "":
                raise ValueError
            host=self.addressBar.toPlainText()
            port=int(self.portBar.toPlainText())
            if self.client.connect_server(host,port):
                msgbox=MessageBox("Connection Successful",("Succesfully connected to "+host+"!"),MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                msgbox.exec()
                _translate = QtCore.QCoreApplication.translate
                self.status_indicator_label.setText(_translate("FTPMainWindow", "<html><head/><body><p><span style=\" color:#2e9449;\">Connected</span></p></body></html>"))
                self.addressBar.setEnabled(False)
                self.portBar.setEnabled(False)
                self.connectButton.setEnabled(False)
                self.setWindowTitle("FTP Client - Connected to "+host)
            else:
                msgbox=MessageBox("Connection Failed","Connection to server failed.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
                msgbox.exec()
        except ValueError:
            msgbox=MessageBox("Connection Failed","Port number entered is invalid.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def populate_server_table(self):
        dirpath=self.ui.textEdit.toPlainText()
        msg=self.client.list_files_server(dirpath)
        if type(msg) == str:
            msgbox=MessageBox("Operation Failed",msg,MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()
        else:
            file_list=msg
            self.server_files_list=file_list
            self.serverTable=self.ui.serverTable
            self.serverTable.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.serverTable.setRowCount(len(file_list))
            for i in range(len(file_list)):
                self.serverTable.setItem(i,0,QTableWidgetItem(str((i+1))))
                self.serverTable.setItem(i,1,QTableWidgetItem(file_list[i][0]))
                if file_list[i][3]:
                    self.serverTable.setItem(i,2,QTableWidgetItem("Folder"))
                else:
                    self.serverTable.setItem(i,2,QTableWidgetItem("File"))
                    header = self.serverTable.horizontalHeader()       
                    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
                    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
    
    def populate_client_table(self):

        dirpath=self.ui.textEdit_5.toPlainText()
        msg=self.client.list_files_client(dirpath)
        if type(msg) == str:
            msgbox=MessageBox("Operation Failed",msg,MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()
        else:
            file_list=msg
            self.clientTable=self.ui.clientTable
            self.clientTable.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.clientTable.setRowCount(len(file_list))
            for i in range(len(file_list)):
                self.clientTable.setItem(i,0,QTableWidgetItem(str((i+1))))
                self.clientTable.setItem(i,1,QTableWidgetItem(file_list[i][0]))
                if file_list[i][3]:
                    self.clientTable.setItem(i,2,QTableWidgetItem("Folder"))
                else:
                    self.clientTable.setItem(i,2,QTableWidgetItem("File"))
            
            header = self.clientTable.horizontalHeader()       
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    def view_client_file_propeties(self):
        try:
            selected_items=self.clientTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.client_files_list[row][0]
                file_propeties=self.client.get_client_file_directory_propeties(file_name)
                file_propeties_dialog=FilePropetiesDialogBox()
                file_propeties_dialog.setLabels(file_propeties)
                file_propeties_dialog.exec_()
        except:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()
    
    def view_server_file_propeties(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.server_files_list[row][0]
                file_propeties=self.client.get_server_file_directory_propeties(file_name)
                if type(file_propeties) == list:
                    file_propeties_dialog=FilePropetiesDialogBox()
                    file_propeties_dialog.setLabels(file_propeties)
                    file_propeties_dialog.exec_()
                else:
                    msgbox=MessageBox("Error",file_propeties,MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
                    msgbox.exec()

        except Exception:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def showAbout(self):
        about_dialog=AboutDialogBox()
        about_dialog.exec_()

    def rename_server_file(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.server_files_list[row][0]
                rename_dialog=RenameDialogBox(self,file_name)
                rename_dialog.exec_()
                if self.new_file_name == "":
                    msgbox=MessageBox("File name empty","Give a valid name for the file.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                    return
                elif self.new_file_name!='null':
                    message=self.client.rename_file_or_folder(file_name,self.new_file_name)
                    msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                    self.populate_server_table()


        except Exception:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def upload_file(self):
        try:
            selected_items=self.clientTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.client_files_list[row][0]
                if self.client.server_directory=="":
                    msgbox=MessageBox("Server directory path empty","Navigate to a directory in the server.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                else:
                    message=self.client.upload_file(file_name)
                    msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                    self.populate_server_table()
        except:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def delete_server_file(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.server_files_list[row][0]
                message=self.client.delete_file_or_folder(file_name)
                msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                msgbox.exec()
                self.populate_server_table()
        except:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def download_file(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.server_files_list[row][0]
                if self.client.client_directory=="":
                    msgbox=MessageBox("Client directory path empty","Navigate to a directory in the client.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                else:
                    message=self.client.download_file(file_name)
                    msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                    msgbox.exec()
                    self.populate_client_table()

        except:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def set_read_only(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.server_files_list[row][0]
                message=self.client.set_server_file_read_only(file_name)
                msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                msgbox.exec()
        except Exception:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def change_last_modified(self):
        try:
            selected_items=self.serverTable.selectionModel().selectedRows()
            if len(selected_items)==0:
                msgbox=MessageBox("No item selected","Please select an item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            if len(selected_items)>1:
                msgbox=MessageBox("Multiple items selected","Please select only one item in table.",MessageBox.ICON_WARNING,MessageBox.BUTTONS_OK)
                msgbox.exec()
            else:
                row=selected_items[0].row()
                file_name=self.client.server_files_list[row][0]
                time_edit_dialog=TimeEditDialogBox(self,file_name)
                time_edit_dialog.exec_()
                if self.new_date == "null":
                    pass
                else:
                    message=self.client.set_last_modified(file_name,self.new_date)
                    msgbox=MessageBox("Operation status",message,MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
                    msgbox.exec()


        except:
            msgbox=MessageBox("Error","Some error has occured in performing your requested operation.",MessageBox.ICON_ERROR,MessageBox.BUTTONS_OK)
            msgbox.exec()

    def reset_program(self):
        self.client.reset_program()
        self.ui.textEdit_3.setText('')
        self.ui.textEdit_4.setText('')
        self.ui.textEdit.setText('')
        self.ui.textEdit_5.setText('')
        self.ui.textEdit_3.setEnabled(True)
        self.ui.textEdit_4.setEnabled(True)
        self.ui.connectButton.setEnabled(True)
        self.ui.serverTable.clearContents()
        self.ui.serverTable.setRowCount(0)
        self.ui.clientTable.clearContents()
        self.ui.clientTable.setRowCount(0)
        self.setWindowTitle("FTP Client - Not connected")
        _translate = QtCore.QCoreApplication.translate
        self.status_indicator_label.setText(_translate("FTPMainWindow", "<html><head/><body><p><span style=\" color:#ff0000;\">Not connected</span></p></body></html>"))
        msgbox=MessageBox("Program reset","Program Succesfully reset!",MessageBox.ICON_INFORMATION,MessageBox.BUTTONS_OK)
        msgbox.exec()

    def closeEvent(self,event):
        self.exit_program()

    def exit_program(self):
        self.client.exit_client()
        self.close()


if __name__=="__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())