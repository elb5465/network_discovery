#!/usr/bin/env python
# -------- USING THE SHEBANG ABOVE We can redirect the compiler to the Python executable that runs scripts.

# -------- Below code allows python script to be executable...
# chmod +x myecho.py
# -------- Below code removes extension to make it look like a cmd-line tool.
# Then doing "mv ip_search.py ip_search"
# -------- First, you need to create the ~/bin directory:
# mkdir -p ~/bin
# -------- Next, copy your script to ~/bin:
# cp myecho ~/bin
# -------- Finally, add ~/bin to your PATH:
# export PATH=$PATH":$HOME/bin"
# -------- Can use below to see path
# print(os.sys.path)
# -------- [ TAKEN FROM  https://dbader.org/blog/how-to-make-command-line-commands-with-python ]

# ------------------ SNIPPET ALLOWS YOU TO SEND SHELL COMMANDS AND RETRIEVE THE RESPONSE ---------------------
# import subprocess
# cmd = 'echo "hello world"'
# returned_output = subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT)
# print((returned_output).decode('utf-8'))

import json
import sys
import os
import subprocess 
import socket    
from mac_vendor_lookup import MacLookup

def send_to_cmdLine(cmd):
    return subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT)

def get_OS():
    os_name = os.name
    if (os_name == "nt"):
        print("Windows OS Detected.")
        return "Windows"
    elif (os_name == "posix"):
        print("Mac/Linux OS Detected")
        return "Linux"
    else:
        print("{} is unrecognized".format(os.name))
        return "Other"


def get_ipHost_info():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is: " + hostname)    
    print("Your Computer IP Address is: " + IPAddr) 
    return hostname, IPAddr

# ---------- Use below line before any code if running this as a standalone script that is not used by other modules ---------
# if __name__ == "__main__":
#------------------------------------------------------------------------------------------------------------------



#From testing on Mac, cmd line response is decoded already, but Windows still needs to be decoded.
cmd_response = send_to_cmdLine("arp -a")
if get_OS()=="Windows":
    cmd_response = cmd_response.decode('utf-8')
print(cmd_response)

#parse the list and filter out the words that are irrelevant
parsed_list = str(cmd_response).split()
noNoWords = ["Interface:", "Internet", "Address", "---", "Physical", "Type"]
parsed_list = list(filter(lambda x: (x not in noNoWords) and ("0x" not in x), parsed_list))

cnt = 0
while len(parsed_list) > cnt+1:
    #get rid of heading IP.
    if (parsed_list[cnt+1]) and ("." in (parsed_list[cnt] and parsed_list[cnt+1])) and (not parsed_list[cnt].isalpha()):
        print(parsed_list[cnt])
        parsed_list.remove(parsed_list[cnt])
    cnt += 1

# print(parsed_list)

# Key:    the vendor name of the MAC address.
# Value:  a list of devices from that vendor.
network_dict = {}
# Key:    the fqdn of the IP address.
# Value:  the ip, mac, static/dynamic, etc.
device_dict = {}
 
idx = 0
name = "undefined"
ip_mac_type = []
static_addrs = []
mac_name = ""

for i in parsed_list:
    ip_mac_type.append(i) 

    #if list is full for the trio, then add it to the dictionary and restart the process with the next three
    if len(ip_mac_type)%3==0:

        #ignore and add to separate list if of static type.
        if ("static" in ip_mac_type):
            static_addrs.append(ip_mac_type)
        
        #Otherwise, if its dynamic type...
            #get the fqdn of the IP.
            #lookup MAC addr vendor name.
            #add device info to device dictionary
            #add device dicts to network dict with vendor name
        else:
            with open('network_scan_results.JSON') as json_file:
                data = json.load(json_file)
                # print(data)

            if ip_mac_type[0] in str(data):
                pass
            else:
                name = socket.getfqdn(ip_mac_type[0])
                mac_name = MacLookup().lookup(ip_mac_type[1])
                device_dict[name] = ip_mac_type

                
                if mac_name in network_dict:
                    network_dict[mac_name].update({name: device_dict[name]})
                else:
                    network_dict[mac_name] = device_dict
                
                #reset device dict so it doesn't keep growing
            device_dict = {}

        #reset trio list.
        ip_mac_type = []

print("\nNETWORK DICTIONARY: ")
print(network_dict)
print("\nSTATIC LIST ADDRESSES: ")
print(static_addrs)

formatted_json_network_results = json.dumps(network_dict, indent = 8, sort_keys=True)
print(formatted_json_network_results)

network_scan_results = open("network_scan_results.json", "w+")
if formatted_json_network_results != {}:
    network_scan_results.write(formatted_json_network_results)
network_scan_results.close()


        

