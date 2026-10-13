import plots as plot_library
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================
if __name__ == "__main__":
    st.set_page_config(
        page_title="Aircraft Design",
        page_icon="✈️",
        layout="wide",
    )

    st.title("✈️ Aircraft Design")

    # ============================================================
    # SIDEBAR — DESIGN PARAMETERS
    # ============================================================

    with st.sidebar:
        st.header("Analysis")

        page = st.radio(
            "Select discipline",
            [
                "Overview",
                "Aerodynamics",
                "Propulsion",
                "Weights",
            ],
        )

    with st.sidebar:
        st.divider()

        if page == "Overview":
            st.header("Design parameters")

            # --------------------------------------------------------
            # Aerodynamics
            # --------------------------------------------------------

            with st.expander("Geometry", expanded=True):
                npax_per_row = st.slider(
                    "Number of passengers per row",
                    min_value=3,
                    max_value=10,
                    value=4,
                    step=1,
                )

                npax = st.slider(
                    "Number of passengers",
                    min_value=10 * npax_per_row,
                    max_value=100 * npax_per_row,
                    value=20 * npax_per_row,
                    step=npax_per_row,
                )

                wing_area = st.slider(
                    "Wing area [m²]",
                    min_value=50.0,
                    max_value=300.0,
                    value=150.0,
                    step=5.0,
                )

            # --------------------------------------------------------
            # Propulsion
            # --------------------------------------------------------

            with st.expander("🔥 Propulsion", expanded=True):
                thrust_to_weight = st.slider(
                    "Thrust-to-weight ratio",
                    min_value=0.1,
                    max_value=0.5,
                    value=0.25,
                    step=0.01,
                )

                sfc = st.slider(
                    "Specific fuel consumption",
                    min_value=0.3,
                    max_value=1.2,
                    value=0.6,
                    step=0.01,
                )

            # --------------------------------------------------------
            # Weight
            # --------------------------------------------------------

            with st.expander("⚖️ Weight", expanded=True):
                mtow = st.slider(
                    "MTOW [kg]",
                    min_value=10_000,
                    max_value=150_000,
                    value=50_000,
                    step=1_000,
                )

                payload = st.slider(
                    "Payload [kg]",
                    min_value=1_000,
                    max_value=50_000,
                    value=10_000,
                    step=500,
                )

            # --------------------------------------------------------
            # Performance
            # --------------------------------------------------------

            with st.expander("🚀 Performance", expanded=False):
                cruise_speed = st.slider(
                    "Cruise speed [m/s]",
                    min_value=100,
                    max_value=300,
                    value=230,
                    step=5,
                )

                cruise_altitude = st.slider(
                    "Cruise altitude [m]",
                    min_value=5_000,
                    max_value=15_000,
                    value=10_000,
                    step=500,
                )

    # ============================================================
    # CALCULATION
    # ============================================================
    # The right numbers we should get is npax=150, 6 pax per rows, wing_area=122.4
    if page == "Overview":
        show_reference_aircraft = st.checkbox(
            "Show reference aircraft outline",
            key="ref_aircraft_outline",
        )
        # "Right answers" should be here, 150, 6, 122.4, 1.0, 0.09 and 2.0 * 111.2e3
        fig = plot_library.aircraft_geometry_plot(
            npax=npax,
            npax_per_row=npax_per_row,
            wing_area=122.4,
            htp_volume_coefficient=1.0,
            vtp_volume_coefficient=0.09,
            mto_thrust=2.0 * 111.2e3,
            show_reference_aircraft=show_reference_aircraft,
        )

        fig.update_layout(
            xaxis_title="Design variable",
            yaxis_title="Performance",
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )

        # ============================================================
        # MAIN LAYOUT
        # ============================================================
        col_plot, col_fom = st.columns([2, 1])

        # ============================================================
        # LEFT — PLOT
        # ============================================================

        with col_plot:
            st.subheader("Aircraft geometry")

            st.plotly_chart(fig, width="stretch")

        # ============================================================
        # RIGHT — FIGURES OF MERIT
        # ============================================================

        with col_fom:
            st.subheader("Figures of merit")

            st.metric(
                label="MTOW",
                value=f"{mtow:,} kg",
            )

            st.metric(
                label="Payload",
                value=f"{payload:,} kg",
            )

            st.metric(
                label="Aspect ratio",
                value=f"{10.0:.1f}",
            )

            st.metric(
                label="Wing loading",
                value="—",
                help="To be calculated",
            )

            st.metric(
                label="L/D",
                value="—",
                help="To be calculated",
            )

            st.metric(
                label="Range",
                value="—",
                help="To be calculated",
            )
