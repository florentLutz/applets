import numpy as np
import plotly.graph_objects as go
import streamlit as st

CL_MAX_LDG = 3.00
CL_MAX_TO = 2.56
CD_MIN = 0.024
CD_I_COEFF = (
    1.0 / np.pi / 9.4 / 0.95
)  # With an assumed AR of 9.4 and oswald coeff of 0.95

V_Y = 175  # kts IAS, speed best rate of climb for A320

RHO_0 = 1.225  # In kg/m3
P_CRUISE = 21662  # In Pa, pressure at 39000 ft
G = 9.81
MU = 0.04


@st.cache_data
def constraints_diagram(
    stall_speed: float,
    tofl: float,
    rate_of_climb: float,
    cruise_mach: float,
    wing_loading_design: float,
    thrust_loading_design: float,
) -> (go.Figure, list, list):
    """
    Returns the figure corresponding to the constraint diagram of the aircraft using data
    representative of commercial jet and assess the validity of the input design point

    :param stall_speed: desired stall speed for the aircraft in kts
    :param tofl: desired takeoff field length in m
    :param rate_of_climb: desired rate of climb at Vy
    :param cruise_mach: desired cruise Mach number
    :param wing_loading_design: wing loading at design point
    :param thrust_loading_design: thrust loading at design point
    :param cruise_mach: desired cruise Mach number
    :return: constraint diagram plot, a list of satisfied constraints,
             a list of violated constraints
    """

    respected_constraints, broken_constraints = [], []

    # Wing loading will be interpreted here as MTOW (kg)/wing area (m²), meaning since in some cases
    # mass varies, it will require adaptation
    wing_loading = np.linspace(100, 900, 801)

    # Stall constraint is fairly simple, we'll do it inline. 0.85 is the MLW to MTOW ratio
    wing_loading_ldg = (
        RHO_0 * (stall_speed * 0.5144) ** 2.0 * CL_MAX_LDG / 2.0 / G / 0.85
    )
    if wing_loading_design <= wing_loading_ldg:
        respected_constraints.append("Landing")
    else:
        broken_constraints.append("Landing")

    takeoff_constraint_thrust_loading = _takeoff_constraint(tofl, wing_loading)
    if thrust_loading_design >= np.interp(
        wing_loading_design, wing_loading, takeoff_constraint_thrust_loading
    ):
        respected_constraints.append("Takeoff")
    else:
        broken_constraints.append("Takeoff")

    climb_constraint_thrust_loading = _climb_constraint(rate_of_climb, wing_loading)
    if thrust_loading_design >= np.interp(
        wing_loading_design, wing_loading, climb_constraint_thrust_loading
    ):
        respected_constraints.append("Climb")
    else:
        broken_constraints.append("Climb")

    cruise_constraint_thrust_loading = _cruise_constraint(cruise_mach, wing_loading)
    if thrust_loading_design >= np.interp(
        wing_loading_design, wing_loading, cruise_constraint_thrust_loading
    ):
        respected_constraints.append("Cruise")
    else:
        broken_constraints.append("Cruise")

    fig = _create_figure(
        wing_loading,
        wing_loading_ldg,
        takeoff_constraint_thrust_loading,
        climb_constraint_thrust_loading,
        cruise_constraint_thrust_loading,
    )

    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=[wing_loading_design],
            y=[thrust_loading_design],
            marker={
                "size": 20,
                "color": "red",
                "symbol": "star"

            },
            name="Design point"
        )
    )

    return fig, respected_constraints, broken_constraints


@st.cache_data
def _create_figure(
    wing_loading: np.ndarray,
    wing_loading_ldg: float,
    takeoff_constraint_thrust_loading: np.ndarray,
    climb_constraint_thrust_loading: np.ndarray,
    cruise_constraint_thrust_loading: np.ndarray,
) -> go.Figure:
    """
    Creates the figure associated with the input constraints

    :param wing_loading: array of wing loading at which constraints are evaluated
    :param wing_loading_ldg: limit wing loading for stall criterio
    :param takeoff_constraint_thrust_loading: takeoff constraint at input wing loading
    :param climb_constraint_thrust_loading: climb constraint at input wing loading
    :param cruise_constraint_thrust_loading: cruise constraint at input wing loading
    :return:
    """

    fig = go.Figure()

    # Stall constraint
    fig.add_vrect(
        x0=wing_loading_ldg,
        x1=max(wing_loading),
        fillcolor="rgba(150, 150, 150, 0.10)",
        line_width=0,
        layer="below",
    )
    fig.add_vline(
        x=wing_loading_ldg,
        line_color="gray",
        line_dash="dash",
        line_width=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0.01, 0.01],
            mode="lines",
            line={"color": "rgba(150, 150, 150, 1.0)", "width": 2, "dash": "dash"},
            fill="tozeroy",
            fillcolor="rgba(150, 150, 150, 0.1)",
            name="Landing constraint",
            showlegend=True,
        ),
    )
    # Takeoff constraint
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=takeoff_constraint_thrust_loading,
            mode="lines",
            line={"color": "rgba(0, 0, 255, 1.0)", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(0, 0, 255, 0.10)",
            name="Takeoff constraint",
            showlegend=True,
        ),
    )
    # Climb constraint
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb_constraint_thrust_loading,
            mode="lines",
            line={"color": "rgba(0, 255, 0, 1.0)", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(0, 255, 0, 0.10)",
            name="Climb constraint",
            showlegend=True,
        ),
    )
    # Cruise constraint
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=cruise_constraint_thrust_loading,
            mode="lines",
            line={"color": "rgba(255, 0, 0, 1.0)", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(255, 0, 0, 0.10)",
            name="Cruise constraint",
            showlegend=True,
        ),
    )

    fig.update_layout(
        height=800,
        width=800,
    )
    fig.update_xaxes(
        range=[min(wing_loading), max(wing_loading)],
        ticks="outside",
        tickmode="array",
        tickvals=np.arange(min(wing_loading), max(wing_loading), 100),
    )
    fig.update_yaxes(range=[0.0, 1.0])

    return fig


@st.cache_data
def _takeoff_constraint(
    tofl: float,
    wing_loading: np.ndarray,
) -> np.ndarray:
    """
    Returns the trace corresponding to the takeoff roll constraints. Will be computed using the
    "magic line" formula.

    :param tofl: desired takeoff field length in m
    :param wing_loading: wing loading in kg/m²
    :return: the thrust loading required to satisfy the takeoff constraint at the input wing loading
    """
    wing_loading_imperial_units = wing_loading * 0.2048161  # In lbs/ft²
    tofl_ft = tofl / 0.3048

    return 37.5 / CL_MAX_TO / tofl_ft * wing_loading_imperial_units


@st.cache_data
def _climb_constraint(
    rate_of_climb: float,
    wing_loading: np.ndarray,
) -> np.ndarray:
    """
    Returns the trace corresponding to the takeoff roll constraints. Will be computed using the
    "magic line" formula.

    :param rate_of_climb: desired rate of climb in ft/min at Vy
    :param wing_loading: wing loading in kg/m²
    :return: the thrust loading required to satisfy the climb constraint at the input wing loading
    """

    v_y_si = V_Y * 0.5144  # In m/s
    v_z_si = rate_of_climb * 0.00508  # In m/s
    p_dyn = 0.5 * RHO_0 * v_y_si**2.0  # Assumed at sea level because flemme

    return (
        v_z_si / v_y_si
        + p_dyn / wing_loading * CD_MIN
        + CD_I_COEFF / p_dyn * wing_loading
    )


@st.cache_data
def _cruise_constraint(
    cruise_mach: float,
    wing_loading: np.ndarray,
) -> np.ndarray:
    """
    Returns the trace corresponding to the takeoff roll constraints. Will be computed using the
    "magic line" formula.

    :param cruise_mach: desired cruise Mach number
    :param wing_loading: wing loading in kg/m²
    :return: the thrust loading required to satisfy the cruise constraint at the input wing loading
    """

    p_dyn = 0.7 * P_CRUISE * cruise_mach**2.0

    return p_dyn * CD_MIN / wing_loading + CD_I_COEFF / p_dyn * wing_loading
