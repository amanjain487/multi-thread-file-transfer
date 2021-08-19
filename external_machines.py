import socket
import threading
import hashlib
import os
from struct import unpack, pack
import time
import random


# request file parts which is already received partially..
def partial_file(for_failure, host, machine_details, f_path, f_name, tfs, nop):
    wrong = True
    # get file details, which server holds particular part
    download_socket = socket.socket()
    part = machine_details[1]
    proper_path = os.path.join(f_path, f_name)
    total_size = machine_details[2]
    start = machine_details[3]
    port = machine_details[0]
    try:
        # check how much bytes already received for each part
        to_check = tfs + (len(str(tfs)) * (part-1))
        while lock.locked():
            time.sleep(0.01)
            continue
        # acquire lock on file, to avoid any other thread access the same file concurrently.
        lock.acquire()
        dummy = open(proper_path, "rb")
        dummy.seek(to_check, 0)
        how_much = int(dummy.read(len(str(tfs))).decode())
        dummy.close()
        lock.release()
        if how_much == total_size:
            print("Part " + str(part) + " already received completely...")
            download_socket.close()
            return
        print("Connecting with " + str(port) + " for part " + str(part) + " of the requested file.")
        download_socket.connect((host, port))
        part_info = tfs + (len(str(tfs)) * (part - 1))
        already_received = how_much
        # try receiving the missing data
        while True:
            to_send = f_name
            sha1_hasher = hashlib.sha1(to_send.encode())
            download_socket.sendall("p".encode() + str.encode(to_send))
            sent_or_not = download_socket.recv(2048)
            if sent_or_not.decode() == "received":
                download_socket.sendall("h".encode() + sha1_hasher.digest())
                correct_or_not = download_socket.recv(2048)
                if correct_or_not.decode() == "incorrect":
                    continue
                else:
                    break
            else:
                continue
        received_size = 0
        now = how_much
        current = start + now
        required_from = now
        position = pack('>Q', required_from)
        download_socket.sendall(position)
        while True:
            leng = download_socket.recv(8)
            (length,) = unpack('>Q', leng)
            data = b""
            while len(data) < length:
                to_read = length - len(data)
                data += download_socket.recv(2048 if to_read > 2048 else to_read)
            download_socket.sendall("h".encode())
            hash_value = hashlib.sha1(data)
            server_hash = download_socket.recv(2048)
            if server_hash != hash_value.digest():
                download_socket.sendall("i".encode())
                continue
            else:
                download_socket.sendall("c".encode())
                # if "end" is received, it means complete file has been sent and received
                already_received += len(data)
                received = str(already_received)
                while len(received) != len(str(tfs)):
                    received = '0' + received
                if data != "end".encode():
                    while lock.locked():
                        time.sleep(0.01)
                        continue
                    # acquire lock on file, to avoid any other thread access the same file concurrently.
                    lock.acquire()
                    with open(proper_path, "rb+") as to_write:
                        to_write.seek(current)
                        to_write.write(data)
                        to_write.seek(part_info, 0)
                        to_write.write(str(received).encode())
                    lock.release()
                    received_size += len(data)
                    current += len(data)
                else:
                    download_socket.close()
                    wrong = False
                    break
    # handle errors like
    # connection with server lost and so on
    except Exception:
        if wrong:
            print("Server " + str(port) + " is down...")
            download_socket.close()
            error_socket = socket.socket()
            # connect with different server, and fetch details about another server which holds the same part..
            port = random.randint(5041, 5090)
            while True:
                try:
                    error_socket.connect((host, port))
                    hasher = hashlib.sha1(f_name.encode())
                    error_socket.sendall("z".encode() + str.encode(f_name))
                    sent_or_not = error_socket.recv(2048)
                    if sent_or_not.decode() == "received":
                        error_socket.sendall("h".encode() + hasher.digest())
                        correct_or_not = error_socket.recv(2048)
                        if correct_or_not.decode() == "incorrect":
                            raise Exception
                        else:
                            break
                    else:
                        raise Exception
                except socket.error:
                    port = random.randint(5041, 5090)
                    continue
            # fetch the machine details
            pa = pack('>Q', int(part))
            error_socket.sendall(pa)
            pa = pack('>Q', dictt[part])
            error_socket.sendall(pa)
            dictt[part] += 1
            leng = error_socket.recv(8)
            (leng,) = unpack('>Q', leng)
            data = error_socket.recv(leng)
            machine_details = data.decode()
            mach = machine_details.split(", ")
            machine_details = []
            for ex in mach:
                machine_details.append(int(ex))
            error_socket.close()
            # start another thread with the newly fetched server and receive files
            partial_file(for_failure, host, machine_details, f_path, f_name, tfs, nop)


# download file part completely
def fetch_file(for_failure, host, machine_details, f_path, f_name, tfs, nop):
    # fetch port details and file part details
    proper_path = os.path.join(f_path, f_name)
    download_socket = socket.socket()
    port = machine_details[0]
    part = machine_details[1]
    wrong = True
    part_info = tfs + (len(str(tfs)) * (part-1))
    zeros = ['0' for _ in range(len(str(tfs)))]
    zer = ""
    zer = zer.join(zeros)
    while lock.locked():
        time.sleep(0.01)
        continue
    lock.acquire()
    with open(proper_path, "rb+") as to_write:
        to_write.seek(part_info, 0)
        to_write.write(str(zer).encode())
    lock.release()
    already_received = 0
    print("Connecting with " + str(port) + " for part " + str(part) + " of the requested file.")

    # try connecting with server and receiving the file
    try:
        download_socket.connect((host, port))
        while True:
            to_send = f_name
            sha1_hasher = hashlib.sha1(to_send.encode())
            download_socket.sendall("d".encode() + str.encode(to_send))
            sent_or_not = download_socket.recv(2048)
            if sent_or_not.decode() == "received":
                download_socket.sendall("h".encode() + sha1_hasher.digest())
                correct_or_not = download_socket.recv(2048)
                if correct_or_not.decode() == "incorrect":
                    continue
                else:
                    break
            else:
                continue
        received_size = 0
        start = machine_details[3]
        current = start
        # start receiving blocks sent by server
        while True:
            leng = download_socket.recv(8)
            (length,) = unpack('>Q', leng)
            data = b""
            while len(data) < length:
                to_read = length - len(data)
                data += download_socket.recv(2048 if to_read > 2048 else to_read)
            download_socket.sendall("h".encode())
            hash_value = hashlib.sha1(data)
            server_hash = download_socket.recv(2048)
            if server_hash != hash_value.digest():
                download_socket.sendall("i".encode())
                continue
            else:
                download_socket.sendall("c".encode())
                # if "end" is received, it means complete file has been received
                already_received += len(data)
                received = str(already_received)
                while len(received) != len(str(tfs)):
                    received = '0' + received
                if data != "end".encode():
                    while lock.locked():
                        time.sleep(0.01)
                        continue
                    lock.acquire()
                    with open(proper_path, "rb+") as to_write:
                        to_write.seek(current)
                        to_write.write(data)
                        to_write.seek(part_info, 0)
                        to_write.write(str(received).encode())
                    lock.release()
                    received_size += len(data)
                    current += len(data)
                else:
                    download_socket.close()
                    wrong = False
                    break
    # handle errors like
    # connection with server failed
    except Exception:
        if wrong:
            print("Server " + str(port) + " is down...")
            download_socket.close()
            error_socket = socket.socket()
            # connect with different port and start different thread with that server
            port = random.randint(5041, 5090)
            while True:
                try:
                    error_socket.connect((host, port))
                    hasher = hashlib.sha1(f_name.encode())
                    error_socket.sendall("z".encode() + str.encode(f_name))
                    sent_or_not = error_socket.recv(2048)
                    if sent_or_not.decode() == "received":
                        error_socket.sendall("h".encode() + hasher.digest())
                        correct_or_not = error_socket.recv(2048)
                        if correct_or_not.decode() == "incorrect":
                            raise Exception
                        else:
                            break
                    else:
                        raise Exception
                except socket.error:
                    port = random.randint(5041, 5090)
                    continue
            pa = pack('>Q', int(part))
            error_socket.sendall(pa)
            pa = pack('>Q', dictt[part])
            error_socket.sendall(pa)
            dictt[part] += 1
            leng = error_socket.recv(8)
            (leng,) = unpack('>Q', leng)
            data = error_socket.recv(leng)
            machine_details = data.decode()
            mach = machine_details.split(", ")
            machine_details = []
            for ex in mach:
                machine_details.append(int(ex))
            error_socket.close()
            fetch_file(for_failure, host, machine_details, f_path, f_name, tfs, nop)


hhost = '127.0.0.1'
pport = random.randint(5041, 5090)
lock = threading.Lock()
file_found = False

while True:
    client_socket = socket.socket()
    file_name = input('Enter File Name: ')
    try:
        client_socket.connect((hhost, pport))
        dictt = {}
        while True:
            while True:
                too_send = file_name
                hashh = hashlib.sha1(too_send.encode())
                client_socket.sendall("f".encode() + str.encode(too_send))
                sent_or_nott = client_socket.recv(2048)
                if sent_or_nott.decode() == "received":
                    client_socket.sendall("h".encode() + hashh.digest())
                    correct_or_nott = client_socket.recv(2048)
                    if correct_or_nott.decode() == "incorrect":
                        continue
                    else:
                        break
                else:
                    continue
            file_details = client_socket.recv(1024)
            file_details = file_details.decode()
            file_details = file_details[:]
            if file_details == "missing":
                print("File not found in server....")
                print("Please request for different file...")
                client_socket.close()
            else:
                file_found = True
            if file_found:
                # file_details = file_details.split(", ", 1)[1]
                no_of_parts = file_details.split(", ", 1)[0]
                no_of_parts = int(no_of_parts)
                machine_detailss = file_details.split(", ", 1)[-1][3:-3]
                machine_list = machine_detailss.split(")', '(")
                proper_machine_list = []
                total_file_size = 0
                for machine in machine_list:
                    machine_row = []
                    machine = machine.split(", ")
                    for item in machine:
                        machine_row.append(int(item.strip()))
                    proper_machine_list.append(machine_row)
                # client_socket.close()
                for machine in proper_machine_list:
                    total_file_size += machine[2]
                #file_path = r"/home/peace/Desktop"  
                file_path = input("Enter the Path where you want to download : ")
                file_fetching_threads = []
                proper_pathh = os.path.join(file_path, file_name)
                if not os.path.exists(proper_pathh):
                    dummmy = open(proper_pathh, "wb+")
                    dummmy.close()
                    for machine in proper_machine_list:
                        dictt[machine[1]] = 1
                        file_fetching = threading.Thread(target=fetch_file,
                                                         args=(
                                                             client_socket, '127.0.0.1', machine, file_path,
                                                             file_name, total_file_size, no_of_parts))
                        file_fetching_threads.append(file_fetching)
                        file_fetching.start()
                    for z in file_fetching_threads:
                        z.join()
                else:
                    print("Checking for already received file and its parts...")
                    if os.stat(str(proper_pathh)).st_size > total_file_size:
                        for machine in proper_machine_list:
                            dictt[machine[1]] = 1
                            file_fetching = threading.Thread(target=partial_file,
                                                             args=(
                                                                 client_socket, '127.0.0.1', machine, file_path,
                                                                 file_name, total_file_size, no_of_parts))
                            file_fetching_threads.append(file_fetching)
                            file_fetching.start()
                        for z in file_fetching_threads:
                            z.join()
                break
        print("File Received successfully....")
        f = open(proper_pathh, "rb+")
        f.truncate(total_file_size)
        f.close()
        _ = input("Press Enter to exit...")
        break

    except Exception as e:
        print(str(e))
        if file_found:
            pport = random.randint(5041, 5090)
        continue
client_socket.close()
