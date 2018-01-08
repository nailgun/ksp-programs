import math
import time

from .BaseStage import BaseStage


class Launch(BaseStage):
    def execute(self):
        # Pre-launch setup
        self.vessel.control.sas = False
        self.vessel.control.rcs = False
        self.vessel.control.throttle = 1.0

        # Countdown...
        self.log.info('3...')
        time.sleep(1)
        self.log.info('2...')
        time.sleep(1)
        self.log.info('1...')
        time.sleep(1)
        self.log.info('Launch!')

        # Activate the first stage
        self.vessel.control.activate_next_stage()
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)
