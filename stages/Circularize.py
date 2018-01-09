import math

from .NodeManoeuvre import NodeManoeuvre


class Circularize(NodeManoeuvre):
    def execute(self):
        self.log.info('Planning circularization manoeuvre')
        delta_v = self.calc_delta_v()
        node = self.add_node(self.conn.space_center.ut + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)
        self.perform_manoeuvre(node)

    def calc_delta_v(self):
        # vis-viva equation

        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        return v2 - v1
