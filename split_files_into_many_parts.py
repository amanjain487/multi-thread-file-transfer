import os
import random
import sys
import csv

# how many arguments/file names passed
n = len(sys.argv)
# open the fileparts file
f = open("files_fileparts.txt", "r")
file_parts_tracker = open("files_fileparts.txt", "a")
csv_reader = csv.reader(f, delimiter="\t")
csv_writer = csv.writer(file_parts_tracker, delimiter="\t")

# for each file passed as argument
for i in range(1, n):
    # determine file properties like name, size using provided file path
    file_path = sys.argv[i]
    try:
        file = open(sys.argv[i], "rb")
    except:
        print("File not found...")
        continue
    original_file_size = os.stat(str(file_path)).st_size
    file_name = os.path.basename(file_path)
    # if file already in server, display and exit the loop
    is_present = False
    for row in csv_reader:
        if row[0] == file_name:
            print("File already present in server... Proceed to next file...")
            file_parts_tracker.close()
            is_present = True
            break
    if is_present:
        continue

    # capture the file partition details in a list
    file_size = original_file_size
    machines_list = []
    to_check_machines_list = []
    part_number = 0
    total_partitioned = 0
    # keep partitioning unless file size is less than one-tenth of original file size
    while file_size > 0:
        part_number += 1
        if file_size > original_file_size / 10:
            current_size = random.randint(1, file_size)
        else:
            current_size = file_size
        # make 5 copies of each part
        for z in range(5):
            internal_machine = random.randint(5041, 5090)
            while internal_machine in to_check_machines_list:
                internal_machine = random.randint(5041, 5090)
            machines_list.append(tuple(
                [internal_machine, part_number, current_size, total_partitioned, total_partitioned + current_size]))
            to_check_machines_list.append(internal_machine)
            directory = "d" + str(internal_machine)
            if not os.path.exists('Internal_Machines/' + directory):
                os.makedirs('Internal_Machines/' + directory)
            to_write = open('Internal_Machines/' + directory + "/" + file_name, "wb")
            file.seek(total_partitioned, os.SEEK_SET)
            to_write.write(file.read(current_size))
            to_write.close()
        file_size = file_size - current_size
        total_partitioned = total_partitioned + current_size
    # save all the file partition details in a file accessible by all servers
    file_details = [file_name, part_number, machines_list]
    csv_writer.writerow(file_details)
file_parts_tracker.close()
