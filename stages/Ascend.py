import math
import time

from .BaseStage import BaseStage


class Ascend(BaseStage):
    turn_start_altitude = 250
    turn_end_altitude = 45000
    target_altitude = 150000

    def execute(self):
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.wait()
        self.vessel.control.throttle = 1.0

        altitude = self.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        apoapsis = self.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        stage_2_resources = self.vessel.resources_in_decouple_stage(stage=2, cumulative=False)
        srb_fuel = self.add_stream(stage_2_resources.amount, 'SolidFuel')

        # Main ascent loop
        srbs_separated = False
        turn_angle = 0
        while True:
            # Gravity turn
            if altitude() > self.turn_start_altitude and altitude() < self.turn_end_altitude:
                frac = ((altitude() - self.turn_start_altitude) /
                        (self.turn_end_altitude - self.turn_start_altitude))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

            # Separate SRBs when finished
            if not srbs_separated:
                if srb_fuel() < 0.1:
                    self.vessel.control.activate_next_stage()
                    srbs_separated = True
                    self.log.info('SRBs separated')

            # Decrease throttle when approaching target apoapsis
            if apoapsis() > self.target_altitude * 0.9:
                self.log.info('Approaching target apoapsis')
                break

        # Disable engines when target apoapsis is reached
        self.vessel.control.throttle = 0.25
        while apoapsis() < self.target_altitude:
            pass
        self.log.info('Target apoapsis reached')
        self.vessel.control.throttle = 0.0

        # Wait until out of atmosphere
        self.log.info('Coasting out of atmosphere')
        while altitude() < 70500:
            pass
