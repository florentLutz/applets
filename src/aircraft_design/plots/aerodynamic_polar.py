import numpy as np
import plotly.graph_objects as go
import streamlit as st

UNIT_REYNOLDS = 6000000.0  # Representative value for 35000ft with a Mach of 0.8
MACH_NUMBER = 0.8  # Representative value, no link with constraint diagram


@st.cache_data
def aircraft_aerodynamic_polar_plot(
    wing_area: float, htp_area: float, vtp_area: float
) -> (go.Figure, float):
    """
    Returns a figure plot of the aircraft aerodynamic polar.

    :param wing_area: area of the wing
    :param htp_area: area of the HTP
    :param vtp_area: area of the VTP
    :return: aircraft aerodynamic polar plot figure
    """

    fig = go.Figure()

    cl = np.arange(0, 0.91, 0.01)

    # The aerodynamic can't be run unless the geometry has (at least I want to make sure that it is
    # the case), so this should be available and filled in
    aircraft_data = st.session_state.aircraft_data

    cd0_fuselage = _fuselage_cd0(
        aircraft_data.fuselage_length,
        aircraft_data.fuselage_width,
        aircraft_data.fuselage_width,  # Approximation height is width
        aircraft_data.fuselage_wetted_area,
        cl,
        wing_area,
    )
    cd0_wing = _compute_cd0_lifting_surface(
        wing_area,
        aircraft_data.mac_length,
        0.12,
        aircraft_data.wing_sweep_angle,
        0.04,
        wing_area * 2.1,
        cl,
        cambered=True,
    )
    cd0_horizontal_tail = _compute_cd0_lifting_surface(
        wing_area,
        aircraft_data.htp_mean_chord,
        0.1,
        np.radians(28.0),
        0.01,
        2.0 * htp_area,
        cl,
    )
    cd0_vertical_tail = _compute_cd0_lifting_surface(
        wing_area,
        aircraft_data.vtp_mean_chord,
        0.1,
        np.radians(35.0),
        0.01,
        2.0 * vtp_area,
        cl,
    )
    cd0_others = np.full_like(cd0_fuselage, 0.0015 + 0.0003)
    cd0_parasitic = 0.107 * (
        cd0_fuselage + cd0_wing + cd0_horizontal_tail + cd0_vertical_tail + cd0_others
    )

    cd_profile = (
        cd0_fuselage
        + cd0_wing
        + cd0_horizontal_tail
        + cd0_vertical_tail
        + cd0_others
        + cd0_parasitic
    )

    components = [
        (cd0_fuselage, "1. Fuselage"),
        (cd0_fuselage + cd0_wing, "2. Wing"),
        (cd0_fuselage + cd0_wing + cd0_horizontal_tail, "3. Horizontal tail"),
        (
            cd0_fuselage + cd0_wing + cd0_horizontal_tail + cd0_vertical_tail,
            "4. Vertical tail",
        ),
        (
            cd0_fuselage
            + cd0_wing
            + cd0_horizontal_tail
            + cd0_vertical_tail
            + cd0_others,
            "5. Others",
        ),
        (
            cd0_fuselage
            + cd0_wing
            + cd0_horizontal_tail
            + cd0_vertical_tail
            + cd0_others
            + cd0_parasitic,
            "6. Parasitic drag",
        ),
    ]

    y_arrows = [0.555, 0.575, 0.600, 0.620, 0.640, 0.650]
    x_arrows = []

    for idx, (cd, name) in enumerate(components):
        fig.add_trace(
            go.Scatter(
                x=cd,
                y=cl,
                mode="lines",
                name=name,
                line={"color": "gray", "width": 1.5, "dash": "dash"},
                showlegend=False,
            )
        )
        x_arrow = np.interp(y_arrows[idx], cl, cd)
        x_arrows.append(x_arrow)

    fig.add_trace(
        go.Scatter(
            x=cd_profile,
            y=cl,
            mode="lines",
            name="Total profile drag",
            line={"color": "black", "width": 1.7},
            showlegend=False,
        )
    )

    fig.add_annotation(
        x=np.interp(0.875, cl, cd_profile) + 2e-3,
        y=0.875,
        text="<b>Total profile drag</b>",
        showarrow=False,
        font={"size": 23, "color": "black"},
        xanchor="left",
    )

    induced_drag = 0.04257945865760537 * cl**2
    total_drag = cd_profile + induced_drag

    fig.add_trace(
        go.Scatter(
            x=total_drag,
            y=cl,
            mode="lines",
            name="Total drag",
            line={"color": "black", "width": 3},
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=np.interp(0.82, cl, total_drag) + 2e-3,
        y=0.82,
        text="<b>Total drag</b>",
        showarrow=False,
        font={"size": 23, "color": "black"},
        xanchor="left",
    )

    idx_best = np.argmax(cl / total_drag)
    cd_best = total_drag[idx_best]
    cl_best = cl[idx_best]
    l_d_max = cl_best / cd_best
    fig.add_trace(
        go.Scatter(
            x=[cd_best],
            y=[cl_best],
            mode="markers",
            marker={"color": "green", "size": 11},
            showlegend=False,
        )
    )

    x_tangent = np.array([0, cd_best])
    y_tangent = (cl_best / cd_best) * x_tangent

    fig.add_trace(
        go.Scatter(
            x=x_tangent,
            y=y_tangent,
            mode="lines",
            line={"color": "green", "width": 2.2},
            showlegend=False,
        )
    )

    fig.add_annotation(
        x=cd_best + 2e-3,
        y=cl_best,
        text="<b>Best L/D</b>",
        showarrow=False,
        font={"size": 23, "color": "green"},
        xanchor="left",
    )

    x_starts = [0] + x_arrows[:-1]

    for i, (x0, x1, y) in enumerate(zip(x_starts, x_arrows, y_arrows), start=1):
        fig.add_annotation(
            x=x1,
            y=y,
            ax=x0,
            ay=y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text="",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1.2,
            arrowcolor="black",
        )
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=y + 0.018,
            text=f"<b>{i}.</b>",
            showarrow=False,
            font={"size": 19, "color": "black"},
        )

    legend_text = (
        "<b>1. Fuselage<br>"
        "2. Wing<br>"
        "3. Horizontal tail plane<br>"
        "4. Vertical tail plane<br>"
        "5. Others (nacelle &amp; pylons)<br>"
        "6. Parasitic drag</b>"
    )

    fig.add_annotation(
        x=0.115,
        y=0.225,
        xref="x",
        yref="y",
        text=legend_text,
        showarrow=False,
        align="left",
        xanchor="right",
        yanchor="top",
        font={"size": 18, "color": "black"},
    )

    fig.update_layout(
        title={
            "text": "Aircraft drag polar",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        xaxis={
            "title": "",
            "range": [0, 0.12],
            "dtick": 0.02,
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
        },
        yaxis={
            "title": "",
            "range": [0, 0.9],
            "dtick": 0.1,
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

    return fig, l_d_max


def _get_flat_plate_friction_drag_coefficient(
    length: float, mach: float, reynolds: float
) -> float:
    """

    :param length: flat plate length in meters
    :param mach: Mach number
    :param reynolds: Reynolds number
    :return: Drag coefficient w.r.t. a surface of area length*1 m**2
    """
    c_f = 0.455 / (
        (1 + 0.144 * mach**2) ** 0.65 * (np.log10(reynolds * length)) ** 2.58
    )
    return c_f


@st.cache_data
def _fuselage_cd0(
    fuselage_length: float,
    fuselage_width: float,
    fuselage_height: float,
    fuselage_wetted_area: float,
    cl: np.ndarray,
    reference_area: float,
) -> np.ndarray:
    """
    Computes the fuselage profile drag for input values of lift coefficient

    :param fuselage_length: fuselage length, in m
    :param fuselage_width: fuselage height, in m
    :param fuselage_height: fuselage width, in m
    :param fuselage_wetted_area: fuselage wetted area, in m²
    :param cl: aircraft lift coefficient
    :param reference_area: reference area in m²
    :return: the profile drag of the fuselage at various lift coefficient.
    """

    cf_fus = _get_flat_plate_friction_drag_coefficient(
        fuselage_length, MACH_NUMBER, UNIT_REYNOLDS
    )

    cd0_friction_fus = (
        (0.98 + 0.745 * np.sqrt(fuselage_height * fuselage_width) / fuselage_length)
        * cf_fus
        * fuselage_wetted_area
        / reference_area
    )
    cd0_upsweep_fus = (
        (0.0029 * cl**2 - 0.0066 * cl + 0.0043)
        * (0.67 * 3.6 * fuselage_height * fuselage_width)
        / reference_area
    )
    return cd0_friction_fus + cd0_upsweep_fus


@st.cache_data
def _compute_cd0_lifting_surface(
    reference_area: float,
    mac_length: float,
    thickness_ratio: float,
    sweep_25: float,
    interaction_coeff: float,
    wet_area: float,
    cl: np.ndarray,
    *,
    cambered: bool = False,
):
    """
    Computes CD0 for a lifting surface.

    Friction coefficient is assessed from :cite:`raymer:1999` (Eq 12.27).
    Corrections for lifting surfaces are from :cite:`supaero:2014`.

    :param reference_area: reference area in m²
    :param mac_length: mean aerodynamic chord in m
    :param thickness_ratio: thickness ratio, no unit
    :param sweep_25: sweep angle at 25% chord, in rad
    :param interaction_coeff: ratio of additional drag due to interaction effects
    :param wet_area: wet surface area of the lifting surface
    :param cl: aircraft lift coefficient
    :param cambered: True if airfoil is cambered
    :return: CD0 value
    """
    # Drag coefficient for flat plate (
    cf = _get_flat_plate_friction_drag_coefficient(
        mac_length, MACH_NUMBER, UNIT_REYNOLDS
    )

    # Contribution of relative thickness
    thickness_contribution = 4.688 * thickness_ratio**2 + 3.146 * thickness_ratio

    # Contribution of camber
    if cambered:
        camber_contribution = (
            2.859 * (cl / np.cos(sweep_25) ** 2) ** 3
            - 1.849 * (cl / np.cos(sweep_25) ** 2) ** 2
            + 0.382 * (cl / np.cos(sweep_25) ** 2)
            + 0.06
        )
    else:
        camber_contribution = 0.0

    # Correction from sweep angle
    sweep_correction = (
        1 - 0.000178 * np.degrees(sweep_25) ** 2 - 0.0065 * np.degrees(sweep_25)
    )

    cd0 = (
        (
            (thickness_contribution + camber_contribution) * sweep_correction
            + interaction_coeff
            + 1
        )
        * cf
        * wet_area
        / reference_area
    )

    return cd0
