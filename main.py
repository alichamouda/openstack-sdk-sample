import argparse
from connect import OpenstackSession
import time
import sys

import openstack
from openstack.config import loader

openstack.enable_logging(False, stream=sys.stdout)

session = OpenstackSession()
time.sleep(2)
print("Deleting Everything ...")
time.sleep(2)
session.delete_everything()