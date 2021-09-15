from definitions.network import Network
from definitions.security_groups import SecurityGroups
from definitions.keypairs import Keypairs


class ComputeInstance:

    servers = {}
    prepared_instances = []
    instance_definitions = [
    {
        "name": 'portailssh',
        "exposed": True,
        "replicas": 1,
        "image_name": 'cirros',
        "flavor": 'cirros',
        "security_groups": [{"name":"ssh"},{"name":"icmp"}],
        "network": "vpc-my-app",
        "keypair_name":"kp-admin"
    }]

    def __init__(self,name,exposed,replicas,image_name,flavor,security_groups, network, keypair_name):
        self.name = name
        self.exposed = exposed
        self.replicas = replicas
        self.image_name = image_name
        self.flavor = flavor
        self.security_groups = security_groups
        self.network = network
        self.keypair_name = keypair_name

    def prepare_instances():
        for instance in ComputeInstance.instance_definitions:
            ComputeInstance.prepared_instances.append(
                ComputeInstance(
                    instance["name"],
                    instance["exposed"],
                    instance["replicas"], 
                    instance["image_name"], 
                    instance["flavor"], 
                    instance["security_groups"],
                    instance["network"],
                    instance["keypair_name"]))

    def create_servers(connection):
        ComputeInstance.prepare_instances()
        for instance in ComputeInstance.prepared_instances:
            print("Creating Server "+ instance.name)
            image = connection.compute.find_image(instance.image_name)
            flavor = connection.compute.find_flavor(instance.flavor)
            network = connection.network.find_network(instance.network)
            keypair = Keypairs.get_by_name(instance.keypair_name)
            server = connection.compute.create_server(
                name=instance.name, 
                image_id=image.id,
                flavor_id=flavor.id,
                networks=[{"uuid": network.id}], 
                key_name=keypair.name)
            server = connection.compute.wait_for_server(server)
            ComputeInstance.servers[instance.name] = server

            for sg in instance.security_groups:
                connection.compute.add_security_group_to_server(server, SecurityGroups.find_by_name(sg["name"]))

            if instance.exposed:
                connection.compute.add_floating_ip_to_server(server,Network.get_floating_ip().floating_ip_address)
    
    def list_servers(connection):
        return connection.compute.servers()


    def find_server_by_name(connection, servername):
        servers = ComputeInstance.list_servers(connection)
        for server in servers:
            if server.name == servername:
                return server
        return None


        