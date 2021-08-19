import os

# open 50 terminals
for i in range(5041, 5091):
    my_server = os.system("(gnome-terminal --title=" + str(i) + " -- python3 server_instance.py " + str(i) + "); sleep 0.2; xdotool windowminimize $(xdotool search --name " + str(i) + "|head -1)")
