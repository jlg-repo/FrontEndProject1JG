import streamlit as st
import pandas as pd

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
col1, col2 = st.columns(2)  # this is setting up 2 columns
with col1:  # with column 1 we put these in top down order
    quarters = df["quarter"].unique().tolist()  # gets the values from the quarter column and stores them as a list
    quarters = sorted(quarters)  # sorts that list smallest to largest
    quarter_options = ["All quarters"] + quarters  # appends "All quarters" to the front of the list as an option
    quarter_choice = st.selectbox("Filter by quarter", quarter_options)  # this makes a dropdown with the list of quarters
with col2:  # with column 2 we put these in top down order
    search_text = st.text_input("Search by language name", placeholder="e.g. Py")  # text input box for searching, placeholder is the grey text shown before you type

filtered = df  # start with all of the 2021 rows, then narrow it down below

if quarter_choice != "All quarters":  # if the user picked a specific quarter, filter down to that quarter
    matches_quarter = filtered["quarter"] == quarter_choice  # boolean series that is True for rows in the chosen quarter
    filtered = filtered[matches_quarter]  # filter by that boolean series to get a new dataframe

if search_text:  # if the user typed something in the search box, filter by language name
    matches_search = filtered["name"].str.contains(search_text, case=False, na=False)  # returns a column of True/False where the name contains the search text, case insensitive, na=False treats not a number as False not unknown for missing values
    filtered = filtered[matches_search]  # filter by that boolean series to get a new dataframe

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

st.caption("Programming Language Info Site")  # caption at the bottom of the page
