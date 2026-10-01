import streamlit as st


# Configure the page title, icon, and wide layout for this app.
st.set_page_config(page_title="Home", page_icon="", layout="wide")

# need to set up multiple pages layout: sidebar, tabs, etc. Some way to jump to the content on the other pages

st.write("# Home Page ")

st.write("  Log in to access the site. ")

# This page holds the login form. The two pages under pages/ are gated and check auth.py on load.


# Initialize the authenticated flag the first time the app runs in a session.
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Initialize the username the first time the app runs in a session.
if "username" not in st.session_state:
    st.session_state["username"] = None

st.title(" Programming Languages Site Login")
st.caption("Please log in to continue")

# If the visitor is already authenticated, skip the form and show a welcome message.
if st.session_state["authenticated"] == True:
    st.success(f"Logged in as {st.session_state['username']}.")
    st.write("Use the sidebar to choose from the pages.")
else:
    # st.form groups the two inputs and the submit button so the app only reruns once, on submit.
    login_form = st.form("login_form")

    # Add the username field inside the form.
    entered_username = login_form.text_input("Username")

    # Add the password field inside the form. type="password" masks the characters as they are typed.
    entered_password = login_form.text_input("Password", type="password")

    # Add the submit button inside the form.
    submitted = login_form.form_submit_button("Log in")

    # Only check credentials after the form has been submitted.
    if submitted == True:
        # Read the correct username out of secrets.toml.
        correct_username = st.secrets["credentials"]["username"]
        # Read the correct password out of secrets.toml.
        correct_password = st.secrets["credentials"]["password"]

        # Compare the entered credentials against the ones in secrets.toml.
        username_matches = entered_username == correct_username
        password_matches = entered_password == correct_password

        # Both fields must match before access is granted.
        if username_matches and password_matches:
            st.session_state["authenticated"] = True
            st.session_state["username"] = entered_username
            # Rerun so the welcome message replaces the form immediately.
            st.rerun()
        else:
            st.error("Incorrect username or password.")


st.sidebar.success("Select a page.")
