from crewai.tools import tool
from langchain_community.utilities.reddit_search import RedditSearchAPIWrapper
import os


@tool("Reddit Search Tool")
def reddit_search_tool(
    query: str,
    subreddit: str = None,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 5,
) -> str:
    """
    Search Reddit for posts matching the query.
    Args:
        query (str): The search query.
        subreddit (str, optional): Subreddit to search in.
        sort (str, optional): Sort order ('relevance', 'hot', 'top', 'new', 'comments').
        time_filter (str, optional): Time filter ('all', 'day', 'hour', 'month', 'week', 'year').
        limit (int, optional): Number of results to return.
    Returns:
        str: Search results as a string.
    """
    api_wrapper = RedditSearchAPIWrapper(
        reddit_client_id=os.environ["REDDIT_CLIENT_ID"],
        reddit_client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        reddit_user_agent=os.environ["REDDIT_USER_AGENT"],
    )
    results = api_wrapper.run(
        query=query,
        subreddit=subreddit,
        sort=sort,
        time_filter=time_filter,
        limit=limit,
    )
    return str(results)
