import os
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional, Union

from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip
from openai import AzureOpenAI
import librosa

from . import segment_parser
from . import transcriber
from .text_drawer import (
    get_text_size_ex,
    create_text_ex,
    blur_text_clip,
    Word,
)

# Output directory for generated files
OUT_DIR: str = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT_DIR, exist_ok=True)

# Caches for performance
shadow_cache: Dict[int, Any] = {}
lines_cache: Dict[int, Any] = {}

# Azure OpenAI client for TTS
client = AzureOpenAI(
    azure_deployment="tts",
    api_version="2024-05-01-preview",
    api_key=os.environ["AZURE_OPENAI_TTS_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_TTS_ENDPOINT"],
)


def get_output_path(filename: str) -> str:
    """
    Returns the full output path for a given filename.
    """
    return os.path.join(OUT_DIR, filename)


def fits_frame(
    line_count: int, font: str, font_size: int, stroke_width: int, frame_width: int
) -> Callable[[str], bool]:
    """
    Returns a function that checks if a given text fits within the specified frame constraints.
    """

    def fit_function(text: str) -> bool:
        lines = calculate_lines(text, font, font_size, stroke_width, frame_width)
        return len(lines["lines"]) <= line_count

    return fit_function


def calculate_lines(
    text: str, font: str, font_size: int, stroke_width: int, frame_width: int
) -> Dict[str, Any]:
    """
    Splits text into lines that fit within the frame width, using caching for performance.
    Returns a dict with 'lines' (list of line dicts) and 'height' (total height).
    """
    global lines_cache
    arg_hash = hash((text, font, font_size, stroke_width, frame_width))
    if arg_hash in lines_cache:
        return lines_cache[arg_hash]

    lines: List[Dict[str, Any]] = []
    line_to_draw: Optional[Dict[str, Any]] = None
    line = ""
    words = text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font, font_size, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width < frame_width:
            line_to_draw = {
                "text": line.strip(),
                "height": line_height,
            }
            word_index += 1
        else:
            if not line_to_draw:
                print(f"NOTICE: Word '{line.strip()}' is too long for the frame!")
                line_to_draw = {
                    "text": line.strip(),
                    "height": line_height,
                }
                word_index += 1

            lines.append(line_to_draw)
            total_height += line_height
            line_to_draw = None
            line = ""

    if line_to_draw:
        lines.append(line_to_draw)
        total_height += line_height

    data = {
        "lines": lines,
        "height": total_height,
    }
    lines_cache[arg_hash] = data
    return data


def create_shadow(
    text: str, font_size: int, font: str, blur_radius: float, opacity: float = 1.0
) -> Any:
    """
    Creates a blurred shadow text clip for overlay, using caching for performance.
    """
    global shadow_cache
    arg_hash = hash((text, font_size, font, blur_radius, opacity))
    if arg_hash in shadow_cache:
        return shadow_cache[arg_hash].copy()

    shadow = create_text_ex(text, font_size, "black", font, opacity=opacity)
    shadow = blur_text_clip(shadow, int(font_size * blur_radius))
    shadow_cache[arg_hash] = shadow.copy()
    return shadow


def get_font_path(font: str) -> str:
    """
    Returns the full path to a font file, searching in the assets/fonts directory if needed.
    Raises FileNotFoundError if not found.
    """
    if os.path.exists(font):
        return font
    dirname = os.path.dirname(__file__)
    font_path = os.path.join(dirname, "assets", "fonts", font)
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font '{font}' not found")
    return font_path


def get_video_path(video_name: str) -> str:
    """
    Returns the full path to a video file, searching in the assets/videos directory if needed.
    Raises FileNotFoundError if not found.
    """
    if os.path.exists(video_name):
        return video_name
    dirname = os.path.dirname(__file__)
    video_path = os.path.join(dirname, "assets", "videos", video_name)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video '{video_name}' not found")
    return video_path


def add_captions(
    video: VideoFileClip,
    audio_file: Optional[str],
    img_file: Optional[str],
    output_file: Optional[str],
    font: str = "Bangers-Regular.ttf",
    font_size: int = 100,
    font_color: str = "yellow",
    stroke_width: int = 3,
    stroke_color: str = "black",
    highlight_current_word: bool = True,
    word_highlight_color: str = "red",
    line_count: int = 2,
    fit_function: Optional[Callable[[str], bool]] = None,
    padding: int = 50,
    shadow_strength: float = 1.0,
    shadow_blur: float = 0.1,
    print_info: bool = False,
    initial_prompt: Optional[str] = None,
    segments: Optional[Any] = None,
) -> None:
    """
    Adds animated captions and optional image overlay to a video, then writes the result to output_file.
    """
    _start_time = time.time()
    font = get_font_path(font)

    if print_info:
        print("Extracting audio...")

    if segments is None:
        if print_info:
            print("Transcribing audio...")
        segments = transcriber.transcribe_with_api(audio_file, initial_prompt)

    if print_info:
        print("Generating video elements...")

    text_bbox_width = video.w - padding * 2
    clips: List[Any] = [video]

    captions = segment_parser.parse(
        segments=segments,
        fit_function=fit_function
        if fit_function
        else fits_frame(
            line_count,
            font,
            font_size,
            stroke_width,
            text_bbox_width,
        ),
    )

    for caption in captions:
        captions_to_draw = []
        if highlight_current_word:
            for i, word in enumerate(caption["words"]):
                if i + 1 < len(caption["words"]):
                    end = caption["words"][i + 1].start
                else:
                    end = word.end
                captions_to_draw.append(
                    {
                        "text": caption["text"],
                        "start": word.start,
                        "end": end,
                    }
                )
        else:
            captions_to_draw.append(caption)

        for current_index, caption in enumerate(captions_to_draw):
            line_data = calculate_lines(
                caption["text"], font, font_size, stroke_width, text_bbox_width
            )
            text_y_offset = video.h // 2 - line_data["height"] // 2
            index = 0
            for line in line_data["lines"]:
                pos = ("center", text_y_offset)
                words = line["text"].split()
                word_list = []
                for w in words:
                    word_obj = Word(w)
                    if highlight_current_word and index == current_index:
                        word_obj.set_color(word_highlight_color)
                    index += 1
                    word_list.append(word_obj)

                # Create shadow
                shadow_left = shadow_strength
                while shadow_left >= 1:
                    shadow_left -= 1
                    shadow = create_shadow(
                        line["text"], font_size, font, shadow_blur, opacity=1
                    )
                    shadow = shadow.set_start(caption["start"])
                    shadow = shadow.set_duration(caption["end"] - caption["start"])
                    shadow = shadow.set_position(pos)
                    clips.append(shadow)
                if shadow_left > 0:
                    shadow = create_shadow(
                        line["text"], font_size, font, shadow_blur, opacity=shadow_left
                    )
                    shadow = shadow.set_start(caption["start"])
                    shadow = shadow.set_duration(caption["end"] - caption["start"])
                    shadow = shadow.set_position(pos)
                    clips.append(shadow)

                # Create text
                text_clip = create_text_ex(
                    word_list,
                    font_size,
                    font_color,
                    font,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                )
                text_clip = text_clip.set_start(caption["start"])
                text_clip = text_clip.set_duration(caption["end"] - caption["start"])
                text_clip = text_clip.set_position(pos)
                clips.append(text_clip)
                text_y_offset += line["height"]

    end_time = time.time()
    generation_time = end_time - _start_time

    if print_info:
        print(
            f"Generated in {generation_time // 60:02.0f}:{generation_time % 60:02.0f} ({len(clips)} clips)"
        )
        print("Rendering video...")

    if img_file is not None:
        image = ImageClip(img_file)
        image = image.set_duration(3)
        image = image.set_position(("center", "center"))
        image = image.set_start(0)
        clips.append(image)

    video_with_text = CompositeVideoClip(clips)
    if audio_file is not None:
        audio_clip = AudioFileClip(audio_file)
        video_with_text.audio = audio_clip

    if output_file is None:
        output_file = get_output_path("with_transcript.mp4")

    video_with_text.write_videofile(
        filename=output_file,
        codec="libx264",
        fps=video.fps,
        logger="bar" if print_info else None,
        remove_temp=True,
        audio_codec="pcm_s32le",
        threads=8,
    )

    end_time = time.time()
    total_time = end_time - _start_time
    render_time = total_time - generation_time

    print(f"Generated in {generation_time // 60:02.0f}:{generation_time % 60:02.0f}")
    print(f"Rendered in {render_time // 60:02.0f}:{render_time % 60:02.0f}")
    print(f"Done in {total_time // 60:02.0f}:{total_time % 60:02.0f}")


def generate_video_audio(transcript: str, audio_filename: str) -> float:
    """
    Generates speech audio from transcript and saves it to the given filename.
    Returns the duration of the audio in seconds.
    """
    speech_file_path = get_output_path(audio_filename)
    response = client.audio.speech.create(model="tts-1", voice="echo", input=transcript)
    response.stream_to_file(speech_file_path)
    return librosa.get_duration(path=speech_file_path)


def generate_video(img_file: Optional[str], transcript: str, post_title: str) -> None:
    """
    Generates a video with captions and optional image overlay, using the transcript and post title.
    The audio file is named dynamically based on the post title.
    """
    if not transcript.startswith(post_title):
        transcript = post_title + ". " + transcript

    # Use a dynamic audio filename based on post_title
    safe_title = "".join(
        c for c in post_title if c.isalnum() or c in (" ", "_", "-")
    ).rstrip()
    audio_filename = f"speech_{safe_title}.wav"
    audio_duration = generate_video_audio(transcript, audio_filename)
    video_duration = audio_duration + 0.5

    base_clip = VideoFileClip(get_video_path("base.mp4"))
    clip = base_clip.set_duration(video_duration)

    audio_file = get_output_path(audio_filename)
    video_output_file = get_output_path(f"{safe_title}.mp4")
    add_captions(
        video=clip,
        audio_file=audio_file,
        img_file=img_file,
        output_file=video_output_file,
    )
