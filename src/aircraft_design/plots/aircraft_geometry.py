import pathlib

import numpy as np
import plotly.graph_objects as go
from PIL import Image


def aircraft_geometry_plot(
    npax: float,
    npax_per_row: float,
    wing_area: float,
    htp_area: float,
    mto_thrust: float,
) -> go.Figure:
    """
    Returns a figure plot of the top view of the wing.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param npax: number of passenger in the cabin, applet should ensure that it is a multiple of
                npax_per_row
    :param npax_per_row: number of passenger in a row cabin
    :param wing_area: area of the wing
    :param htp_area: area of the htp
    :param mto_thrust: thrust of one engine at sea level static
    :return: wing plot figure
    """

    # Tweak this the right visual on the final aircraft
    seat_width = 0.48
    seat_length = 0.9
    aisle_width = 0.43

    n_aisle = 1.0 if npax_per_row < 6.0 else 2.0
    n_rows = npax / npax_per_row

    w_cabin = (
        npax_per_row * seat_width
        + aisle_width * n_aisle
        + (npax_per_row + 2) * 0.051
        + 0.05
    )
    fuselage_width = w_cabin * 1.06
    fuselage_height = fuselage_width / 2.0 + 0.14
    cabin_length = seat_length * n_rows
    front_length = 1.7 * fuselage_height
    rear_length = 4.75 * fuselage_height

    fuselage_trace_x = np.array([])
    fuselage_trace_y = np.array([])

    # Be careful here, the x coordinate for the aircraft is the y for plotly
    nose_x = -np.linspace(0, front_length, 25)  # 25 should be enough
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

    tail_x = -np.linspace(0, rear_length, 25)
    tail_y = -np.sqrt(
        (fuselage_width / 2.0) ** 2.0
        * (1.0 - (np.abs(tail_x)) ** 2.0 / rear_length**2.0)
    )

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

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fuselage_trace_y,
            y=fuselage_trace_x,
            mode="lines",
            line={"color": "black"},
            showlegend=False,
        )
    )
    # just add a trace to serve as a ruler
    fig.add_trace(
        go.Scatter(x=[-35.80 / 2, 35.80 / 2], y=[-37.57, -37.57], showlegend=False)
    )

    a320_top_view = Image.open(
        pathlib.Path(__file__).parent / "resources" / "Airbus_A320.png"
    )

    span_actual_a320 = 35.80
    length_actual_a320 = 37.57
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
        height=800,
        width=800,
    )

    return fig
