# Multiple Client - Server File Transfer System

## Under the Guidance of Damodar K Kulkarni, Asst Professor at Department of Computer Science, Pune University

## Table of Contents
- [Table of Contents]()
- [Why Multiple Server Instances?]
- [Benefits of Multiple Server Instances]
- [Description]
- [Installation/Requirements]
- [Contents]
- [Procedure to Run Demo]
- [Future Planning]
- [Contributors]

### Why Multiple Server Instances?

- To avoid failure of complete server.
- If we have only one instance, failure in that instance will result in whole service offered by server going down.

### Benefits of Multiple Server Instances

- We have duplicate file copies in many server instances.
- So, if a machine fails, client/user can still receive the file from other machine which has the same file.
- This model can still fail if all the machines go down simulataneously or one after another.
- But that scenario is practically rare when we have huge number of machines in a system.
- Since we have multiple server machines, we can have multiple clients getting service from mutiple server machines.

## Description

- It is a server system with multiple sever instances running.

- We need to create/copy/move files in each server machine before we start the server.
- A client can connect with sever and requeest a file.
- If a client is downloading the file for first time, complete file will be downloaded/transferred.
- But, if a client already has part of file received on his previous attempts and he again attempts to save file in the same directory, then only the missing file part will be transferred and not complete file again, thus reducing overhead.
  - The above feature is very useful when we want to transfer a file of size `1000 GB` and the user already has received `700 GB`, transferring that `700 GB` again is complete wastage of resources.

## Installation/Requirements

- **OS Platform**
  - Linux Distribution - Ubuntu
- **Programming Environment**
  - Python 3.8+
- **Packages**
  - xdotool
  - gnome-terminal
- **Python Libraries**
  - socket
  - threading
  - csv
  - struct
  - hashlib
  - csv

## Contents

- `SD1_SD2_Assignment`

  - `clients.sh`

    - Bash script to create new instances of client

  - `external_machines.py`

    - Python script for client instances.
    - Client request and receive file through this script.

  - `files_fileparts.txt`

    - Text file which contains details about all the files stored in the server machines.
    - Accessible by all server instances.

  - `multiple_client_server.sh`

    - Bash script to start the whole server system.
    - Load files into server machines and also start 50 instances of server.

  - `README.md`

    - The file you are reading currently. :p

  - `server.py`

    - Python script to start 50 instances of server machines.
    - Each in new gnome-terminal

  - `server_instance.py`

    - Server machine script, listens for client requests and responds to client requests.

  - `split_files_into_many_parts.py`

    - Split a file into many parts and load them into server machine instances.
    - Each part is stored in 5 machines.

## Procedure to Run Demo

1. Open a terminal in the project folder or change directory to project folder.
2. Type the following command to run the script file.

   `bash multiple_client_server.sh`

3. The execution of above command will prompt user to enter a number for how many files to split and preload in server.

   `How many files to store in your server ?`

4. Enter any number and for the specified number, enter complete path of files to load into server machines.
5. Those files will be split into many random parts and each part will be saved in 5 server machines to act as backup in case of any machine failure.

   `Enter complete path of File 1 :`

6. Once all files are loaded, `50` server instances will be started, one in each terminal.
7. If you do not wish to preload any files, simply enter 0 in step 3.
8. However, when you run the server system for firsr time, the system will not contain any preloaded files.
9. Once 50 server instances are started, a new terminal will popup, asking user to enter "start" to start a client system.

   `"Enter 'start' to initiate Client 1 or Enter 'exit' to Exit"`

10. If you enter start, a new client machine will start and it will prompt for file name to download/receive from server.
11. If the requested file is present in server, then download location will be asked and after that download/transfer will start.
12. When the above is being done, you can terminate certain server instance or client by specifying server port number or client number in the terminal in which `multiple_client_server.sh` was executed.

## Future Planning

1. Client uploads file in server.
2. Client delete files in server uploaded by him/her.
3. CLient rename files in server uploaded by him/her.

## Contributors

```text
Aman Kumar,
Machine Learning Intern at MathonGo,
Computer Science Student at Department of Computer Science, Pune University,
Email-Id - aman498jain@gmail.com
```
