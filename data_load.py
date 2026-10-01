# data_load.py
# Shared data loading helpers used by the pages in pages/.
# Every loader is wrapped in st.cache_data, so a file is read from disk once and then
# reused. Without the cache, every widget click would re-read the whole CSV from scratch.

import pandas as pd
import requests
import streamlit as st


@st.cache_data  # streamlit stores the returned dataframe and hands back the same one next run
def load_pull_requests():
    # Load the whole pull request dataset (name, year, quarter, count).
    df = pd.read_csv("prs.csv")
    return df


@st.cache_data  # same idea: the repo count file only gets read once
def load_repo_counts():
    # Load the repo count dataset (language, num_repos).
    df = pd.read_csv("repos.csv")
    return df


@st.cache_data(ttl=3600)  # ttl=3600 means the cached answer expires after an hour, so live data stays fresh
def fetch_github_language(language):
    # Ask the GitHub search API how many public repos use this language, and which are the most starred.
    # This is a plain GET request: no API key and no login, just a URL with a query string.
    url = "https://api.github.com/search/repositories"

    # q=language:"Python" is GitHub's search syntax for "repos written in Python".
    # The quotes keep names with spaces together: without them, language:Jupyter Notebook would
    # search for Jupyter repos that mention the word Notebook.
    # sort/order ask for the most starred first, per_page keeps the response small.
    params = {
        "q": f'language:"{language}"',
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
    }

    # try/except so a dropped connection shows a message instead of crashing the page.
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        return None

    # GitHub limits unauthenticated search to a few requests per minute. Any non-200
    # (usually 403 for rate limiting) means we have no usable data this run.
    if response.status_code != 200:
        return None

    # .json() turns the response body into a normal python dictionary.
    data = response.json()
    return data
