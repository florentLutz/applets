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

            with st.expander("🌬️ Aerodynamics", expanded=True):
                aspect_ratio = st.slider(
                    "Wing aspect ratio",
                    min_value=5.0,
                    max_value=15.0,
                    value=9.0,
                    step=0.1,
                )

                sweep = st.slider(
                    "Wing sweep [deg]",
                    min_value=0.0,
                    max_value=45.0,
                    value=25.0,
                    step=1.0,
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
    if page == "Overview":
        fig = plot_library.aircraft_geometry_plot(150, 6, 120, 35, 25000.0)

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
                value=f"{aspect_ratio:.1f}",
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
