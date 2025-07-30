from textwrap import dedent
from crewai import Agent


class RedditPostFinderAgent:
    def __init__(self, tools, llm) -> None:
        self.agent = Agent(
            role="Senior Social Media Specialist",
            goal="Search Reddit to find potential posts that can be used to create viral Instagram Reels",
            backstory=dedent(
                """\
            You are a Instagram expert who knows which content is likely to get the most viewings and interactions. Your primary task is to find interesting 
            and popular Reddit posts that can be turned into compelling voiceover Instagram Reels. Stories are your main target, but other types of posts are also 
            acceptable if they have viral potential. Your deep understanding of social media trends and Instagram's algorithm helps you identify posts with 
            high viral potential. Be selective and choose posts that are most likely to go viral."""
            ),
            llm=llm,
            tools=tools,
        )

    def get_agent(self) -> Agent:
        return self.agent
