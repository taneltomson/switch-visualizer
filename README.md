# switch-visualizer

Asks CDP data from configured Cisco switches over SNMP and creates a html page that creates a visual graph of given switches.

Created HTML page locally saves layout changes by user and reloads them on next visit. 
Updated data (after running the python program) can be loaded using the reset button.

TODO:
* Checksum check to detect change of backing data for webpage?
* Logging to a file?
* tooltips save on page leave? maybe use a table for other devices? More info on other devices?

#### Requirements:
* Linux (might work on others but haven't tested)
* Python 3 (something along the lines of `apt install build-essential python3-dev python3-pip python3-setuptools python3-wheel`)
* easysnmp python library (needs libsnmp and snmp mibs).
See https://easysnmp.readthedocs.io/en/latest/#installation for instructions
* Switches (duh) that share CDP/LLDP data over SNMP.

#### Usage
* `$ git clone https://github.com/taneltomson/switch-visualizer.git`
* `$ cd switch-visualizer/`
* `$ cp config.ini.sample config.ini`
* Edit config.ini to your needs
* Run using `$ python3 src/main.py`. This creates a file `src/web/data.js` which stores gathered data and is used by the web page.
* Resulting web page is accessible from src/web/index.html using web browser
