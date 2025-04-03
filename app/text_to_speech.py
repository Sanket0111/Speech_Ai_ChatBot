#!/usr/bin/env python3
"""
Text-to-Speech conversion module (Bonus).
Converts translated text back into speech.

Assignment Deliverable: Bonus
"""

import os
import json
import argparse
import tempfile
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Language code mapping for TTS
LANGUAGE_CODES = {
    "hindi": "hi",
    "bengali": "bn",
    "telugu": "te",
    "marathi": "mr",
    "tamil": "ta",
    "urdu": "ur",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa"
}

def load_translation(translation_file):
    """Load translation from JSON file."""
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translation = json.load(f)
        return translation
    except Exception as e:
        print(f"Error loading translation: {e}")
        return None

def find_translation_file():
    """Find the most recent translation file."""
    data_dir = Path("app/data")
    
    # First check for assignment deliverable file
    if os.path.exists(os.path.join(data_dir, "translated.json")):
        return os.path.join(data_dir, "translated.json")
    
    translation_files = list(data_dir.glob("translated_*.json"))
    
    if not translation_files:
        print("No translation files found in data directory.")
        return None
    
    # Sort by modification time, newest first
    translation_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return str(translation_files[0])

def text_to_speech(text, language, output_file=None):
    """Convert text to speech and save as audio file."""
    try:
        print(f"Converting text to speech in {language}...")
        
        # Create gTTS object
        tts = gTTS(text=text, lang=language, slow=False)
        
        # If output file is not specified, create a temp file
        if output_file is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            output_file = temp_file.name
            temp_file.close()
        
        # Save to file
        tts.save(output_file)
        print(f"Speech saved to: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"Error converting text to speech: {e}")
        return None

def concatenate_audio_segments(translation, language, output_dir="app/data"):
    """Generate speech for each segment and concatenate them."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean the title to create a valid filename
        safe_title = "".join(c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in translation.get("title", "output"))
        safe_title = safe_title.strip().replace(' ', '_')
        
        # Final output file
        output_file = os.path.join(output_dir, f"speech_{language}_{safe_title}.mp3")
        
        # Also save as output_audio.mp3 for assignment deliverable
        assignment_output = os.path.join(output_dir, "output_audio.mp3")
        
        # Create a temp directory for segment audio files
        temp_dir = tempfile.mkdtemp()
        
        # Generate speech for each segment
        segment_files = []
        total_segments = len(translation["segments"])
        
        for i, segment in enumerate(translation["segments"]):
            if i % 10 == 0:
                print(f"Processing segment {i+1}/{total_segments}")
            
            # Create speech for translated text
            segment_file = os.path.join(temp_dir, f"segment_{i}.mp3")
            text_to_speech(segment["translated"], language, segment_file)
            segment_files.append(segment_file)
        
        # Concatenate all segments
        print("Concatenating audio segments...")
        combined = AudioSegment.empty()
        
        for segment_file in segment_files:
            audio_segment = AudioSegment.from_mp3(segment_file)
            combined += audio_segment
            
            # Add a short pause between segments
            pause = AudioSegment.silent(duration=500)  # 500ms pause
            combined += pause
        
        # Export final audio
        combined.export(output_file, format="mp3")
        
        # Also export as assignment deliverable
        combined.export(assignment_output, format="mp3")
        
        # Clean up temp files
        for segment_file in segment_files:
            try:
                os.remove(segment_file)
            except:
                pass
        
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        print(f"Complete audio saved to: {output_file}")
        print(f"Assignment deliverable saved as: {assignment_output}")
        return output_file
        
    except Exception as e:
        print(f"Error creating concatenated audio: {e}")
        return None

def main():
    """Main function to convert translated text to speech."""
    parser = argparse.ArgumentParser(description="Convert translated text to speech.")
    parser.add_argument("--input", type=str, help="Input translation JSON file")
    parser.add_argument("--output", type=str, help="Output audio file")
    parser.add_argument("--language", type=str, help="Language code for speech synthesis")
    
    args = parser.parse_args()
    
    # Find translation file if not provided
    if args.input is None:
        args.input = find_translation_file()
        if args.input is None:
            print("No translation file found.")
            return
    
    # Load translation data
    translation = load_translation(args.input)
    
    if translation:
        # Determine language from translation or argument
        if args.language:
            language_code = LANGUAGE_CODES.get(args.language.lower())
            if language_code is None:
                print(f"Unsupported language: {args.language}")
                return
        else:
            # Try to get language from translation data
            target_language = translation.get("target_language")
            if target_language:
                language_code = target_language
            else:
                print("Language not specified and not found in translation data.")
                return
        
        # Generate speech and concatenate segments
        output_file = concatenate_audio_segments(translation, language_code, os.path.dirname(args.output) if args.output else "app/data")
        
        if output_file:
            print(f"Successfully converted text to speech and saved to {output_file}")
            return output_file
    
    print("Text-to-speech conversion failed.")
    return None

if __name__ == "__main__":
    main() 