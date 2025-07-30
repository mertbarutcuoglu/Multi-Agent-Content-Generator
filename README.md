# Multi-Agent Content Generator: Reddit to Narrated Instagram Reels

**Multi-Agent Content Generator** is an experimental multi-agent system that generates "brain rot" Instagram Reels by combining trending Reddit stories with Minecraft video backgrounds. 

This project leverages [CrewAI](https://github.com/joaomdmoura/crewAI) to orchestrate a crew of AI agents that search Reddit, select engaging posts, write video transcripts, and generate Instagram hashtags—automating the creation of viral short-form content.

> **Note:** This is a weekend project to test CrewAI for building multi-agent systems. The code is experimental and intended for learning and prototyping.

## Features

- **Multi-Agent Workflow:** Uses CrewAI to coordinate specialized agents:
  - **RedditPostFinderAgent:** Searches a given subreddit for engaging posts.
  - **CopywriterAgent:** Writes a transcript for the video based on the selected Reddit post.
  - **InstagramSpecialistAgent:** Generates relevant hashtags for Instagram.
- **Automated Video Generation:** Combines the Reddit story transcript with a Minecraft video background and overlays the generated title image.
- **Customizable Input:** Accepts any subreddit as input, allowing for flexible content generation.
- **Azure OpenAI Integration:** Utilizes GPT-4o and GPT-4o-mini models for content generation.
- **Reddit API Integration:** Fetches posts using PRAW and custom search tools.
- **Image and Video Processing:** Uses MoviePy, OpenCV, and other libraries for media generation.

## How It Works

1. **Input:** Specify a subreddit (via CLI or prompt).
2. **Agent Orchestration:** CrewAI coordinates the following tasks:
    - **Find a Reddit Post:** The RedditPostFinderAgent searches the subreddit and selects a suitable post.
    - **Write Voiceover Script:** The CopywriterAgent generates a transcript for the video.
    - **Generate Hashtags:** The InstagramSpecialistAgent creates relevant hashtags for the post.
3. **Image Generation:** A title image is generated for the video using the post's title, author, and subreddit.
4. **Video Generation:** The transcript is combined with a Minecraft video background and the generated title image to produce a final Instagram-ready video.

## Setup

### Requirements

- **Python 3.10+**
- [ffmpeg](https://ffmpeg.org/) (ensure it's installed and accessible at `/opt/homebrew/bin/ffmpeg` or update the `IMAGEIO_FFMPEG_EXE` variable)
- Azure OpenAI account and API keys
- Reddit API credentials

### Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for Python package management. Install dependencies with:

```bash
uv pip install -r pyproject.toml
```
This will install all dependencies specified in `pyproject.toml`.

### Environment Variables

Create a `.env` file in the project root and set the following variables:

```env
# DEFAULT AZURE OPENAI VARIABLES
AZURE_API_BASE=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=

# GPT-4o / MINI VARIABLES
AZURE_OPENAI_GPT4O_ENDPOINT=
AZURE_OPENAI_GPT4O_API_KEY=

# WHISPER VARIABLES
AZURE_OPENAI_WHISPER_ENDPOINT=
AZURE_OPENAI_WHISPER_API_KEY=

# TTS VARIABLES
AZURE_OPENAI_TTS_ENDPOINT=
AZURE_OPENAI_TTS_API_KEY=

# REDDIT VARIABLES
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=

# MISC
IMAGEIO_FFMPEG_EXE="/opt/homebrew/bin/ffmpeg"
```

---

## Usage

Run the main script and specify a subreddit:

```bash
uv run main.py --post_sub Paranormal
```

If `--post_sub` is not provided, you will be prompted to enter a subreddit.

The script will:
- Search the subreddit for a suitable post
- Generate a transcript and hashtags
- Create a title image
- Produce a video with a Minecraft background and the Reddit story

The output video will be saved in the project directory.

---

## Example

```bash
uv run main.py --post_sub Paranormal
```

This will generate an Instagram Reel using a post from r/Paranormal, with a Minecraft video background and all content (transcript, hashtags, title image) created by the agents.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Credits

- Minecraft video asset and Reddit content are used for educational and prototyping purposes only.
