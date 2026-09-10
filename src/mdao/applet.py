import pathlib
import streamlit as st
import pandas as pd
import openmdao.api as om
import plotly.graph_objects as go

import openmdao_components as component_library

DATA_FOLDER_PATH = pathlib.Path(__file__).parent / "data"
OPTIMIZER_LIST = [
    "COBYLA",
    "Powell",
    "BFGS",
    "basinhopping",
    "CG",
    "SLSQP",
    "shgo",
    "TNC",
    "L-BFGS-B",
    "differential_evolution",
    "Newton-CG",
    "COBYQA",
    "Nelder-Mead",
    "trust-constr",
    "dual_annealing",
]

TEST_FUNCTIONS = {
    "Sphere": {"filename": "data_sphere.csv", "openmdao_component": "SphereFunction"},
    "Jones": {"filename": "data_jones.csv", "openmdao_component": "JonesFunction"},
    "Bean": {"filename": "data_bean.csv", "openmdao_component": "BeanFunction"},
    "Himmelblau": {
        "filename": "data_himmelblau.csv",
        "openmdao_component": "HimmelblauFunction",
    },
    "Ackley": {"filename": "data_ackley.csv", "openmdao_component": "AckleyFunction"}
}


@st.cache_data
def load_data(test_function: str = "Sphere"):

    if test_function in TEST_FUNCTIONS:
        data_file_path = DATA_FOLDER_PATH / TEST_FUNCTIONS[test_function]["filename"]
    else:
        # Defaults to sphere problem when it is unknown
        data_file_path = DATA_FOLDER_PATH / TEST_FUNCTIONS["Sphere"]["filename"]

    return pd.read_csv(data_file_path)


def clear_optimizer_history():
    st.session_state["optim_desvar"]["x_history"] = []
    st.session_state["optim_desvar"]["y_history"] = []


def run_driver():
    # This function works if the problem has been set up before the first call
    # It also needs all model to implement a x and y history (because I can't use recorders)
    problem.model.objective_function.x_history = []
    problem.model.objective_function.y_history = []

    problem.run_driver()

    st.session_state["optim_desvar"]["x_history"] = (
        problem.model.objective_function.x_history
    )
    st.session_state["optim_desvar"]["y_history"] = (
        problem.model.objective_function.y_history
    )
    st.session_state["optim_desvar"]["objective"] = problem.get_val("z")[0]


if __name__ == "__main__":
    # Setup cache
    st.set_page_config(
        page_title="Optimisation",
        layout="wide",
    )

    if "optim_desvar" not in st.session_state:
        st.session_state.optim_desvar = {
            "x_history": [],
            "y_history": [],
            "objective": None,
        }

    st.title("Typical MDAO test cases")

    st.sidebar.write("Test case selection")
    st.session_state.test_function = st.sidebar.selectbox(
        label="Choose an test case",
        options=TEST_FUNCTIONS.keys(),
        on_change=clear_optimizer_history,
        index=list(TEST_FUNCTIONS.keys()).index("Sphere"),
    )

    # Load background data
    df = load_data(st.session_state.test_function)

    x_for_display = df["x"].to_numpy()
    range_x_for_display = max(x_for_display) - min(x_for_display)
    y_for_display = df["y"].to_numpy()
    range_y_for_display = max(y_for_display) - min(y_for_display)

    step_x = list(set(list(x_for_display)))[1] - list(set(list(x_for_display)))[0]
    step_y = list(set(list(y_for_display)))[1] - list(set(list(y_for_display)))[0]

    st.sidebar.write("Starting point selection")
    x_starting_point = st.sidebar.slider(
        "X starting point",
        min_value=min(x_for_display),
        max_value=max(x_for_display),
        step=step_x,
        on_change=clear_optimizer_history,
    )
    y_starting_point = st.sidebar.slider(
        "Y starting point",
        min_value=min(y_for_display),
        max_value=max(y_for_display),
        step=step_y,
        on_change=clear_optimizer_history,
    )

    st.sidebar.write("Optimizer selection")
    st.session_state.optimizer_selection = st.sidebar.selectbox(
        label="Choose an optimizer",
        options=OPTIMIZER_LIST,
        on_change=clear_optimizer_history,
    )
    st.session_state.optimizer_tolerance = st.sidebar.number_input(
        "Optimizer tolerance in power of 10",
        min_value=-9,
        max_value=-1,
        step=1,
        value=-5,
    )

    st.sidebar.button("Run Driver", on_click=run_driver)

    problem = om.Problem(reports=False)
    model = problem.model
    component_name = TEST_FUNCTIONS[st.session_state.test_function][
        "openmdao_component"
    ]
    subsystem = component_library.__dict__[component_name]()
    model.add_subsystem("objective_function", subsys=subsystem, promotes=["*"])

    problem.driver = om.ScipyOptimizeDriver()
    problem.driver.options["optimizer"] = st.session_state.optimizer_selection
    # COBYLA by default, since first name in the list
    problem.driver.options["tol"] = 10**st.session_state.optimizer_tolerance

    model.add_design_var("x", lower=min(x_for_display), upper=max(x_for_display))
    model.add_design_var("y", lower=min(y_for_display), upper=max(y_for_display))
    model.add_objective("z")

    problem.setup()

    problem.set_val("x", x_starting_point)
    problem.set_val("y", y_starting_point)

    if st.session_state["optim_desvar"]["x_history"]:
        optim_x, optim_y, objective_value = (
            st.session_state["optim_desvar"]["x_history"],
            st.session_state["optim_desvar"]["y_history"],
            st.session_state["optim_desvar"]["objective"],
        )

        for_print_obj = f"{objective_value:.3f}"
        for_print_desvar = f"[{optim_x[-1]:.3f}, {optim_y[-1]:.3f}]"
        for_print_n_func_call = f"{len(optim_x) - 1}"

    else:
        optim_x, optim_y, objective_value = [], [], None

        for_print_obj = "N/A"
        for_print_desvar = "[N/A, N/A]"
        for_print_n_func_call = "N/A"

    col_heatmap, col_results = st.columns([4, 1])

    with col_heatmap:
        fig = go.Figure(
            data=go.Heatmap(
                z=df["z"].to_numpy(),
                x=x_for_display,
                y=y_for_display,
                colorscale="Viridis",
                hovertemplate="X: %{x}<br>Y: %{y}<br>Value: %{z}<extra></extra>",
            )
        )
        starting_point = go.Scatter(
            x=[x_starting_point],
            y=[y_starting_point],
            marker=dict(color="black", size=15, symbol="cross"),
            showlegend=False,
        )
        fig.add_trace(starting_point)

        fig.update_layout(
            xaxis_title="X",
            yaxis_title="Y",
            height=int(800 * range_y_for_display / range_x_for_display),
            width=800,
            margin=dict(l=5, r=5, t=5, b=5),
        )
        fig.update_xaxes(range=[min(x_for_display), max(x_for_display)])
        fig.update_yaxes(range=[min(y_for_display), max(y_for_display)])

        if optim_x:
            optimizer_trace = go.Scatter(
                x=optim_x,
                y=optim_y,
                mode="lines+markers",
                marker=dict(color="red", size=8),
                line=dict(color="red"),
                showlegend=False,
                name="Optimizer",
                customdata=list(range(0, len(optim_x) + 0)),
                hovertemplate="X: %{x}<br>Y: %{y}<br>Func call: %{customdata}<extra></extra>",
            )
            fig.add_trace(optimizer_trace)

        st.plotly_chart(fig)

    with col_results:
        st.subheader("Optimisation results")
        st.metric(label="Optimal point", value=for_print_desvar)
        st.metric(label="Score", value=for_print_obj)
        st.metric(label="Function calls", value=for_print_n_func_call)
