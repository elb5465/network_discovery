from __future__ import print_function
from docopt import docopt
import network_discovery
import sys

def main():
    # arguments = docopt(__doc__)
    #no arguements needed, but they would go here if they were
    #ex:
    # op_sys = str(arguments['<operating_system>'])
    args_list = sys.argv
    print(args_list)

    if ("--noJSON" in args_list):
        network_discovery.includeJSON = False

    

    network_discovery.main()

if __name__ == "__main__":
    main()
