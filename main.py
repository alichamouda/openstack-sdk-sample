import argparse
from connect import OpenstackSession
import time
import sys

import openstack
from openstack.config import loader

openstack.enable_logging(False, stream=sys.stdout)

session = OpenstackSession()
time.sleep(60)
print("Deleting Everything ...")
time.sleep(60)
session.delete_everything()