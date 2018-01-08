import time

from .BaseStage import BaseStage


class Launch(BaseStage):
    def execute(self):
        if self.vessel.situation.name not in ('pre_launch', 'landed'):
            self.log.error('Invalid situation: %s', self.vessel.situation)
            return

        self.vessel.control.throttle = 1.0

        # Countdown...
        self.log.info('3...')
        time.sleep(1)
        self.log.info('2...')
        time.sleep(1)
        self.log.info('1...')
        time.sleep(1)
        self.log.info('Launch!')

        self.vessel.control.activate_next_stage()
