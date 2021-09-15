

from definitions.instances import ComputeInstance
from definitions.router import Router
from definitions.network import Network
from definitions.security_groups import SecurityGroups
from definitions.keypairs import Keypairs
import openstack


class OpenstackSession:

    def __init__(self):
        self.cloud_name = "openstack"
        self.connection = self.create_connection_from_config()
        Keypairs.build_keys_on_stack(self.connection)
        SecurityGroups.create_security_groups(self.connection)
        Network.create_networks(self.connection)
        Router.create_router(self.connection)
        ComputeInstance.create_servers(self.connection)
    

    def create_connection_from_config(self):
        return openstack.connect(cloud=self.cloud_name)



