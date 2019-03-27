import configparser
import logging as log
import os


def die_with_error(msg, err):
    print("ERROR:", msg, "-", err)
    exit(1)


def read_config_file():
    config = configparser.ConfigParser()

    switches = []
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
    try:
        config.read(file_path)
        config = config['Application Config']

        if 'debug' in config.keys() and config['debug'].lower() == 'false':
            log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        default_community = config['defaultCommunityString']

        for switch in config['switches'].split("\n"):
            switch = switch.split(" ")

            switches.append((switch[0],
                             switch[1] if len(switch) == 2 else default_community))

    except KeyError as key:
        die_with_error("Config file " + file_path + " not found or incorrect. Did not find config ", key)

    return switches
