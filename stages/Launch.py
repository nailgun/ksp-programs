import time

from .BaseStage import BaseStage


class Launch(BaseStage):
    countdown = 3

    def execute(self):
        if self.vessel.situation.name not in ('pre_launch', 'landed'):
            self.log.error('Invalid situation: %s', self.vessel.situation)
            return

        self.vessel.control.throttle = 1.0

        if self.countdown < 1:
            time.sleep(1)
        else:
            self.exec_countdown()

        self.log.info('Launch!')
        self.vessel.control.activate_next_stage()

    def exec_countdown(self):
        for i in range(self.countdown, 0, -1):
            self.log.info('%s...', i)
            time.sleep(1)
