import openmdao.api as om

from openmdao_components import SphereFunction


if __name__ == "__main__":
    problem = om.Problem()
    model = problem.model
    model.add_subsystem("objective_function", subsys=SphereFunction(), promotes=["*"])

    problem.driver = om.ScipyOptimizeDriver()
    problem.driver.options["optimizer"] = "SLSQP"
    problem.driver.options["tol"] = 1e-9
    problem.driver.options["disp"] = True

    model.add_design_var("x", lower=-2.0, upper=2.0)
    model.add_design_var("y", lower=-2.0, upper=2.0)
    model.add_objective("z")

    problem.setup()

    problem.set_val("x", -1.9)
    problem.set_val("y", -1.0)

    problem.run_driver()

    print(model.objective_function.x_history)
