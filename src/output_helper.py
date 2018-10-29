import os
import logging as log


def create_js_data_file(data):
    tab = '  '

    log.info('Writing output')

    with open(os.path.join(os.path.dirname(__file__), 'web/data.js'), 'w') as outfile:
        outfile.write('elements_data = {\n')

        outfile.write(tab + 'nodes: [\n')
        for (sysName, node_data) in data['nodes'].items():
            outfile.write(tab + tab + '{ data: {\n')
            outfile.write(tab + tab + tab + 'id: "' + sysName + '",\n')
            outfile.write(tab + tab + tab + 'otherDevices: [\n')
            if 'otherDevices' in node_data.keys():
                for other_device in node_data['otherDevices']:
                    outfile.write(tab + tab + tab + tab + '{\n')
                    outfile.write(tab + tab + tab + tab + tab + 'sysName: "' + other_device['sysName'] + '",\n')
                    outfile.write(tab + tab + tab + tab + tab + 'address: "' + other_device['address'] + '",\n')
                    outfile.write(tab + tab + tab + tab + tab + 'srcPort: "' + other_device['srcPort'] + '",\n')
                    outfile.write(tab + tab + tab + tab + tab + 'trgPort: "' + other_device['trgPort'] + '",\n')
                    outfile.write(tab + tab + tab + tab + '},\n')
            outfile.write(tab + tab + tab + '],\n')

            outfile.write(tab + tab + ' } },\n')
        outfile.write(tab + '],\n')

        outfile.write(tab + 'edges: [\n')
        for name, values in data['edges'].items():
            outfile.write(tab + tab + '{ data: {\n')
            outfile.write(tab + tab + tab + 'source: "' + values['source'] + '",\n')
            outfile.write(tab + tab + tab + 'target: "' + values['target'] + '",\n')
            outfile.write(tab + tab + tab + 'targetPort: "' + values['targetPort'] + '",\n')
            outfile.write(tab + tab + tab + 'sourcePort: "' + values['sourcePort'] + '"\n')
            outfile.write(tab + tab + ' } },\n')
        outfile.write(tab + '],\n')

        outfile.write('}\n')
