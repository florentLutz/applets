import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


@st.cache_data
def aircraft_empty_mass_breakdown(
    wing_area: float,
    mtow: float,
    htp_area: float,
    vtp_area: float,
    mto_thrust: float,
    npax: int,
) -> (go.Figure, float):
    """
    Returns a figure plot of the breakdown of the aircraft empty mass.

    :param wing_area: area of the wing in m²
    :param mtow: MTOW of the aircraft in kg
    :param htp_area: area of the HTP in m²
    :param vtp_area: area of the VTP in m²
    :param mto_thrust: total thrust at sea level static in N
    :param npax: number of passenger in the cabin
    :return: aircraft empty mass breakdown plot figure, aircraft empty mass
    """

    mass_breakdown, _ = _compute_mass_breakdown(
        wing_area, mtow, htp_area, vtp_area, mto_thrust, npax
    )

    sorted_mass_breakdown = sorted(
        mass_breakdown.items(), key=lambda x: x[1], reverse=True
    )

    components = [item[0] for item in sorted_mass_breakdown]
    masses = [item[1] for item in sorted_mass_breakdown]

    owe = sum(masses)
    masses_in_percentages = [mass / owe * 100 for mass in masses]

    vertical_spacing = 0.1

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.50, 0.50],
        specs=[[{"type": "bar"}], [{"type": "domain"}]],
        subplot_titles=[
            "<b>Component mass distribution</b>",
            "<b>Mass contribution</b>",
        ],
        vertical_spacing=vertical_spacing,
    )

    fig.add_trace(
        go.Bar(
            x=masses,
            y=components,
            orientation="h",
            marker={"line": {"color": "black", "width": 0.6}},
            text=[
                f"{m:.1f} kg ({p:.1f}%)" for m, p in zip(masses, masses_in_percentages)
            ],
            textposition="outside",
            textfont={"family": "Arial", "size": 12, "color": "black"},
            hovertemplate=("<b>%{y}</b><br>Mass: %{x:.2f} kg<extra></extra>"),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            labels=components,
            values=masses,
            hole=0.45,
            marker={"line": {"color": "white", "width": 2}},
            textinfo="percent",
            textposition="inside",
            textfont={"family": "Arial", "size": 12, "color": "white"},
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Mass: %{value:.2f} kg<br>"
                "Contribution: %{percent}"
                "<extra></extra>"
            ),
            sort=False,
            showlegend=True,
            legendgroup="mass",
        ),
        row=2,
        col=1,
    )

    donut_y_top = fig.data[1].domain.y[1] - vertical_spacing

    fig.update_layout(
        title={
            "text": "Aircraft mass breakdown",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        width=1400,
        height=max(1000, 65 * len(components) + 450),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Arial", "size": 13, "color": "#344563"},
        margin={"l": 170, "r": 100, "t": 110, "b": 70},
        legend={
            "orientation": "v",
            "x": 1.02,
            "y": donut_y_top,
            "font": {"family": "Arial", "size": 12},
        },
        showlegend=True,
    )

    fig.update_xaxes(
        title_text="Mass [kg]",
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False,
        showline=True,
        linecolor="black",
        ticks="outside",
        range=[0, max(masses) * 1.35],
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="",
        autorange="reversed",
        showgrid=False,
        showline=False,
        ticks="",
        tickfont={"family": "Arial", "size": 12, "color": "#344563"},
        row=1,
        col=1,
    )

    return fig, owe


@st.cache_data
def _compute_mass_breakdown(
    wing_area: float,
    mtow: float | np.ndarray,
    htp_area: float,
    vtp_area: float,
    mto_thrust: float,
    npax: int,
) -> (dict, float | np.ndarray):
    """
    Returns the breakdown of the aircraft empty mass as dict with item names and mass. Separated in
    another function because we will likely use it for MTOW looping.

    :param wing_area: area of the wing in m²
    :param mtow: MTOW of the aircraft in kg
    :param htp_area: area of the HTP in m²
    :param vtp_area: area of the VTP in m²
    :param mto_thrust: total thrust at sea level static in N
    :param npax: number of passenger in the cabin
    :return: aircraft empty mass breakdown plot figure, aircraft empty mass
    """

    aircraft_data = st.session_state.aircraft_data

    # GD method
    wing_mass = (
        (
            1.1
            * 0.00428
            * (wing_area * 10.76391) ** 0.48
            * aircraft_data.wing_aspect_ratio
            * 0.85**0.43
            * (mtow * 2.20462 * 3.8) ** 0.84
            * aircraft_data.wing_taper_ratio**0.14
        )
        / ((100 * 0.12) ** 0.76 * np.cos(aircraft_data.wing_sweep_angle) ** 1.54)
        / 2.20462
    )
    # Torenbeek method. Vd is taken as 385 KEAS
    htp_mass = (
        1.1
        * (htp_area * 10.76391)
        * (
            3.81
            * (htp_area * 10.76391) ** 0.2
            * 385
            / (1000 * np.cos(np.radians(28.0)) ** 0.5)
            - 0.287
        )
        / 2.20462
    )
    vtp_mass = (
        1.0
        * (vtp_area * 10.76391)
        * (
            3.81
            * (vtp_area * 10.76391) ** 0.2
            * 385
            / (1000 * np.cos(np.radians(35.0)) ** 0.5)
            - 0.287
        )
        / 2.20462
    )
    # Torenbeek version
    fuselage_mass = (
        0.021
        * 1.08
        * (
            (
                385 * aircraft_data.htp_lever_arm / (2.0 * aircraft_data.fuselage_width)
            )  # Conversion from m to ft is not necessary here, it cancels out
            ** 0.5
        )
        * (aircraft_data.fuselage_wetted_area * 10.76391) ** 1.2
        / 2.20462
    )
    # Torenbeek
    nacelle_mass = 0.065 * mto_thrust * 0.2248089431 / 2.20462
    # GD method
    landing_gear_mass = 62.61 * (mtow * 2.20462 / 1000.0) ** 0.84 / 2.20462
    paint_mass = 0.180 * (
        wing_area * 2.1
        + htp_area * 2.1
        + vtp_area * 2.1
        + aircraft_data.fuselage_wetted_area
    )

    engine_mass = (14.1e-3 * mto_thrust / 2.0 + 648) * 2.0 * 1.55
    # 2 tanks and 2 engine, 23860l of mission fuel (we'll break the loop here)
    fuel_system_mass = (80 * 3 + 15 * 2**0.5 * (23860 * 0.264172) ** 0.333) / 2.20462
    engine_control_mass = (
        88.46
        * (
            2.0
            * (aircraft_data.fuselage_length + aircraft_data.wing_span)
            * 3.280839895
            / 100.0
        )
        ** 0.294
        / 2.20462
    )
    engine_starting_systems_mass = (
        9.33 * (engine_mass * 2.20462 / 1000.0) ** 1.078 / 2.20462
    )
    unconsummables_mass = 25 * 2.0 + 0.0035 * 23860 * 0.762  # 23860l of Jet A1 in kg

    flight_controls_mass = 0.64 * (mtow * 2.20462) ** 0.6667 / 2.20462
    hydraulics_mass = 0.009 * mtow
    electrical_mass = 0.0174 * mtow  # Cessna method adapted to commercial AC
    instrumentation_mass = (
        160 + 0.006 * mtow * 2.20462
    ) / 2.20462 + 100.0  # 100kg of radar
    ecs_systems_mass = (
        6.75 * (aircraft_data.cabin_length * 3.280839895) ** 1.28 / 2.20462
    )
    insulation_mass = 9.3 * aircraft_data.fuselage_length * aircraft_data.fuselage_width
    oxygen_systems_mass = 7 * (2.0 + npax) ** 0.702 / 2.20462
    apu_mass = 0.008 * mtow

    # 2 FDC, 4 CC, 5.16 PSI in the cabin for 8000 ft
    furnishing_mass = (
        110
        + 32 * npax
        + 60
        + 0.6 * npax**1.33
        + 2.01 * npax**1.12
        + (npax * (1.0 + 5.16) / 100.0) ** 0.505
        + 0.771 * mtow * 2.20462 / 1000.0
    ) / 2.20462

    crew_mass = 2.0 * 85.0 + 4.0 * 75.0  # 85 per PT, 75 per PNC

    owe = (
        wing_mass
        + htp_mass
        + vtp_mass
        + fuselage_mass
        + nacelle_mass
        + landing_gear_mass
        + paint_mass
        + engine_mass
        + fuel_system_mass
        + engine_control_mass
        + engine_starting_systems_mass
        + unconsummables_mass
        + flight_controls_mass
        + hydraulics_mass
        + electrical_mass
        + instrumentation_mass
        + ecs_systems_mass
        + insulation_mass
        + oxygen_systems_mass
        + apu_mass
        + furnishing_mass
        + crew_mass
    )

    mass_dict = {
        "Wing": wing_mass,
        "HTP": htp_mass,
        "VTP": vtp_mass,
        "Fuselage": fuselage_mass,
        "Nacelles": nacelle_mass,
        "Landing gear": landing_gear_mass,
        "Paint": paint_mass,
        "Engine": engine_mass,
        "Fuel system": fuel_system_mass,
        "Engine control": engine_control_mass + engine_starting_systems_mass,
        "Unconsummables": unconsummables_mass,
        "Flight controls": flight_controls_mass,
        "Hydraulic system": hydraulics_mass,
        "Electric system": electrical_mass,
        "Instrumentation": instrumentation_mass,
        "ECS & IPS": ecs_systems_mass,
        "Insulation": insulation_mass,
        "Oxygen": oxygen_systems_mass,
        "APU": apu_mass,
        "Furnishing": furnishing_mass,
        "Crew": crew_mass,
    }

    return mass_dict, owe
