from crewai import Task
from textwrap import dedent


class FindRedditPostTask:
    def __init__(self, agent):
        self.task = Task(
            description=dedent(
                """\
            Search the {post_sub} subreddit to find today's 5 popular and engaging posts which
            have the potential to become viral Instagram Reels voiceover videos. Focus on stories or other compelling content
            that can be read as a voiceover. Then choose one of those 5 posts, ensuring the post selection is based on its potential
            to get the highest views and interactions according to Instagram's algorithm."""
            ),
            expected_output=dedent(
                """\
            1 carefully chosen Reddit post, that is less then 200 words, from the subreddit's 5 most popular posts of the day that can be used to create viral Instagram Reels voiceover videos. 
            The output should contain the post title, full post content, the original poster's username, and the name of the subreddit."""
            ),
            agent=agent,
        )

    def get_task(self):
        return self.task
