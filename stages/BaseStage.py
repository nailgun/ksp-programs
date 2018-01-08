import logging


class BaseStage:
    autodecouple = True

    def __init__(self, conn, vessel, watcher, **options):
        self.conn = conn
        self.vessel = vessel
        self.watcher = watcher
        self.options = options

        for k, v in options.items():
            setattr(self, k, v)

        self.log = logging.getLogger(self.__class__.__name__)
        self._streams = []
        self._nodes = []
        self._drawings = []
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

    def add_drawing(self, drawing):
        self._drawings.append(drawing)
        return drawing

    def debug_display_reference_frame(self, reference_frame):
        for axis in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            self.add_drawing(self.conn.drawing.add_direction(axis, reference_frame)).color = axis

    def _cleanup(self):
        self._reset_auto_pilot()

        for stream in self._streams:
            stream.remove()
        self._streams = []

        for node in self._nodes:
            node.remove()
        self._nodes = []

        for drawing in self._drawings:
            drawing.remove()
        self._drawings = []

    def _reset_auto_pilot(self):
        self.vessel.auto_pilot.disengage()
        self.vessel.auto_pilot.reference_frame = self.vessel.surface_reference_frame
        self.vessel.auto_pilot.target_pitch_and_heading(0, 0)
        self.vessel.auto_pilot.target_roll = float('nan')

    def __repr__(self):
        options_repr = ', '.join(['{}={}'.format(k, v) for k, v in self.options.items()])
        if options_repr:
            return '{}({})'.format(self.__class__.__name__, options_repr)
        else:
            return self.__class__.__name__
