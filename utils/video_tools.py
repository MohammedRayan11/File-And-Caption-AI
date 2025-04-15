import os
import concurrent.futures
import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import whisper
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
from pydub import AudioSegment  # For adding background music
from pydub.effects import normalize  # For audio normalization
import logging
from language_tool_python import LanguageTool  # For grammar correction
from langdetect import detect  # For language detection

# Constants
FONT_PATH = "arial.ttf"  # Replace with your font file path
FONT_SIZE = 24
TEXT_COLOR = "white"
BG_COLOR = "black"
MAX_CHARS_PER_LINE = 40
BACKGROUND_MUSIC = "background_music.mp3"  # Path to background music file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Mapping of detected languages to LanguageTool language codes
LANGUAGE_TOOL_CODES = {
    "en": "en-US",  # English
    "es": "es",     # Spanish
    "fr": "fr",     # French
    "de": "de",     # German
    "it": "it",     # Italian
    "pt": "pt",     # Portuguese
    "ru": "ru",     # Russian
    "zh": "zh",     # Chinese
    "ja": "ja",     # Japanese
    "ar": "ar",     # Arabic
    "hi": "hi",     # Hindi
    "bn": "bn",     # Bengali
    "tr": "tr",     # Turkish
    "nl": "nl",     # Dutch
    "pl": "pl",     # Polish
    "el": "el",     # Greek
    "sv": "sv",     # Swedish
    "fi": "fi",     # Finnish
    "vi": "vi",     # Vietnamese
    "th": "th",     # Thai
    "ur": "ur",     # Urdu
}

def extract_audio(video_path, audio_path):
    """Extract audio from a video using MoviePy."""
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        logging.info(f"Audio extracted and saved to {audio_path}")
        return True
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")
        raise

def transcribe_audio(audio_path):
    """Transcribe audio to text using Whisper with GPU acceleration if available."""
    try:
        model = whisper.load_model("base")  # Use "medium" or "large" for higher accuracy
        result = model.transcribe(audio_path, fp16=True, word_timestamps=True)
        logging.info("Audio transcription completed successfully.")
        return result
    except Exception as e:
        logging.error(f"Error transcribing audio: {e}")
        raise

def translate_text(text, dest_language):
    """Translate text to the desired language using Google Translate."""
    try:
        translation = GoogleTranslator(source='auto', target=dest_language).translate(text)
        logging.info(f"Translated text to {dest_language}: {translation}")
        return translation
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text  # Return the original text if translation fails

def detect_language(text):
    """Detect the language of the given text using langdetect."""
    try:
        lang_code = detect(text)
        logging.info(f"Detected language: {lang_code}")
        return lang_code
    except Exception as e:
        logging.error(f"Language detection error: {e}")
        return "en"  # Default to English if detection fails

def correct_grammar(text, language_code=None):
    """Correct grammar using LanguageTool for the detected or specified language."""
    try:
        if not language_code:
            # Detect the language if not provided
            lang_code = detect_language(text)
            language_code = LANGUAGE_TOOL_CODES.get(lang_code, "en-US")  # Default to English if language not supported
        tool = LanguageTool(language_code)
        corrected_text = tool.correct(text)
        logging.info(f"Grammar-corrected text ({language_code}): {corrected_text}")
        return corrected_text
    except Exception as e:
        logging.error(f"Grammar correction error for language {language_code}: {e}")
        return text  # Return the original text if correction fails

def make_text_human_like(text):
    """Make text more human-like using simple heuristics."""
    try:
        # Add filler words or rephrase for a conversational tone
        if not text.endswith((".", "!", "?")):
            text += "."  # Add a period if missing
        return text
    except Exception as e:
        logging.error(f"Human-like text conversion error: {e}")
        return text

def generate_captions(transcription, max_chars_per_line=MAX_CHARS_PER_LINE, dest_language=None):
    """Generate captions from transcription with word-level timestamps and optional translation."""
    captions = []
    current_line = ""
    current_start_time = 0
    current_end_time = 0

    for segment in transcription["segments"]:
        for word in segment["words"]:
            word_text = word["word"]
            word_start = word["start"]
            word_end = word["end"]

            if len(current_line) + len(word_text) + 1 <= max_chars_per_line:
                current_line += " " + word_text if current_line else word_text
                current_end_time = word_end
            else:
                if dest_language:
                    current_line = translate_text(current_line, dest_language)
                current_line = correct_grammar(current_line)  # Automatically detect language and correct grammar
                
                # Only make text human-like if the source and destination languages are different
                if dest_language != "en":
                    current_line = make_text_human_like(current_line)  # Make text more human-like
                
                captions.append((current_line.strip(), current_start_time, current_end_time))
                current_line = word_text
                current_start_time = word_start
                current_end_time = word_end

    if current_line:
        if dest_language:
            current_line = translate_text(current_line, dest_language)
        current_line = correct_grammar(current_line)  # Automatically detect language and correct grammar
        
        # Only make text human-like if the source and destination languages are different
        if dest_language != "en":
            current_line = make_text_human_like(current_line)  # Make text more human-like
        
        captions.append((current_line.strip(), current_start_time, current_end_time))

    logging.info(f"Generated captions: {captions}")
    return captions

def create_text_image(text, font_path, font_size, text_color, bg_color, video_width):
    """Create a text image with proper sizing and positioning."""
    try:
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Ensure the text fits within the video width
        max_text_width = video_width - 40  # Leave 20px padding on each side
        while text_width > max_text_width and font_size > 10:
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        # Create a semi-transparent background
        image = Image.new("RGBA", (video_width, text_height + 20), bg_color)
        draw = ImageDraw.Draw(image)

        # Center the text horizontally
        x = (video_width - text_width) // 2
        y = 10  # Add some padding at the top
        draw.text((x, y), text, font=font, fill=text_color)

        return np.array(image)
    except Exception as e:
        logging.error(f"Error creating text image: {e}")
        raise
def add_captions_to_video(video_path, captions, output_path, font_path=FONT_PATH, font_size=FONT_SIZE, text_color=TEXT_COLOR, bg_color=BG_COLOR, text_style="arial", text_position="bottom"):
    """Add captions to a video, synced with the audio."""
    try:
        video = mp.VideoFileClip(video_path)
        caption_clips = []

        # Map text style to font file
        font_mapping = {
            "arial": "arial.ttf",
            "times": "times.ttf",
            "courier": "cour.ttf",
            "verdana": "verdana.ttf",
            "comic-sans": "comic.ttf",
        }
        font_path = font_mapping.get(text_style, "arial.ttf")  # Default to Arial if style not found

        # Map text position to MoviePy position
        position_mapping = {
            "top": ("center", "top"),
            "bottom": ("center", "bottom"),
            "center": ("center", "center"),
        }
        position = position_mapping.get(text_position, ("center", "bottom"))  # Default to bottom

        for caption, start_time, end_time in captions:
            # Create a text image for the caption
            text_image = create_text_image(caption, font_path, int(font_size), text_color, bg_color, video.size[0])

            # Create a text clip with the correct duration and position
            text_clip = ImageClip(text_image).set_duration(end_time - start_time).set_start(start_time).set_position(position)
            caption_clips.append(text_clip)

        # Combine video and captions
        final_video = CompositeVideoClip([video] + caption_clips)

        # Add background music
        if os.path.exists(BACKGROUND_MUSIC):
            background_music = mp.AudioFileClip(BACKGROUND_MUSIC)
            final_video = final_video.set_audio(mp.CompositeAudioClip([final_video.audio, background_music]))

        # Write the final video
        final_video.write_videofile(output_path, codec="libx264", threads=4, logger=None)
        logging.info(f"Video with captions saved to {output_path}")
    except Exception as e:
        logging.error(f"Error adding captions to video: {e}")
        raise
def process_video(video_path, output_path, dest_language=None, text_style="arial", text_size="24", text_position="bottom", text_color="#ffffff"):
    """Process a video to generate captions and update it."""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        audio_path = os.path.join(temp_dir, "temp_audio.wav")
        extract_audio(video_path, audio_path)

        transcription = transcribe_audio(audio_path)
        print("Transcribed Text:", transcription["text"])

        captions = generate_captions(transcription, dest_language=dest_language)
        print("Generated Captions:", captions)

        # Pass user-selected options to add_captions_to_video
        add_captions_to_video(
            video_path,
            captions,
            output_path,
            font_path=FONT_PATH,
            font_size=int(text_size),
            text_color=text_color,
            bg_color=BG_COLOR,
            text_style=text_style,
            text_position=text_position
        )

        # Clean up temporary files
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        raise