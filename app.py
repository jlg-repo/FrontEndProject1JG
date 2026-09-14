import streamlit as st
import pandas as pd
import altair as alt  # import the altair library, similar to plotly
import plotly.express as px  # import plotly express, a high-level interface for plotly

# display it as a dataframe and complete 2 filtering options
# ( from dropdown, filtering by search, filtering in ascending order etc

st.set_page_config(page_title="2021 Pull Requests", page_icon="🔀", layout="wide")
# this sets the tab title, icon and layout for the streamlit app
st.title("GitHub Pull Requests — 2021")
# this sets the app title
st.caption("Pull request counts by programming language for 2021")
# this sets the app caption

# LOAD ---------------------------------------------------------------------------
df = pd.read_csv("prs.csv")  # load the whole dataset (name, year, quarter, count), large but streamlit loads it quickly
is_2021 = df["year"] == 2021  # boolean series that is True for rows from 2021
df = df[is_2021]  # df of df for only 2021 data, everything below works on this smaller dataframe

# expander
with st.expander("Preview of raw data "):
    st.dataframe(df.head())

    rows = df.shape[0]
    cols = df.shape[1]
    st.write(f"**df.shape** — {rows} rows, {cols} columns.")

    st.write(list(df.columns))

# this is an expander that shows the first few rows of the dataset, its shape and its column names

st.divider()  # dashed line

# FILTERS ------------------------------------------------------------------------
st.subheader("Filter the 2021 pull requests")  # page subheader

lowest_value = int(df["count"].min())  # get the lowest pull request count and store it in a variable (the slider and the reset button both need it)
highest_value = int(df["count"].max())  # get the highest pull request count and store it in a variable

# RESET (session state) ----------------------------------------------------------
# every filter widget below has a key=, which is its name inside st.session_state
# the button has to come before the widgets: streamlit won't let you change a widget's session_state value after that widget has already been drawn on this run
if st.button("Reset filters"):  # st.button is True only on the rerun right after it is clicked
    st.session_state.quarter_choice = "All quarters"  # put the quarter dropdown back to its first option
    st.session_state.search_text = ""  # empty the search box
    st.session_state.min_count = lowest_value  # slide the slider back to the lowest count
    st.rerun()  # rerun the script from the top so the table, metrics and charts redraw with the reset filters

col1, col2, col3 = st.columns(3)  # this is setting up 3 columns
with col1:  # with column 1 we put these in top down order
    quarters = df["quarter"].unique().tolist()  # gets the values from the quarter column and stores them as a list
    quarters = sorted(quarters)  # sorts that list smallest to largest
    quarter_options = ["All quarters"] + quarters  # appends "All quarters" to the front of the list as an option
    quarter_choice = st.selectbox("Filter by quarter", quarter_options, key="quarter_choice")  # this makes a dropdown with the list of quarters
with col2:  # with column 2 we put these in top down order
    search_text = st.text_input("Search by language name", placeholder="e.g. Py", key="search_text")  # text input box for searching, placeholder is the grey text shown before you type
with col3:  # with column 3 we put these in top down order
    min_count = st.slider(  # create a slider for the user to select a minimum pull request count
        "Minimum pull requests",  # the label shown above the slider
        min_value=lowest_value,  # set the minimum value of the slider to the lowest count
        max_value=highest_value,  # set the maximum value of the slider to the highest count
        key="min_count",  # no value= here: the slider starts at min_value on its own, and the reset button sets it through session_state instead
    )

filtered = df  # start with all of the 2021 rows, then narrow it down below

if quarter_choice != "All quarters":  # if the user picked a specific quarter, filter down to that quarter
    matches_quarter = filtered["quarter"] == quarter_choice  # boolean series that is True for rows in the chosen quarter
    filtered = filtered[matches_quarter]  # filter by that boolean series to get a new dataframe

if search_text:  # if the user typed something in the search box, filter by language name
    matches_search = filtered["name"].str.contains(search_text, case=False, na=False)  # returns a column of True/False where the name contains the search text, case insensitive, na=False treats not a number as False not unknown for missing values
    filtered = filtered[matches_search]  # filter by that boolean series to get a new dataframe

meets_minimum = filtered["count"] >= min_count  # boolean series that is True for rows with at least the chosen number of pull requests
filtered = filtered[meets_minimum]  # filter by that boolean series to get a new dataframe

# SORT ---------------------------------------------------------------------------
sort_col1, sort_col2 = st.columns(2)  # set up two columns for sorting options
with sort_col1:  # with col one..
    sort_by = st.selectbox("Sort by", ["count", "name", "quarter"])  # which column to sort on
with sort_col2:  # with col two..
    ascending = st.checkbox("Ascending order", value=False)  # unchecked means largest first

filtered = filtered.sort_values(by=sort_by, ascending=ascending)  # sort the filtered dataframe by the selected column and order

# METRICS ------------------------------------------------------------------------
st.divider()  # dashed line
m1, m2 = st.columns(2)  # set up two columns for metrics

m1.metric("Rows shown", len(filtered))  # m1 shows how many rows survived the filters

if len(filtered) > 0:  # if there is anything in filtered
    total_prs = int(filtered["count"].sum())  # sum the count column and convert to int
else:  # if empty
    total_prs = 0  # set total_prs to 0
m2.metric("Total pull requests (shown)", total_prs)  # m2 shows the combined pull request count

# TABLE — always the filtered data, never the original df -------------------------
st.dataframe(filtered, hide_index=True, use_container_width=True)  # show the filtered dataframe, hide the index, fill the container width

# CHARTS — also always built from filtered, so every filter above changes them ----
st.subheader("Charts")  # charts subheader

if len(filtered) == 0:  # if filtered is empty, print an info box instead of drawing empty charts
    st.info("No languages match the current filters — widen them to see charts.")
else:  # if not empty, show the charts (both charts live inside this else so neither runs on an empty dataframe)
    chart_col1, chart_col2 = st.columns(2)  # two columns, one chart in each

    with chart_col1:  # with chart column 1, we put these in top down order
        st.caption("Altair — top 10 languages by total pull requests (comparing categories → bar chart)")  # a caption for the chart
        language_totals = filtered.groupby("name")["count"].sum().reset_index()  # AGGREGATION: add up every quarter's count for each language, reset_index turns name back into a normal column
        language_totals = language_totals.sort_values(by="count", ascending=False)  # sort so the biggest totals come first
        top_languages = language_totals.head(10)  # keep only the top 10, 100 languages would not fit on one chart
        altair_chart = (  # build an altair chart, store it in a variable called altair_chart
            alt.Chart(top_languages)
            .mark_bar()  # create a bar chart
            .encode(  # encode the x and y axes, color, and tooltip
                x="count:Q",
                y=alt.Y("name:N", sort="-x"),
                color="name:N",
                tooltip=["name", "count"],
            )
        )
        st.altair_chart(altair_chart, use_container_width=True)  # display the altair chart, use the container width to make it responsive

    with chart_col2:  # with chart column 2, we put these in top down order
        st.caption("Plotly — share of pull requests by language, Quarter 1 only (parts of a whole → pie chart)")  # a caption for the chart
        is_q1 = filtered["quarter"] == 1  # boolean series that is True for rows from quarter 1
        q1_rows = filtered[is_q1]  # filter by that boolean series, leaves one row per language for quarter 1
        if len(q1_rows) == 0:  # if the quarter dropdown is on another quarter, or nothing in quarter 1 matches, there is nothing to draw
            st.info("No Quarter 1 rows match the current filters — this pie only shows Quarter 1, so set the quarter filter to 'All quarters' or 1.")
        else:  # if there are quarter 1 rows, draw the pie
            q1_rows = q1_rows.sort_values(by="count", ascending=False)  # sort so the biggest languages come first
            q1_top = q1_rows.head(10)  # keep only the top 10, about 90 slices would be unreadable
            pie = px.pie(  # make a pie chart using plotly express
                q1_top,  # grab the top 10 quarter 1 rows
                names="name",  # one slice per language
                values="count",  # each slice is sized by that language's quarter 1 pull requests
                title="Share of Quarter 1 pull requests (top 10 languages)",
                labels={"name": "Language", "count": "Pull requests"},
            )
            st.plotly_chart(pie, use_container_width=True)  # display the plotly chart, use the container width to make it responsive

st.caption("Programming Language Info Site")  # caption at the bottom of the page
