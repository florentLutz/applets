import plots as plot_library
import streamlit as st
from plots.constants import DESIGN_PAX_MASS

DEFAULT_MTOW = 100e3
DEFAULT_WING_LOADING = 250
DEFAULT_THRUST_LOADING = 0.5
DEFAULT_HTP_VOLUME_COEFFICIENT = 0.5
DEFAULT_VTP_VOLUME_COEFFICIENT = 0.02
DEFAULT_LD_MAX = -1  # Won't be displayed but need to be recognizable
DEFAULT_OWE = -42  # Won't be displayed but need to be recognizable

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

    if "checkpoint_3" not in st.session_state:
        st.session_state.checkpoint_3 = False

    if "checkpoint_4" not in st.session_state:
        st.session_state.checkpoint_4 = False

    if "checkpoint_5" not in st.session_state:
        st.session_state.checkpoint_5 = False

    if "checkpoint_6" not in st.session_state:
        st.session_state.checkpoint_6 = False

    if "mtow" not in st.session_state:
        st.session_state.mtow = DEFAULT_MTOW

    if "wing_loading" not in st.session_state:
        st.session_state.wing_loading = (
            DEFAULT_WING_LOADING  # Initialize at an obviously wrong
        )
        # value for comic effect, in kg/m2

    if "thrust_loading" not in st.session_state:
        st.session_state.thrust_loading = DEFAULT_THRUST_LOADING  # Same, in no units

    if "htp_vol_coeff" not in st.session_state:
        st.session_state.htp_vol_coeff = (
            DEFAULT_HTP_VOLUME_COEFFICIENT  # Same, in no units
        )

    if "vtp_vol_coeff" not in st.session_state:
        st.session_state.vtp_vol_coeff = (
            DEFAULT_VTP_VOLUME_COEFFICIENT  # Same, in no units
        )

    if "l_d_max" not in st.session_state:
        st.session_state.l_d_max = DEFAULT_LD_MAX

    if "owe_structure" not in st.session_state:
        st.session_state.owe_structure = DEFAULT_OWE

    if "owe_performances" not in st.session_state:
        st.session_state.owe_performances = DEFAULT_OWE

    # ============================================================
    # SIDEBAR — DESIGN PARAMETERS
    # ============================================================

    with st.sidebar:
        st.header("Analysis")

        radio_options = ["Overview"]

        # Should actually be added at the end so that if a widget changes and resets those
        # they can be enabled after working once.
        if st.session_state.checkpoint_1:
            radio_options.append("Constraints diagram")
        if st.session_state.checkpoint_2:
            radio_options.append("Aerodynamics")
        if st.session_state.checkpoint_3:
            radio_options.append("Masses")
        if st.session_state.checkpoint_4:
            radio_options.append("Design mission")
        if st.session_state.checkpoint_5:
            radio_options.append("Mass performances loop")
        if st.session_state.checkpoint_6:
            radio_options.append("Payload-range")

        page = st.radio(
            "Select discipline",
            radio_options,
            persist_state="session",
            key="radio_selection",
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
                persist_state="session",
                key="npax_row",
            )
            npax = st.slider(
                "Number of passengers [-]",
                min_value=10 * npax_per_row,
                max_value=100 * npax_per_row,
                value=20 * npax_per_row,
                step=npax_per_row,
                persist_state="session",
                key="npax",
            )

            def _change_checkpoint_1():
                st.session_state.checkpoint_1 = not st.session_state.checkpoint_1

            st.session_state.checkpoint_1 = st.checkbox(
                "Fuselage done",
                key="Fuselage_done",
                on_change=_change_checkpoint_1,
                persist_state="session",
            )

            if st.session_state.checkpoint_2:
                st.session_state.htp_vol_coeff = st.number_input(
                    "HTP volume coefficient [-]",
                    value=DEFAULT_HTP_VOLUME_COEFFICIENT,
                    placeholder="Type a number...",
                    min_value=0.1,
                    max_value=1.1,
                    step=0.01,
                    persist_state="session",
                    key="htp_vol_coeff_widget",
                )
                st.session_state.vtp_vol_coeff = st.number_input(
                    "VTP volume coefficient [-]",
                    value=DEFAULT_VTP_VOLUME_COEFFICIENT,
                    placeholder="Type a number...",
                    min_value=0.01,
                    max_value=0.12,
                    step=0.01,
                    persist_state="session",
                    key="vtp_vol_coeff_widget",
                )

        elif page == "Constraints diagram":
            st.header("Operational requirements")

            approach_speed = st.slider(
                "Approach speed [kts]",
                min_value=100,
                max_value=200,
                value=145,
                step=1,
                persist_state="session",
                key="vapp_cons",
            )
            tofl = st.slider(
                "Takeoff Field Length [m]",
                min_value=1500,
                max_value=3500,
                value=2000,
                step=10,
                persist_state="session",
                key="tofl_cons",
            )
            rate_of_climb = st.slider(
                "Rate of climb [ft/min]",
                min_value=1500,
                max_value=5000,
                value=2000,
                step=100,
                persist_state="session",
                key="roc_cons",
            )
            cruise_mach = st.slider(
                "Cruise Mach number [-]",
                min_value=0.7,
                max_value=0.82,
                value=0.75,
                step=0.01,
                persist_state="session",
                key="m_cons",
            )

        elif page == "Design mission":
            st.header("Design mission definition")

            design_range = st.slider(
                "Design range [nm]",
                min_value=1000,
                max_value=6000,
                value=4000,
                step=50,
                persist_state="session",
                key="design_range",
            )
            st.metric(
                label="Rate of climb [ft/min]",
                value=st.session_state.roc_cons,
            )
            st.metric(
                label="Cruise Mach number [-]",
                value=st.session_state.m_cons,
            )
            st.metric(
                label="Cruise altitude [ft]",
                value=35000.0,
            )
        # No specific sidebar for the aerodynamics, no options to choose from really, just to
        # observe, same for the mass and the mass performances loop.

        elif page == "Payload-range":
            k_l_d_max = st.slider(
                "Aerodynamic improvement factor [-]",
                min_value=0.8,
                max_value=1.2,
                value=1.0,
                step=0.01,
                persist_state="session",
                key="k_l_d_max",
            )
            k_sfc = st.slider(
                "Propulsion improvement factor [-]",
                min_value=0.8,
                max_value=1.2,
                value=1.0,
                step=0.01,
                persist_state="session",
                key="k_sfc",
            )
            k_mass = st.slider(
                "Mass improvement factor [-]",
                min_value=0.8,
                max_value=1.2,
                value=1.0,
                step=0.01,
                persist_state="session",
                key="k_mass",
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
            npax=st.session_state.npax,
            npax_per_row=npax_per_row,
            wing_area=st.session_state.mtow / st.session_state.wing_loading,
            htp_volume_coefficient=st.session_state.htp_vol_coeff,
            vtp_volume_coefficient=st.session_state.vtp_vol_coeff,
            mto_thrust=st.session_state.mtow * 9.81 * st.session_state.thrust_loading,
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
                if st.session_state.mtow == DEFAULT_MTOW:
                    result, init_guess_warning = st.columns([1, 1])
                    with result:
                        st.metric(
                            label="MTOW",
                            value=str(round(st.session_state.mtow, 0)),
                        )
                    with init_guess_warning:
                        st.caption("Initial guess")
                else:
                    st.metric(
                        label="MTOW",
                        value=str(round(st.session_state.mtow, 0)),
                    )

                st.metric(
                    label="Wing loading [kg/m²]",
                    value=str(st.session_state.wing_loading),
                )

                st.metric(
                    label="Thrust loading [-]",
                    value=str(st.session_state.thrust_loading),
                )

            if st.session_state.l_d_max == DEFAULT_LD_MAX:
                st.metric(
                    label="L/D",
                    value="—",
                    help="To be calculated",
                )
            else:
                st.metric(
                    label="L/D",
                    value=round(st.session_state.l_d_max, 2),
                    help="Maximum lift over drag ratio",
                )

            # Until we do the loop to converge the structure and performances OWE are different.
            # Once we have converge, they are by definition, the same
            if (
                abs(
                    1.0
                    - st.session_state.owe_performances / st.session_state.owe_structure
                )
                > 0.01
                or st.session_state.owe_performances == DEFAULT_OWE
            ):
                if st.session_state.owe_structure == DEFAULT_OWE:
                    st.metric(
                        label='OWE "structure"',
                        value="—",
                        help="OWE according to structural criteria",
                    )
                else:
                    st.metric(
                        label='OWE "structure"',
                        value=round(st.session_state.owe_structure, 0),
                        help="OWE according to structural criteria",
                    )

                if st.session_state.owe_performances == DEFAULT_OWE:
                    st.metric(
                        label='OWE "performances"',
                        value="—",
                        help="OWE according to performances criteria",
                    )
                else:
                    st.metric(
                        label='OWE "performances"',
                        value=round(st.session_state.owe_performances, 0),
                        help="OWE according to performances criteria",
                    )
            else:
                st.metric(
                    label="OWE",
                    value=round(st.session_state.owe_performances, 0),
                    help="OWE",
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
                step=1.0,
                persist_state="session",
                key="wing_loading_widget",
            )
            thrust_loading = st.number_input(
                "Design thrust loading [-]",
                value=0.5,
                placeholder="Type a number...",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                persist_state="session",
                key="thrust_loading_widget",
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

        # If the choice of constraint diagram is correct, we move on to the next step.
        if st.session_state.checkpoint_1 and not broken_constraints:
            st.session_state.checkpoint_2 = True
            st.session_state.wing_loading = wing_loading
            st.session_state.thrust_loading = thrust_loading
        else:
            st.session_state.checkpoint_2 = False
            st.session_state.wing_loading = DEFAULT_WING_LOADING
            st.session_state.thrust_loading = DEFAULT_THRUST_LOADING

    if page == "Aerodynamics":
        fig, l_d_max = plot_library.aircraft_aerodynamic_polar_plot(
            wing_area=st.session_state.mtow / st.session_state.wing_loading,
            htp_area=st.session_state.aircraft_data.htp_area,
            vtp_area=st.session_state.aircraft_data.vtp_area,
        )

        fig.update_layout(
            xaxis_title="Drag coefficient Cd [-]",
            yaxis_title="Lift coefficient Cl [-]",
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )

        col_plot, col_fom = st.columns([2, 1])

        with col_plot:
            st.subheader("Aircraft aerodynamics")

            st.plotly_chart(fig, width="stretch")

        with col_fom:
            st.subheader("Figures of merit")
            st.session_state.l_d_max = l_d_max
            st.session_state.checkpoint_3 = True
            st.metric(
                label="L/D",
                value=round(st.session_state.l_d_max, 2),
                help="Maximum lift over drag ratio",
            )

    if page == "Masses":
        fig, owe = plot_library.aircraft_empty_mass_breakdown(
            wing_area=st.session_state.mtow / st.session_state.wing_loading,
            mtow=st.session_state.mtow,
            htp_area=st.session_state.aircraft_data.htp_area,
            vtp_area=st.session_state.aircraft_data.vtp_area,
            mto_thrust=st.session_state.mtow * 9.81 * st.session_state.thrust_loading,
            npax=st.session_state.npax,
        )
        fig.update_layout(
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )
        st.session_state.owe_structure = owe

        col_plot, col_fom = st.columns([2, 1])

        with col_plot:
            st.subheader("Aircraft masses")

            st.plotly_chart(fig, width="stretch")

        with col_fom:
            st.subheader("Figures of merit")

            st.metric(
                label='OWE "structure"',
                value=round(owe, 0),
                help="OWE according to structural criteria",
            )
            # TODO: create a constants.py file with this inside, the altitude, and others ...
            zfw_design = owe + st.session_state.npax * DESIGN_PAX_MASS  # 95 kg per pax
            st.metric(
                label="ZFW",
                value=round(zfw_design, 0),
                help="Zero Fuel Weight on design mission",
            )
            mzfw = owe + st.session_state.npax * 135.0  # 135 kg per pax, at max
            st.metric(
                label="MZFW", value=round(mzfw, 0), help="Maximum Zero Fuel Weight"
            )
            mlw = min(1.06 * mzfw, st.session_state.mtow)
            st.metric(label="MLW", value=round(mlw, 0), help="Maximum Landing Weight")
            st.session_state.checkpoint_4 = True

    if page == "Design mission":
        fig, owe, design_fuel = plot_library.aircraft_design_mission(
            mtow=st.session_state.mtow,
            mto_thrust=st.session_state.mtow * 9.81 * st.session_state.thrust_loading,
            npax=st.session_state.npax,
            design_range=design_range,
        )
        fig.update_layout(
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )
        st.session_state.owe_performances = owe

        col_plot, col_fom = st.columns([2, 1])

        with col_plot:
            st.subheader("Aircraft design mission")

            st.plotly_chart(fig, width="stretch")

        with col_fom:
            st.subheader("Figures of merit")

            st.metric(
                label="Design mission fuel",
                value=round(design_fuel, 0),
                help="Fuel for the design mission",
            )

            st.metric(
                label="Design payload",
                value=round(st.session_state.npax * DESIGN_PAX_MASS, 0),
                help="Payload mass on the design mission",
            )

            st.metric(
                label='OWE "performances"',
                value=round(owe, 0),
                help="OWE according to the performances criterion",
            )
            st.session_state.checkpoint_5 = True

    if page == "Mass performances loop":
        fig, owe, mtow = plot_library.mass_performances_loop(
            npax=st.session_state.npax,
            design_range=st.session_state.design_range,
        )
        fig.update_layout(
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )
        st.session_state.owe_performances = owe
        st.session_state.owe_structure = owe
        st.session_state.mtow = mtow

        col_plot, col_fom = st.columns([2, 1])

        with col_plot:
            st.subheader("Mass performances loop")

            st.plotly_chart(fig, width="stretch")

        with col_fom:
            st.subheader("Figures of merit")

            st.metric(
                label="MTOW",
                value=round(mtow, 0),
                help="Max TakeOff Weight",
            )

            st.metric(
                label="OWE",
                value=round(owe, 0),
                help="OWE",
            )

        st.session_state.checkpoint_6 = True

    if page == "Payload-range":
        fig = plot_library.payload_range(
            mtow=st.session_state.mtow,
            mto_thrust=st.session_state.mtow * 9.81 * st.session_state.thrust_loading,
            npax=st.session_state.npax,
            design_range=st.session_state.design_range,
            owe=st.session_state.owe_performances,
            wing_area=st.session_state.mtow / st.session_state.wing_loading,
            k_l_d_max=k_l_d_max,
            k_sfc=k_sfc,
            k_owe=k_mass,
        )
        fig.update_layout(
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        )

        col_plot, col_fom = st.columns([2, 1])

        with col_plot:
            st.subheader("Payload-range diagram")

            st.plotly_chart(fig, width="stretch")
