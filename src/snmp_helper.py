from collections import OrderedDict

from easysnmp import Session

import logging as log
from oids import *

NOSUCHOBJECT_SNMP_TYPE = 'NOSUCHOBJECT'


def get_cdp_index(snmp_variable):
    """Effectively returns the port index of SNMPVariable. CDP has last oid segment as '101xx' - returns the xx."""
    last_oid_segment = snmp_variable.oid.split('.')[-1]
    return get_cdp_index_from_string(last_oid_segment)


def get_cdp_index_from_string(string):
    string = string.replace('101', '')
    if string.startswith('0'):
        return string[1:]
    return string


def get_lldp_if_index(item):
    return item.oid.split('.')[-1]


def walk_cdp_device_names(session, save_to):
    log.debug('walk_cdp_device_names')
    for item in session.walk(OID_CDP_CACHE_DEVICE_ID):
        sys_name = item.value.replace('"', '')
        cdp_index = get_cdp_index(item)
        log.debug('walk_cdp_device_names - sys_name: %s, cdp_index: %s', sys_name, cdp_index)

        save_to[cdp_index] = {'sysName': sys_name}


def walk_cdp_addresses(session, save_to):
    log.debug('walk_cdp_addresses')
    for item in session.walk(OID_CDP_CACHE_ADDRESS):
        cdp_index = get_cdp_index(item)

        if cdp_index in save_to.keys():
            address = ''
            for split in item.value.replace('"', '').strip(' ').split(' '):
                address += str(int(split, 16)) if address is '' else '.' + str(int(split, 16))
            log.debug('walk_cdp_addresses - address: %s, cdp_index: %s', address, cdp_index)

            save_to[cdp_index]['address'] = address


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
            log.debug('walk_lldp_device_names - device with ifIndex: %s had empty sysName - ignoring', if_index)
            continue

        log.debug('walk_lldp_device_names - sysName: %s, ifIndex: %s', sys_name, if_index)

        if has_sys_name(save_to, sys_name):
            log.debug('walk_cdp_device_names - sysName: %s already found with cdp - ignoring', sys_name)
        else:
            save_to[if_index] = {'sysName': sys_name}


def walk_lldp_ports(session, save_to):
    log.debug('walk_lldp_ports')
    for item in session.walk(OID_LLDP_REM_PORT_DESC):
        log.debug('walk_lldp_ports, got item: %s', item)
        port_desc = item.value.replace('"', '')
        if_index = get_lldp_if_index(item)
        log.debug('walk_lldp_ports trgPort: %s, ifIndex: %s', port_desc, if_index)

        if if_index in save_to.keys() and 'trgPort' not in save_to[if_index].keys():
            save_to[if_index]['trgPort'] = port_desc


def walk_lldp_addresses(session, save_to):
    log.debug('walk_lldp_addresses')
    for item in session.walk(OID_LLDP_REM_MAN_ADDR):
        log.debug('walk_lldp_addresses - got item: %s', item)

        # TODO: easysnmp implementation is weird here. for example gets:
        # <SNMPVariable value='20' (oid='.1.0.8802.1.1.2.1.4.2.1.4.0.1.1.1.4.192.168.11', oid_index='11',
        #                           snmp_type='INTEGER')>
        # when address is 192.168.11.11
        try:
            if_index = item.oid.split('.')[-7]
            address = '.'.join(item.oid.split('.')[-3:]) + '.' + item.oid_index
            if if_index in save_to.keys():
                log.debug('walk_lldp_addresses - address: %s, ifIndex: %s', address, if_index)
                save_to[if_index]['address'] = address
        except Exception:
            log.warn('Problem parsing LLDP address from SNMPVariable: %s', item)


# TODO: What other types are there? Some proprietary names?
def shorten_port_name(name):
    log.debug('shorten_port_name - old name: %s', name)

    name = name.replace('GigabitEthernet', 'Gi')
    name = name.replace('FastEthernet', 'Fa')

    log.debug('shorten_port_name - new name: %s', name)

    return name


def walk_cdp_ports(session, save_to):
    log.debug('walk_cdp_ports')
    for item in session.walk(OID_CDP_CACHE_DEVICE_PORT):
        log.debug('walk_cdp_ports - got item: %s', item)
        if_index = get_cdp_index(item)

        if if_index in save_to.keys():
            port = shorten_port_name(item.value.replace('"', ''))
            log.debug('walk_cdp_ports - port: %s, ifIndex: %s', port, if_index)

            save_to[if_index]['trgPort'] = port


# TODO: Is it needed?
def walk_cdp_capabilities(session, save_to):
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
        cdp_index = get_cdp_index(item)

        if cdp_index in save_to.keys():
            value = int(item.value.replace('"', '').replace(' ', ''))
            log.debug('walk_cdp_capabilities - capabilities: %s, ifIndex: %s', value, cdp_index)

            capabilities = resolve_capabilities(value)
            log.debug("walk_cdp_capabilities - parsed ifIndex: %s capabilities as: %s", cdp_index, capabilities)

            save_to[cdp_index]['capabilities'] = capabilities


def walk_interface_descs(session, save_to):
    log.debug('walk_interface_descs')
    walk = session.walk(OID_IF_IF_DESC)

    for item in walk:
        log.debug('walk_interface_descs - got item: %s', item)

        # Filter out ports we're not interested in.
        # <SNMPVariable value='Vlan1' (oid='.1.3.6.1.2.1.2.2.1.2', oid_index='1', snmp_type='OCTETSTR')>
        if not item.oid_index.startswith('101'):
            log.debug('skipping item %s', item)
            continue

        if_index = get_cdp_index_from_string(item.oid_index)
        if_desc = shorten_port_name(item.value)
        log.debug('walk_interface_descs - ifDesc: %s ifIndex: %s', if_desc, if_index)

        if if_index in save_to.keys() and 'srcPort' not in save_to[if_index].keys():
            save_to[if_index]['srcPort'] = if_desc


def walk_lldp_interface_descs(session, save_to):
    log.debug('walk_lldp_interface_descs')
    walk = session.walk(OID_LLDP_LOC_PORT_ID)

    for item in walk:
        log.debug('walk_lldp_interface_descs - got item: %s', item)

        if_index = item.oid_index
        if_desc = shorten_port_name(item.value.strip('"'))
        log.debug('walk_lldp_interface_descs - ifDesc: %s ifIndex: %s', if_desc, if_index)

        if if_index in save_to.keys() and 'srcPort' not in save_to[if_index].keys():
            save_to[if_index]['srcPort'] = if_desc


def get_snmp_data(address, community):
    # Create an SNMP session to be used for all our requests
    log.debug('Creating session %s %s', address, community)
    session = Session(hostname=address, community=community, version=2, use_sprint_value=True,
                      use_long_names=True, use_numeric=True)

    # Create a dict to store values
    device_data = {'devices': {},
                   'sysName': ask_device_sysname(session)}

    walk_cdp_device_names(session, device_data['devices'])
    walk_cdp_addresses(session, device_data['devices'])
    walk_cdp_capabilities(session, device_data['devices'])
    walk_cdp_ports(session, device_data['devices'])

    walk_lldp_device_names(session, device_data['devices'])
    walk_lldp_addresses(session, device_data['devices'])
    walk_lldp_ports(session, device_data['devices'])

    walk_interface_descs(session, device_data['devices'])
    walk_lldp_interface_descs(session, device_data['devices'])

    log.debug('Gathered device_data:')
    log.debug(device_data)

    return device_data


def ask_device_sysname(session):
    def is_value_available(snmp_variable):
        return snmp_variable.snmp_type is not NOSUCHOBJECT_SNMP_TYPE

    def get_value(snmp_variable):
        return snmp_variable.value.replace('"', '')

    cdp_sysname = session.get(OID_CDP_GLOBAL_DEVICE_ID)
    if is_value_available(cdp_sysname):
        return get_value(cdp_sysname)

    lldp_sysname = session.get(OID_LLDP_LOC_SYS_NAME)
    if is_value_available(lldp_sysname):
        return get_value(lldp_sysname)

    raise Exception('Could not get device sysName with CDP or LLDP.')
