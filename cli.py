from __future__ import print_function
from docopt import docopt
import network_discovery
import subprocess
import sys

def send_cmd(cmd):
    return subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT).decode('utf8')


def check_requirements(req):
    try:
        cmd_response = send_cmd("pip show {}".format(req))
        return True
    except:
        print("Missing required package:")
        print("\t- Make sure \'{}\' is properly installed with pip.".format(req))
        print("\t- Check that your pip installation matches the python installation.")
        return False


def main():
    #---------------- CHECK PACKAGE REQUIREMENTS ----------------------
    if check_requirements("mac_vendor_lookup") and check_requirements("docopt"):


        #---------------- CHECK ARGUMENTS ----------------------
        args_list = sys.argv
        print(args_list)

        help = ["help", "-help", "--help"]
        if args_list[-1] in help:
            print("To use find devices on your network, just type \'network_discovery\' by itself or with these parameters: ")
            print("\t--info \n\t\t~ Displays the package information that is given by \'pip show network_discovery\'")
            print("\t--noJSON \n\t\t~ A JSON file is saved by default. Using this argument displays the output in the console without saving it to a JSON file.")
            print("\t--help \n\t\t~ Brings you to this page.\n")
            network_discovery.help_info = True 

        if ("--noJSON" in args_list):
            network_discovery.includeJSON = False 

        if ("--info" in args_list):
            print(send_cmd("pip show network_discovery"))
            return

        
        #---------------- RUN THE ACTUAL TOOL ----------------------
        network_discovery.main()
    
    else:
        print("\nRequirements must be satisfied before using this tool.")

#----------------------------------------------------------------------
if __name__ == "__main__":
    main()
