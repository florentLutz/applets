import numpy as np
import plotly.graph_objects as go
import streamlit as st

SFC = 15.0  # g/kN/s or kg/N/s
SOS_CRUISE = 295.4
NB_POINT_SWEEP = 500


# @st.cache_data
def aircraft_design_mission(
    mtow: float, mto_thrust: float, npax: int, design_range: float
) -> (go.Figure, float, float):
    """
    Returns a figure illustrating the design mission of the aircraft.

    :param mtow: MTOW of the aircraft in kg
    :param mto_thrust: total thrust at sea level static in N
    :param npax: number of passenger in the cabin
    :param design_range: range of the aircraft's design mission, in nm
    :return: aircraft design mission plot figure, aircraft empty mass according to performance
    criteria and mission fuel
    """
    fuel_dict, distance_dict, owe = _compute_design_mission(
        design_range, mtow, npax, mto_thrust
    )

    range_array = np.cumsum(np.array([0] + list(distance_dict.values())))  # In nm
    mass_array = mtow - np.cumsum(np.array([0] + list(fuel_dict.values())))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=range_array,
            y=mass_array,
            mode="lines+markers",
            name="Aircraft mass",
            line={"color": "#4779D0", "width": 2.5, "shape": "linear"},
            marker={
                "size": 7,
                "color": "#4779D0",
                "line": {"color": "white", "width": 1.5},
                "symbol": "circle",
            },
            hovertemplate=("Range: %{x:.0f} NM<br>Mass: %{y:,.0f} kg<extra></extra>"),
        )
    )

    fig.add_vrect(
        x0=range_array[1],
        x1=range_array[2],
        fillcolor="orange",
        opacity=0.10,
        line_width=0,
        annotation_text="Climb",
        annotation_position="top left",
        annotation_font={"size": 20, "color": "orange"},
    )

    fig.add_vrect(
        x0=range_array[2],
        x1=range_array[3],
        fillcolor="#3498DB",
        opacity=0.08,
        line_width=0,
        annotation_text="Cruise",
        annotation_position="top",
        annotation_font={"size": 20, "color": "#3498DB"},
    )

    fig.add_vrect(
        x0=range_array[3],
        x1=range_array[4],
        fillcolor="green",
        opacity=0.10,
        line_width=0,
        annotation_text="Descent",
        annotation_position="top right",
        annotation_font={"size": 20, "color": "green"},
    )

    fig.add_hline(
        y=mtow,
        line_dash="dash",
        line_color="#3498DB",
        annotation_text="MTOW",
        annotation_position="bottom right",
        annotation_font={"size": 20, "color": "#3498DB"},
    )
    fig.add_hline(
        y=mass_array[-1],
        line_dash="dash",
        line_color="#27AE60",
        annotation_text="MLW",
        annotation_position="top left",
        annotation_font={"size": 20, "color": "#27AE60"},
    )

    fig.add_annotation(
        x=0,
        y=mtow,
        text="Taxi out and takeoff",
        showarrow=False,
        xshift=-15,
        textangle=-90,
        xanchor="center",
        yanchor="top",
        font={"size": 20},
        yshift=-15,
    )

    fig.add_annotation(
        x=design_range,
        y=mass_array[-1],
        text="Landing and taxi in",
        showarrow=False,
        xshift=15,
        yshift=15,
        textangle=-90,
        xanchor="center",
        yanchor="bottom",
        font={"size": 20},
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
            "title": "Aircraft mass [kg]",
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
        },
        template="plotly_white",
        width=1536,
        height=768,
        margin={"l": 40, "r": 25, "t": 48, "b": 40},
        font={"family": "Arial", "size": 15, "color": "#344563"},
        showlegend=False,
    )

    return fig, owe, mass_array[0] - mass_array[-1]


# @st.cache_data
def _compute_design_mission(
    design_range: float, mtow: float | np.ndarray, npax: int, mto_thrust: float
) -> (dict, dict, float):
    """
    Returns the performance of the aircraft on the design mission

    :param mtow: MTOW of the aircraft in kg
    :param mto_thrust: total thrust at sea level static in N
    :param npax: number of passenger in the cabin
    :param design_range: range of the aircraft's design mission, in nm
    :return: A dict with the fuel consumed in each phase, the distance flown in each phase and the
    OWE
    """

    fuel_taxi_takeoff = 0.9 / 100.0 * 2 * mto_thrust / 2.0 * 0.2248089431
    distance_taxi_takeoff = 0.0

    tas_climb = 400.0 * 0.5144  # In m/s, 400 kts based on a 300 KCAS at 20000ft
    vz_climb = st.session_state.roc_cons * 0.00508
    gamma_climb = np.arcsin(vz_climb / tas_climb)
    vx_climb = tas_climb * np.cos(gamma_climb)
    time_to_climb = 35000 / st.session_state.roc_cons * 60.0

    mass_start_climb = mtow - fuel_taxi_takeoff
    thrust_climb = (
        mass_start_climb * 9.81 * (np.sin(gamma_climb) + 1.0 / st.session_state.l_d_max)
    )

    fuel_climb = (
        SFC * thrust_climb / 1000.0 * time_to_climb / 1000.0
    )  # N to kN, and g to kg
    distance_climb = vx_climb * time_to_climb / 1852.0  # In nautical miles
    start_of_cruise_mass = mass_start_climb - fuel_climb

    fuel_descent = fuel_climb / 5.0
    distance_descent = distance_climb * 1.5

    fuel_taxi_in = 0.1 / 100.0 * 2 * mto_thrust / 2.0 * 0.2248089431
    distance_taxi_in = 0.0

    cruise_range = (design_range - distance_climb - distance_descent) * 1852  # In m
    cruise_speed = SOS_CRUISE * st.session_state.m_cons

    # Brute force
    if type(mtow) is float or type(mtow) is np.float64:
        owe_sweep = np.linspace(0.3 * mtow, 0.7 * mtow, NB_POINT_SWEEP)
        zfw_sweep = owe_sweep + npax * 95.0
        lw_sweep = (
            zfw_sweep * 1.06
        )  # 6% reserve, won't be computed here, but could for a nice graph
        end_of_cruise_mass = lw_sweep + fuel_taxi_in + fuel_descent

        fuel_cruise = end_of_cruise_mass * (
            np.exp(
                cruise_range
                * SFC
                * 1e-6
                * 9.81
                / st.session_state.l_d_max
                / cruise_speed
            )
            - 1.0
        )
        idx_right_guess = np.argmin(
            np.abs(start_of_cruise_mass - end_of_cruise_mass - fuel_cruise)
        )
        correct_cruise_fuel = fuel_cruise[idx_right_guess]
        correct_owe = owe_sweep[idx_right_guess]
    else:  # it is an array
        owe_sweep = np.array(
            [np.linspace(0.3 * m, 0.7 * m, NB_POINT_SWEEP) for m in mtow]
        )
        zfw_sweep = owe_sweep + npax * 95.0
        lw_sweep = (
            zfw_sweep * 1.06
        )  # 6% reserve, won't be computed here, but could for a nice graph
        end_of_cruise_mass = lw_sweep + fuel_taxi_in[:, np.newaxis] + fuel_descent[:, np.newaxis]
        fuel_cruise = end_of_cruise_mass * (
            np.exp(
                cruise_range
                * SFC
                * 1e-6
                * 9.81
                / st.session_state.l_d_max
                / cruise_speed
            )
            - 1.0
        )
        idx_right_guess = np.argmin(
            np.abs(start_of_cruise_mass[:, np.newaxis] - end_of_cruise_mass - fuel_cruise), axis=1
        )
        correct_cruise_fuel = fuel_cruise[np.arange(len(mtow)), idx_right_guess]

        correct_owe = owe_sweep[np.arange(len(mtow)), idx_right_guess]

    fuel_dict = {
        "Taxi out and takeoff": fuel_taxi_takeoff,
        "Climb": fuel_climb,
        "Cruise": correct_cruise_fuel,
        "Descent": fuel_descent,
        "Taxi in": fuel_taxi_in,
    }
    distance_dict = {
        "Taxi out and takeoff": distance_taxi_takeoff,
        "Climb": distance_climb,
        "Cruise": cruise_range / 1852.0,
        "Descent": distance_descent,
        "Taxi in": distance_taxi_in,
    }

    return fuel_dict, distance_dict, correct_owe
