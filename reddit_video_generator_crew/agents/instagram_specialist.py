from crewai import Agent
from models.post_details import PostDetails
from textwrap import dedent


class InstagramSpecialistAgent:
    def __init__(self, llm):
        self.agent = Agent(
            role="Senior Instagram Content Specialist",
            goal="Generate optimized Instagram hashtags for increasing views and engagement on a Reel using a given voice-over transcript.",
            backstory=dedent("""\
                As an Instagram expert, you specialize in identifying the most effective hashtags that help Reels go viral. 
                You stay updated with the latest trends and use your knowledge to maximize the reach and interaction of the content you work on.
            """),
            output_pydantic=PostDetails,
            llm=llm,
        )

    def get_agent(self):
        return self.agent
