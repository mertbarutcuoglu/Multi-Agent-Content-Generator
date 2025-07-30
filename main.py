import os
from crewai import Crew
from video_generator import video_generator
from image_generator.image_generator import ImageGenerator
from langchain_openai import AzureChatOpenAI
from reddit_video_generator_crew.agents.reddit_tools import reddit_search_tool

from reddit_video_generator_crew.agents.copywriter import CopywriterAgent
from reddit_video_generator_crew.agents.reddit_post_finder import RedditPostFinderAgent
from reddit_video_generator_crew.agents.instagram_specialist import (
    InstagramSpecialistAgent,
)

from reddit_video_generator_crew.tasks.find_reddit_post import FindRedditPostTask
from reddit_video_generator_crew.tasks.write_voiceover_script import (
    WriteVoiceoverScriptTask,
)
from reddit_video_generator_crew.tasks.write_instagram_hashtags import (
    WriteInstagramHashtags,
)

from dotenv import load_dotenv
import argparse

load_dotenv(override=True)

# Initialize models
gpt4o_mini = AzureChatOpenAI(
    model="azure/gpt-4o-mini",
    api_version="2023-03-15-preview",
    api_key=os.environ["AZURE_OPENAI_GPT4O_API_KEY"],
)

gpt4o = AzureChatOpenAI(
    model="azure/gpt-4o",
    api_version="2024-05-03-preview",
    api_key=os.environ["AZURE_OPENAI_GPT4O_API_KEY"],
)


# Initilize agents
reddit_post_finder = RedditPostFinderAgent([reddit_search_tool], gpt4o).get_agent()

copywriter = CopywriterAgent(gpt4o_mini).get_agent()

instagram_specialist = InstagramSpecialistAgent(gpt4o_mini).get_agent()


# Initialize tasks
find_reddit_post_task = FindRedditPostTask(reddit_post_finder).get_task()


write_voiceover_transcript = WriteVoiceoverScriptTask(
    context=[find_reddit_post_task], agent=copywriter
).get_task()


write_instagram_hashtags = WriteInstagramHashtags(
    [write_voiceover_transcript], instagram_specialist
).get_task()


# Initialize the crew
reddit_video_crew = Crew(
    agents=[reddit_post_finder, copywriter, instagram_specialist],
    tasks=[
        find_reddit_post_task,
        write_voiceover_transcript,
        write_instagram_hashtags,
    ],
    verbose=True,
)

parser = argparse.ArgumentParser(description="Generate Reddit video from a subreddit")
parser.add_argument("--post_sub", type=str, help="Subreddit to use for the post")
args = parser.parse_args()

post_sub = args.post_sub
if not post_sub:
    post_sub = input("Enter subreddit: ")

print("Kicking off crew...")
video_material = reddit_video_crew.kickoff(inputs={"post_sub": post_sub})

print("Idea is ready, generating title image...")
image_generator = ImageGenerator()
fname = image_generator.generate_reddit_title_image(
    video_material.pydantic.post_title,
    video_material.pydantic.user,
    video_material.pydantic.subreddit,
)
image_generator.quit_image_generator()

print("Image is generated, generating video...")
video_generator.generate_video(
    fname, video_material.pydantic.post_content, video_material.pydantic.post_title
)
