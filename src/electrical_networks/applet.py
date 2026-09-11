import streamlit as st
import plotly.graph_objects as go
import numpy as np


def plot_mcc_pm_torque_current(constant):
    mcc_pm_torque_current_fig = go.Figure()
    current = np.linspace(0, 27.5)
    mcc_pm_torque_current_fig.add_scatter(
        x=current,
        y=constant * current,
        mode="lines",
    )
    mcc_pm_torque_current_fig.update_xaxes(
        title="Courant [A]", title_font=dict(size=20)
    )
    mcc_pm_torque_current_fig.update_yaxes(
        title="Couple [N.m]", title_font=dict(size=20), range=[0, 4.169]
    )
    return mcc_pm_torque_current_fig


def plot_mcc_pm_torque_speed(constant, v_batt, windings_resistance):
    mcc_pm_torque_speed_fig = go.Figure()
    rotation_frequency = np.linspace(0.0, 3000.0)
    rotation_speed = rotation_frequency * 2.0 * np.pi / 60
    torque = (
        -(constant**2.0) * rotation_speed + constant * v_batt
    ) / windings_resistance
    mcc_pm_torque_speed_fig.add_scatter(
        x=rotation_frequency,
        y=torque,
        mode="lines",
    )
    mcc_pm_torque_speed_fig.update_xaxes(
        title="Fréquence de rotation [tr/min]", title_font=dict(size=20)
    )
    mcc_pm_torque_speed_fig.update_yaxes(
        title="Couple [N.m]", title_font=dict(size=20), range=[0, 82]
    )
    return mcc_pm_torque_speed_fig


def plot_mcc_pm_speed_current(constant, v_batt, windings_resistance):
    mcc_pm_speed_current_fig = go.Figure()
    current = np.linspace(0, 27.5)
    rotation_speed = v_batt / constant - windings_resistance * current / constant
    rotation_frequency = rotation_speed * 60.0 / 2.0 / np.pi
    mcc_pm_speed_current_fig.add_scatter(
        x=current,
        y=rotation_frequency,
        mode="lines",
    )
    mcc_pm_speed_current_fig.update_xaxes(title="Courant [A]", title_font=dict(size=20))
    mcc_pm_speed_current_fig.update_yaxes(
        title="Fréquence de rotation [tr/min]",
        title_font=dict(size=20),
        range=[0, 3550],
    )
    return mcc_pm_speed_current_fig


def plot_mcc_se_torque_current(constant):
    mcc_pm_torque_current_fig = go.Figure()
    current = np.linspace(0, 27.5)
    mcc_pm_torque_current_fig.add_scatter(
        x=current,
        y=constant * current**2.0,
        mode="lines",
    )
    mcc_pm_torque_current_fig.update_xaxes(
        title="Courant [A]", title_font=dict(size=20)
    )
    mcc_pm_torque_current_fig.update_yaxes(
        title="Couple [N.m]", title_font=dict(size=20), range=[0, 4.169]
    )
    return mcc_pm_torque_current_fig


def plot_mcc_se_torque_speed(
    constant, v_batt, windings_resistance, inductor_resistance
):
    mcc_pm_torque_speed_fig = go.Figure()
    rotation_frequency = np.linspace(0.0, 3000.0)
    rotation_speed = rotation_frequency * 2.0 * np.pi / 60
    torque = (
        constant
        * (
            v_batt
            / (constant * rotation_speed + windings_resistance + inductor_resistance)
        )
        ** 2.0
    )
    mcc_pm_torque_speed_fig.add_scatter(
        x=rotation_frequency,
        y=torque,
        mode="lines",
    )
    mcc_pm_torque_speed_fig.update_xaxes(
        title="Fréquence de rotation [tr/min]", title_font=dict(size=20)
    )
    mcc_pm_torque_speed_fig.update_yaxes(
        title="Couple [N.m]", title_font=dict(size=20), range=[0, 82]
    )
    return mcc_pm_torque_speed_fig


def plot_mcc_se_speed_current(
    constant, v_batt, windings_resistance, inductor_resistance
):
    mcc_pm_speed_current_fig = go.Figure()
    current = np.linspace(1, 27.5)
    rotation_speed = (
        v_batt / current - windings_resistance - inductor_resistance
    ) / constant
    rotation_frequency = rotation_speed * 60.0 / 2.0 / np.pi
    mcc_pm_speed_current_fig.add_scatter(
        x=current,
        y=rotation_frequency,
        mode="lines",
    )
    mcc_pm_speed_current_fig.update_xaxes(
        title="Courant [A]", title_font=dict(size=20)
    )
    mcc_pm_speed_current_fig.update_yaxes(
        title="Fréquence de rotation [tr/min]",
        title_font=dict(size=20),
    )
    return mcc_pm_speed_current_fig


if __name__ == "__main__":
    st.set_page_config(
        page_title="Etude de machines électriques en régime permanent et transitoire",
        layout="wide",
    )

    st.title("Etude de machines électriques en régime permanent et transitoire")

    show_section_1 = st.sidebar.checkbox(
        "Machine à courant continu - aimants permanents",
        key="show_section_1",
    )

    battery_voltage = 56.0

    if show_section_1:
        st.header("Machine à courant continu - aimants permanents")

        mcc_pm_constant = 0.1516
        mcc_pm_re = 0.11

        st.sidebar.subheader("Courbes caractéristiques")

        show_1_1 = st.sidebar.checkbox(
            "Couple = f(courant)",
            key="show_1_1",
        )

        if show_1_1:
            with st.expander("Couple = f(courant)", expanded=True):
                fig = plot_mcc_pm_torque_current(mcc_pm_constant)
                st.plotly_chart(
                    fig,
                    width="stretch",
                )

        show_1_2 = st.sidebar.checkbox(
            "Couple = f(fréquence de rotation)",
            key="show_1_2",
        )

        if show_1_2:
            with st.expander("Couple = f(fréquence de rotation)", expanded=True):
                fig = plot_mcc_pm_torque_speed(
                    mcc_pm_constant, battery_voltage, mcc_pm_re
                )
                st.plotly_chart(
                    fig,
                    width="stretch",
                )

        show_1_3 = st.sidebar.checkbox(
            "Fréquence de rotation = f(courant)",
            key="show_1_3",
        )

        if show_1_3:
            with st.expander("Fréquence de rotation = f(courant)", expanded=True):
                fig = plot_mcc_pm_speed_current(
                    mcc_pm_constant, battery_voltage, mcc_pm_re
                )
                st.plotly_chart(
                    fig,
                    width="stretch",
                )

    st.sidebar.divider()

    show_section_2 = st.sidebar.checkbox(
        "Machine à courant continu - excitation série",
        key="show_section_2",
    )

    if show_section_2:
        st.header("Machine à courant continu - excitation série")

        mcc_se_constant = 0.0055127
        mcc_se_re = 0.02
        mcc_se_ri = 0.1

        st.sidebar.subheader("Courbes caractéristiques")

        show_2_1 = st.sidebar.checkbox(
            "Couple = f(courant)",
            key="show_2_1",
        )

        if show_2_1:
            with st.expander("Couple = f(courant)", expanded=True):
                fig = plot_mcc_se_torque_current(mcc_se_constant)
                st.plotly_chart(
                    fig,
                    width="stretch",
                )

        show_2_2 = st.sidebar.checkbox(
            "Couple = f(fréquence de rotation)",
            key="show_2_2",
        )

        if show_2_2:
            with st.expander("Couple = f(fréquence de rotation)", expanded=True):
                fig = plot_mcc_se_torque_speed(
                    mcc_se_constant, battery_voltage, mcc_se_re, mcc_se_ri
                )
                st.plotly_chart(
                    fig,
                    width="stretch",
                )

        show_2_3 = st.sidebar.checkbox(
            "Fréquence de rotation = f(courant)",
            key="show_2_3",
        )

        if show_2_3:
            with st.expander("Fréquence de rotation = f(courant)", expanded=True):
                fig = plot_mcc_se_speed_current(
                    mcc_se_constant, battery_voltage, mcc_se_re, mcc_se_ri
                )
                st.plotly_chart(
                    fig,
                    width="stretch",
                )
