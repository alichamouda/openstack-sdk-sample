

import os


class Keypairs:
    SSH_DIR = '/home/user/.ssh'

    keypairs = {}
    resolved_keypairs=[]
    keypairs_definition = [{
        'name': 'kp-admin'
    }]
    
    def __init__(self, name):
        self.name = name
        self.location = self.resolve_location()
    
    def resolve_location(self):
        return '{ssh_dir}/id_rsa.{key}'.format(ssh_dir=Keypairs.SSH_DIR, key=self.name)


    def get_by_name(name):
        return Keypairs.keypairs[name]
    

    def delete_keypair(connection):
        print("Deleting keypairs")
        for name in Keypairs.keypairs.keys():
            connection.compute.delete_keypair(Keypairs.keypairs[name])

    def build_keys_on_stack(connection):
        for keypair in Keypairs.keypairs_definition:
            Keypairs.resolved_keypairs.append(Keypairs(keypair['name']))

        for key in Keypairs.resolved_keypairs:
            keypair = connection.compute.find_keypair(key.name)
            if not keypair:
                print("Creating key pair "+ key.name)
                keypair = connection.compute.create_keypair(name=key.name)
                try:
                    os.mkdir(Keypairs.SSH_DIR)
                except OSError as e:
                    print("Folder ~/.ssh exists")
                with open(key.location, 'w') as f:
                    f.write("%s" % keypair.private_key)
                os.chmod(key.location, 0o400)
            Keypairs.keypairs[key.name] = keypair

    