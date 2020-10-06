import socket
import os  # For directory related operations
import pickle  # To send/recieve data in stream (Convert data to bytes object)
import datetime  # For date time operations
import time  # For date time operations
import stat  # To set read-only access to the files
from AES import AESCipher
class FTPClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address=""
        self.server_port=0
        self.client_directory=""
        self.server_directory=""
        self.server_connected=False
        self.aes=AESCipher("serverclientpassword")
    
    def connect_server(self,host,port):
        try:
            self.client_socket.connect((host,port))
            self.server_connected=True
            self.server_address,self.server_port=host,port
            return True
        except:
            return False
    
    def list_files_client(self,dirpath):

        '''
        if a directory in the self.client_directory string doesn't exist:
            False is returned
        else:
            A two dimensional list, is sent to the client. Each inner list contains three strings and a boolean value- Name of each file,
            their size in MB, their date modified and whether are they a subdirectory.
            Example: [ ["Example1.pdf", "1.2548", "01-01-1970 12:00:00 AM", False], 
                    ["Example2.jpg", "1.2548", "01-01-1970 12:00:00 AM", False]
                    ["Documents", "1.2548", 01-01-1970 12:00:00 AM", True] ..]
        '''

        if os.path.isdir(dirpath):  # To check whether the string points to a valid directory

            # Returns list of files names and sub directory
            file_name_list = os.listdir(dirpath)
            files_list = []  # Empty file list
            for file_name in file_name_list:

                file_record = []  # Empty record (Inner list)

                file_record.append(file_name)  # Add file name to the list
                # Get the full file/directoy path by appending it to intial directory
                file_path = dirpath +"\\"+ file_name

                # returns size of file/directory in bytes
                size_in_bytes = os.path.getsize(file_path)
                # Manual conversion of bytes to MB
                size_in_mb = (size_in_bytes/1024)/1024
                # Append size to list as a string
                file_record.append(str(size_in_mb))

                '''
                os.path.gmtime(file_path) returns the time modified in seconds
                time.gmtime(time) returns a time object with seconds
                time.strftime(time_format,time_object) returns a string of the time object in the specified format
                (DD-MM-YYYY hh:mm:ss AM/PM in this case)

                '''
                last_modified_time = time.strftime(
                    "%d-%m-%Y %I:%M:%S %p", time.gmtime(os.path.getmtime(file_path)))
                # Append the last modified time string
                file_record.append(last_modified_time)

                # Appends whether directory or not
                file_record.append(os.path.isdir(file_path))
                # Append record to the main file list
                files_list.append(file_record)
            self.client_directory=dirpath
            self.client_files_list=files_list
            return files_list     
        else:
            return "The path is not valid."

    def list_files_server(self,dirpath):
        if self.server_address=="":
            return "The client is not connected to server."
        else:
            try:
                command="LIST@"+dirpath
                command=self.aes.encrypt(command)
                self.client_socket.send(pickle.dumps(command))
                data=pickle.loads(self.get_data_from_server())
                self.server_directory=dirpath
                self.server_files_list=data
                return data
            except:
                return "The operation you requested got failed."
            
    def download_file(self,file_name):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        if os.path.isfile(file_path):
            try:
                command="DOWNLOAD@"+file_path
                command=self.aes.encrypt(command)
                self.client_socket.send(pickle.dumps(command))
                data=pickle.loads(self.get_data_from_server())
                if type(data)==str:
                    raise Exception
            except:
                return "An error occured in downloading the file."
            
            try:
                # Create a file with the given path if the file doesn't exist
                with open((self.client_directory+"\\"+file_name), 'xb') as file_object:
                    # Write the contents to the file
                    file_object.write(data)
                # Send success message
                return "File download Successfull!"

            except FileExistsError:  # Another file already exists with the same name
                return "File with same name already exists."
            except: # Someother error
                return "An error occured in downloading the file."

        else:
            return "The selected entity is not a file. Is it a folder?"
        
    def upload_file(self,file_name):
        file_path= file_path=self.client_directory+file_name if self.client_directory.endswith("\\") else self.client_directory+"\\"+file_name
        if os.path.isfile(file_path):
            command="UPLOAD@"+file_path
            command=self.aes.encrypt(command)
            self.client_socket.send(pickle.dumps(command))
            signal=pickle.loads(self.get_data_from_server()) #To get OK signal from server
            try:

                # Open the file in the Read and Binary mode
                with open(file_path, 'rb') as file_object:

                    # Read the file contents and store as binary format
                    file_contents = file_object.read()
                    # Send them to the client
                    self.client_socket.send(pickle.dumps(file_contents))
                    message= pickle.loads(self.get_data_from_server())
                    return message

            except FileNotFoundError:  # File doesn't exist

               return "Your requested file does not exist."

            except PermissionError:  # Sufficient Permissions not enough

                return  "Permission is not available to download."

            except:  # Some other error

                return "An error occured while trying to download your file."
        else:
            return "The selected entity is not a file. Is it a folder?"
    
    def rename_file_or_folder(self,file_name,new_name):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "RENAME@"+file_path
        command=self.aes.encrypt(command)
        self.client_socket.send(pickle.dumps(command))
        signal=self.get_data_from_server() #To get OK signal from server
        self.client_socket.send(pickle.dumps(new_name))
        message=pickle.loads(self.get_data_from_server())
        return message
    
    def set_read_only(self,file_name,new_name):

        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "SETREADONLY@"+file_path
        command=self.aes.encrypt(command)
        self.client_socket.send(pickle.dumps(command))
        message=pickle.loads(self.get_data_from_server())
        return message

    def set_last_modified(self,file_name,new_time):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "SETLASTMODIFIED@"+file_path
        command=self.aes.encrypt(command)
        #Encryption code
        self.client_socket.send(pickle.dumps(command))
        signal=self.get_data_from_server() #To get OK signal from server
        self.client_socket.send(pickle.dumps(new_time))
        message=pickle.loads(self.get_data_from_server())
        return message

    def get_server_file_directory_propeties(self,file_name):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "PROPETIES@"+file_path
        command=self.aes.encrypt(command)
        self.client_socket.send(pickle.dumps(command))
        lmtime_exec=pickle.loads(self.get_data_from_server())
        if type(lmtime_exec)==list:
            for file_record in self.server_files_list:
                if file_record[0]==file_name:
                    file_info=file_record[0:2]
                    break
            file_info=file_info+lmtime_exec
            file_info[2],file_info[3]=file_info[3],file_info[4]
            return file_info
        else:
            return lmtime_exec

    def get_client_file_directory_propeties(self,file_name):
        
        for file_record in self.client_files_list:
            if file_record[0]==file_name:
                file_info=file_record[0:3]
                isdir=file_record[3]
                file_info.append(False if isdir else True)
                break
        file_path= file_path=self.client_directory+file_name if self.client_directory.endswith("\\") else self.client_directory+"\\"+file_name
        if isdir:
            file_info.append(True if len(os.listdir(file_path))==0 else False)
        else:

            try:
                if os.path.isdir(file_path):  # If file is directory
                    file_info.append(False)
                else:
                    # To check whether a file can be executed, it must be given read,write and execute permissions
                    os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    '''
                    os.access() method checks whether a file can be written,read or be executed.
                    The second argument helps in checking.
                    os.R_OK: To check readability
                    os.W_OK: To check writability
                    os.X_OK : To check executability

                    '''
                    if os.access(file_path, os.X_OK):
                        file_info.append(True)
                    else:
                        file_info.append(False)

            except FileNotFoundError:  # File/Directory not found
                file_info.append(False)
            except:  # Some other error
                file_info.append(False)
            
        return file_info

    def delete_file_or_folder(self,file_name):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "DELETE@"+file_path
        command=self.aes.encrypt(command)
        self.client_socket.send(pickle.dumps(command))
        message=pickle.loads(self.get_data_from_server())
        return message

    def set_server_file_read_only(self,file_name):
        file_path=self.server_directory+file_name if self.server_directory.endswith("\\") else self.server_directory+"\\"+file_name
        command= "SETREADONLY@"+file_path
        command=self.aes.encrypt(command)
        self.client_socket.send(pickle.dumps(command))
        message=pickle.loads(self.get_data_from_server())
        return message

    def exit_client(self):
        try:
            self.client_socket.send(pickle.dumps(self.aes.encrypt("CLOSE")))
            self.client_socket.close() 
        except OSError:
            pass   

    def reset_program(self):
        self.client_socket.send(pickle.dumps(self.aes.encrypt("CLOSE")))
        self.client_socket.close() 
        self.__init__()

    def get_data_from_server(self):
        data = b''  # Initially no data
        packet_size = 4096  # Sample packet size for recv(). Can be changed.
        '''
        Since the amount of content of the file is unknown, the following loop, collects data from
        client until EOF is reached.

        '''
        while True:  # Loop until EOF
            packet_content = self.client_socket.recv(packet_size)  # Get 4096 bytes from client
            data += packet_content  # Append the recieved content to existing content
            '''
                To identify EOF, len(packet_content) < packet_size can be used
                For the final packet the size will be either 0 or some value less than 4096

                (Assume the file size is 'N' bytes, Then the total number of packets is (N/4096) + 1 packets
                with the final packet having the length N % 4096 bytes )
                
                This same approach is prefered whenever large data is recieved,

            '''
            if len(packet_content) < packet_size:  # Final packet recieved
                break
    
        return data
