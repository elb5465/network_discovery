import time
import sys
import os
import subprocess 
import socket  
import json
from mac_vendor_lookup import MacLookup

includeJSON = True
help_info = False
use_cli = False

class Network_Discovery:
    """
    This class will allow the user to find devices on the current network and collect their
    IP/MAC addresses. Additionally, it will use those addresses to get the FQDN and Vendor Name of each device so 
    that it can organize and store the information in a JSON file, as well as displaying the contents of
    the JSON in the console.

    """
    def __init__(self):
        # this is a list of words to remove that show up after parsing on Mac and Windows.
        self.words_to_rmv = ["Interface:", "Internet", "Address", "---", "Physical", "Type", "at", "on", "en0", "eth0", "eth1", "eth2", "eth3", "ifscope", "[ethernet]", "[ether]", "permanent", "ens3", "en1", "en2", "ens0", "ens1", "ens2"]
        self.network_dict = {}
        self.os = ""
        self.device_dict = {}
        self.device_info = []
        self.static_addrs = []
        self.name = ""
        self.mac_name = ""
        self.idx = 0


    #-----------------------------------------------------------------------------------------------------------
    def check_requirements(self, req):
        """ Check if the package requirements are met before executing. """
        cmd_response = ""
        try:
            cmd_response = send_cmd("pip show {}".format(req))
            return True
        except:
            print(cmd_response)
            print("Missing required package:")
            print("\t- Make sure \'{}\' is properly installed with pip.".format(req))
            print("\t- Check that your pip installation matches the python installation.")
            return False

    #-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_OS():
        """Get the Operating System that this tool is being run with."""
        os_name = os.name
        if (os_name == "nt"):
            print("Windows OS Detected.\nThis may take up to a minute depending on connection-quality.")
            return "Windows"
        elif (os_name == "posix"):
            print("Mac/Linux OS Detected\nThis may take up to a minute depending on connection-quality.")
            return "Linux"
        else:
            print("{} is unrecognized".format(os.name))
            return "Other"

    #-----------------------------------------------------------------------------------------------------------
    def send_to_cmdLine(self, cmd):
        """Used to send a string 'cmd' to the terminal and return its response in utf-8 format."""
        return subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT).decode('utf8')

    #-----------------------------------------------------------------------------------------------------------
    def filter_response(self, cmd):
        """Used to send a string 'cmd' to the terminal and return its filtered output accordingly for the OS."""
        self.os = self.get_OS()

        cmd_response = self.send_to_cmdLine(cmd)
        # parse the list and filter out the words that are irrelevant.
        parsed_response = str(cmd_response).split()
        parsed_response = list(filter(lambda x: (x not in self.words_to_rmv) and ("0x" not in x), parsed_response))

        # Windows has extra unnecessary heading IP, so remove that if on Windows OS.
        if self.os=="Windows":
            parsed_response = self.remove_win_heading(parsed_response)

        return parsed_response


    #-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_ipHost_info():
        """This is an alternative method that may be used to collect host name and IP if needed."""
        hostname = socket.gethostname()    
        IPAddr = socket.gethostbyname(hostname)    
        print("Your Computer Name is: " + hostname)    
        print("Your Computer IP Address is: " + IPAddr) 
        return hostname, IPAddr


    #-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def fix_mac_addr(mac_addr):
        """This will standardize any MAC addresses that are below the typical 12 digits.
        On Mac OS, some MAC addresses show up without the leading zero in front of some  
        sections. MacLookup only works if that 12-digit style is followed, so this adds those leading
        zeroes before performing MacLookup.
        """
        new = list(filter(lambda x: (x!=":") and (x!="-"), mac_addr))
        temp_str = ""

        if len(new) < 12:
            mac_addr_split = mac_addr.split(":")

            for section in mac_addr_split:
                if len(section)==1:
                    temp_str+= "0"+section
                else:
                    temp_str+=section

                if (len(temp_str) < 17):
                        temp_str+=":"

            return temp_str
        else:
            return mac_addr


    #-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def remove_win_heading(parsed_list):
        """Removes the additional IP heading from Windows command response that are not used."""
        cnt = 0
        while len(parsed_list) > cnt+1:
            # get rid of heading IP.
            if (parsed_list[cnt+1]) and ("." in (parsed_list[cnt] and parsed_list[cnt+1])) and (not parsed_list[cnt].isalpha()):
                parsed_list.remove(parsed_list[cnt])
            cnt += 1
        return parsed_list

    #-----------------------------------------------------------------------------------------------------------
    def store_device_info(self, device_info):
        """Gather and store the FQDN and vendor-name to make a dictionary for each device containing that information."""
        if (self.os=="Windows" and device_info[-1] == "static"):
            self.static_addrs.append(device_info)

        if (self.os!="Windows"):
            # removing the name for Mac/Linux to normalize the list across OS's
            self.device_info.remove(device_info[0])
            self.device_info[0] = device_info[0].replace('(', '')
            self.device_info[0] = device_info[0].replace(')', '')


        mac_addr = self.fix_mac_addr(device_info[1])


        ip = device_info[0]
        self.name = socket.getfqdn(ip)


        if (self.name == ip):
            self.name = "Unknown_" + str(self.idx)
            self.idx+=1
        else:
            pass 


        try:
            self.mac_name = MacLookup().lookup(mac_addr)
        except:
            pass        

        
        self.device_dict[self.name] = device_info


    #-----------------------------------------------------------------------------------------------------------
    def store_network_devices(self, name, mac_name, device_info, device_dict):
        """mac_vendor_lookup does not seem to work with any devices that were listed as static on Windows,
        so for Windows it will skip them, but for Linux it will still add them."""
        if (device_info[-1]!="static"):
            if mac_name not in self.network_dict:
                self.network_dict[mac_name] = device_dict
            else:
                self.network_dict[mac_name].update({name: device_dict[name]})

            # removing the type in windows to normalize the list as [IP_address, MAC_address] across OS's
            if (self.os=="Windows"):
                self.device_info.remove(device_info[2])


    #-----------------------------------------------------------------------------------------------------------
    def dict_to_JSON(self):
        """Takes a dict, sorts it and formats it like a JSON. Then, it prints it out in the console and sends the same
        result to a new JSON file in the directory that this tool is run, unless --noJSON is specified as an argument."""
        print("-------------------------------------------------------------------------")
        print("\nOutput that was sent to JSON file, \'network_scan_results.json\': ")
        print("-------------------------------------------------------------------------")

        formatted_json_network_results = json.dumps(self.network_dict, indent = 8, sort_keys=True)
        print(formatted_json_network_results)

        if includeJSON:
            network_scan_results = open("network_scan_results.json", "w+")
            network_scan_results.write(formatted_json_network_results)
            network_scan_results.close()
        else: 
            # print("NO JSON INCLUDED\n")
            pass




#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def main():
    nw = Network_Discovery() 

    if use_cli==False:

        #---------------- CHECK ARGUMENTS ----------------------
        args_list = sys.argv
        # print(args_list)

        help = ["help", "-help", "--help"]
        if args_list[-1] in help:
            print("To use find devices on your network, just type \'network_discovery\' by itself or with these parameters: ")
            print("\t--info \n\t\t~ Displays the package information that is given by \'pip show network_discovery\'")
            print("\t--noJSON \n\t\t~ A JSON file is saved by default. Using this argument displays the output in the console without saving it to a JSON file.")
            print("\t--help \n\t\t~ Brings you to this page.\n")
            # help_info = True 
            return "--help"

        if ("--noJSON" in args_list):
            includeJSON = False 

        if ("--info" in args_list):
            print(nw.send_to_cmdLine("pip show network_discovery"))
            return


    print("-------------------------------------------------------------------------")

    # send arp command and save the decoded response.
    parsed_response = nw.filter_response("arp -a")

    nw.idx = 1
    # iterate through the list of name/ip/mac's and organize them into a nested dict.
    for i in parsed_response:

        nw.device_info.append(i) 
        
        # if list is full for the trio, then populate the dictionary and restart the process with the next set.
        if len(nw.device_info)%3==0:
            
            nw.store_device_info(nw.device_info)
            nw.store_network_devices(nw.name, nw.mac_name, nw.device_info, nw.device_dict)

            # reset the device info and dict for each device to keep them as separate entries in the network_dict.
            nw.device_info=[]
            nw.device_dict={}
    
    nw.dict_to_JSON()
    return nw.network_dict
    



#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    resp = main()
    if resp=="--help":
        help(Network_Discovery)


