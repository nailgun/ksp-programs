import threading


class Watcher(threading.Thread):
    def __init__(self, conn, vessel):
        super(Watcher, self).__init__(name='Watcher', daemon=True)

        self.conn = conn
        self.vessel = vessel

        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.current_stage = self.conn.add_stream(getattr, self.vessel.control, 'current_stage')

        self._current_stage_resources_lock = threading.RLock()
        self._current_stage_resources = None
        self._update_current_stage_resources()

    @property
    def current_stage_resources(self):
        with self._current_stage_resources_lock:
            return self._current_stage_resources

    def run(self):
        while True:
            prev_stage = self.current_stage()
            while True:
                current_stage = self.current_stage()
                if prev_stage != current_stage:
                    self._update_current_stage_resources()
                    prev_stage = current_stage

    def _update_current_stage_resources(self):
        with self._current_stage_resources_lock:
            if self._current_stage_resources:
                self._current_stage_resources.remove()

            self._current_stage_resources = self.conn.add_stream(self.vessel.resources_in_decouple_stage,
                                                                 self.current_stage() - 1)
