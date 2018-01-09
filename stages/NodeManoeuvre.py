import math

import math2
from .BaseStage import BaseStage


class NodeManoeuvre(BaseStage):
    lead_time = 5
    max_delta_v_error = 0.1
    burn_slowdown_factor = 8.37

    def perform_manoeuvre(self, node):
        delta_v = node.remaining_delta_v
        self.log.info('DeltaV: %s', delta_v)

        burn_time = self.calc_burn_time(delta_v)
        self.log.info('Burn time: %s', burn_time)

        self.orientate(node)
        self.wait_until_burn(node, burn_time)
        self.execute_burn(node, burn_time)

    def calc_burn_time(self, delta_v):
        # rocket equation

        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        return (m0 - m1) / flow_rate

    def orientate(self, node):
        self.log.info('Orientating ship for burn')
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

    def wait_until_burn(self, node, burn_time):
        self.log.info('Waiting until burn')
        self.conn.space_center.warp_to(node.ut - self.lead_time - (burn_time / 2.))

        self.log.info('Ready to execute burn')
        with self.conn.stream(getattr, node, 'time_to') as time_to_node:
            while time_to_node() - (burn_time / 2.) > 0:
                pass

    def execute_burn(self, node, burn_time):
        self.log.info('Executing burn')

        slowdown_dv = burn_time * self.burn_slowdown_factor

        with self.conn.stream(getattr, node, 'remaining_delta_v') as remaining_delta_v:
            dv = remaining_delta_v()
            prev_dv = dv

            while self.max_delta_v_error < dv:
                if self.quantize_dv(dv) > self.quantize_dv(prev_dv):
                    self.log.error('Breaking burn due to increasing manoeuvre delta-V')
                    break

                prev_dv = dv
                dv = remaining_delta_v()

                if dv > slowdown_dv:
                    self.vessel.control.throttle = 1.0
                else:
                    self.vessel.control.throttle = dv / slowdown_dv

        self.vessel.control.throttle = 0.0

    def quantize_dv(self, dv):
        return math2.quantize(dv, self.max_delta_v_error)
