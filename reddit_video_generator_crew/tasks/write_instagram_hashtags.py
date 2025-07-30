from crewai import Task
from textwrap import dedent
from models.post_details import PostDetails


class WriteInstagramHashtags:
    def __init__(self, context, agent):
        self.task = Task(
            description=dedent(
                """\
                Using the provided voice-over transcript, which is derived from a cleaned-up Reddit post, generate a set of 
                optimized hashtags specifically tailored to enhance the Instagram Reel's visibility and engagement. Your goal 
                is to ensure the content reaches as many viewers as possible.
                """
            ),
            expected_output=dedent(
                """\
                A Reddit post with the cleaned up content, including the post title,  subreddit name(without the /r prefix) 
                and the original poster's username, and a comprehensive list of 10-15 optimized Instagram hashtags.
                """
            ),
            context=context,
            agent=agent,
            output_pydantic=PostDetails,
        )

    def get_task(self):
        return self.task
