# This page holds the problem statement for the site and explains why the pages are split the way they are.
# It is deliberately not login gated: a visitor should be able to read what the site is for before logging in.
# The two data pages after it are gated
import streamlit as st

st.set_page_config(page_title="About", page_icon="📋", layout="wide")

st.title("About This Site")
st.caption("What this site is for, and how it is put together")

# PROBLEM STATEMENT --------------------------------------------------------------
st.header("Problem statement")

# st.tabs splits the three parts of the problem statement so each one can be read on its
# own instead of as one long wall of text.
who_tab, what_tab, why_tab = st.tabs(["Who it is for", "The problem", "Why it matters"])

with who_tab:  # with the first tab we put these in top down order
    st.subheader("Who is this for")
    st.write(
        "New programmers choosing a first or second language. That means students in an intro "
        "course, people teaching themselves, and career switchers who have been told to 'just "
        "learn to code' without being told what to learn."
    )

with what_tab:  # with the second tab we put these in top down order
    st.subheader("What problem are they facing")
    st.write(
        "They cannot tell which languages are actually widely used. The advice they get is "
        "anecdotal, and the blog posts they find are listicles written for search traffic that "
        "contradict each other. The real evidence does exist in public GitHub activity, but it "
        "comes as hundreds of thousands of rows, which is not something a beginner can read."
    )

with why_tab:  # with the third tab we put these in top down order
    st.subheader("Why does it matter")
    st.write(
        "Language choice decides what a beginner has access to. A widely used language has the "
        "mature libraries, the maintained tutorials, the answered questions, and the job "
        "listings. Picking a language with a small ecosystem means months spent fighting the "
        "toolchain instead of learning to program, and that is usually when people quit."
    )

st.divider()  # dashed line

# PAGE STRUCTURE ----------------------------------------------------------------
st.header("Why the site is split into these pages")

st.write(
    "Each page answers one question a beginner actually asks, in the order they ask it. "
    "The split is by question, not by data source."
)

# st.columns puts the three page descriptions side by side so the structure is visible at a glance.
about_col, trends_col, live_col = st.columns(3)

with about_col:  # with column 1 we put these in top down order
    st.subheader("About")
    st.write("**Question:** what is this, and can I trust the numbers?")
    st.write(
        "The problem statement and the data sources live here. A beginner who does not know "
        "what question the site answers has no reason to believe any chart on it."
    )

with trends_col:  # with column 2 we put these in top down order
    st.subheader("Trends")
    st.write("**Question:** has this language been growing or fading?")
    st.write(
        "Uses the Kaggle GitHub dataset, which covers 2011 to 2021. Direction over years is "
        "something only a historical dataset can show, so this page owns the history."
    )

with live_col:  # with column 3 we put these in top down order
    st.subheader("Live Check")
    st.write("**Question:** where does it stand right now?")
    st.write(
        "Calls the GitHub API live. The Kaggle data stops at 2021, which is the single biggest "
        "weakness in it, so this page exists specifically to close that gap."
    )

st.divider()  # dashed line

# DATA SOURCES ------------------------------------------------------------------
st.header("Where the data comes from")

# An expander keeps the source notes available without pushing the page structure off screen.
with st.expander("Data sources and known limitations"):
    st.write(
        "**Historical data:** the GitHub Programming Languages dataset on Kaggle, which counts "
        "pull requests and issues per language per quarter from 2011 to 2021."
    )
    st.write("https://www.kaggle.com/datasets/isaacwen/github-programming-languages-data")

    st.write(
        "**Live data:** the GitHub REST search API, which reports how many public repos "
        "currently use a language and which of those have the most stars. No API key is used."
    )
    st.write("https://api.github.com/search/repositories")

    st.write(
        "**Limitation:** the Kaggle data ends in 2021, and five years is a long time in "
        "computer science. That is why the Live Check page exists. A second limitation is that "
        "GitHub activity measures open source work, so languages used mostly inside companies "
        "are undercounted."
    )

st.info("Log in on the Login page to open the Trends and Live Check pages.")