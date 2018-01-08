import logging


class BaseStage:
    def __init__(self, conn, vessel):
        self.conn = conn
        self.vessel = vessel
        self.log = logging.getLogger(self.__class__.__name__)
        self._streams = []
        self._nodes = []
        self._executing = False

    def __call__(self):
        self._executing = True
        try:
            return self.execute()
        finally:
            self._executing = False
            self._cleanup()

    def execute(self):
        raise NotImplementedError

    def add_stream(self, func, *args, **kwargs):
        if not self._executing:
            raise Exception('Stage.add_stream() can only be called during stage execution')
        stream = self.conn.add_stream(func, *args, **kwargs)
        self._streams.append(stream)
        return stream

    def add_node(self, *args, **kwargs):
        if not self._executing:
            raise Exception('Stage.add_node() can only be called during stage execution')
        node = self.vessel.control.add_node(*args, **kwargs)
        self._nodes.append(node)
        return node

    def _cleanup(self):
        for stream in self._streams:
            stream.remove()
        self._streams = []

        for node in self._nodes:
            node.remove()
        self._nodes = []
