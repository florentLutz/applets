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

    # Initialize checkpoints, should only trigger at the beginning of session
    if "checkpoint_1" not in st.session_state:
        st.session_state.checkpoint_1 = False

    if "checkpoint_2" not in st.session_state:
        st.session_state.checkpoint_2 = False

    if "MTOW" not in st.session_state:
        st.session_state.mtow = 100e3

    # ============================================================
    # SIDEBAR — DESIGN PARAMETERS
    # ============================================================

    with st.sidebar:
        st.header("Analysis")

        radio_options = ["Overview"]

        if st.session_state.checkpoint_1:
            radio_options.append("Constraints diagram")

        page = st.radio(
            "Select discipline",
            radio_options,
        )

    with st.sidebar:
        st.divider()

        if page == "Overview":
            st.header("Design parameters")

            # --------------------------------------------------------
            # Aerodynamics
            # --------------------------------------------------------
            st.subheader("Geometry")

            npax_per_row = st.slider(
                "Number of passengers per row [-]",
                min_value=3,
                max_value=10,
                value=4,
                step=1,
            )
            npax = st.slider(
                "Number of passengers [-]",
                min_value=10 * npax_per_row,
                max_value=100 * npax_per_row,
                value=20 * npax_per_row,
                step=npax_per_row,
            )

            def _change_checkpoint_1():
                st.session_state.checkpoint_1 = not st.session_state.checkpoint_1

            st.checkbox(
                "Fuselage done", key="Fuselage_done", on_change=_change_checkpoint_1
            )

            # --------------------------------------------------------
            # Propulsion
            # --------------------------------------------------------

        elif page == "Constraints diagram":
            st.header("Operational requirements")

            approach_speed = st.slider(
                "Approach speed [kts]",
                min_value=100,
                max_value=200,
                value=145,
                step=1,
            )
            tofl = st.slider(
                "Takeoff Field Length [m]",
                min_value=1500,
                max_value=3500,
                value=2000,
                step=10,
            )
            rate_of_climb = st.slider(
                "Rate of climb [ft/min]",
                min_value=1500,
                max_value=5000,
                value=2000,
                step=100,
            )
            cruise_mach = st.slider(
                "Cruise Mach number [-]",
                min_value=0.7,
                max_value=0.82,
                value=0.75,
                step=0.01,
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

            if not st.session_state.checkpoint_2:
                st.metric(
                    label="MTOW",
                    value="—",
                )
            else:
                result, init_guess_warning = st.columns([1,1])
                with result:
                    st.metric(
                        label="MTOW",
                        value=str(st.session_state.mtow),
                    )
                with init_guess_warning:
                    st.caption("Initial guess")

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

    if page == "Constraints diagram":
        col_plot_constraints, col_point_validity = st.columns([2, 1])

        with col_point_validity:
            st.subheader("Design point selection")
            wing_loading = st.number_input(
                "Design wing loading [kg/m²]",
                value=450.0,
                placeholder="Type a number...",
                min_value=100.0,
                max_value=900.0,
                step=1.0
            )
            thrust_loading = st.number_input(
                "Design thrust loading [-]",
                value=0.5,
                placeholder="Type a number...",
                min_value=0.0,
                max_value=1.0,
                step=0.01
            )

        constraint_diagram, respected_constraints, broken_constraints = (
            plot_library.constraints_diagram(
                stall_speed=approach_speed
                / 1.22,  # Classic ratio between approach and stall speed,
                tofl=tofl,
                rate_of_climb=rate_of_climb,
                cruise_mach=cruise_mach,
                wing_loading_design=wing_loading,
                thrust_loading_design=thrust_loading,
            )
        )

        constraint_diagram.update_layout(
            xaxis_title="Wing loading [kg/m²]",
            yaxis_title="Thrust loading [-]",
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )

        with col_plot_constraints:
            st.subheader("Constraint diagram")

            st.plotly_chart(constraint_diagram, width="stretch")

        with col_point_validity:
            st.subheader("Validated constraints")

            for constraint in respected_constraints:
                st.write(constraint)

            st.subheader("Broken constraints")

            for constraint in broken_constraints:
                st.write(constraint)

        if st.session_state.checkpoint_1 and not broken_constraints:
            st.session_state.checkpoint_2 = True
        else:
            st.session_state.checkpoint_2 = False