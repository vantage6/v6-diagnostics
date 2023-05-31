import vantage6.client as v6client

IMAGE = 'harbor2.vantage6.ai/algorithms/n2n-diagnostics'


class N2NDiagnosticsClient:

    def __init__(self, client: v6client.Client,*, image=IMAGE, tag:str='latest'):
        self.client = client
        self.image = image
        self.tag = tag
        self.tagged_image = f'{image}:{tag}'

    def echo(self, master_node, collaboration_id, other_nodes):
        task = self.client.task.create(collaboration=collaboration_id,
                                       organizations=[master_node],
                                       name='test_echo',
                                       image=self.tagged_image, description='test',
                                       input={'method': 'echo', 'master': True,
                                              'kwargs': {
                                                  'other_nodes': other_nodes}})

        return task

    def wait(self, nodes, collaboration_id):
        task = self.client.task.create(collaboration=collaboration_id,
                                       organizations=nodes,
                                       name='test_wait',
                                       image=self.image, description='test',
                                       input={'method': 'wait', 'master': False})

        return task
