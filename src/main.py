import easysnmp
import logging as log
import snmp_helper
import config_helper
import output_helper

switches = config_helper.read_config_file()


log.debug('Got following switches as input:')
log.debug(switches)

combined_data = {
    'nodes': {},
    'edges': {}
}


def add_node(node_data, data):
    if node_data['sysName'] not in data['nodes']:
        data['nodes'][node_data['sysName']] = {}


def add_other_device(local_data, connection_data, add_to):
    if 'otherDevices' not in add_to['nodes'][local_data['sysName']].keys():
        add_to['nodes'][local_data['sysName']]['otherDevices'] = []

    add_to['nodes'][local_data['sysName']]['otherDevices'].append(connection_data)


def add_edge(local_data, connection_data, add_to):
    def create_str_key(src, trg):
        return src + " -> " + trg

    key = create_str_key(local_data['sysName'], connection_data['sysName'])
    if create_str_key(connection_data['sysName'], local_data['sysName']) not in add_to['edges'].keys():
        if key not in add_to['edges'].keys():
            add_to['edges'][key] = {}
            add_to['edges'][key]['source'] = local_data['sysName']
            add_to['edges'][key]['target'] = connection_data['sysName']
            add_to['edges'][key]['sourcePort'] = connection_data['srcPort']
            add_to['edges'][key]['targetPort'] = connection_data['trgPort']
    else:
        log.debug('ignoring %s because reverse already exists!', key)


for switch in switches:
    address = switch[0]
    community = switch[1]
    log.info("Asking data from switch, addr: %s, community: %s", address, community)

    try:
        # Ask data from the switch
        switch_values = snmp_helper.get_snmp_data(address, community)

        # Add the switch itself
        add_node(switch_values, combined_data)

        # Go through switch's connections
        for (index, connection_data) in switch_values['devices'].items():
            # Only add switches, ignore other devices
            # TODO: Host part configurable? Disable of finding other switches?
            if 'capabilities' in connection_data.keys() \
                    and ('Switch' not in connection_data['capabilities'] or 'Host' in connection_data['capabilities']):
                add_other_device(switch_values, connection_data, combined_data)
                continue
            else:
                # Add device connected to the switch and the connection
                add_node(connection_data, combined_data)
                add_edge(switch_values, connection_data, combined_data)

    except easysnmp.exceptions.EasySNMPTimeoutError as e:
        print("SNMP Error:", e)

log.debug("combined data:")
log.debug(combined_data)


output_helper.create_js_data_file(combined_data)

log.info('Done.')
