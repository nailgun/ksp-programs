import math2
from .BaseStage import BaseStage


class Ascend(BaseStage):
    turn_start_altitude = 250
    turn_end_altitude = 45000
    target_altitude = 150000
    full_throttle_portion = 0.9
    finalizing_throttle = 0.25

    def execute(self):
        altitude = self.add_stream(getattr, self.vessel.flight(), 'mean_altitude')

        self.gravity_turn(altitude)
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.wait()
        self.vessel.control.throttle = 1.0

        apoapsis = self.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        stage_2_resources = self.vessel.resources_in_decouple_stage(stage=2, cumulative=False)
        srb_fuel = self.add_stream(stage_2_resources.amount, 'SolidFuel')

        # Main ascent loop
        srbs_separated = False
        full_throttle_max_apoapsis = self.target_altitude * self.full_throttle_portion
        while apoapsis() < full_throttle_max_apoapsis:
            self.gravity_turn(altitude)

            # Separate SRBs when finished
            if not srbs_separated:
                if srb_fuel() < 0.1:
                    self.vessel.control.activate_next_stage()
                    srbs_separated = True
                    self.log.info('SRBs separated')

        self.wait_apoapsis(apoapsis)

        self.log.info('Target apoapsis reached')
        self.vessel.control.throttle = 0.0

    def gravity_turn(self, altitude):
        alt = math2.clamp(self.turn_start_altitude, altitude(), self.turn_end_altitude)
        frac = (alt - self.turn_start_altitude) / (self.turn_end_altitude - self.turn_start_altitude)
        turn_angle = frac * 90
        self.vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    def wait_apoapsis(self, apoapsis):
        self.log.info('Approaching target apoapsis')
        self.vessel.control.throttle = self.finalizing_throttle
        while apoapsis() < self.target_altitude:
            pass
