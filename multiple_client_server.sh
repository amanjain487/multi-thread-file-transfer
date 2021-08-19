#!/bin/bash
export DISPLAY=:0
clear
xdotool getactivewindow windowmove 0 0 windowsize 800 550
echo "How many files to store in your server ? "
read number_of_files

for ((counter= 1; counter<=number_of_files; counter++ ))
do
  echo "Enter complete path of File $counter : "
  # shellcheck disable=SC2162
  read file_path
  python3 split_files_into_many_parts.py "$file_path"
done

printf "\nStarting 50 servers...\n"
python3 server.py
echo "Servers are ready.... Head to 'Start Clients here' terminal to initiate clients"

gnome-terminal --title="Start Clients here" -- bash clients.sh
sleep 0.1
xdotool search --name "Start Clients here" windowmove 10 510 windowsize 800 550


valid=True
while [ $valid ]
do
  sleep 3
  x=$(xdotool search --name "Client 1")
  if [[ $x ]]; then
    break
  fi
done

while [ $valid ]
do
  echo "Enter port no to get that server down or client number to get client down..."
  echo "Server port numbers are 5040 to 5090..."
  # shellcheck disable=SC2162
  read port_no
  if [ $port_no -gt 5040 -a $port_no -lt 5091 ]; then
    xdotool search --name "$port_no" windowclose
  else
    xdotool search --name "Client $port_no" windowclose
  fi
done

