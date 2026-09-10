import numpy as np
import openmdao.api as om


class HimmelblauFunction(om.ExplicitComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.x_history = []
        self.y_history = []

    def initialize(self):
        self.options.declare("number_of_points", default=1)

    def setup(self):
        number_of_points = self.options["number_of_points"]

        self.add_input("x", val=0.0, shape=number_of_points, units="unitless")
        self.add_input("y", val=0.0, shape=number_of_points, units="unitless")

        self.add_output("z", val=0, shape=number_of_points, units="unitless")

    def setup_partials(self):
        number_of_points = self.options["number_of_points"]

        self.declare_partials(
            of="*",
            wrt="*",
            method="exact",
            rows=np.arange(number_of_points),
            cols=np.arange(number_of_points),
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        self.x_history.append(inputs["x"][0])
        self.y_history.append(inputs["y"][0])

        outputs["z"] = (inputs["x"] ** 2.0 + inputs["y"] - 11.0) ** 2.0 + (
            inputs["x"] + inputs["y"] ** 2.0 - 7.0
        ) ** 2.0

    def compute_partials(self, inputs, partials, discrete_inputs=None):

        partials["z", "x"] = (
            4.0 * inputs["x"] ** 3.0
            + 4.0 * inputs["x"] * inputs["y"]
            - 42.0 * inputs["x"]
            + 2.0 * inputs["y"] ** 2.0
            - 14.0
        )
        partials["z", "y"] = (
            2.0 * inputs["x"] ** 2.0
            + 4.0 * inputs["x"] * inputs["y"]
            + 4.0 * inputs["y"] ** 3.0
            - 26.0 * inputs["y"]
            - 22.0
        )
