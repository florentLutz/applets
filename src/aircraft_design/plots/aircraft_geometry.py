import pathlib
from dataclasses import dataclass, field

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image


@dataclass
class AircraftGeometry:
    """
    Class used as a way to handily pass information on the aircraft computed by drawing function. To
    avoid overloading, only information required in multiple drawing functions should be added. Also
    as this dataclass does not provide default value, the order in which the function are called
    will matter to avoid error
    """

    front_length: float = field(default=None)
    cabin_length: float = field(default=None)
    fuselage_width: float = field(default=None)
    fuselage_length: float = field(default=None)
    rear_length: float = field(default=None)
    fa_length: float = field(default=None)
    mac_length: float = field(default=None)
    wing_span: float = field(default=None)
    wing_root_leading_edge_x: float = field(default=None)
    wing_tip_leading_edge_x: float = field(default=None)


@st.cache_data
def aircraft_geometry_plot(
    npax: int,
    npax_per_row: int,
    wing_area: float,
    htp_volume_coefficient: float,
    vtp_volume_coefficient: float,
    mto_thrust: float,
    *,
    show_reference_aircraft: bool = False,
) -> go.Figure:
    """
    Returns a figure plot of the top view of the wing.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param npax: number of passenger in the cabin, applet should ensure that it is a multiple of
                npax_per_row
    :param npax_per_row: number of passenger in a row cabin
    :param wing_area: area of the wing
    :param htp_volume_coefficient: volume coefficient of the HTP
    :param vtp_volume_coefficient: volume coefficient of the VTP
    :param mto_thrust: total thrust at sea level static
    :param show_reference_aircraft: show the outline of the reference aircraft for comparison
    :return: wing plot figure
    """

    aircraft_data = AircraftGeometry()

    # Fuselage
    fuselage_trace_x, fuselage_trace_y = _fuselage_trace(
        npax, npax_per_row, aircraft_data
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fuselage_trace_y,
            y=fuselage_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )

    # Wing
    left_wing_trace_x, left_wing_trace_y = _wing_trace(wing_area, aircraft_data)

    fig.add_trace(
        go.Scatter(
            x=left_wing_trace_y,
            y=left_wing_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=-left_wing_trace_y,
            y=left_wing_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )

    # HTP
    left_htp_trace_x, left_htp_trace_y = _htp_trace(
        wing_area, htp_volume_coefficient, aircraft_data
    )

    fig.add_trace(
        go.Scatter(
            x=left_htp_trace_y,
            y=left_htp_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=-left_htp_trace_y,
            y=left_htp_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )

    # VTP
    left_vtp_trace_x, left_vtp_trace_y = _vtp_trace(
        wing_area, vtp_volume_coefficient, aircraft_data
    )

    fig.add_trace(
        go.Scatter(
            x=left_vtp_trace_y,
            y=left_vtp_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=-left_vtp_trace_y,
            y=left_vtp_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )

    # Nacelle
    left_nacelle_trace_x, left_nacelle_trace_y = _nacelle_trace(
        mto_thrust / 2.0, aircraft_data
    )

    fig.add_trace(
        go.Scatter(
            x=left_nacelle_trace_y,
            y=left_nacelle_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=-left_nacelle_trace_y,
            y=left_nacelle_trace_x,
            mode="lines",
            line={"color": "black", "width": 5},
            showlegend=False,
        )
    )

    a320_top_view = Image.open(
        pathlib.Path(__file__).parent / "resources" / "Airbus_A320.png"
    )

    span_actual_a320 = 35.80
    length_actual_a320 = 39.38
    # Not actually true, more 37.57, but if we don't do that the picture appears squished
    if show_reference_aircraft:
        fig.add_layout_image(
            {
                "source": a320_top_view,
                "xref": "x",
                "yref": "y",
                "x": 0.0,
                "y": 0.0,
                "sizey": length_actual_a320,
                "sizex": span_actual_a320,
                "sizing": "stretch",
                "opacity": 0.75,
                "layer": "below",
                "xanchor": "center",
                "yanchor": "top",
            }
        )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_visible=False,
        yaxis_visible=False,
        height=int(800 * length_actual_a320 / span_actual_a320),
        width=800,
    )
    # This should make it so that it is always centered on the trace
    fig.update_xaxes(
        range=[-span_actual_a320 * 1.05 / 2.0, span_actual_a320 * 1.05 / 2.0]
    )
    fig.update_yaxes(range=[0.0, -length_actual_a320 * 1.05].sort())

    return fig


@st.cache_data
def _fuselage_trace(
    npax: int, npax_per_row: int, aircraft: AircraftGeometry
) -> (np.ndarray, np.ndarray):
    """
    Returns a figure plot of the top view of the fuselage.

    :param npax: number of passenger in the cabin, applet should ensure that it is a multiple of
                npax_per_row
    :param npax_per_row: number of passenger in a row cabin
    :param aircraft: AircraftGeometry object used to pass locally computed information about the
                    aircraft
    :return: fuselage plot figure as a set of x and y coordinates
    """

    # Tweak this the right visual on the final aircraft
    seat_width = 0.48
    seat_length = 0.95
    aisle_width = 0.43

    n_aisle = 1.0 if npax_per_row < 6.0 else 2.0
    n_rows = npax / npax_per_row

    w_cabin = (
        npax_per_row * seat_width
        + aisle_width * n_aisle
        + (npax_per_row + 2) * 0.051
        + 0.05
    )
    aircraft.fuselage_width = fuselage_width = w_cabin * 1.06
    fuselage_height = fuselage_width / 2.0 + 0.14
    aircraft.cabin_length = cabin_length = seat_length * n_rows
    aircraft.front_length = front_length = 1.7 * fuselage_height
    aircraft.rear_length = rear_length = 4.75 * fuselage_height

    aircraft.fuselage_length = front_length + cabin_length + rear_length

    fuselage_trace_x = np.array([])
    fuselage_trace_y = np.array([])

    # Be careful here, the x coordinate for the aircraft is the y for plotly
    nose_x = -np.linspace(0, front_length, 50)  # 25 should be enough
    nose_y = -np.sqrt(
        (fuselage_width / 2.0) ** 2.0
        * (1.0 - (np.abs(nose_x) - front_length) ** 2.0 / front_length**2.0)
    )

    fuselage_trace_x = np.concatenate((fuselage_trace_x, nose_x))
    fuselage_trace_y = np.concatenate((fuselage_trace_y, nose_y))

    cylinder_x = np.array([-front_length, -front_length - cabin_length])
    cylinder_y = np.array([-fuselage_width / 2.0, -fuselage_width / 2.0])

    fuselage_trace_x = np.concatenate((fuselage_trace_x, cylinder_x))
    fuselage_trace_y = np.concatenate((fuselage_trace_y, cylinder_y))

    tail_x = -np.linspace(0, rear_length, 50)
    tail_y = _rear_cone_trace(fuselage_width, rear_length, tail_x)

    fuselage_trace_x = np.concatenate(
        (fuselage_trace_x, tail_x - front_length - cabin_length)
    )
    fuselage_trace_y = np.concatenate((fuselage_trace_y, tail_y))

    fuselage_trace_x = np.concatenate(
        (fuselage_trace_x, -rear_length - tail_x - front_length - cabin_length)
    )
    fuselage_trace_y = np.concatenate((fuselage_trace_y, -np.flip(tail_y)))

    fuselage_trace_x = np.concatenate((fuselage_trace_x, np.flip(cylinder_x)))
    fuselage_trace_y = np.concatenate((fuselage_trace_y, -cylinder_y))

    fuselage_trace_x = np.concatenate((fuselage_trace_x, -front_length - nose_x))
    fuselage_trace_y = np.concatenate((fuselage_trace_y, -np.flip(nose_y)))

    return fuselage_trace_x, fuselage_trace_y


@st.cache_data
def _rear_cone_trace(
    fuselage_width: float, rear_cone_length: float, rear_cone_x: np.ndarray
) -> np.ndarray:
    """
    Returns the y position, along the tail cone, of the input x position

    :param fuselage_width: width of the fuselahe
    :param rear_cone_length: length of the rear cone
    :param rear_cone_x: x position of points to draw along the rear cone
    :return: corresponding y_position
    """

    return -np.sqrt(
        (fuselage_width / 2.0) ** 2.0
        * (1.0 - (np.abs(rear_cone_x)) ** 2.0 / rear_cone_length**2.0)
    )


@st.cache_data
def _wing_trace(
    wing_area: float, aircraft: AircraftGeometry
) -> (np.ndarray, np.ndarray):
    """
    Returns a figure plot of the top view of the wing.

    :param wing_area: area of the wing
    :param aircraft: AircraftGeometry object used to pass locally computed information about the
                    aircraft
    :return: wing plot figure as a set of x and y coordinates
    """
    # Wings.
    aspect_ratio = 10.47
    sweep_angle = 23.0 * np.pi / 180.0
    taper_ratio = 0.240
    kink_ratio = 0.4

    aircraft.fa_length = fa_length = (
        aircraft.front_length + 0.46 * aircraft.cabin_length
    )
    aircraft.wing_span = span = np.sqrt(aspect_ratio * wing_area)
    aircraft.mac_length = (
        1.25 * wing_area / span
    )  # A few tweaks are required here and there

    root_chord = 2.0 * wing_area / span / (1.0 + taper_ratio)
    tip_chord = root_chord * taper_ratio
    aircraft.wing_root_leading_edge_x = root_chord_leading_edge_x = (
        fa_length - 0.25 * root_chord
    )
    aircraft.wing_tip_leading_edge_x = tip_chord_leading_edge_x = (
        fa_length + span / 2.0 * np.sin(sweep_angle) - 0.25 * tip_chord
    )

    left_wing_trace_x = -np.array(
        [
            root_chord_leading_edge_x,
            tip_chord_leading_edge_x,
            tip_chord_leading_edge_x + tip_chord,
            root_chord_leading_edge_x + root_chord,
            root_chord_leading_edge_x + root_chord,
            root_chord_leading_edge_x,
        ]
    )
    left_wing_trace_y = np.array(
        [
            -aircraft.fuselage_width / 2.0,
            -span / 2.0,
            -span / 2.0,
            -span / 2.0 * kink_ratio,
            -aircraft.fuselage_width / 2.0,
            -aircraft.fuselage_width / 2.0,
        ]
    )

    return left_wing_trace_x, left_wing_trace_y


@st.cache_data
def _htp_trace(
    wing_area: float, htp_volume_coefficient, aircraft: AircraftGeometry
) -> (np.ndarray, np.ndarray):
    """
    Returns a figure plot of the top view of the HTP.

    :param wing_area: area of the wing
    :param htp_volume_coefficient: volume coefficient of the HTP
    :param aircraft: AircraftGeometry object used to pass locally computed information about the
                    aircraft
    :return: HTP plot figure as a set of x and y coordinates
    """

    htp_aspect_ratio = 5.5
    sweep_angle = 29.0 * np.pi / 180.0
    taper_ratio = 0.256

    htp_lever_arm = aircraft.fuselage_length * 0.85 - aircraft.fa_length
    htp_area = htp_volume_coefficient * wing_area * aircraft.mac_length / htp_lever_arm
    htp_span = np.sqrt(htp_area * htp_aspect_ratio)

    # Length between nose and htp aerodynamic center position
    htp_fa_length = 0.89 * aircraft.fuselage_length

    root_chord = 2.0 * htp_area / htp_span / (1.0 + taper_ratio)
    tip_chord = root_chord * taper_ratio
    root_chord_leading_edge_x = htp_fa_length - 0.25 * root_chord
    tip_chord_leading_edge_x = (
        htp_fa_length + htp_span / 2.0 * np.sin(sweep_angle) - 0.25 * tip_chord
    )

    left_htp_trace_x = -np.array(
        [
            root_chord_leading_edge_x,
            tip_chord_leading_edge_x,
            tip_chord_leading_edge_x + tip_chord,
            root_chord_leading_edge_x + root_chord,
        ]
    )
    htp_root_le_wrt_con_start = (
        root_chord_leading_edge_x - aircraft.front_length - aircraft.cabin_length
    )
    htp_root_te_wrt_con_start = htp_root_le_wrt_con_start + root_chord
    left_htp_trace_y = np.array(
        [
            _rear_cone_trace(
                aircraft.fuselage_width,
                aircraft.rear_length,
                np.array([htp_root_le_wrt_con_start]),
            ).item(),
            -htp_span / 2.0,
            -htp_span / 2.0,
            _rear_cone_trace(
                aircraft.fuselage_width,
                aircraft.rear_length,
                np.array([htp_root_te_wrt_con_start]),
            ).item(),
        ]
    )

    return left_htp_trace_x, left_htp_trace_y


@st.cache_data
def _vtp_trace(
    wing_area: float, vtp_volume_coefficient: float, aircraft: AircraftGeometry
) -> (np.ndarray, np.ndarray):
    """
    Returns a figure plot of the top view of the VTP.

    :param wing_area: area of the wing
    :param vtp_volume_coefficient: volume coefficient of the VTP
    :param aircraft: AircraftGeometry object used to pass locally computed information about the
                    aircraft
    :return: VTP plot figure as a set of x and y coordinates
    """

    vtp_aspect_ratio = 1.82
    taper_ratio = 0.303

    vtp_lever_arm = aircraft.fuselage_length * 0.85 - aircraft.fa_length
    vtp_area = vtp_volume_coefficient * wing_area * aircraft.wing_span / vtp_lever_arm
    htp_span = np.sqrt(vtp_area * vtp_aspect_ratio)

    # Length between nose and htp aerodynamic center position
    vtp_fa_length = 0.825 * aircraft.fuselage_length

    root_chord = 4.0 * vtp_area / htp_span / (1.0 + taper_ratio)

    vtp_x_adim = np.linspace(0, 1, 50)
    # Equation for NACA0012 modified a bit
    vtp_y_adim = -0.3 * (
        0.298222773 * np.sqrt(vtp_x_adim)
        - 0.127125232 * vtp_x_adim
        - 0.357907906 * vtp_x_adim**2.0
        + 0.291984971 * vtp_x_adim**3.0
        - 0.105174606 * vtp_x_adim**4.0
    )

    vtp_x_absolute = vtp_fa_length - 0.25 * root_chord + vtp_x_adim * root_chord

    return -vtp_x_absolute, vtp_y_adim * root_chord


@st.cache_data
def _nacelle_trace(
    mto_thrust: float, aircraft: AircraftGeometry
) -> (np.ndarray, np.ndarray):
    """
    Returns a figure plot of the top view of the nacele.

    :param mto_thrust: nominal thrust of 1 engine in N
    :param aircraft: AircraftGeometry object used to pass locally computed information about the
                    aircraft
    :return: nacelle plot figure as a set of x and y coordinates
    """

    mto_thrust_lbf = mto_thrust * 0.2248089431
    mto_thrust_lbf_ref = 112.2e3 * 0.2248089431

    nacelle_diameter = 0.9 * 2.37 * np.sqrt(mto_thrust_lbf / mto_thrust_lbf_ref)
    nacelle_length = 0.85 * 4.44 * np.sqrt(mto_thrust_lbf / mto_thrust_lbf_ref)

    # In the aircraft coordinate system
    nacelle_center_y_coordinate = 0.338 * aircraft.wing_span / 2.0

    # To facilitate, we will make it so that the center of the back of the nacelle will be on the
    # wing
    nacelle_start_x_coordinate = np.interp(
        nacelle_center_y_coordinate,
        [aircraft.fuselage_width / 2.0, aircraft.wing_span / 2.0],
        [aircraft.wing_root_leading_edge_x, aircraft.wing_tip_leading_edge_x],
    )
    nacelle_end_x_coordinate = np.interp(
        nacelle_center_y_coordinate - nacelle_diameter / 2.0,
        [aircraft.fuselage_width / 2.0, aircraft.wing_span / 2.0],
        [aircraft.wing_root_leading_edge_x, aircraft.wing_tip_leading_edge_x],
    )

    nacelle_trace_x = -np.array(
        [
            nacelle_start_x_coordinate,
            nacelle_start_x_coordinate,
            nacelle_start_x_coordinate - nacelle_length,
            nacelle_start_x_coordinate - nacelle_length,
            nacelle_end_x_coordinate,
        ]
    )
    nacelle_trace_y = -np.array(
        [
            nacelle_center_y_coordinate,
            nacelle_center_y_coordinate + nacelle_diameter / 2.0,
            nacelle_center_y_coordinate + nacelle_diameter / 2.0,
            nacelle_center_y_coordinate - nacelle_diameter / 2.0,
            nacelle_center_y_coordinate - nacelle_diameter / 2.0,
        ]
    )

    return nacelle_trace_x, nacelle_trace_y
