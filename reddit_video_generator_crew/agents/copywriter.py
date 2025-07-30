from crewai import Agent
from textwrap import dedent


class CopywriterAgent:
    def __init__(self, llm):
        self.agent = Agent(
            role="Copywriter",
            goal="Clean up the given Reddit Post for a Instagram Reels voiceover script.",
            backstory=dedent(
                """\
            You are a Reddit expert with a deep understanding of internet lingo. You have a keen eye for detail, ensuring your tasks are completed correctly.
            You know how to clean up Reddit posts to make them suitable for Instagram Reels voiceover scripts, maintaining the original context and details while
            removing unnecessary or confusing elements.
            """
            ),
            llm=llm,
        )

    def get_agent(self):
        return self.agent
