# Socket programming - Server
import socket
import os  # For directory related operations
import pickle  # To send/recieve data in stream (Convert data to bytes object)
import datetime  # For date time operations
import time  # For date time operations
import stat  # To set read-only access to the files
from AES import AESCipher

class FTPServer:
    def __init__(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((socket.gethostname(), 2001))
        self.server_socket.listen(5)
        self.aes=AESCipher("serverclientpassword")
        print("Server started!!")
        self.connection, self.address = self.server_socket.accept()
        self.dirpath=""
        print("Connection recieved from ", self.address[0])
        self.accept_commands()

    def list_files(self, dirpath):
        '''
        Takes a directory path (string) as an argument.
        if a directory in the given path doesn't exist:
            An encoded string saying such a directory doesn't exist is sent to the client.
        else:
            A two dimensional list, is sent to the client. Each inner list contains three strings and a boolean value- Name of each file,
            their size in MB, their date modified and whether are they a subdirectory.
            Example: [ ["Example1.pdf", "1.2548", "01-01-1970 12:00:00 AM", False], 
                    ["Example2.jpg", "1.2548", "01-01-1970 12:00:00 AM", False]
                    ["Documents", "1.2548", 01-01-1970 12:00:00 AM", True] ..]
        '''

        if os.path.isdir(dirpath):  # To check whether the string points to a valid directory

            # Returns list of files names and sub directory
            file_name_list = os.listdir(dirpath+"\\")
            self.dirpath=dirpath
            files_list = []  # Empty file list
            for file_name in file_name_list:

                file_record = []  # Empty record (Inner list)

                file_record.append(file_name)  # Add file name to the list
                # Get the full file/directoy path by appending it to intial directory
                file_path = dirpath +"\\"+file_name

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

            files_list = pickle.dumps(files_list)  # Encode the main file list
            self.connection.send(files_list)  # Send the main file list
        else:
            # Send the message after encoding
            self.connection.send(pickle.dumps("Directory doesn't exist"))

    def download_file(self, file_path):
        '''
        Takes the file path (string) as an arguement and checks whether a valid file exists.
        If the file is present, it's contents are sent as a bytes object.
        An error message is sent otherwise.

        '''
        try:

            # Open the file in the Read and Binary mode
            with open(file_path, 'rb') as file_object:

                # Read the file contents and store as binary format
                file_contents = file_object.read()
                # Send them to the client
                self.connection.send(pickle.dumps(file_contents))

        except FileNotFoundError:  # File doesn't exist

            self.connection.send(pickle.dumps(
                "Your requested file does not exist. "))

        except PermissionError:  # Sufficient Permissions not enough

            self.connection.send(pickle.dumps(
                "Permission is not available to download"))

        except:  # Some other error

            self.connection.send(pickle.dumps(
                "An error occured while trying to download your file."))

    def upload_file(self, file_path):
        '''
        Takes the path as an arguement.
        If the file is not present, the file contents are recieved from client as bytes object 
        and a new file is created with the same name. 
        An error message if already a file with same name exists or some other error occurs.

        '''
        try:
            file_name=file_path[file_path.rindex('\\'):]
            new_file_path=self.dirpath+file_name

            file_contents = pickle.loads(
                self.get_data_from_client())  # Get file contents
            # Create a file with the given path if the file doesn't exist
            with open(new_file_path, 'xb') as file_object:
                # Write the contents to the file
                file_object.write(file_contents)
            # Send success message
            self.connection.send(pickle.dumps("Upload Successful."))

        except FileExistsError:  # Another file already exists with the same name
            self.connection.send(pickle.dumps(
                "File with same name already exists."))
        except:  # Someother error
            self.connection.send(pickle.dumps(
                "An error occured while trying to upload your file."))

    def delete_file(self, file_path):
        '''

        Takes the file path as an arguement.
        If the file is present, it is deleted .
        An error message if the file does not exist or some other error occurs.

        NOTE: This does NOT work for directories. To remove directories, use remove_directory() instead.

        '''

        try:
            os.remove(file_path)  # Remove file
            # Send success message
            self.connection.send(pickle.dumps("File deleted!!"))
        except FileNotFoundError:  # File does not exist
            self.connection.send(pickle.dumps("File does not exist."))

        except PermissionError:  # Permissions not available
            self.connection.send(pickle.dumps(
                "Sufficient permissions not available. Is this a directory?"))

        except:  # Some other error
            self.connection.send(pickle.dumps(
                "There was some error in performing delete operation."))

    def remove_directory(self, dir_path):
        '''

        Takes the file path as an arguement.
        If the directory is present, it is removed.
        The directory to be removed MUST be empty.
        An error message if the directory does not exist, directory is not empty or some other error occurs.

        NOTE: This does NOT work for files. To remove directories, use delete_file() instead.

        '''
        try:
            os.rmdir(dir_path)  # Remove directory
            # Send success message
            self.connection.send(pickle.dumps("Directory removed!"))

        except FileNotFoundError:  # Directory does not exist
            self.connection.send(pickle.dumps(
                "Specified directory does not exist."))

        except PermissionError:  # Permissions not available
            self.connection.send(pickle.dumps(
                "Sufficient permissions not available."))

        except NotADirectoryError:
            self.connection.send(pickle.dumps(
                "The path does not lead to a valid directory. Is it a file?"))
        except OSError:  # Directory not empty
            self.connection.send(pickle.dumps(
                "The specified directory is not empty."))

        except:  # Some other error
            self.connection.send(pickle.dumps(
                "There was some error in performing delete operation."))

    def check_file_or_directory(self, file_path):
        '''

        Takes the file path as an arguement.
        Sends a message to the client, stating whether the path denotes a file or a directory.
        An error message is sent if any error occurs.

        '''
        try:
            if os.path.isfile(file_path):  # If the path denotes to a file
                self.connection.send(pickle.dumps("The path denotes a file."))
            elif os.path.isdir(file_path):  # If the path denotes a directory
                self.connection.send(pickle.dumps(
                    "The path denotes a directory."))
            else:
                self.connection.send(pickle.dumps(
                    "No such file/directory exists."))
        except:  # If any exception occurs
            self.connection.send(pickle.dumps(
                "Some error has occured in processing your request."))

    def rename_file_or_directory(self, file_path, new_name):
        ''' 
        Takes a file/directory path and a string for new name as an arguement and renames the specified 
        file or directory.
        An error message is thrown if the file doesn't exist or any other error occurs.

        '''
        try:
            root_dir=file_path[0:file_path.rindex('\\')+1]
            new_path=root_dir+new_name
            os.rename(file_path, new_path)  # Rename file/folder
            # Send success message
            self.connection.send(pickle.dumps("Rename Successfull!!"))

        except FileNotFoundError:  # File/Directory does not exist
            self.connection.send(pickle.dumps(
                "Specified file/directory does not exist."))

        except Exception as e:  # If any exception occurs
            self.connection.send(pickle.dumps(
                "Some error has occured in processing your request."))

    def set_file_read_only(self, file_path):
        '''
        Takes a file/directory path as an arguement and sets its 'read only' attribute to true.

        '''
        try:
            ''' 
             os.chmod() changes the mode of the file to the one specified as second argument
             Modes:-
             stat.S_IREAD : Read by owner.
             stat.S_IRWXU : Read, write, and execute by owner
             stat.S_IRWXG : Read, write, and execute by group
             stat.S_IRGRP : Read by group
             stat.S_IRWXO : Read, write, and execute by others.
             stat.S_IROTH : Read by others

             '''

            # Set file to read only by owner/group and others
            os.chmod(file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

            # Send success message
            self.connection.send(pickle.dumps(
                "File/Directory set to read-only!"))

        except FileNotFoundError:  # File/Directory does not exist
            self.connection.send(pickle.dumps(
                "Specified file/directory does not exist."))

        except:  # If any exception occurs
            self.connection.send(pickle.dumps(
                "Some error has occured in processing your request."))

    def clear_file_read_only(self, file_path):
        '''
        Takes a file/directory path as an arguement and sets its 'read only' attribute to false.

        '''
        try:
            ''' 
             os.chmod() changes the mode of the file to the one specified as second argument
             Modes:-
             stat.S_IREAD : Read by owner.
             stat.S_IRWXU : Read, write, and execute by owner
             stat.S_IRWXG : Read, write, and execute by group
             stat.S_IRGRP : Read by group
             stat.S_IRWXO : Read, write, and execute by others.
             stat.S_IROTH : Read by others

            '''
            # Set file/directory to read, write and executable  by owner,group and others
            os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            # Send success message
            self.connection.send(pickle.dumps(
                "File/Directory set to read-write!"))

        except FileNotFoundError:  # File/Directory does not exist
            self.connection.send(pickle.dumps(
                "Specified file/directory does not exist."))

        except:  # If any exception occurs
            self.connection.send(pickle.dumps(
                "Some error has occured in processing your request."))

    def get_last_modified_time(self, file_path, return_the_value=False):
        '''
        Gets the file path as an arguement, and sends the last modified time in the format DD-MM-YYYY hh:mm:ss AM/PM 
        (Such as "01-01-1970 12:00:00 AM").
        An error message is sent to the client if file is not present or some other error occurs.

        '''
        try:
            '''
                os.path.gmtime(file_path) returns the time modified in seconds
                time.gmtime(time) returns a time object with seconds
                time.strftime(time_format,time_object) returns a string of the time object in the specified format
                (DD-MM-YYYY hh:mm:ss AM/PM in this case)

            '''
            last_modified_time = time.strftime(
                "%d-%m-%Y %I:%M:%S %p", time.gmtime(os.path.getmtime(file_path)))
            # Send the time as a string
            if return_the_value:
                return last_modified_time
            else:
                self.connection.send(pickle.dumps(last_modified_time))

        except FileNotFoundError:  # File/Directory not found
            if return_the_value:
                return "File/Directory not found."
            else:
                self.connection.send(pickle.dumps("File/Directory not found."))

        except:  # Some other error
            if return_the_value:
                return "Some error occured while processing your request."
            else:
                self.connection.send(pickle.dumps(
                    "Some error occured while processing your request."))

    def set_last_modified_time(self, file_path, new_time):
        '''
            Takes the file path and new time as a string in the format  DD-MM-YYYY hh:mm:ss AM/PM (Such as "01-01-1970 12:00:00 AM").
            Sets the file's last modified time to new time.
            An error is thrown if file is not present, the string is not in specified format or any other exception occurs.
        '''
        try:
            # Convert the date time string to a datetime object
            datetime_object = datetime.datetime.strptime(
                new_time, "%d-%m-%Y %I:%M:%S %p")
            # Returns a time.struct_time object from datetime object
            time_object = datetime_object.timetuple()
            # Convert time_object to seconds (float value)
            modified_time = time.mktime(time_object)

            # This may confuse you, but datetime objects and time.struct_time objects are different.
            # The latter is passed as an argument to the function that modifies the last modified date.

            # There is another attribute to a file called "Accessed time"
            accessed_time = modified_time

            # According to logic, A file must be accessed before its modified. Hence, both are same.
            # Set the new modified time
            os.utime(file_path, (accessed_time, modified_time))
            self.connection.send(pickle.dumps("Modified time changed succesfully!"))

        except ValueError:  # new_time string not in specified format
            self.connection.send(pickle.dumps(
                "The time is not in the correct format."))

        except FileNotFoundError:  # File/directory not found
            self.connection.send(pickle.dumps("File/Directory not found."))

        except:  # Any other error
            self.connection.send(pickle.dumps(
                "Some error occured while processing your request."))

    def check_if_executable(self, file_path, return_the_value=False):
        ''' 
        Takes a file path as an argument and checks whether its an executable file or not.
        An error message is sent if file not found or some other exception occurs.

        '''
        try:
            if os.path.isdir(file_path):  # If file is directory
                if return_the_value:
                    return False
                else:
                    self.connection.send(pickle.dumps(
                        "The path is a directory, not a file"))
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
                    if return_the_value:
                        return True
                    else:
                        self.connection.send(pickle.dumps(
                            "The file is an executable file."))
                else:
                    if return_the_value:
                        return False
                    else:
                        self.connection.send(pickle.dumps(
                            "The file is not an executable file."))

        except FileNotFoundError:  # File/Directory not found
            if return_the_value:
                return False
            else:
                self.connection.send(pickle.dumps("File/Directory not found."))

        except:  # Some other error
            if return_the_value:
                return False
            else:
                self.connection.send(pickle.dumps("Some error occured while processing your request."))

    def get_exec_empty(self, file_path):
        '''
        Takes the file path as an arguement.
        if the path is a file then a list is returned in this order [Is File, Is Executable]
        Example: [True,False]
        if the path is a directory then a list is returned in this order [Is File, Is Empty]
        [False,True]
        '''
        try:
            if os.path.isfile(file_path):
                details = []
                details.append(True)
                details.append(self.get_last_modified_time(file_path, True))
                details.append(self.check_if_executable(file_path, True))
                self.connection.send(pickle.dumps(details))
            elif os.path.isdir(file_path):
                details = []
                details.append(False)
                details.append(self.get_last_modified_time(file_path, True))
                details.append(True if len(os.listdir(file_path))==0 else False)
                self.connection.send(pickle.dumps(details))
            else:
                self.connection.send(pickle.dumps("The path is invalid."))
        except:
            self.connection.send(pickle.dumps("There is an error in processing your request."))

    def accept_commands(self):
        while True:
            data = self.aes.decrypt(pickle.loads(self.get_data_from_client())).split("@")
            command = data[0]
            if command == "LIST":
                dirpath = data[1]
                self.list_files(dirpath)
            elif command == "DOWNLOAD":
                dirpath = data[1]
                self.download_file(dirpath)
            elif command == "UPLOAD":
                file_path = data[1]
                self.connection.send(pickle.dumps("OK"))
                self.upload_file(file_path)
            elif command == "SETREADONLY":
                file_path = data[1]
                self.set_file_read_only(file_path)
            elif command == "SETLASTMODIFIED":
                file_path=data[1]
                self.connection.send(pickle.dumps("OK"))
                new_time=pickle.loads(self.get_data_from_client())
                self.set_last_modified_time(file_path,new_time)
            elif command == "RENAME":
                file_path=data[1]
                self.connection.send(pickle.dumps("OK"))
                new_name=pickle.loads(self.get_data_from_client())
                self.rename_file_or_directory(file_path,new_name)
            elif command == "PROPETIES":
                file_path=data[1]
                self.get_exec_empty(file_path)
            elif command == "DELETE":
                file_path=data[1]
                if os.path.isfile(file_path):
                    self.delete_file(file_path)
                else:
                    self.remove_directory(file_path)
            elif command == "CLOSE":
                self.connection.send(pickle.dumps("Server stopped!"))
                self.connection.close()
                print("Thank you for using our server! Have a wonderful day!")
                break
            else:
                self.connection.send(pickle.dumps("Wrong Command"))

    def get_data_from_client(self):
        data = b''  # Initially no data
        packet_size = 4096  # Sample packet size for recv(). Can be changed.
        '''
        Since the amount of content of the file is unknown, the following loop, collects data from
        client until EOF is reached.

        '''
        while True:  # Loop until EOF
            packet_content = self.connection.recv(
                packet_size)  # Get 4096 bytes from client
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


server = FTPServer()
