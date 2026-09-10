import numpy as np
import openmdao.api as om


class BeanFunction(om.ExplicitComponent):
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

        outputs["z"] = (
            (1 - inputs["x"]) ** 2.0
            + (1 - inputs["y"]) ** 2.0
            + 0.5 * inputs["x"] ** 4.0
            - 2.0 * inputs["x"] ** 2.0 * inputs["y"]
            + 2.0 * inputs["y"] ** 2.0
        )

    def compute_partials(self, inputs, partials, discrete_inputs=None):

        partials["z", "x"] = (
            -2.0 * (1 - inputs["x"])
            + 2.0 * inputs["x"] ** 3.0
            - 4.0 * inputs["x"] * inputs["y"]
        )
        partials["z", "y"] = (
            -2.0 * (1 - inputs["y"]) - 2.0 * inputs["x"] ** 2.0 + 4.0 * inputs["y"]
        )
