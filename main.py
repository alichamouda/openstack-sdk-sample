import argparse
from connect import OpenstackSession
import os
import sys

import openstack
from openstack.config import loader

openstack.enable_logging(False, stream=sys.stdout)


# connection = create_connection_from_config()

# subnet = create_network(connection)
# secgroup = open_ssh_and_ping_port(connection)
# main_router = create_router(connection, subnet)
# server = create_server(connection)
# fip = create_floating_ip_and_join_sg(connection, secgroup)
# kp = create_keypair(connection)

session = OpenstackSession()