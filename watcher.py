import logging
import threading


class Watcher(threading.Thread):
    def __init__(self, conn, vessel):
        super(Watcher, self).__init__(name='Watcher', daemon=True)

        self.conn = conn
        self.vessel = vessel

        self.log = logging.getLogger(self.__class__.__name__)
        self.autodecouple = False

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

                self.do_background_jobs()

    def do_background_jobs(self):
        if self.autodecouple:
            self.decouple_when_ready()

    def decouple_when_ready(self):
        if self.is_ready_to_decouple():
            self.log.info('Decouple! No resources left in the stage.')
            self.vessel.control.activate_next_stage()

    def is_ready_to_decouple(self):
        stage_resources = self.current_stage_resources()

        for resource_name in stage_resources.names:
            if stage_resources.amount(resource_name) > 0.1:
                return False

        return True

    def _update_current_stage_resources(self):
        with self._current_stage_resources_lock:
            if self._current_stage_resources:
                self._current_stage_resources.remove()

            self._current_stage_resources = self.conn.add_stream(self.vessel.resources_in_decouple_stage,
                                                                 self.current_stage() - 1)
