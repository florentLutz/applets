import streamlit as st
import tabs as tabs_library

if __name__ == "__main__":
    st.set_page_config(
        page_title="Mise en pratique - réseaux électriques embarqués",
        layout="wide",
    )

    tab_be_2, tab_be_4 = st.tabs(["BE2 - Machines électriques", "BE4 - Réseau HVDC"])
    with tab_be_2:
        tabs_library.produce_tab_be2()
