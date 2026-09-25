import numpy as np
import plotly.graph_objects as go
import streamlit as st

PERIOD = 50e-6
TIME_STEP = PERIOD / 500.0


def background_legend():
    legend = "<div style='display: flex; gap: 20px; flex-wrap: wrap;'>"

    legend += """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 50px;
                height: 35px;
                background-color: rgba(0, 128, 0, 0.15);
                border: 1px solid rgba(128,128,128,0.4);
            "></div>
            <span>K1 closed</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 50px;
                height: 35px;
                background-color: rgba(128, 0, 0, 0.15);
                border: 1px solid rgba(128,128,128,0.4);
            "></div>
            <span>K2 closed</span>
        </div>
    """

    legend += "</div>"

    st.markdown(legend, unsafe_allow_html=True)


def plot_v_h(u_dc: float) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    v_h = np.where(k1_closed, u_dc, 0.0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=v_h, mode="lines", name=r"V_h", line={"width": 5})
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=1.05 * u_dc,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        u_dc,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="U_DC",
        annotation_position="bottom right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[0, 1.025 * u_dc])
    fig.update_xaxes(range=[0, 0.995 * max(time)])

    return fig


def plot_v_l(u_dc: float, u_battery: float) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    v_l = np.where(k1_closed, u_dc - u_battery, -u_battery)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=v_l, mode="lines", name=r"V_l", line={"width": 5})
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=-1.05 * u_battery,
        y1=1.05 * (u_dc - u_battery),
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        u_dc - u_battery,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="U_DC - U_b",
        annotation_position="bottom right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )
    fig.add_hline(
        -u_battery,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="- U_b",
        annotation_position="top right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[-1.025 * u_battery, 1.025 * (u_dc - u_battery)])
    fig.update_xaxes(range=[0, 0.995 * max(time)])

    return fig


def plot_i_b(
    u_dc: float,
    u_battery: float,
    inductance: float,
    mean_value: float,
    delta: float,
    alpha: float,
    mode: str = "normal",
) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    sign = -1.0 if mode == "secours" else 1.0

    i_b = np.where(
        k1_closed,
        (u_dc - u_battery) / inductance * (time % PERIOD)
        + sign * mean_value
        - delta / 2.0,
        -u_battery / inductance * ((time - alpha * PERIOD) % PERIOD)
        + sign * mean_value
        + delta / 2.0,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=i_b, mode="lines", name=r"V_l", line={"width": 5})
    )

    # We show the amplitude at the first peak
    fig.add_shape(
        type="line",
        x0=time[k2_closed_starts[0]],
        x1=time[k2_closed_starts[0]],
        y0=sign * mean_value - delta / 2.0,
        y1=sign * mean_value + delta / 2.0,
        line={"width": 2, "dash": "dash", "color": "grey"},
    )

    fig.add_annotation(
        x=time[k2_closed_starts[0]],
        y=sign * delta,
        text=r"Delta i_b",
        showarrow=False,
        xshift=-5,
        yshift=-15,
        xanchor="right",
        font={"size": 17, "color": "grey"},
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=1.05 * sign * (mean_value + delta / 2.0),
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        sign * mean_value,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="<i_b>",
        annotation_position="top right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[0.0, 1.025 * sign * (mean_value + delta / 2.0)].sort())
    fig.update_xaxes(range=[0, 0.995 * max(time)])

    return fig


def plot_i_e(
    u_dc: float,
    u_battery: float,
    inductance: float,
    mean_value: float,
    delta: float,
    mode: str = "normal",
) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    sign = -1.0 if mode == "secours" else 1.0

    i_e = np.where(
        k1_closed,
        (u_dc - u_battery) / inductance * (time % PERIOD)
        + sign * mean_value
        - delta / 2.0,
        0,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=i_e, mode="lines", name=r"V_l", line={"width": 5})
    )

    # We show the amplitude at the first peak
    fig.add_shape(
        type="line",
        x0=time[k2_closed_starts[0]] + PERIOD / 50.0,
        x1=time[k2_closed_starts[0]] + PERIOD / 50.0,
        y0=sign * mean_value - delta / 2.0,
        y1=sign * mean_value + delta / 2.0,
        line={"width": 2, "dash": "dash", "color": "grey"},
    )

    # We add a slight offset to make it cleaner
    fig.add_annotation(
        x=time[k2_closed_starts[0]] + PERIOD / 50.0,
        y=sign * delta,
        text=r"Delta i_b",
        showarrow=False,
        xshift=+5,
        yshift=-15,
        xanchor="left",
        font={"size": 17, "color": "grey"},
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=1.05 * sign * (mean_value + delta / 2.0),
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        sign * mean_value,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="<i_b>",
        annotation_position="top right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[0.0, 1.025 * sign * (mean_value + delta / 2.0)].sort())
    fig.update_xaxes(range=[0, 0.995 * max(time)])

    return fig


def plot_i_k2(
    u_battery: float,
    inductance: float,
    mean_value: float,
    delta: float,
    alpha: float,
    mode: str = "normal",
) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    sign = -1.0 if mode == "secours" else 1.0

    i_k2 = np.where(
        k1_closed,
        0,
        -(
            -u_battery / inductance * ((time - alpha * PERIOD) % PERIOD)
            + sign * mean_value
            + delta / 2.0
        ),
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=i_k2, mode="lines", name=r"V_l", line={"width": 5})
    )

    # We show the amplitude at the first peak
    fig.add_shape(
        type="line",
        x0=time[k2_closed_starts[0]] - PERIOD / 50.0,
        x1=time[k2_closed_starts[0]] - PERIOD / 50.0,
        y0=-(sign * mean_value - delta / 2.0),
        y1=-(sign * mean_value + delta / 2.0),
        line={"width": 2, "dash": "dash", "color": "grey"},
    )

    fig.add_annotation(
        x=time[k2_closed_starts[0]] - PERIOD / 50.0,
        y=-sign * delta,
        text=r"Delta i_b",
        showarrow=False,
        xshift=-5,
        yshift=-15,
        xanchor="right",
        font={"size": 17, "color": "grey"},
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=-(1.05 * sign * (mean_value + delta / 2.0)),
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        -sign * mean_value,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="<i_b>",
        annotation_position="top right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[0.0, -1.025 * sign * (mean_value + delta / 2.0)].sort())
    fig.update_xaxes(range=[0, 0.995 * max(time)])

    return fig


def plot_v_k1(u_dc: float) -> go.Figure:

    k1_closed = st.session_state.k1_closed
    time = st.session_state.time
    k1_closed_starts = st.session_state.k1_closed_starts
    k2_closed_starts = st.session_state.k2_closed_starts

    v_k1 = np.where(k1_closed, 0.0, u_dc)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time, y=v_k1, mode="lines", name=r"V_l", line={"width": 5})
    )

    for idx, _ in enumerate(k2_closed_starts):
        fig.add_vrect(
            x0=time[k1_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            fillcolor="green",
            opacity=0.15,
            line_width=0,
            layer="below",
        )
        # In theory this is unsafe because we are not guaranteed that idx + 1 us available but in
        # practice k1_closed_starts is one element bigger
        fig.add_vrect(
            x0=time[k2_closed_starts[idx]] - TIME_STEP / 2.0,
            x1=time[k1_closed_starts[idx + 1]] - TIME_STEP / 2.0,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        height=300,
        width=1200,
        margin={"l": 5, "r": 5, "t": 5, "b": 5},
    )

    # Axe X
    fig.add_shape(
        type="line",
        x0=0,
        x1=1.01 * max(time),
        y0=0,
        y1=0,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    # Axe Y
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0.0,
        y1=1.05 * u_dc,
        xref="x",
        yref="y",
        line={"width": 2},
    )

    fig.add_hline(
        u_dc,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text="U_DC",
        annotation_position="bottom right",
        annotation={"font": {"size": 17, "color": "grey"}, "align": "left"},
    )

    fig.update_yaxes(range=[0.0, 1.025 * u_dc])
    fig.update_xaxes(range=[0.0, 0.995 * max(time)])

    return fig


def produce_tab_be4():
    st.title("Réseau électrique de bord à courant continu HVDC")

    col_sidebar, col_results = st.columns([1, 4])

    st.markdown(
        """
        <style>
        [data-testid="stHorizontalBlock"] > div:nth-child(1) {
            border-right: 1px solid rgba(128, 128, 128, 0.3);
            padding-right: 2rem;
        }

        [data-testid="stHorizontalBlock"] > div:nth-child(2) {
            padding-left: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with col_sidebar:
        battery_voltage = st.slider(
            "Battery voltage", min_value=140.0, max_value=230.0, step=1.0
        )

        show_section_1 = st.checkbox(
            "Mode chargement de la batterie",
            key="show_be_4_section_1",
        )

        if show_section_1:
            st.subheader("Mode normal - chargement de la batterie")
            show_v_h_mode_1 = st.checkbox(
                "V_h(t)",
                key="show_mode_1_V_h",
            )
            show_v_l_mode_1 = st.checkbox(
                "V_L(t)",
                key="show_mode_1_V_L",
            )
            show_i_b_mode_1 = st.checkbox(
                "i_b(t)",
                key="show_mode_1_i_b",
            )
            show_i_e_mode_1 = st.checkbox(
                "i_e(t)",
                key="show_mode_1_i_e",
            )
            show_i_k2_mode_1 = st.checkbox(
                "i_k2(t)",
                key="show_mode_1_i_k2",
            )
            show_v_k1_mode_1 = st.checkbox(
                "V_k1(t)",
                key="show_mode_1_V_k1",
            )

        st.divider()

        show_section_2 = st.checkbox(
            "Mode secours",
            key="show_be_4_section_2",
        )
        if show_section_2:
            st.subheader("Mode secours")
            show_v_h_mode_2 = st.checkbox(
                "V_h(t)",
                key="show_mode_2_V_h",
            )
            show_v_l_mode_2 = st.checkbox(
                "V_L(t)",
                key="show_mode_2_V_L",
            )
            show_i_b_mode_2 = st.checkbox(
                "i_b(t)",
                key="show_mode_2_i_b",
            )
            show_i_e_mode_2 = st.checkbox(
                "i_e(t)",
                key="show_mode_2_i_e",
            )
            show_i_k2_mode_2 = st.checkbox(
                "i_k2(t)",
                key="show_mode_2_i_k2",
            )
            show_v_k1_mode_2 = st.checkbox(
                "V_k1(t)",
                key="show_mode_2_V_k1",
            )

    dc_network_voltage = 270.0
    alpha_main = battery_voltage / dc_network_voltage
    inductance_main = 1.68e-3
    mean_value_ib = battery_voltage * PERIOD * (1.0 - alpha_main) / inductance_main
    delta_ib = (
        dc_network_voltage * alpha_main * (1.0 - alpha_main) / inductance_main * PERIOD
    )

    # Span over 3 periods
    st.session_state.time = np.arange(0.0, 3.0 * PERIOD, TIME_STEP)
    st.session_state.k1_closed = k1_closed = (
        st.session_state.time % PERIOD <= alpha_main * PERIOD
    )

    # Check all change in True/False status
    switch_status_change = np.r_[
        0, np.where(k1_closed[1:] != k1_closed[:-1])[0] + 1
    ].tolist()
    switch_status_change.append(len(k1_closed) - 1)
    # K1 is closed every two change and starts open
    st.session_state.k1_closed_starts = switch_status_change[::2]
    st.session_state.k2_closed_starts = switch_status_change[1::2]

    with col_results:
        background_legend()

        if show_section_1:
            st.header("Mode normal - chargement de la batterie")

            if show_v_h_mode_1:
                with st.expander(r"V_h(t)", expanded=True):
                    fig = plot_v_h(u_dc=dc_network_voltage)
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

            if show_v_l_mode_1:
                with st.expander(r"V_l(t)", expanded=True):
                    fig = plot_v_l(u_dc=dc_network_voltage, u_battery=battery_voltage)
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

            if show_i_b_mode_1:
                with st.expander(r"i_b(t)", expanded=True):
                    fig = plot_i_b(
                        u_dc=dc_network_voltage,
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                        alpha=alpha_main,
                    )
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

            if show_i_e_mode_1:
                with st.expander(r"i_e(t)", expanded=True):
                    fig = plot_i_e(
                        u_dc=dc_network_voltage,
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                    )
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

            if show_i_k2_mode_1:
                with st.expander(r"i_k2(t)", expanded=True):
                    fig = plot_i_k2(
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                        alpha=alpha_main,
                    )
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

            if show_v_k1_mode_1:
                with st.expander(r"V_k1(t)", expanded=True):
                    fig = plot_v_k1(u_dc=dc_network_voltage)
                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

        if show_section_2:
            st.header("Mode secours")

            if show_v_h_mode_2:
                with st.expander(r"V_h(t)", expanded=True):
                    fig = plot_v_h(u_dc=dc_network_voltage)
                    st.plotly_chart(fig, width="stretch", key="v_h_mode_2")

            if show_v_l_mode_2:
                with st.expander(r"V_l(t)", expanded=True):
                    fig = plot_v_l(u_dc=dc_network_voltage, u_battery=battery_voltage)
                    st.plotly_chart(fig, width="stretch", key="v_l_mode_2")

            if show_i_b_mode_2:
                with st.expander(r"i_b(t)", expanded=True):
                    fig = plot_i_b(
                        u_dc=dc_network_voltage,
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                        alpha=alpha_main,
                        mode="secours",
                    )
                    st.plotly_chart(fig, width="stretch", key="i_b_mode_2")

            if show_i_e_mode_2:
                with st.expander(r"i_e(t)", expanded=True):
                    fig = plot_i_e(
                        u_dc=dc_network_voltage,
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                        mode="secours",
                    )
                    st.plotly_chart(fig, width="stretch", key="i_e_mode_2")

            if show_i_k2_mode_2:
                with st.expander(r"i_k2(t)", expanded=True):
                    fig = plot_i_k2(
                        u_battery=battery_voltage,
                        inductance=inductance_main,
                        mean_value=mean_value_ib,
                        delta=delta_ib,
                        alpha=alpha_main,
                        mode="secours",
                    )
                    st.plotly_chart(fig, width="stretch", key="i_k2_mode_2")

            if show_v_k1_mode_2:
                with st.expander(r"V_k1(t)", expanded=True):
                    fig = plot_v_k1(u_dc=dc_network_voltage)
                    st.plotly_chart(fig, width="stretch", key="v_k1_mode_2")
