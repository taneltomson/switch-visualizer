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
        log.debug('add_node - Adding node with sysname: %s', node_data['sysName'])
        data['nodes'][node_data['sysName']] = {}


def add_other_device(snmp_data, other_device_data, add_to):
    if 'otherDevices' not in add_to['nodes'][snmp_data['sysName']].keys():
        add_to['nodes'][snmp_data['sysName']]['otherDevices'] = []

    add_to['nodes'][snmp_data['sysName']]['otherDevices'].append(other_device_data)


def add_edge(local_data, connection_data, add_to):
    def create_str_key(src, trg):
        return src + " -> " + trg

    key = create_str_key(local_data['sysName'], connection_data['sysName'])
    if create_str_key(connection_data['sysName'], local_data['sysName']) not in add_to['edges'].keys():
        log.debug('creating %s', key)

        connection_other_devices = add_to['nodes'][connection_data['sysName']]['otherDevices']
        for item in connection_other_devices:
            if item['sysName'] == local_data['sysName']:
                other_device_data = item
                connection_other_devices.remove(item)
                break

        if key not in add_to['edges'].keys():
            add_to['edges'][key] = {}

        add_to['edges'][key]['source'] = local_data['sysName']
        add_to['edges'][key]['target'] = connection_data['sysName']

        if 'srcPort' in connection_data.keys():
            scr_port = connection_data['srcPort']
        elif 'trgPort' in other_device_data.keys():
            scr_port = other_device_data['trgPort']
        else:
            scr_port = ''

        if 'trgPort' in connection_data.keys():
            trg_port = connection_data['trgPort']
        elif 'srcPort' in other_device_data.keys():
            trg_port = other_device_data['srcPort']
        else:
            trg_port = ''

        add_to['edges'][key]['sourcePort'] = scr_port
        add_to['edges'][key]['targetPort'] = trg_port

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
        for (index, other_device_data) in switch_values['devices'].items():
            log.debug('handling other device - index: %s, data: %s', index, other_device_data)

            if other_device_data['sysName'] in combined_data['nodes'].keys():  # dict(switches).keys():
                add_edge(switch_values, other_device_data, combined_data)
            else:
                add_other_device(switch_values, other_device_data, combined_data)

        log.debug('combined data: %s', combined_data)
        log.debug(combined_data)

    except easysnmp.exceptions.EasySNMPTimeoutError:
        log.exception('SNMP Error.')
        log.warn('Skipping device: %s with community: %s due to above errors.', address, community)
    except easysnmp.exceptions.EasySNMPConnectionError:
        log.exception('Problem connecting to device: %s with community: %s.', address, community)
        log.warn('Skipping device: %s with community: %s due to above errors.', address, community)
    except Exception:  # TODO: Create custom exception for bl related stuff
        log.exception('Something went wrong when asking data from device: %s', address)
        log.warn('Skipping device: %s with community: %s due to above errors.', address, community)

log.debug("combined data:")
log.debug(combined_data)


output_helper.create_js_data_file(combined_data)

log.info('Done.')
