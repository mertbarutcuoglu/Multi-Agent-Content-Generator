from crewai import Task
from textwrap import dedent


class WriteVoiceoverScriptTask:
    def __init__(self, context, agent):
        self.task = Task(
            description=dedent(
                """\
            Using the given Reddit post, clean up the content to create a Instagram Reels voiceover script. Content will be the transcript.
            Replace Reddit-specific acronyms (e.g., 'TIFU') with their full words. Remove any added details, like edits, that were not part of the initial post to
            make the script concise, without adding or removing any meaningful information. Do not remove any parts of the initial original post."""
            ),
            expected_output=dedent(
                """\
            A cleaned-up Reddit post with the edited content, including the post title, subreddit name (without the /r prefix) and 
            the original poster's username. The output should be ready for a Instagram Reels voiceover script."""
            ),
            context=context,
            agent=agent,
        )

    def get_task(self):
        return self.task
