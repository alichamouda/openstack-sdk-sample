
import argparse
import os
import sys

import openstack
from openstack.config import loader

openstack.enable_logging(False, stream=sys.stdout)

#: Defines the OpenStack Config cloud key in your config file,
#: typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the examples will be run and what resource defaults
#: will be used to run the examples.
TEST_CLOUD = os.getenv('OS_TEST_CLOUD', 'openstack')
EXAMPLE_CONFIG_KEY = os.getenv('OPENSTACKSDK_EXAMPLE_CONFIG_KEY', 'example')
config = loader.OpenStackConfig()
cloud = openstack.connect(cloud=TEST_CLOUD)


class Opts:
    def __init__(self, cloud_name='openstack', debug=False):
        self.cloud = cloud_name
        self.debug = debug
        # Use identity v3 API for examples.
        self.identity_api_version = '3'


def _get_resource_value(resource_key, default):
    return config.get_extra_config(
        EXAMPLE_CONFIG_KEY).get(resource_key, default)


S_SSH_PORTAL = 'portailssh'
S_FRONTEND = 'frontend'
S_BACKEND = 'backend'

IMAGE_NAME = _get_resource_value('image_name', 'cirros')
FLAVOR_NAME = _get_resource_value('flavor_name', 'cirros')
NETWORK_NAME = _get_resource_value('network_name', 'private-net')
SUBNET_NAME = _get_resource_value('subnet_name', 'subnet-1')
KEYPAIR_NAME = _get_resource_value('keypair_name', 'kp')
SECGROUP_NAME = _get_resource_value('secgroup_name', 'secgrp-1')
MAIN_ROUTER_NAME = _get_resource_value('router_name', 'router-0-1')
SSH_DIR = _get_resource_value(
    'ssh_dir', '{home}/.ssh'.format(home=os.path.expanduser("~")))
PRIVATE_KEYPAIR_FILE = _get_resource_value(
    'private_keypair_file', '{ssh_dir}/id_rsa.{key}'.format(
        ssh_dir=SSH_DIR, key=KEYPAIR_NAME))


def create_connection_from_config():
    return openstack.connect(cloud=TEST_CLOUD)


def create_network(conn):
    print("Create Network:")

    example_network = conn.network.create_network(
        name=NETWORK_NAME)
    example_subnet = conn.network.create_subnet(
        name=SUBNET_NAME,
        network_id=example_network.id,
        ip_version='4',
        dns_nameservers=["192.44.75.10","192.108.115.2"],
        cidr='172.16.100.0/24',
        gateway_ip='172.16.100.1')
    return example_subnet
    print("Network & subnet Created")

def open_ssh_and_ping_port(conn):
    print("Open a port:")

    example_sec_group = conn.network.create_security_group(
        name=SECGROUP_NAME)

    example_rule = conn.network.create_security_group_rule(
        security_group_id=example_sec_group.id,
        direction='ingress',
        remote_ip_prefix='0.0.0.0/0',
        protocol='TCP',
        port_range_max='22',
        port_range_min='22',
        ethertype='IPv4')
    
    example_rule = conn.network.create_security_group_rule(
        security_group_id=example_sec_group.id,
        direction='ingress',
        remote_ip_prefix='0.0.0.0/0',
        protocol='icmp',
        port_range_max=None,
        port_range_min=None,
        ethertype='IPv4')
    print("SG Created")
    return example_sec_group

def create_router(conn, subnet):
    print('Creating Router')
    external_network = conn.network.find_network('external')
    print('... External network fetched')
    main_router = conn.network.create_router(
        name=MAIN_ROUTER_NAME,
        external_gateway_info= {'network_id': external_network.id}
    )
    #conn.router_add_gateway(router, external_network.id)
    conn.network.add_interface_to_router(main_router, subnet_id=subnet.id)

    return main_router

def create_keypair(conn):
    keypair = conn.compute.find_keypair(KEYPAIR_NAME)

    if not keypair:
        print("Create Key Pair:")

        keypair = conn.compute.create_keypair(name=KEYPAIR_NAME)

        print(keypair)

        try:
            os.mkdir(SSH_DIR)
        except OSError as e:
            print("error")

        with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
            f.write("%s" % keypair.private_key)

        os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)

    return keypair

def create_server(conn):
    print("Create Server:")

    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)
    keypair = create_keypair(conn)

    server = conn.compute.create_server(
        name=S_SSH_PORTAL, 
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)



    return server


def list_servers(conn):
    return conn.compute.servers()


def find_server_by_name(conn, servername):
    servers = list_servers(conn)
    for server in servers:
        if server.name == servername:
            return server
    return None

def create_floating_ip_and_join_sg(conn,secgroup):
    network = conn.network.find_network('external')
    sshserver=find_server_by_name(conn, S_SSH_PORTAL)
    networkp = conn.network.find_network(NETWORK_NAME)
    floatingip = conn.network.create_ip(floating_network_id=network.id)
    conn.compute.add_floating_ip_to_server(sshserver,floatingip.floating_ip_address)
    conn.compute.add_security_group_to_server(sshserver, secgroup)
    return floatingip


connection = create_connection_from_config()

subnet = create_network(connection)
secgroup = open_ssh_and_ping_port(connection)
main_router = create_router(connection, subnet)
server = create_server(connection)
fip = create_floating_ip_and_join_sg(connection, secgroup)
# kp = create_keypair(connection)

print("ssh -i {key} cirros@{ip}".format(
    key=PRIVATE_KEYPAIR_FILE,
    ip=fip.floating_ip_address))