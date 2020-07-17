import time
import sys
import os
import subprocess 
import socket  
import json
from mac_vendor_lookup import MacLookup

#----------------------- Function to send shell cmd from Python and retrieve result ------------------------
def send_to_cmdLine(cmd):
    return subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT).decode('utf-8')

#---------------------------- Function to determine OS that this is running on  ----------------------------
def get_OS():
    os_name = os.name
    if (os_name == "nt"):
        print("Windows OS Detected.\n")
        return "Windows"
    elif (os_name == "posix"):
        print("Mac/Linux OS Detected\n")
        return "Linux"
    else:
        print("{} is unrecognized".format(os.name))
        return "Other"

#---------------------------- Function to get current host IP nd name from its IP  --------------------------
def get_ipHost_info():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is: " + hostname)    
    print("Your Computer IP Address is: " + IPAddr) 
    return hostname, IPAddr

#---------------------------- Function to determine OS that this is running on  ----------------------------
"""
On Mac some MAC_addresses show up without the leading zero in front of what are 
2 digit sections, with a total of 12 numbers. MacLookup only works if that style
is followed, so this fixes any MAC_addresses that are missing those zeros.
"""
def fix_mac_addr(mac_addr):
    new = list(filter(lambda x: (x!=":") and (x!="-"), mac_addr))
    temp_str = ""
    if len(new)==11:
        i = 0
        while len(temp_str)<17:
            if mac_addr[i]==":" and mac_addr[i+2] ==":":
                temp_str += ":0"
            else:
                temp_str += mac_addr[i]
            i+=1
        # print(temp_str)
        return temp_str
    else:
        return mac_addr

def remove_win_heading(parsed_list):
    cnt = 0
    while len(parsed_list) > cnt+1:
        #get rid of heading IP.
        if (parsed_list[cnt+1]) and ("." in (parsed_list[cnt] and parsed_list[cnt+1])) and (not parsed_list[cnt].isalpha()):
            print(parsed_list[cnt])
            parsed_list.remove(parsed_list[cnt])
        cnt += 1
    return parsed_list
#-----------------------------------------------------------------------------------------------------------


def discover():
    print("-------------------------------------------------------------------------")
    #declare variables for the overall structure.
    network_dict = {}
    device_dict = {}
    device_info = []
    static_addrs = []
    name = ""
    mac_name = ""
    idx = 0

    #this is a list of words to remove that show up after parsing on Mac and Windows.
    words_to_rmv = ["Interface:", "Internet", "Address", "---", "Physical", "Type", "at", "on", "en0", "ifscope", "[ethernet]", "permanent"]

    #send arp command and save the decoded response.
    cmd_response = send_to_cmdLine("arp -a")

    #parse the list and filter out the words that are irrelevant.
    parsed_list = str(cmd_response).split()
    parsed_list = list(filter(lambda x: (x not in words_to_rmv) and ("0x" not in x), parsed_list))

    #find out operating system because the arp -a command returns in different format between OS's.
    op_sys = get_OS()

    #Windows has extra unnecessary heading IP, so remove that if on Windows OS.
    if op_sys=="Windows":
        parsed_list = remove_win_heading(parsed_list)

    #iterate through the list of name/ip/mac's and organize them into a nested dict.
    for i in parsed_list:
        #add the ip/mac addresses and type to a list. For Win, not using the type now, but may want to know whether static or dynamic in future.
        device_info.append(i) 
        
        #if list is full for the trio, then add it to the dictionary and restart the process with the next three
        if len(device_info)%3==0:
        
            #get the fqdn of the IP if hidden.
            #lookup MAC addr vendor name (modify to add 0 if not standard length).
            #add device info to device dictionary
            #add device dicts to network dict with vendor name
            if (op_sys=="Windows" and device_info[2] != "static"):
                static_addrs.append(device_info)
            elif (op_sys=="Windows"):
                name = socket.getfqdn(device_info[0])
                mac_name = MacLookup().lookup(device_info[1])
                device_dict[name] = device_info
                device_info.remove(device_info[2])
            else:
                pass


            if op_sys=="Linux":
                if (device_info[0] == "?"):
                    name = socket.getfqdn(device_info[0])
                    device_info[0] = name

                name = device_info[0]
                if device_info[0]=="unallocated.barefruit.co.uk":
                    pass
                else:
                    mac_addr = fix_mac_addr(device_info[2])
                    mac_name = MacLookup().lookup(mac_addr)
                    device_info[1] = device_info[1].replace('(', '')
                    device_info[1] = device_info[1].replace(')', '')
                    device_dict[device_info[0]] = [device_info[1], mac_addr]
                    
            if (device_info[0] != "unallocated.barefruit.co.uk"):
                if mac_name not in network_dict:
                    network_dict[mac_name] = device_dict
                else:
                    network_dict[mac_name].update({name: device_dict[name]})

            #reset trio list.
            device_info=[]
            #reset device dict so it doesn't keep growing
            device_dict={}


    formatted_json_network_results = json.dumps(network_dict, indent = 8, sort_keys=True)
    print("-------------------------------------------------------------------------")
    print("\nOutput that was sent to JSON file, \'network_scan_results.json\': ")
    print("-------------------------------------------------------------------------")
    print(formatted_json_network_results)

    network_scan_results = open("network_scan_results.json", "w+")
    network_scan_results.write(formatted_json_network_results)
    network_scan_results.close()

