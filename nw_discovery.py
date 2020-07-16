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
import time
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
        print("Windows OS Detected.\n")
        return "Windows"
    elif (os_name == "posix"):
        print("Mac/Linux OS Detected\n")
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
print("-------------------------------------------------------------------------")
noNoWords = ["Interface:", "Internet", "Address", "---", "Physical", "Type", "at", "on", "en0", "ifscope", "[ethernet]", "permanent"]


#From testing on Mac, cmd line response is decoded already, but Windows still needs to be decoded.
cmd_response = send_to_cmdLine("arp -a")
op_sys = get_OS()
if op_sys=="Linux":
    cmd_response = cmd_response.decode('utf-8')
    print(cmd_response)
    #parse the list and filter out the words that are irrelevant
    parsed_list = str(cmd_response).split()
    parsed_list = list(filter(lambda x: (x not in noNoWords) and ("0x" not in x), parsed_list))
    print(parsed_list, "\n")

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
        
            #get the fqdn of the IP if hidden.
            #lookup MAC addr vendor name (modify to add 0 if not standard length).
            #add device info to device dictionary
            #add device dicts to network dict with vendor name
            if (ip_mac_type[0]=="?"):
                name = socket.getfqdn(ip_mac_type[0])
                print(ip_mac_type[0])
                ip_mac_type[0] = name
                print("\nNAME: ", name)

            name = ip_mac_type[0]
            if ip_mac_type[0]=="unallocated.barefruit.co.uk":
                pass
                print(ip_mac_type)
            else:
                #check len of mac to see if it is the standard size of 12 it needs to be.
                new = list(filter(lambda x: (x!=":") and (x!="-"), ip_mac_type[2]))
                temp_str = ""
                # add a zero to the first index of a mac address section that contains only 1 number instead of 2.
                if len(new)==11:
                    i = 0
                    while len(temp_str)<17:
                        if ip_mac_type[2][i]==":" and ip_mac_type[2][i+2] ==":":
                            temp_str += ":0"
                        else:
                            temp_str += ip_mac_type[2][i]
                        i+=1
                    ip_mac_type[2] = temp_str

                # try: 
                mac_name = MacLookup().lookup(ip_mac_type[2])
                ip_mac_type[1] = ip_mac_type[1].replace('(', '')
                ip_mac_type[1] = ip_mac_type[1].replace(')', '')
                device_dict[ip_mac_type[0]] = [ip_mac_type[1], ip_mac_type[2]]
                
                if mac_name not in network_dict:
                    network_dict[mac_name] = device_dict
                else:
                    network_dict[mac_name].update({name: device_dict[name]})
                print(mac_name)

                # except:
                #     print(EnvironmentError)

                print(ip_mac_type)
                
            print(device_dict, "\n")
            ip_mac_type=[]
            device_dict={}
#---------------------------------------------------------------------------------

                # device_dict.update({idx:mac_name})
         

            # print("\nMAC_NAME: ", mac_name)
            # print("NAME: ", name)
            # print(device_dict)
            
            # if len(device_dict)!=0:

                # if mac_name not in network_dict:
                #     network_dict[mac_name] = device_dict
                # else:
                #     network_dict[mac_name].update({name: device_dict[name]})
            # else:
            #     print("HELLO: ", mac_name, device_dict)
            # #reset device dict so it doesn't keep growing
            # device_dict = {}

            # #reset trio list.
            # ip_mac_type = []

    print("\nNETWORK DICTIONARY: ")
    print(network_dict)

    formatted_json_network_results = json.dumps(network_dict, indent = 8, sort_keys=True)
    print("\nOUTPUT THAT WAS SENT TO JSON FILE")
    print(formatted_json_network_results)

    network_scan_results = open("network_scan_results.json", "w+")
    network_scan_results.write(formatted_json_network_results)
    network_scan_results.close()




elif op_sys=="Windows":
    cmd_response = cmd_response.decode('utf-8')
    print(cmd_response)

    #parse the list and filter out the words that are irrelevant
    parsed_list = str(cmd_response).split()
    parsed_list = list(filter(lambda x: (x not in noNoWords) and ("0x" not in x), parsed_list))
    print(parsed_list)

    cnt = 0
    while len(parsed_list) > cnt+1:
        #get rid of heading IP.
        if (parsed_list[cnt+1]) and ("." in (parsed_list[cnt] and parsed_list[cnt+1])) and (not parsed_list[cnt].isalpha()):
            print(parsed_list[cnt])
            parsed_list.remove(parsed_list[cnt])
        cnt += 1

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
                name = socket.getfqdn(ip_mac_type[0])
                # mac_name = MacLookup().lookup(ip_mac_type[1])
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
    print("\nOUTPUT THAT WAS SENT TO JSON FILE")
    print(formatted_json_network_results)

    network_scan_results = open("network_scan_results.json", "w+")
    network_scan_results.write(formatted_json_network_results)
    network_scan_results.close()


else:
    "Operating System Not Mac/Linux or Windows"    

