

class Network:

    networks = {}
    subnets = {}
    floating_ip = None
    external_network_name='external'
    dns = ["192.44.75.10","192.108.115.2"]
    network_definitions = [{
        "name": "vpc-my-app",
        "subnets": [
            {
                "name": 'sn-admin',
                "cidr":'172.16.1.0/24',
                "gateway_ip":'172.16.1.1',
                "dns": dns,
            }
            ]
        }]


    def get_subnet_by_name(name):
        return Network.subnets[name]

    def get_network_by_name(name):
        return Network.networks[name]

    def get_floating_ip():
        return Network.floating_ip

    def create_networks(connection):
        external_network = connection.network.find_network(Network.external_network_name)
        Network.networks[Network.external_network_name]=external_network
        floatingip = connection.network.create_ip(floating_network_id=external_network.id)
        Network.floating_ip = floatingip

        for definition in Network.network_definitions:
            print("Creating Network "+definition["name"])
            network = connection.network.create_network(name=definition["name"])
            Network.networks[definition["name"]] = network
            for subnet_definition in definition["subnets"]:
                print("|_____ Creating subnet "+subnet_definition["name"])
                subnet = connection.network.create_subnet(
                    name=subnet_definition["name"],
                    network_id=network.id,
                    ip_version='4',
                    dns_nameservers=subnet_definition["dns"],
                    cidr=subnet_definition["cidr"],
                    gateway_ip=subnet_definition["gateway_ip"])
                Network.subnets[subnet_definition["name"]] = subnet
