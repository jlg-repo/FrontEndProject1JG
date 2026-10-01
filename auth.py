# auth.py
# Shared authentication helper used by app.py and every page in pages/.
# Keeping this logic in one place means every gated page checks access the same way.

import streamlit as st


def check_auth():
    # Read the authenticated flag out of session state.
    # get() defaults to False, so a first-time visitor counts as logged out.
    is_authenticated = st.session_state.get("authenticated", False)

    # If the visitor is not authenticated, stop rendering the rest of the page.
    if is_authenticated == False:
        # Show a message explaining why the page is empty.
        st.warning("You must log in on the Login page before viewing this page.")
        # st.stop() halts execution here, so no protected content below this line ever renders.
        st.stop()


def show_logout_button():
    # Every gated page gets the same logout control in the sidebar.
    logout_clicked = st.sidebar.button("Log out")

    # If the visitor clicked the button, clear the authenticated flag.
    if logout_clicked == True:
        st.session_state["authenticated"] = False
        # Clear the stored username too, so the sidebar greeting disappears on the next run.
        st.session_state["username"] = None
        # Rerun the app immediately so the login page shows right away instead of after the next click.
        st.rerun()
