from pydantic import BaseModel


class PostDetails(BaseModel):
    post_title: str
    post_content: str
    subreddit: str
    user: str
    hashtags: str
