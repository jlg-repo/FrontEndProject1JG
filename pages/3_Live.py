# The Kaggle data on the Trends page stops at 2021. This page exists to close that gap:
# it asks the GitHub API what is true right now and puts the two numbers side by side.

import streamlit as st
import pandas as pd
import altair as alt  # import the altair library, similar to plotly

from auth import check_auth, show_logout_button
from data_load import load_pull_requests, load_repo_counts, fetch_github_language

st.set_page_config(page_title="Live Check", page_icon="📡", layout="wide")

# Block access immediately if the visitor is not authenticated.
check_auth()


# Show the logout button in the sidebar.
show_logout_button()


st.title("Live Check — GitHub Today")
st.caption(f"Logged in as {st.session_state['username']}")

st.caption("Live public repo counts from the GitHub API, next to the 2021 pull request totals")

# LOAD ---------------------------------------------------------------------------
repos = load_repo_counts()  # language, num_repos — cached, used here just to build the dropdown options
prs = load_pull_requests()  # the historical pull request data, cached, used for the 2021 comparison column

# Build the list of languages to offer. Sorting by num_repos first means the dropdown starts
# with the languages a beginner has actually heard of, instead of alphabetical obscurities.
popular = repos.sort_values(by="num_repos", ascending=False)  # biggest first
language_options = popular["language"].head(30).tolist()  # keep the top 30, 450 languages is too many for a dropdown
language_options = sorted(language_options)  # now sort those 30 alphabetically so they are easy to find

# READ THE VALUE HANDED OVER BY THE TRENDS PAGE ----------------------------------
# .get() is used instead of [] because a visitor can land here without stopping on Trends first.
carried_language = st.session_state.get("focus_language", None)

if carried_language in language_options:  # only trust the carried value if it is actually one of our options
    default_languages = [carried_language]  # start the multiselect on the language the user was just looking at
    st.success(f"Carried over from the Trends page: **{carried_language}**")
else:
    default_languages = ["Python"]  # a sensible starting point for a site aimed at beginners
    st.info("Pick a language on the Trends page and it will be pre-loaded here.")

st.divider()  # dashed line

# WIDGETS ------------------------------------------------------------------------
st.subheader("Compare languages on GitHub today")

widget_col1, widget_col2 = st.columns(2)  # two columns for the two controls

with widget_col1:  # with column 1 we put these in top down order
    selected_languages = st.multiselect(  # a multiselect so several languages can be compared at once
        "Languages to compare",  # the label shown above the box
        language_options,  # the top 30 languages built above
        default=default_languages,  # whatever the Trends page handed over
    )

with widget_col2:  # with column 2 we put these in top down order
    sort_choice = st.radio(  # a radio so only one sort order can be active
        "Sort the results by",
        ["Public repos today", "Pull requests in 2021"],
    )

# The GitHub search API allows a limited number of unauthenticated requests per minute, and
# this page makes one request per selected language, so warn before that becomes a problem.
if len(selected_languages) > 5:
    st.warning("That is a lot of languages at once. GitHub limits anonymous requests, so some may come back empty.")

# EMPTY RESULT CASE — nothing picked means there is nothing to ask GitHub about -----
if len(selected_languages) == 0:
    st.info("No languages selected. Pick at least one above to pull live data from GitHub.")
    st.stop()  # halts the page here, so none of the charts below try to run on an empty selection

# CALL THE API -------------------------------------------------------------------
live_rows = []  # collect one row per language that came back successfully
failed_languages = []  # collect the ones that did not, so we can report them honestly

for language in selected_languages:  # one request per language, each cached for an hour
    github_data = fetch_github_language(language)

    if github_data is None:  # None means the request failed or we got rate limited
        failed_languages.append(language)
    else:
        # total_count is GitHub's count of public repos matching language:<name>
        live_rows.append({"language": language, "repos_today": github_data["total_count"]})

if len(failed_languages) > 0:  # tell the user exactly which languages are missing and why
    st.warning(f"GitHub did not return data for: {', '.join(failed_languages)}. This is usually the anonymous rate limit — wait a minute and rerun.")

# EMPTY RESULT CASE — every request failed, so there is still nothing to show ------
if len(live_rows) == 0:
    st.error("No live data came back from GitHub. Wait a minute for the rate limit to reset, then rerun.")
    st.stop()  # nothing below can run without live data

live = pd.DataFrame(live_rows)  # turn the list of dictionaries into a dataframe

# JOIN THE 2021 DATA ONTO THE LIVE DATA ------------------------------------------
is_2021 = prs["year"] == 2021  # boolean series that is True for rows from 2021
prs_2021 = prs[is_2021]  # cut the historical data down to 2021 only

# AGGREGATION: add up all four quarters so each language has one 2021 total
totals_2021 = prs_2021.groupby("name")["count"].sum().reset_index()  # reset_index turns name back into a normal column
totals_2021 = totals_2021.rename(columns={"name": "language", "count": "prs_2021"})  # rename so the column names match for the merge

# how="left" keeps every language we have live data for, even if 2021 has no row for it
compare = live.merge(totals_2021, on="language", how="left")
compare["prs_2021"] = compare["prs_2021"].fillna(0).astype(int)  # a missing 2021 value means no recorded activity, so 0

# DERIVED METRIC: how far each language moved in the ranking between 2021 and today.
#  Ranks do not care about the size of either sample, only
# about the order within it, so a rank comparison is the honest version of this metric.

# A language with no 2021 rows cannot be placed in the 2021 ranking at all, so those languages are
# left out of the ranking and get a blank cell .
ranked = compare[compare["prs_2021"] > 0].copy()  # .copy() so we are not editing a slice of compare

# rank() turns the counts into positions. ascending=False puts the biggest count at rank 1, and
# method="min" means a tie takes the better of the two positions instead of an average like 2.5.
ranked["rank_2021"] = ranked["prs_2021"].rank(ascending=False, method="min")
ranked["rank_today"] = ranked["repos_today"].rank(ascending=False, method="min")

ranked["rank_change"] = ranked["rank_2021"] - ranked["rank_today"]

# Put the three rank columns back onto every row. how="left" leaves the unranked languages blank.
rank_columns = ["language", "rank_2021", "rank_today", "rank_change"]
compare = compare.merge(ranked[rank_columns], on="language", how="left")

# Turn the number of places moved into something readable at a glance.
movement_labels = []  # build the movement column one row at a time
for change in compare["rank_change"]:
    if pd.isna(change):  # no 2021 data, so there is nothing to compare against
        movement_labels.append("")
    elif change > 0:
        movement_labels.append(f"▲ {int(change)}")  # climbed the ranking since 2021
    elif change < 0:
        movement_labels.append(f"▼ {int(abs(change))}")  # slipped down the ranking since 2021
    else:
        movement_labels.append("no change")  # same position in both rankings
compare["movement"] = movement_labels

# SORT ---------------------------------------------------------------------------
if sort_choice == "Public repos today":  # pick the column the radio asked for
    sort_column = "repos_today"
else:
    sort_column = "prs_2021"

compare = compare.sort_values(by=sort_column, ascending=False)  # biggest first, by whichever column was chosen

# METRICS ------------------------------------------------------------------------
st.divider()  # dashed line
m1, m2, m3 = st.columns(3)  # set up three columns for metrics

m1.metric("Languages compared", len(compare))  # how many came back from the API

total_repos = int(compare["repos_today"].sum())  # DERIVED: add up the live repo counts across the selection
m2.metric("Public repos (selected)", f"{total_repos:,}")  # the :, puts thousands separators in

biggest_row = compare.sort_values(by="repos_today", ascending=False).iloc[0]  # the single largest language in the selection
m3.metric("Most used right now", biggest_row["language"])  # show its name

# TABLE --------------------------------------------------------------------------
st.dataframe(  # show the joined comparison, hide the index, fill the container width
    compare,
    hide_index=True,
    use_container_width=True,
    column_config={  # friendlier column headers than the raw dataframe names
        "language": "Language",
        "repos_today": st.column_config.NumberColumn("Public repos today", format="%d"),
        "prs_2021": st.column_config.NumberColumn("Pull requests in 2021", format="%d"),
        "rank_2021": st.column_config.NumberColumn("Rank in 2021", format="%d"),
        "rank_today": st.column_config.NumberColumn("Rank today", format="%d"),
        "movement": "Movement",
        "rank_change": None,  # None hides the raw number, the movement column already says it with an arrow
    },
)

# Two things a reader could otherwise get wrong about the ranking above.
st.caption(
    "Ranks are only within the languages selected above, so adding or removing a language "
    "changes them. Both rankings count public GitHub activity, which undercounts languages "
    "used mostly on private company code."
)

# CHART --------------------------------------------------------------------------
st.subheader("Charts")  # charts subheader

st.caption(f"Altair — {sort_choice.lower()} by language (comparing categories → bar chart)")  # the caption follows the radio too

live_chart = (  # build an altair chart, store it in a variable called live_chart
    alt.Chart(compare)
    .mark_bar()  # create a bar chart
    .encode(  # encode the x and y axes, color, and tooltip
        # both axes read sort_column, so switching the radio redraws the chart instead of
        # leaving it stuck on one measure, old version hard coded repos_today here, so sort wasn't working
        x=alt.X(f"{sort_column}:Q", title=sort_choice),
        y=alt.Y("language:N", sort=alt.EncodingSortField(field=sort_column, order="descending"), title="Language"),
        color="language:N",
        tooltip=["language", "repos_today", "prs_2021"],
    )
)
st.altair_chart(live_chart, use_container_width=True)  # display the altair chart, use the container width to make it responsive

# top repos
st.divider()  # dashed line
st.subheader("Most starred repositories")

# Only offer languages we actually got data for, so this dropdown can never pick a failed one.
available_languages = compare["language"].tolist()

detail_language = st.selectbox("Show the most starred repos for", available_languages)  # a dropdown to pick one language

detail_data = fetch_github_language(detail_language)  # already cached from the loop above, so this costs nothing

if detail_data is None:  # the cache could have expired between the loop and here
    st.warning("Could not load repositories for this language right now.")
else:
    repo_items = detail_data["items"]  # items is the list of repositories GitHub sent back

    # empty result: a valid response can still contain zero repositories
    if len(repo_items) == 0:
        st.info(f"GitHub returned no repositories for {detail_language}.")
    else:
        repo_rows = []  # build one row per repository
        for item in repo_items:
            repo_rows.append({
                "repo": item["full_name"],  # owner/name
                "stars": item["stargazers_count"],  # how many people starred it
                "description": item["description"],  # one line, can be None
            })

        repo_table = pd.DataFrame(repo_rows)  # turn the list of dictionaries into a dataframe

        average_stars = int(repo_table["stars"].mean())  # the mean star count of the top 10
        st.metric(f"Average stars across the top {len(repo_table)} {detail_language} repos", f"{average_stars:,}")

        st.dataframe(  # show the repo table, hide the index, fill the container width
            repo_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "repo": "Repository",
                "stars": st.column_config.NumberColumn("Stars", format="%d"),
                "description": "Description",
            },
        )

st.caption("Programming Language Info Site")  # caption at the bottom of the page