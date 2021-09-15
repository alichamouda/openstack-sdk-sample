from definitions.network import Network


class Router:
    routers={}

    prepared_routers=[]
    router_definitions=[{
        "name": "rt-admin",
        "subnets": [
            {
                "name": "sn-admin"
            }
        ]
    }]

    def __init__(self, name, subnets):
        self.name=name
        self.subnets = subnets

    def create_router(connection):

        for definition in Router.router_definitions:
            Router.prepared_routers.append(Router(definition["name"], definition["subnets"]))


        for p_router in Router.prepared_routers:
            print('Creating Router '+ p_router.name)
            router = connection.network.create_router(
                name=p_router.name,
                external_gateway_info= {'network_id': Network.get_network_by_name(Network.external_network_name).id}
            )
            for subnet in p_router.subnets:
                connection.network.add_interface_to_router(router, subnet_id=Network.get_subnet_by_name(subnet["name"]).id)
            Router.routers[router.name]=router

    def delete_routers(connection):
        print("Deleting Routers")
        for p_router in Router.prepared_routers:
            router = Router.routers[p_router.name]
            for subnet in p_router.subnets:
                connection.network.remove_interface_from_router(router, subnet_id=Network.get_subnet_by_name(subnet["name"]).id)
            
            connection.network.delete_router(router)