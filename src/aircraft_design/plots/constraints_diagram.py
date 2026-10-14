import numpy as np
import plotly.graph_objects as go
import streamlit as st

CL_MAX_LDG = 3.00
CL_MAX_TO = 2.56
CD_MIN = 0.024
CD_I_COEFF = 1. / np.pi / 9.4 / 0.95  # With an assumed AR of 9.4 and oswald coeff of 0.95

V_Y = 175  # kts IAS, speed best rate of climb for A320

RHO_0 = 1.225  # In kg/m3
RHO_CRUISE = 0.38  # In kg/m3
G = 9.81
MU = 0.04


@st.cache_data
def constraints_diagram(
    stall_speed: float,
    tofl: float,
    rate_of_climb: float,
) -> go.Figure:
    """
    Returns the figure corresponding to the constraint diagram of the aircraft using data
    representative of commercial jet.

    :param stall_speed: desired stall speed for the aircraft in kts
    :param tofl: desired takeoff field length in m
    :param rate_of_climb: desired rate of climb at Vy
    :return: constraint diagram plot
    """

    fig = go.Figure()

    # Wing loading will be interpreted here as MTOW (kg)/wing area (m²), meaning since in some cases
    # mass varies, it will require adaptation
    wing_loading = np.linspace(100, 900, 801)

    # Stall constraint is fairly simple, we'll do it inline.
    wing_loading_ldg = RHO_0 * (stall_speed * 0.5144) ** 2.0 * CL_MAX_LDG / 2.0 / G

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
            showlegend=True
        ),
    )

    # Takeoff constraint
    takeoff_constraint_thrust_loading = _takeoff_constraint(tofl, wing_loading)
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=takeoff_constraint_thrust_loading,
            mode="lines",
            line={"color": "rgba(0, 0, 255, 1.0)", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(0, 0, 255, 0.10)",
            name="Takeoff constraint",
            showlegend=True
        ),
    )

    # Climb constraint
    climb_constraint_thrust_loading = _climb_constraint(rate_of_climb, wing_loading)
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb_constraint_thrust_loading,
            mode="lines",
            line={"color": "rgba(0, 255, 0, 1.0)", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(0, 255, 0, 0.10)",
            name="Climb constraint",
            showlegend=True
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
    fig.update_yaxes(
        range=[0., 1.]
    )

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
    :return:
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
    :return:
    """

    v_y_si = V_Y * 0.5144  # In m/s
    v_z_si = rate_of_climb * 0.00508  # In m/s
    p_dyn = 0.5 * RHO_0 * v_y_si ** 2.0  # Assumed at sea level because flemme

    return v_z_si / v_y_si + p_dyn / wing_loading * CD_MIN + CD_I_COEFF / p_dyn * wing_loading
