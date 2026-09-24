import pathlib

import numpy as np
import openmdao.api as om
import pandas as pd

from mdao.openmdao_components.jones import JonesFunction

if __name__ == "__main__":
    search_domain_x = np.linspace(-1, 3, 101)
    search_domain_y = np.linspace(-1, 3, 101)

    x_for_partials = search_domain_x[int(len(search_domain_x) / 2)]
    y_for_partials = search_domain_y[int(len(search_domain_y) / 2)]

    search_domain_x, search_domain_y = np.meshgrid(search_domain_x, search_domain_y)
    meshgrid_x = search_domain_x.flatten()
    meshgrid_y = search_domain_y.flatten()

    problem = om.Problem(reports=False)
    model = problem.model
    model.add_subsystem(
        "data",
        subsys=JonesFunction(number_of_points=len(meshgrid_x)),
        promotes=["*"],
    )
    model.nonlinear_solver = om.NonlinearRunOnce()
    problem.setup()

    problem.set_val("x", val=meshgrid_x)
    problem.set_val("y", val=meshgrid_y)

    problem.run_model()

    meshgrid_z = problem.get_val("z")

    df = pd.DataFrame(
        {
            "x": meshgrid_x,
            "y": meshgrid_y,
            "z": meshgrid_z,
        }
    )

    output_file_path = pathlib.Path(__file__).parent.parent / "data" / "data_jones.csv"

    df.to_csv(output_file_path, index=False)

    # Check partials
    partials_problem = om.Problem(reports=False)
    partials_model = partials_problem.model
    partials_model.add_subsystem(
        "data",
        subsys=JonesFunction(),
        promotes=["*"],
    )
    partials_model.nonlinear_solver = om.NonlinearRunOnce()
    partials_problem.setup()
    partials_problem.set_val("x", val=x_for_partials)
    partials_problem.set_val("y", val=y_for_partials)

    partials_problem.run_model()
    partials_problem.check_partials(compact_print=True)
