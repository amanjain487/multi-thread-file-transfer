import socket
import threading
import sys
import csv
import hashlib
from struct import pack, unpack


# function for each client which will connect simultaneously
def client_threads(connection, port):
    while True:
        # check connection and identify what the request from client
        # 1. File details
        # 2. Actual file contents completely
        # 3. Partial file contents
        data = connection.recv(4096)
        request_type = data[0:1].decode()
        connection.sendall(str.encode("received"))
        hash_value = connection.recv(2048)
        hash_value = hash_value[1:]
        hasher = hashlib.sha1(data[1:])
        # use hashing to check if the message sent is received properly or not
        if hasher.digest() != hash_value:
            connection.sendall(str.encode("incorrect"))
            continue
        else:
            connection.sendall(str.encode("correct"))
            break

    f = ""
    # retrieve file parts/file details
    if request_type == "f":
        # fetch file details from file_fileparts.txt file and send the information to client
        file_name = data.decode()[1:]
        fileparts = open("files_fileparts.txt", "r")
        reader = csv.reader(fileparts, delimiter="\t")
        # perform the required formatting
        sent = False
        for file in reader:
            if file[0] == file_name:
                file_details = file[1] + ", "
                machine_list = []
                f = file[2][2:-2]
                f = f.split('), (')
                for z in range(int(file[1])):
                    machine_list.append("(" + str(f[z * 5]) + ")")
                file_details += str(machine_list)
                # send the file details
                connection.sendall(str.encode(str(file_details)))
                connection.sendall(str.encode(""))
                print("File details of " + str(file_name) + " sent successfully...")
                sent = True
                break
        # if file not found, send missing message
        if not sent:
            connection.sendall(str.encode(str("missing")))
            connection.sendall(str.encode(""))
            print(str(file_name) + " requested, but not found...")

    # get different server details for a particular file part, if server goes down.
    if request_type == "z":
        # fetch file details and which part of file is required
        file_name = data.decode()[1:]
        fileparts = open("files_fileparts.txt", "r")
        reader = csv.reader(fileparts, delimiter="\t")
        # get other server list which has that file part
        for file in reader:
            if file[0] == file_name:
                print(file[1])
                f = file[2][2:-2]
                f = f.split('), (')
        pa = connection.recv(8)
        (part,) = unpack('>Q', pa)
        pa = connection.recv(8)
        (attempt_number,) = unpack('>Q', pa)
        machine_list = str(f[((part - 1) * 5) + attempt_number])
        leng = pack('>Q', len(machine_list))
        print(machine_list)
        # send the details of a machine holding that part other than one which is already down
        connection.sendall(leng)
        connection.sendall(machine_list.encode())
        print("Details of part " + str(part) + " of " + str(file_name) + " sent successfully...")

    # send actual contents of file requested
    if request_type == "d":
        # get file details
        file_name = data.decode()[1:]
        to_send = open('Internal_Machines/d' + str(port) + "/" + file_name, "rb")
        block_size = 500000
        data = to_send.read(block_size)
        # start sending files block by block
        sent = 0
        while len(data) > 0:
            while True:
                sha1_hasher = hashlib.sha1(data)
                length = pack('>Q', len(data))
                connection.sendall(length)
                connection.sendall(data)
                sent += len(data)
                print(sent)
                _ = connection.recv(2048)
                connection.sendall(sha1_hasher.digest())
                dummy = connection.recv(2048)
                if dummy.decode() == "c":
                    data = to_send.read(block_size)
                    break
                else:
                    continue
        to_send.close()
        # send a message to notify that complete part sent
        while True:
            data = "end".encode()
            length = pack('>Q', len(data))
            connection.sendall(length)
            connection.sendall(data)
            sha1_hasher = hashlib.sha1("end".encode())
            _ = connection.recv(2048)
            connection.sendall(sha1_hasher.digest())
            data = connection.recv(2048)
            if data.decode() == "c":
                break
            else:
                continue
        print(str(file_name) + " sent successfully...")

    # request partial file
    # when certain part of file is previously sent, to avoid resending that...
    elif request_type == "p":
        # determine file details and amount of byte sent previously
        file_name = data.decode()[1:]
        to_send = open('Internal_Machines/d' + str(port) + "/" + file_name, "rb")
        block_size = 500000
        f = connection.recv(8)
        (from_where,) = unpack('>Q', f)
        to_send.seek(from_where, 0)
        data = to_send.read(block_size)
        # start sending remaining part
        while len(data) > 0:
            while True:
                sha1_hasher = hashlib.sha1(data)
                length = pack('>Q', len(data))
                connection.sendall(length)
                connection.sendall(data)
                _ = connection.recv(2048)
                connection.sendall(sha1_hasher.digest())
                dummy = connection.recv(2048)
                if dummy.decode() == "c":
                    data = to_send.read(block_size)
                    break
                else:
                    continue
        to_send.close()
        # send a message to notify that complete part sent
        while True:
            data = "end".encode()
            length = pack('>Q', len(data))
            connection.sendall(length)
            connection.sendall(data)
            sha1_hasher = hashlib.sha1("end".encode())
            _ = connection.recv(2048)
            connection.sendall(sha1_hasher.digest())
            data = connection.recv(2048)
            if data.decode() == "c":
                break
            else:
                continue
        print(str(file_name) + "sent successfully...")
    connection.close()


# change host and port details from here
host = '127.0.0.1'
p = int(sys.argv[1])
# create socket
server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
thread_count = 0
# bind socket
try:
    server_socket.bind((host, p))
    print("Server with port number " + str(p) + " started...")
    server_socket.listen(5)
except socket.error as e:
    print(str(e))

# wait for client connection request
while True:
    print("Waiting for Client Request...")
    client, address = server_socket.accept()
    print("Server " + str(p) + ' - Connected to: ' + address[0] + ':' + str(address[1]))
    # start a thread with the connected client, and start listening for other clients....
    client_thread = threading.Thread(target=client_threads, args=(client, p))
    client_thread.start()
# server_socket.close()
