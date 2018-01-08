import math
import time

from .BaseStage import BaseStage


class Circularize(BaseStage):
    lead_time = 5

    def execute(self):
        self.log.info('Planning circularization burn')
        delta_v = self.calc_delta_v()
        node = self.add_node(self.conn.space_center.ut + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)
        burn_time = self.calc_burn_time(delta_v)

        self.orientate(node)
        self.wait_until_burn(burn_time)
        self.execute_burn(burn_time)
        self.fine_tune(node)

    def calc_delta_v(self):
        # vis-viva equation

        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        return v2 - v1

    def calc_burn_time(self, delta_v):
        # rocket equation

        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        return (m0 - m1) / flow_rate

    def orientate(self, node):
        self.log.info('Orientating ship for circularization burn')
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

    def wait_until_burn(self, burn_time):
        self.log.info('Waiting until circularization burn')
        burn_ut = self.conn.space_center.ut + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        self.conn.space_center.warp_to(burn_ut - self.lead_time)

        self.log.info('Ready to execute burn')
        with self.conn.stream(getattr, self.vessel.orbit, 'time_to_apoapsis') as time_to_apoapsis:
            while time_to_apoapsis() - (burn_time / 2.) > 0:
                pass

    def execute_burn(self, burn_time):
        self.log.info('Executing burn')
        self.vessel.control.throttle = 1.0
        time.sleep(burn_time - 0.1)

    def fine_tune(self, node):
        self.log.info('Fine tuning')

        self.vessel.control.throttle = 0.05

        with self.conn.stream(node.remaining_burn_vector, node.reference_frame) as remaining_burn:
            prev_remaining_burn = remaining_burn()[1]
            while remaining_burn()[1] <= prev_remaining_burn:
                prev_remaining_burn = remaining_burn()[1]

        self.vessel.control.throttle = 0.0
