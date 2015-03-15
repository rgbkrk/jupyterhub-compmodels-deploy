from tornado import gen
from dockerspawner import DockerSpawner, SystemUserSpawner

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
    def start(self, image=None, extra_create_kwargs=None):
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
        if extra_create_kwargs is None:
            extra_create_kwargs = {}
        if 'mem_limit' not in extra_create_kwargs:
            extra_create_kwargs['mem_limit'] = '1g'
        if 'working_dir' not in extra_create_kwargs:
            extra_create_kwargs['working_dir'] = self.homedir
        yield DockerSpawner.start(
            self, image=image, extra_create_kwargs=extra_create_kwargs)

        # figure out what the node is and then get its ip
        name = yield self.lookup_node_name()
        self.user.server.ip = self.node_info[name]
        self.log.info("{} was started on {} ({}:{})".format(
            self.container_name, name, self.user.server.ip, self.user.server.port))

        self.log.info(self.env)
