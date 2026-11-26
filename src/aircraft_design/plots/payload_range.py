import numpy as np
import plotly.graph_objects as go
import streamlit as st

from .constants import DESIGN_PAX_MASS, MAX_PAX_MASS

SFC = 17.0  # g/kN/s
SOS_CRUISE = 295.4


def payload_range(
    mtow: float,
    mto_thrust: float,
    npax: int,
    design_range: float,
    owe: float,
    wing_area: float,
    k_l_d_max: float,
    k_sfc: float,
    k_owe: float,
) -> go.Figure:
    """
    Returns a figure illustrating the payload range capabilities of the aircraft with the reference
    mission highlighted

    :param mtow: MTOW of the aircraft in kg
    :param owe: mass of the aircraft when empty
    :param mto_thrust: total thrust at sea level static in N
    :param npax: number of passenger in the cabin
    :param design_range: range of the aircraft's design mission, in nm
    :param wing_area: area of the wing in m²
    :param k_l_d_max: improvement factor for the aerodynamic
    :param k_sfc: improvement factor for the propulsion
    :param k_owe: improvement factor for the k_owe
    :return: aircraft design mission plot figure, aircraft empty mass according to performance
    criteria and mission fuel
    """

    # Need it here, but isn't computed anywhere, so will infer it from wing area. 0.14 is the
    # average wing thickness
    mfw = (
        4570.0
        + wing_area**1.5
        * 224
        * st.session_state.aircraft_data.wing_aspect_ratio**-0.4
        * 0.14
    )

    # The assumption that the MTOW line is an actual line will introduce a 1% difference on the
    # range achievable at design payload. To make it nicer, we will introduce a small scaling factor
    range_mtow_segment = _compute_range(
        np.array([mtow, mtow]),
        owe,
        mto_thrust,
        np.array([npax * MAX_PAX_MASS, mtow - owe - mfw]),
        1.0,
        1.0,
        1.0,
    )
    scaling_factor = (
        np.interp(
            npax * DESIGN_PAX_MASS,
            np.flip(np.array([npax * MAX_PAX_MASS, mtow - owe - mfw])),
            np.flip(range_mtow_segment),
        )
        / design_range
    )

    # First draw the envelope, at point A, B, C, D and E. C won't actually be computed but should
    # fall on the design mission. Point A doesn't need to be computed
    payload_array = np.array([npax * MAX_PAX_MASS, mtow - owe - mfw, 0.0])
    tow_array = np.array(
        [
            mtow,
            mtow,
            k_owe * owe + mfw,
        ]
    )
    range_array = (
        _compute_range(
            tow_array, owe, mto_thrust, payload_array, k_l_d_max, k_sfc, k_owe
        )
        / scaling_factor
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=np.concatenate((np.array([0]), range_array)),
            y=np.concatenate((np.array([npax * MAX_PAX_MASS]), payload_array)),
            mode="lines+markers",
            name="Payload-range enveloppe",
            line={"color": "#4779D0", "width": 2.5, "shape": "linear"},
            marker={
                "size": 15,
                "color": "#4779D0",
                "line": {"color": "white", "width": 2.5},
                "symbol": "circle",
            },
            hovertemplate=(
                "Range: %{x:.0f} NM<br>Payload mass: %{y:,.0f} kg<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[design_range],
            y=[npax * DESIGN_PAX_MASS],
            mode="markers",
            name="Design mission",
            marker={
                "size": 20,
                "color": "  #79D047",
                "line": {"color": "white", "width": 3},
                "symbol": "circle",
            },
            hovertemplate=(
                "Range: %{x:.0f} NM<br>Payload mass: %{y:,.0f} kg<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title={
            "text": "Aircraft design mission",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        xaxis={
            "title": "Range [nm]",
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
        },
        yaxis={
            "title": "Payload [kg]",
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
        },
        template="plotly_white",
        width=1536,
        height=768,
        margin={"l": 40, "r": 25, "t": 48, "b": 40},
        font={"family": "Arial", "size": 15, "color": "#344563"},
        showlegend=True,
        legend={"yanchor": "top", "y": 0.99, "xanchor": "right", "x": 0.99},
    )

    return fig


def _compute_range(
    tow: float | np.ndarray,
    owe: float,
    mto_thrust: float,
    payload_mass: float | np.ndarray,
    k_l_d_max: float,
    k_sfc: float,
    k_owe: float,
):
    """
    Computes the range that the aircraft can achieve in the given configuration. Will use the
    formulas than in the design mission but since they will be used differently and for speed up, it
    will be duplicated here, which is never a good thing.

    :param tow: mass of the aircraft at takeoff
    :param owe: mass of the aircraft when empty
    :param mto_thrust: total thrust at sea level static in N
    :param payload_mass: payload mass at takeoff
    :param k_l_d_max: improvement factor for the aerodynamic
    :param k_sfc: improvement factor for the propulsion
    :param k_owe: improvement factor for the k_owe
    :return: the range that can be achieved in the given configuration
    """

    fuel_taxi_takeoff = 0.9 / 100.0 * 2 * mto_thrust / 2.0 * 0.2248089431
    distance_taxi_takeoff = 0.0

    tas_climb = 400.0 * 0.5144  # In m/s, 400 kts based on a 300 KCAS at 20000ft
    vz_climb = (
        st.session_state.roc_cons * 0.00508 / 1.5625
    )  # Avg value, Vz decreases after initial climb
    gamma_climb = np.arcsin(vz_climb / tas_climb)
    vx_climb = tas_climb * np.cos(gamma_climb)
    time_to_climb = 35000 / st.session_state.roc_cons * 60.0

    mass_start_climb = tow - fuel_taxi_takeoff
    thrust_climb = (
        mass_start_climb
        * 9.81
        * (
            np.sin(gamma_climb) + 1.0 / (st.session_state.l_d_max * k_l_d_max)
        )  # Unrealistic to always fly at max L/D but hey, simpler to assume it
    )

    fuel_climb = (
        1.5 * SFC * thrust_climb / 1000.0 * time_to_climb / 1000.0
    )  # N to kN, and g to kg, 1.5 penalty to account for not ideal climb profile.
    distance_climb = vx_climb * time_to_climb / 1852.0  # In nautical miles
    start_of_cruise_mass = mass_start_climb - fuel_climb

    fuel_descent = fuel_climb / 5.0
    distance_descent = distance_climb * 1.5

    fuel_taxi_in = 0.1 / 100.0 * 2 * mto_thrust / 2.0 * 0.2248089431
    distance_taxi_in = 0.0

    cruise_speed = SOS_CRUISE * st.session_state.m_cons
    end_of_cruise_mass = (
        1.06 * (k_owe * owe + payload_mass) + fuel_taxi_in + fuel_descent
    )

    cruise_range = (
        cruise_speed
        * (st.session_state.l_d_max * k_l_d_max)
        / 9.81
        / (k_sfc * SFC * 1e-6)
        * np.log(start_of_cruise_mass / end_of_cruise_mass)
        / 1852.0
    )  # In nm

    return (
        distance_taxi_takeoff
        + distance_climb
        + cruise_range
        + distance_descent
        + distance_taxi_in
    )
