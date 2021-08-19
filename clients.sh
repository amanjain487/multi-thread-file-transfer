#!/bin/bash

echo "Start clients from here...."
echo "Warning : Starting too many clients is fine, but receiving files concurrently in many clients at once might make your system hang or crash..."
valid=True
declare -i count=1
while [ $valid ]
do
  echo "Enter 'start' to initiate Client $count or Enter 'exit' to Exit"
  # shellcheck disable=SC2162
  read input
  if [[ ( $input == "exit") || ( $input == "EXIT") || ( $input == "Exit") ]]; then
    break
  elif [[ ($input == "start" || $input == "START" ||$input == "Start") ]]; then
    gnome-terminal --title="Client $count" -- python3 external_machines.py
    sleep 0.2
    x=800
    offset=50
    xdotool search --name "Client $count" windowmove $(($x + (($count-1) * $offset)))  $((($count-1) * $offset)) windowsize 800 550
    sleep 0.2
    count+=1
    if [[ $count -eq 5040 ]]; then
      count=5091
    fi
  fi
done
read waiting
