import os
import logging as log


tab = '    '


def get(item, key):
    return item[key] if key in item.keys() else ''


def write_line(num_tabs, msg, file):
    file.write(tab * num_tabs + msg + '\n')


def create_js_data_file(data):
    log.info('Writing output')

    with open(os.path.join(os.path.dirname(__file__), 'web/data.js'), 'w') as outfile:
        write_line(0, 'elements_data = {', outfile)

        write_line(1, 'nodes: [', outfile)
        for (sysName, node_data) in data['nodes'].items():
            write_line(2, '{ data: {', outfile)
            write_line(3, 'id: "' + sysName + '",', outfile)
            write_line(3, 'otherDevices: [', outfile)
            if 'otherDevices' in node_data.keys():
                for other_device in node_data['otherDevices']:
                    write_line(4, '{', outfile)
                    write_line(5, 'sysName: "' + other_device['sysName'] + '",', outfile)
                    write_line(5, 'address: "' + get(other_device, 'address') + '",', outfile)
                    write_line(5, 'srcPort: "' + get(other_device, 'srcPort') + '",', outfile)
                    write_line(5, 'trgPort: "' + get(other_device, 'trgPort') + '",', outfile)
                    write_line(4, '},', outfile)
            write_line(3, '],', outfile)
            write_line(2, ' } },', outfile)
        write_line(1, '],', outfile)

        write_line(1, 'edges: [', outfile)
        for name, values in data['edges'].items():
            write_line(2, '{ data: {', outfile)
            write_line(3, 'source: "' + values['source'] + '",', outfile)
            write_line(3, 'target: "' + values['target'] + '",', outfile)
            write_line(3, 'targetPort: "' + values['targetPort'] + '",', outfile)
            write_line(3, 'sourcePort: "' + values['sourcePort'] + '"', outfile)
            write_line(2, ' } },', outfile)
        write_line(1, '],', outfile)

        write_line(0, '}', outfile)
