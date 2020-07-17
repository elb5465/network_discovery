from __future__ import print_function
from docopt import docopt
import network_discovery

def main():
    # arguments = docopt(__doc__)
    #no arguements needed, but they would go here if they were
    #ex:
    # op_sys = str(arguments['<operating_system>'])

    network_discovery.discover()

if __name__ == "__main__":
    main()
