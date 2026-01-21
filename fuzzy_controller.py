"""
Fuzzy PD controller

Trapezoidal membership functions
MIN T-norm
MAX aggregation
"""

import numpy as np

class FuzzyController:

    # preparation of controller
    def __init__(
        self,
        output_min: float = -150.0,
        output_max: float = 250.0,
        universe_min: float = -1.0,
        universe_max: float = 1.0,
        universe_step: float = 0.01,
    ):
        self.output_min = output_min
        self.output_max = output_max

        self.u_universe = np.arange(universe_min, universe_max, universe_step)

        self.prev_error = 0.0

    # reset internal state of fuzzy controller
    def reset(self):
        self.prev_error = 0.0

    # implement zeros for p, i, and d (for )
    def get_components(self):
        return 0.0, 0.0, 0.0

    # membership function
    @staticmethod
    def trapmf(x, a, b, c, d):
        if x <= a or x >= d:
            return 0.0
        elif b <= x <= c:
            return 1.0
        elif a < x < b:
            return (x - a) / (b - a)
        else:
            return (d - x) / (d - c)

    # define fuzzify intervals (like P in PID)
    def fuzzify_error(self, e):
        return {
            "NB": self.trapmf(e, -100, -100, -60, -40),
            "NS": self.trapmf(e, -60, -30, -15, 0),
            "Z":  self.trapmf(e, -10, -2, 2, 10),
            "PS": self.trapmf(e, 0, 15, 30, 60),
            "PB": self.trapmf(e, 40, 60, 100, 100),
        }

    # fuzzify direction of changes (like D in PID)
    def fuzzify_ce(self, ce):
        return {
            "N": self.trapmf(ce, -100, -80, -40, 0),
            "Z": self.trapmf(ce, -10, -1, 1, 10),
            "P": self.trapmf(ce, 0, 40, 80, 100),
        }

    # output values
    def output_sets(self, u):
        return {
            "NB": self.trapmf(u, -1.0, -1.0, -0.8, -0.5),
            "NS": self.trapmf(u, -0.8, -0.5, -0.2, 0.0),
            "Z":  self.trapmf(u, -0.11, -0.01, 0.01, 0.11),
            "PS": self.trapmf(u, 0.0, 0.2, 0.5, 0.8),
            "PB": self.trapmf(u, 0.5, 0.8, 1.0, 1.0),
        }

    # rules of controller (if fuzzify_error is "PB" and fuzzify_ce is "P" take output values from "PB")
    def rules(self, e, ce):
        return [
            ("PB", "P", "PB"),
            ("PB", "Z", "PB"),
            ("PB", "N", "PS"),

            ("PS", "P", "PB"),
            ("PS", "Z", "PS"),
            ("PS", "N", "Z"),

            ("Z",  "P", "PS"),
            ("Z",  "Z", "Z"),
            ("Z",  "N", "NS"),

            ("NS", "P", "Z"),
            ("NS", "Z", "NS"),
            ("NS", "N", "NB"),

            ("NB", "P", "NS"),
            ("NB", "Z", "NB"),
            ("NB", "N", "NB"),
        ]

    # making decision from rules
    def infer(self, e_sets, ce_sets):
        aggregated = np.zeros_like(self.u_universe)

        for e_label, ce_label, u_label in self.rules(e_sets, ce_sets):
            activation = min(e_sets[e_label], ce_sets[ce_label])    # T-norm MIN

            if activation == 0:
                continue

            u_mf = np.array([
                min(activation, self.output_sets(u)[u_label])
                for u in self.u_universe
            ])

            aggregated = np.maximum(aggregated, u_mf)   # S-norm MAX

        return aggregated

    # one, number output from fuzzy rules
    def defuzzify(self, aggregated):
        if np.sum(aggregated) == 0:
            return 0.0

        return np.sum(self.u_universe * aggregated) / np.sum(aggregated)

    # control cycle
    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        error = setpoint - measurement
        ce = (error - self.prev_error) / dt if dt > 0 else 0.0

        e_sets = self.fuzzify_error(error)
        ce_sets = self.fuzzify_ce(ce)

        aggregated = self.infer(e_sets, ce_sets)
        u_norm = self.defuzzify(aggregated)

        # powe scalling
        u = u_norm * self.output_max

        # saturation
        u = max(self.output_min, min(u, self.output_max))

        self.prev_error = error
        return u

