

class SecurityGroups:

    security_groups={}
    prepared_sg=[]
    sg_definitions = [{
        "name": "ssh",
        "protocol": "tcp",
        "port": 22,
    },{
        "name": "icmp",
        "protocol": "icmp",
        "port": None,
    },{
        "name": "http",
        "protocol": "tcp",
        "port": 80,
    }]

    def __init__(self,name,protocol,port):
        self.name = name
        self.protocol = protocol
        self.port=port
    
    def find_by_name(name):
        return SecurityGroups.security_groups[name]

    def prepare_security_groups():
        for sg in SecurityGroups.sg_definitions:
            SecurityGroups.prepared_sg.append(SecurityGroups(sg["name"],sg["protocol"], sg["port"]))
    
    def create_security_groups(connection):
        SecurityGroups.prepare_security_groups()
        
        for p_sg in SecurityGroups.prepared_sg:
            print("Creating Security Group "+ p_sg.name)
            sg = connection.network.create_security_group(name=p_sg.name)

            connection.network.create_security_group_rule(
                security_group_id=sg.id,
                direction='ingress',
                remote_ip_prefix='0.0.0.0/0',
                protocol=p_sg.protocol,
                port_range_max=p_sg.port,
                port_range_min=p_sg.port,
                ethertype='IPv4')
            SecurityGroups.security_groups[p_sg.name]=sg
    

            
