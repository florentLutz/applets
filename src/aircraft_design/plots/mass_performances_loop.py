import numpy as np
import plotly.graph_objects as go
import streamlit as st

from .aircraft_design_mission import _compute_design_mission
from .empty_mass_breakdown import _compute_mass_breakdown

DEFAULT_MTOW = (
    100e3  # This is the MTOW previous computations have used, is shared with applets
)
# but should be in a dedicated constants.py file

NB_POINTS_MTOW_SWEEP = 500


def mass_performances_loop(npax: int, design_range: float) -> (go.Figure, float):
    """
    Returns a figure illustrating the mass performance loop.

    :param npax: number of passenger in the cabin
    :param design_range: range of the aircraft's design mission, in nm
    :return: aircraft mass-performances loop plot figure, aircraft empty mass according to
    performance criteria and mission fuel
    """

    # The limiting factor of doing it this way is that aerodynamic polar will not be updated,
    # leading to potential discrepancies.

    # Based on Transport Aircraft Weight Estimation as a Function of Range and Number of Passengers,
    # only useful for a first approximation, the looping will provide the rest
    mtow_guess = (
        267600
        * np.exp(-(((npax - 679.7) / 414.4) ** 2.0))
        / (1.0 - 0.003246 * (design_range * 1.852) ** 0.4822)
    )  # In kg, hopefully
    mtow_sweep = np.linspace(
        round(mtow_guess * 0.75), round(mtow_guess * 1.25), NB_POINTS_MTOW_SWEEP
    )

    # Because I'm a smartass, I'll scale the areas using a factor instead of recomputing
    # everything. Since wing loading is constant, and so are HTP and VTP volume coefficient,
    # HTP and VTP area actually scale as the mtow ** 3/2 (actually as the wing area ** 3/2)
    _, owe_structure = _compute_mass_breakdown(
        wing_area=mtow_sweep / st.session_state.wing_loading,
        mtow=mtow_sweep,
        htp_area=st.session_state.aircraft_data.htp_area
        * (mtow_sweep / DEFAULT_MTOW) ** (3.0 / 2.0),
        vtp_area=st.session_state.aircraft_data.vtp_area
        * (mtow_sweep / DEFAULT_MTOW) ** (3.0 / 2.0),
        mto_thrust=mtow_sweep * 9.81 * st.session_state.thrust_loading,
        npax=npax,
    )

    _, _, owe_performances = _compute_design_mission(
        design_range=design_range,
        mtow=mtow_sweep,
        npax=npax,
        mto_thrust=mtow_sweep * 9.81 * st.session_state.thrust_loading,
    )

    converged_mtow = np.interp(0, owe_performances - owe_structure, mtow_sweep)
    converged_owe = np.interp(converged_mtow, mtow_sweep, owe_performances)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=mtow_sweep,
            y=owe_structure,
            mode="lines",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=mtow_sweep,
            y=owe_performances,
            mode="lines",
        )
    )

    fig.update_layout(
        title={
            "text": "Aircraft mass-performances loop",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        xaxis={
            "title": "MTOW [kg]",
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

    return fig, converged_owe, converged_mtow
