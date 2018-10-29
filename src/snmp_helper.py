from collections import OrderedDict

from easysnmp import Session

import logging as log
from oids import *


def get_cdp_if_index(item):
    return item.oid.split('.')[-1]


def get_lldp_if_index(item):
    return item.oid.split('.')[-1]


def walk_cdp_device_names(session, save_to):
    log.debug('walk_cdp_device_names')
    for item in session.walk(OID_CDP_CACHE_DEVICE_ID):
        sys_name = item.value.replace('"', '')
        if_index = get_cdp_if_index(item)
        log.debug('walk_cdp_device_names - sysName: %s, ifIndex: %s', sys_name, if_index)

        save_to[if_index] = {'sysName': sys_name}


def walk_lldp_device_names(session, save_to):
    def has_sys_name(list, sys_name):
        for item in list.values():
            if item['sysName'] == sys_name:
                return True
        return False

    log.debug('walk_lldp_device_names')
    for item in session.walk(OID_LLDP_REM_SYS_NAME):
        sys_name = item.value.replace('"', '')
        if_index = get_lldp_if_index(item)

        if sys_name == '':
            log.debug('walk_lldp_device_names', 'device with ifIndex:', if_index, 'had empty sysName - ignoring')
            continue

        log.debug('walk_lldp_device_names', 'sysName:', sys_name, 'ifIndex:', if_index)

        if has_sys_name(save_to, sys_name):
            log.debug('walk_cdp_device_names', 'sysName:', sys_name, 'already found with cdp - ignoring')
        else:
            save_to[if_index] = {'sysName': sys_name}


def walk_lldp_ports(session, save_to):
    log.debug('walk_lldp_ports')
    for item in session.walk(OID_LLDP_REM_PORT_DESC):
        log.debug('walk_lldp_ports', item)
        port_desc = item.value.replace('"', '')
        if_index = get_lldp_if_index(item)
        log.debug('walk_lldp_ports', 'trgPort:', port_desc, 'ifIndex:', if_index)

        if if_index in save_to.keys():
            save_to[if_index]['trgPort'] = port_desc


def walk_lldp_addresses(session, save_to):
    log.debug('walk_lldp_addresses')
    for item in session.walk(OID_LLDP_REM_MAN_ADDR):
        log.debug('walk_lldp_addresses - %s', item)
        port_desc = item.value.replace('"', '')
        if_index = get_lldp_if_index(item)
        log.info('walk_lldp_addresses - trgPort: %s, ifIndex: %s', port_desc, if_index)

        if if_index in save_to.keys():
            save_to[if_index]['address'] = port_desc


def walk_cdp_addresses(session, name, save_to):
    log.debug('walk_cdp_addresses')
    for item in session.walk(OID_CDP_CACHE_ADDRESS):
        if_index = get_cdp_if_index(item)
        address = ''
        for split in item.value.replace('"', '')[:-1].split(' '):
            address += str(int(split, 16)) if address is '' else '.' + str(int(split, 16))
        log.debug('walk_cdp_addresses - address: %s, ifIndex: %s', address, if_index)

        if if_index in save_to.keys():
            save_to[if_index][name] = address


# TODO: What other types are there? Some proprietary names?
def shorten_port_name(name):
    log.debug('shorten_port_name - old name: %s', name)

    name = name.replace('GigabitEthernet', 'Gi')
    name = name.replace('FastEthernet', 'Fa')

    log.debug('shorten_port_name - new name: %s', name)

    return name


def walk_cdp_ports(session, name, save_to):
    log.debug('walk_cdp_ports')
    for item in session.walk(OID_CDP_CACHE_DEVICE_PORT):
        log.debug('walk_cdp_ports - got item: %s', item)
        if_index = get_cdp_if_index(item)
        port = shorten_port_name(item.value.replace('"', ''))
        log.debug('walk_cdp_ports - port: %s, ifIndex: %s', port, if_index)

        if if_index in save_to.keys():
            save_to[if_index][name] = port


def walk_cdp_capabilities(session, name, save_to):
    log.debug('walk_cdp_capabilities')

    def resolve_capabilities(got_value):
        # https://community.cisco.com/t5/network-management/cdpcachecapabilities-where-is-the-cdp-spec/td-p/1120164
        capability_values = OrderedDict([
            (100, "Remotely managed"),
            (80, "VoIP Phone"),
            (40, "Repeater"),
            (20, "IGMP"),
            (10, "Host"),
            (8, "Switch"),
            (4, "SR Bridge"),
            (2, "TB Bridge"),
            (1, "Router")
        ])
        device_capabilities = []

        for (number, value) in capability_values.items():
            if got_value <= 0:
                break

            if got_value >= number:
                device_capabilities.append(value)
                got_value = got_value - number

        return device_capabilities

    walk = session.walk(OID_CDP_CACHE_CAPABILITIES)

    for item in walk:
        log.debug('walk_cdp_capabilities - got item: %s', item)
        if_index = get_cdp_if_index(item)
        value = int(item.value.replace('"', '').replace(' ', ''))
        log.debug('walk_cdp_capabilities - capabilities: %s, ifIndex: %s', value, if_index)

        capabilities = resolve_capabilities(value)
        log.debug("walk_cdp_capabilities - parsed ifIndex: %s capabilities as: %s", if_index, capabilities)

        if if_index in save_to.keys():
            save_to[if_index][name] = capabilities


def walk_interface_descs(session, name, save_to):
    log.debug('walk_interface_descs')
    walk = session.walk(OID_IF_IF_DESC)

    for item in walk:
        log.debug('walk_interface_descs - got item: %s', item)

        if_index = item.oid_index
        if_desc = shorten_port_name(item.value)
        log.debug('walk_interface_descs - ifDesc: %s ifIndex: %s', if_desc, if_index)

        if if_index in save_to.keys():
            save_to[if_index][name] = if_desc


def get_snmp_data(address, community):
    # Create an SNMP session to be used for all our requests
    log.debug("Creating session %s %s", address, community)
    session = Session(hostname=address, community=community, version=2, use_sprint_value=True, use_numeric=True,
                      best_guess=0)

    # Create a dict to store values
    snmp_data = {'devices': {}}

    # Ask info about local device (switch itself)
    snmp_data['sysName'] = session.get(OID_CDP_GLOBAL_DEVICE_ID).value.replace('"', '')

    walk_cdp_device_names(session, snmp_data['devices'])
    walk_cdp_addresses(session, 'address', snmp_data['devices'])
    walk_cdp_capabilities(session, 'capabilities', snmp_data['devices'])
    walk_cdp_ports(session, 'trgPort', snmp_data['devices'])

    # walk_lldp_device_names(session, snmp_data['devices'])
    # walk_lldp_addresses(session, snmp_data['devices'])
    # walk_lldp_ports(session, snmp_data['devices'])

    walk_interface_descs(session, 'srcPort', snmp_data['devices'])

    log.debug('Gathered snmp_data:')
    log.debug(snmp_data)

    return snmp_data
