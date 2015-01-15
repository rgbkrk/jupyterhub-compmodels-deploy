from tornado import gen
from dockerspawner import SystemUserSpawner

class SwarmSpawner(SystemUserSpawner):

    container_ip = '0.0.0.0'

    @gen.coroutine
    def lookup_node_name(self):
        """Find the name of the swarm node that the container is running on."""
        containers = yield self.docker('containers', all=True)
        for container in containers:
            if container['Id'] == self.container_id:
                name, = container['Names']
                node, container_name = name.lstrip("/").split("/")
                raise gen.Return(node)

    @gen.coroutine
    def get_container(self):
        self.log.debug("Getting container '%s'", self.container_name)
        containers = yield self.docker('containers', all=True)
        for c in containers:
            for name in c['Names']:
                node, container_name = name.lstrip("/").split("/")
                if container_name == self.container_name:
                    self.container_id = c['Id']
                    raise gen.Return(c)
        self.log.info("Container '%s' is gone", self.container_name)
        # my container is gone, forget my id
        self.container_id = ''

    @gen.coroutine
    def start(self, **kwargs):
        # look up mapping of node names to ip addresses
        info = yield self.docker('info')
        node_info = info['DriverStatus']
        num_nodes = int(node_info[0][1])
        self.node_info = {}
        for i in range(1, num_nodes + 1):
            node, ip_port = node_info[i]
            self.node_info[node] = ip_port.split(":")[0]
        self.log.debug("Swarm nodes are: {}".format(self.node_info))

        # start the container
        yield super(SwarmSpawner, self).start(**kwargs)

        # figure out what the node is and then get its ip
        name = yield self.lookup_node_name()
        self.user.server.ip = self.node_info[name]
        self.log.info("{} was started on {} ({}:{})".format(
            self.container_name, name, self.user.server.ip, self.user.server.port))

        self.log.info(self.env)
