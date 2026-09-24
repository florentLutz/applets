import pathlib

import numpy as np
import openmdao.api as om
import pandas as pd

from mdao.openmdao_components.sphere import SphereFunction

if __name__ == "__main__":
    search_domain_x = np.linspace(-2, 2, 101)
    search_domain_y = np.linspace(-2, 2, 101)

    search_domain_x, search_domain_y = np.meshgrid(search_domain_x, search_domain_y)
    meshgrid_x = search_domain_x.flatten()
    meshgrid_y = search_domain_y.flatten()

    problem = om.Problem(reports=False)
    model = problem.model
    model.add_subsystem(
        "data",
        subsys=SphereFunction(number_of_points=len(meshgrid_x)),
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

    output_file_path = pathlib.Path(__file__).parent.parent / "data" / "data_sphere.csv"

    df.to_csv(output_file_path, index=False)
